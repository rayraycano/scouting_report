import requests
from typing import Iterable, Any, Dict
from llms.interface import LLM
import json
import os


PROVIDER_STR = "perplexity"
_VALID_NAMES = {
    "llama-3-sonar-small-32k-chat",
    "llama-3-sonar-small-32k-online",
    "llama-3-sonar-large-32k-chat",
    "llama-3-sonar-large-32k-online",
    "llama-3-8b-instruct",
    "llama-3-70b-instruct",
    "mixtral-8x7b-instruct",
}


class PerplexityLLM(LLM):

    def __init__(self, model_name: str):
        self.api_key = os.environ["PERPLEXITY_API_KEY"]
        if model_name not in _VALID_NAMES:
            raise Exception("invalid model name: {}".format(model_name))

        self.name = "-".join([PROVIDER_STR, model_name])
        self.model_name = model_name

    def _create_request(self, system_prompt: str, user_prompt: str) -> Dict[str, Any]:
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        return payload

    def request_stream(
        self, system_prompt: str, user_prompt: str, **kwargs
    ) -> Iterable[str]:
        pass

    def request(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        req = self._create_request(system_prompt, user_prompt)
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "authorization": f"Bearer {self.api_key}",
        }
        url = "https://api.perplexity.ai/chat/completions"
        response = requests.post(url, json=req, headers=headers)
        if not response.ok:
            print(response)
            raise Exception("response not ok")
        try:
            body = json.loads(response.text)
            return json.loads(
                body["choices"][0]["message"]["content"].replace("[END]", "")
            )
        except:
            return response.text

    def get_name(self) -> str:
        return self.name
