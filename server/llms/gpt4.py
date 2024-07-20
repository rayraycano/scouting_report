from typing import Iterable

from openai import OpenAI
from llms.interface import LLM

_GPT_4_MODEL_ID = "gpt-4-0125-preview"


def generate_model_name(id: str):
    return f"openai-{id}"


GPT_4_MODEL_NAME = generate_model_name(_GPT_4_MODEL_ID)


class GPT4(LLM):
    def __init__(self, model_id):
        self.client = OpenAI()
        self.model_id = model_id

    def get_name(self):
        return generate_model_name(self.model_id)

    def request_stream(
        self, system_prompt: str, user_prompt: str, **kwargs
    ) -> Iterable[str]:
        # TODO: Investigate how to handle the streaming responses
        stream = self.client.chat.completions.create(
            model=self.model_id,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            stream=True,
            **kwargs,
        )
        for chunk in stream:
            if chunk.choices[0].delta:
                yield chunk.choices[0].delta.content

    def request(self, system_prompt, user_prompt, **kwargs) -> str:

        completion = self.client.chat.completions.create(
            model=self.model_id,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            **kwargs,
        )
        return completion.choices[0].message.content
