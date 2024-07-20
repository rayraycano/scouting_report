import os
import time
from typing import Iterable

import modal
from llms.interface import LLM

MODEL_ID = "modal-vllm-mixtral"
_MODEL_DIR = "/model"
_MODEL_NAME = "mistralai/Mixtral-8x7B-Instruct-v0.1"
_GPU_CONFIG = modal.gpu.A100(memory=80, count=2)


def download_model_to_image(model_dir, model_name):
    from huggingface_hub import snapshot_download
    from transformers.utils import move_cache

    os.makedirs(model_dir, exist_ok=True)

    snapshot_download(
        model_name,
        local_dir=model_dir,
        ignore_patterns=["*.pt", "*.bin"],  # Using safetensors
    )
    move_cache()


vllm_image = (
    modal.Image.debian_slim()
    .pip_install(
        "vllm==0.4.0.post1",
        "torch==2.1.2",
        "transformers==4.39.3",
        "ray==2.10.0",
        "hf-transfer==0.1.6",
        "huggingface_hub==0.22.2",
    )
    .env({"HF_HUB_ENABLE_HF_TRANSFER": "1"})
    .run_function(
        download_model_to_image,
        timeout=60 * 20,
        kwargs={"model_dir": _MODEL_DIR, "model_name": _MODEL_NAME},
    )
)

stub = modal.Stub("vllm-scouting-report")


@stub.cls(
    gpu=_GPU_CONFIG,
    timeout=60 * 10,
    container_idle_timeout=60 * 10,
    allow_concurrent_inputs=10,
    image=vllm_image,
)
class ModalModel(LLM):

    def __init__(self):
        self.model_id = MODEL_ID

    def get_name(self) -> str:
        return self.model_id

    @modal.enter()
    def start_engine(self):
        from vllm.engine.arg_utils import AsyncEngineArgs
        from vllm.engine.async_llm_engine import AsyncLLMEngine

        print("🥶 cold starting inference")
        start = time.monotonic_ns()

        engine_args = AsyncEngineArgs(
            model=_MODEL_DIR,
            tensor_parallel_size=_GPU_CONFIG.count,
            gpu_memory_utilization=0.90,
            enforce_eager=False,  # capture the graph for faster inference, but slower cold starts
            disable_log_stats=True,  # disable logging so we can stream tokens
            disable_log_requests=True,
        )
        self.template = "<s> [INST] {system} \n {user} [/INST] "

        # this can take some time!
        self.engine = AsyncLLMEngine.from_engine_args(engine_args)
        duration_s = (time.monotonic_ns() - start) / 1e9
        print(f"🏎️ engine started in {duration_s:.0f}s")

    def request_stream(
        self, system_prompt: str, user_prompt: str, **kwargs
    ) -> Iterable[str]:
        pass

    def request(self, system_prompt, user_prompt, **kwargs) -> str:
        text = []
        with stub.run() as ctx:
            for t in self._request.remote_gen(system_prompt, user_prompt):
                text.append(t)
        return "".join(text)

    @modal.method()
    async def _request(self, system_prompt, user_prompt, *args, **kwargs) -> str:
        from vllm import SamplingParams
        from vllm.utils import random_uuid

        sampling_params = SamplingParams(
            temperature=0.75,
            max_tokens=4096 * 4,
            repetition_penalty=1.1,
        )

        request_id = random_uuid()
        result_generator = self.engine.generate(
            self.template.format(system=system_prompt, user=user_prompt),
            sampling_params,
            request_id,
        )
        index, num_tokens = 0, 0
        start = time.monotonic_ns()
        async for output in result_generator:
            if output.outputs[0].text and "\ufffd" == output.outputs[0].text[-1]:
                continue
            text_delta = output.outputs[0].text[index:]
            index = len(output.outputs[0].text)
            num_tokens = len(output.outputs[0].token_ids)
            yield text_delta

        duration_s = (time.monotonic_ns() - start) / 1e9

        print(
            f"\n\tGenerated {num_tokens} tokens from {_MODEL_NAME} in {duration_s:.1f}s,"
            f" throughput = {num_tokens / duration_s:.0f} tokens/second on {_GPU_CONFIG}.\n"
        )

    @modal.method()
    async def completion_stream(self, user_question):
        from vllm import SamplingParams
        from vllm.utils import random_uuid

        sampling_params = SamplingParams(
            temperature=0.75,
            max_tokens=128,
            repetition_penalty=1.1,
        )

        request_id = random_uuid()
        result_generator = self.engine.generate(
            self.template.format(user=user_question),
            sampling_params,
            request_id,
        )
        index, num_tokens = 0, 0
        start = time.monotonic_ns()
        async for output in result_generator:
            if output.outputs[0].text and "\ufffd" == output.outputs[0].text[-1]:
                continue
            text_delta = output.outputs[0].text[index:]
            index = len(output.outputs[0].text)
            num_tokens = len(output.outputs[0].token_ids)

            yield text_delta
        duration_s = (time.monotonic_ns() - start) / 1e9

        yield (
            f"\n\tGenerated {num_tokens} tokens from {_MODEL_NAME} in {duration_s:.1f}s,"
            f" throughput = {num_tokens / duration_s:.0f} tokens/second on {_GPU_CONFIG}.\n"
        )

    @modal.exit()
    def stop_engine(self):
        if _GPU_CONFIG.count > 1:
            import ray

            ray.shutdown()
