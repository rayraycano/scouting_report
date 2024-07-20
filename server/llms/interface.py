from typing import Iterable
import abc


class LLM(abc.ABC):

    @abc.abstractmethod
    def request_stream(
        self, system_prompt: str, user_prompt: str, **kwargs
    ) -> Iterable[str]:
        pass

    @abc.abstractmethod
    def request(self, system_prompt: str, user_prompt: str, **kwargs) -> str:
        pass

    @abc.abstractmethod
    def get_name(self) -> str:
        pass
