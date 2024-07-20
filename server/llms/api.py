from typing import Dict, List
from llms.gpt4 import GPT4, GPT_4_MODEL_NAME, _GPT_4_MODEL_ID
from llms.baseten import BasetenModel, _BASETEN_MODEL_ID
from llms.modal import ModalModel
from llms.interface import LLM
from llms.modal import MODEL_ID as MODAL_MIXTRAL_ID
from llms.baseten import MODEL_ID as BASETEN_MIXTRAL_ID


def primary_model_name() -> str:
    return GPT_4_MODEL_NAME


def secondary_model_names() -> List[str]:
    return [MODAL_MIXTRAL_ID, BASETEN_MIXTRAL_ID]


def init_models() -> List[LLM]:
    gpt4 = GPT4(_GPT_4_MODEL_ID)
    baseten_mixtral = BasetenModel(_BASETEN_MODEL_ID)
    modal_mixtral = ModalModel()

    return [
        gpt4,
        baseten_mixtral,
        modal_mixtral,
    ]
