import os

# chain
from langchain_core.runnables import RunnableBranch

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


class leagal_bot:
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
    vectordb = VectorDB()

    chain = None

    def __init__(self):
        if not leagal_bot.chain:
            self._create_chain()

    def _create_chain(self):
        # 路由链
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
        router_chain = router_prompt | leagal_bot.basic_llm | RouterOutputParser()
        # leagal_bot.chain = router_chain
        # lawyer chain
        lawyer_prompt = PromptTemplate(
            template=LawyerTemplate,
            input_variables=["input"],
        )
        lawyer_chain = lawyer_prompt | leagal_bot.basic_llm | StrOutputParser()
        # explain chain
        explain_prompt = PromptTemplate(
            template=ExplainTemplate,
            input_variables=["input"],
        )
        explain_chain = explain_prompt | leagal_bot.basic_llm | StrOutputParser()
        # retriever
        retriever = leagal_bot.vectordb.retriever

        # branch
        branch = RunnableBranch(
            (lambda x: x["router"]["destination"] is None, lawyer_chain),
            (lambda x: "lawyer" in x["router"]["destination"], lawyer_chain),
            (lambda x: "explain" in x["router"]["destination"], explain_chain),
            lawyer_chain,
        )

        # 最终链
        leagal_bot.chain = {
            "router": router_chain,
            "laws": retriever,
            "input": PromptTemplate.from_template("{input}"),
        } | branch

    def invoke(self, query):
        return leagal_bot.chain.invoke(query)

    def stream(self, query):
        for i in leagal_bot.chain.stream(query):
            yield i
