import os
import uuid
import logging

# chain
from langchain_core.runnables import RunnableBranch
from langchain_core.runnables import RunnableLambda

# model
from langchain_community.llms.ctransformers import CTransformers
from langchain_openai import ChatOpenAI  # ChatOpenAI模型

# callbacks
from langchain_core.callbacks import StreamingStdOutCallbackHandler

# tools
from .vector_db import VectorDB

# prompt
from langchain.prompts import PromptTemplate
from .prompt import MULTI_PROMPT_ROUTER_TEMPLATE as RounterTemplate
from .prompt import LAWYER_PROMPT_TEMPLATE as LawyerTemplate
from .prompt import EXPLAIN_PROMPT_TEMPLATE as ExplainTemplate

# parser
from langchain.chains.router.llm_router import RouterOutputParser
from langchain_core.output_parsers import StrOutputParser

# history
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from .history import ChatHistory

# config
from .config import Config


class legal_bot:
    basic_llm = ChatOpenAI(
        model=Config.LLM_CONFIG["model"],
        api_key=Config.LLM_CONFIG["api_key"],
        base_url=Config.LLM_CONFIG["base_url"],
        temperature=Config.LLM_CONFIG["temperature"],
        # callbacks=[StreamingStdOutCallbackHandler()],
    )

    # legal_llm = CTransformers(
    #     model=Config.LLM_CONFIG["model_path"],
    #     model_type=Config.LLM_CONFIG["model_type"],
    #     config={"temperature": Config.LLM_CONFIG["temperature"], "gpu_layers": 500},
    #     # callbacks=[StreamingStdOutCallbackHandler()],
    # )

    vectordb = VectorDB()  # 向量数据库

    chain = None  # 对话链
    chat_history = ChatHistory()  # 对话历史管理器

    def __init__(self):
        if not legal_bot.chain:
            self._create_chain()

    def _create_chain(self):
        # router chain
        prompt_dicts = [
            {
                "key": "lawyer",
                "description": "适合根据相关法条回答实际问题",
            },
            {
                "key": "explain",
                "description": "适合回答相关法律条文或概念相关的问题",
            },
        ]
        router_template = RounterTemplate.format(
            destinations="\n".join([f"{p['key']}: {p['description']}" for p in prompt_dicts])
        )
        router_prompt = PromptTemplate(
            template=router_template,
            input_variables=["input"],
        )
        router_chain = router_prompt | legal_bot.basic_llm | RouterOutputParser()
        # lawyer chain
        lawyer_prompt = PromptTemplate(
            template=LawyerTemplate,
            input_variables=["input", "laws"],
        )
        lawyer_chain = lawyer_prompt | legal_bot.basic_llm | StrOutputParser()
        # explain chain
        explain_prompt = PromptTemplate(
            template=ExplainTemplate,
            input_variables=["input"],
        )
        explain_chain = explain_prompt | legal_bot.basic_llm | StrOutputParser()
        # retriever
        retriever = legal_bot.vectordb.retriever

        # branch
        branch = RunnableBranch(
            (lambda x: x["router"]["destination"] is None, lawyer_chain),
            (lambda x: "lawyer" in x["router"]["destination"], lawyer_chain),
            (lambda x: "explain" in x["router"]["destination"], explain_chain),
            lawyer_chain,
        )

        # 最终链
        chain = {
            "router": router_chain,
            "laws": RunnableLambda(lambda x: "".join(legal_bot.vectordb.get_similar_contents(x["input"]))),
            "input": PromptTemplate.from_template("{input}"),
            "history": PromptTemplate.from_template("{history}"),
        } | branch

        legal_bot.chain = RunnableWithMessageHistory(
            chain,
            legal_bot.chat_history.get_session_history,
            input_messages_key="input",
            history_messages_key="history",
        )

    def invoke(self, query: str, session_id: str = None):
        try:
            if not session_id:
                session_id = str(uuid.uuid4())
            if not self.validate_input(query):
                return "输入内容不合法,请重新输入"
            ans = legal_bot.chain.invoke(
                {"input": query},
                config={"configurable": {"session_id": session_id}},
            )
            return ans
        except Exception as e:
            logging.error(f"Error in invoke: {str(e)}")
            return "抱歉，系统出现了一些问题，请稍后再试。"

    def stream(self, query: str, session_id: str = None):
        try:
            if not session_id:
                session_id = str(uuid.uuid4())
            if not self.validate_input(query):
                yield "输入内容不合法,请重新输入"
                return
            for i in legal_bot.chain.stream(
                {"input": query},
                config={"configurable": {"session_id": session_id}},
            ):
                yield i
        except Exception as e:
            logging.error(f"Error in stream: {str(e)}")
            yield "抱歉，系统出现了一些问题，请稍后再试。"

    def validate_input(self, query: str) -> bool:
        if not query or len(query.strip()) == 0:
            return False
        if len(query) > 1000:  # 限制输入长度
            return False
        return True
