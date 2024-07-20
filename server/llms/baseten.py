from typing import Iterable

import requests
import os
from llms.interface import LLM

_BASETEN_MODEL_ID = "4q92ynxw"  # Mixtral 8x7B Instruct TRT-LLM Weights Only Quantized


def format_model_id(id: str):
    return f"baseten-{id}"


MODEL_ID = format_model_id(_BASETEN_MODEL_ID)


class BasetenModel(LLM):
    def __init__(self, model_id: str):
        self.model_id = model_id
        self.api_key = os.environ["BASETEN_API_KEY"]

    def get_name(self):
        return f"baseten-{self.model_id}"

    def request_stream(
        self, system_prompt: str, user_prompt: str, **kwargs
    ) -> Iterable[str]:
        pass

    def request(self, system_prompt, user_prompt, **kwargs) -> str:

        resp = requests.post(
            f"https://model-{self.model_id}.api.baseten.co/production/predict",
            headers={"Authorization": f"Api-Key {self.api_key}"},
            json={
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "max_tokens": 32768,
            },
        )
        return resp.content.decode("utf-8")
