import os
import uuid

# chain
from langchain_core.runnables import RunnableBranch
from langchain_core.runnables import RunnableLambda

# model
from langchain_community.llms.ctransformers import CTransformers
from langchain_openai import ChatOpenAI  # ChatOpenAI模型

# callbacks
from langchain_core.callbacks import StreamingStdOutCallbackHandler
import legal_chatbot

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


class legal_bot:
    basic_llm = ChatOpenAI(
        model=os.environ["LLM_MODELEND"],
        api_key=os.environ["OPENAI_API_KEY"],
        base_url=os.environ["OPENAI_BASE_URL"],
        temperature=0,
        # callbacks=[StreamingStdOutCallbackHandler()],
    )

    # legal_llm = CTransformers(
    #     model=os.environ.get("MODEL_PATH"),
    #     model_type=os.environ.get("MODEL_TYPE"),
    #     config={"temperature": 0.1, "gpu_layers": 500},
    #     callbacks=[StreamingStdOutCallbackHandler()],
    # )

    vectordb = VectorDB()  # 向量数据库

    chain = None  # 对话链

    store = {}  # 存储历史对话

    @classmethod
    def get_session_history(cls, session_id: str) -> BaseChatMessageHistory:
        if session_id not in cls.store:
            cls.store[session_id] = ChatMessageHistory()
        return cls.store[session_id]

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
            legal_bot.get_session_history,
            input_messages_key="input",
            history_messages_key="history",
        )

    def invoke(self, query: str, session_id: str = None):
        if not session_id:
            session_id = str(uuid.uuid4())
        ans = legal_bot.chain.invoke(
            {"input": query},
            config={"configurable": {"session_id": session_id}},
        )
        if not session_id:
            legal_bot.store.pop(session_id, None)
        return ans

    def stream(self, query: str, session_id: str = None):
        if not session_id:
            session_id = str(uuid.uuid4())
        for i in legal_bot.chain.stream(
            {"input": query},
            config={"configurable": {"session_id": session_id}},
        ):
            yield i
        if not session_id:
            legal_bot.store.pop(session_id, None)
