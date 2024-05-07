import json
import requests
import logging
from typing import List
from langchain.chains.llm import LLMChain
from langchain.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_community.callbacks import get_openai_callback
from langchain_core.messages import SystemMessage

from ..common.Answer import Answer
from ..helpers.ConfigHelper import ConfigHelper
from ..helpers.LLMHelper import LLMHelper
from ..helpers.EnvHelper import EnvHelper

from .AnsweringToolBase import AnsweringToolBase

logger = logging.getLogger(__name__)


class FunctionAnswerTool(AnsweringToolBase):
    def __init__(self) -> None:
        self.name = "FunctionAnswer"
        self.env_helper = EnvHelper()
        self.llm_helper = LLMHelper()
        self.verbose = True

        self.config = ConfigHelper.get_active_config_or_default()

    def answer_question(
        self, question: str, chat_history: List[dict], **kwargs
    ) -> Answer:

        response = requests.post(
            f"{self.env_helper.RAJA_ENDPOINT}/api/pack",
            json=json.dumps(kwargs),
            timeout=5,
        )

        answering_prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(content=self.config.prompts.answering_system_prompt),
                SystemMessage(content=self.env_helper.AZURE_OPENAI_SYSTEM_MESSAGE),
                MessagesPlaceholder("chat_history"),
                HumanMessagePromptTemplate.from_template(
                    self.config.prompts.answering_user_prompt
                ),
            ]
        )

        llm_helper = LLMHelper()

        answer_generator = LLMChain(
            llm=llm_helper.get_llm(),
            prompt=answering_prompt,
            verbose=self.verbose,
        )

        articles = json.dumps(
            {
                "retrieved_documents": [
                    {
                        "[doc"
                        + str(i + 1)
                        + "]": {
                            "description": source["short_description"],
                            "sku_title": source["sku_title"],
                        }
                    }
                    for i, source in enumerate(response.json())
                ],
            },
            separators=(",", ":"),
        )

        with get_openai_callback() as cb:
            result = answer_generator(
                {
                    "chat_history": chat_history,
                    "question": question,
                    "sources": articles,
                }
            )

        answer = result["text"]
        logger.debug(f"Answer: {answer}")

        answer = Answer(
            question=question,
            answer=answer,
            source_documents=[],
            prompt_tokens=cb.prompt_tokens,
            completion_tokens=cb.completion_tokens,
        )

        return answer
