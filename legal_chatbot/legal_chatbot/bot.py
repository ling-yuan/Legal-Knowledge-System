import os
import uuid
import logging

# chain
from langchain_core.runnables import RunnableBranch
from langchain_core.runnables import RunnableLambda

# model
from openai import OpenAI
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
        self.sensitive_words = ["敏感词1", "敏感词2"]  # 添加敏感词列表

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
            input_variables=["input", "history", "laws"],
        )
        lawyer_chain = lawyer_prompt | legal_bot.basic_llm | StrOutputParser()
        # explain chain
        explain_prompt = PromptTemplate(
            template=ExplainTemplate,
            input_variables=["input", "history", "laws"],
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
            "laws": RunnableLambda(lambda x: "\n".join(legal_bot.vectordb.get_similar_contents(x["input"]))),
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
                return {
                    "status": False,
                    "thinking": "",
                    "answer": "输入内容不合法,请重新输入",
                }
            ans = legal_bot.chain.invoke(
                {"input": query},
                config={"configurable": {"session_id": session_id}},
            )
            return {
                "status": "answer",
                "thinking": "",
                "answer": ans,
            }
        except Exception as e:
            logging.error(f"Error in invoke: {str(e)}")
            return {
                "status": False,
                "thinking": "",
                "answer": "抱歉，系统出现了一些问题，请稍后再试。",
            }

    def stream(self, query: str, session_id: str = None):
        try:
            if not session_id:
                session_id = str(uuid.uuid4())
            if not self.validate_input(query):
                yield {
                    "status": False,
                    "thinking": "",
                    "answer": "输入内容不合法,请重新输入",
                }
                return
            for i in legal_bot.chain.stream(
                {"input": query},
                config={"configurable": {"session_id": session_id}},
            ):
                yield {
                    "status": "answer",
                    "thinking": "",
                    "answer": i,
                }
        except Exception as e:
            logging.error(f"Error in stream: {str(e)}")
            yield {
                "status": False,
                "thinking": "",
                "answer": "抱歉，系统出现了一些问题，请稍后再试。",
            }

    def validate_input(self, query: str) -> bool:
        if not query or len(query.strip()) == 0:
            return False
        if len(query) > 1000:  # 限制输入长度
            return False
        if any(word in query for word in self.sensitive_words):  # 检查敏感词
            return False
        return True


class legal_bot_thinking:

    chat_model = ChatOpenAI(
        model=Config.LLM_CONFIG["chat_model"],
        api_key=Config.LLM_CONFIG["api_key"],
        base_url=Config.LLM_CONFIG["base_url"],
        temperature=Config.LLM_CONFIG["temperature"],
    )

    thinking_model = OpenAI(
        api_key=Config.LLM_CONFIG["api_key"],
        base_url=Config.LLM_CONFIG["base_url"],
    )

    vectordb = VectorDB()  # 向量数据库

    chat_history = ChatHistory()  # 对话历史管理器

    def __init__(self):
        self.sensitive_words = ["敏感词1", "敏感词2"]  # 添加敏感词列表
        self._generate_router_chain()

    def _generate_router_chain(self):
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
        legal_bot_thinking.router_chain = router_prompt | legal_bot_thinking.chat_model | RouterOutputParser()

    def stream(self, query: str, session_id: str = None):
        try:
            exist_session_id = True
            if not session_id:
                exist_session_id = False
                session_id = str(uuid.uuid4())
            if not self.validate_input(query):
                yield {
                    "status": False,
                    "thinking": "",
                    "answer": "输入内容不合法,请重新输入",
                }
                return
            # 获取路由链中返回的destination
            router_result = legal_bot_thinking.router_chain.invoke({"input": query})
            # 根据destination选择合适的prompt
            prompt = PromptTemplate(
                template=ExplainTemplate if router_result["destination"] == "explain" else LawyerTemplate,
                input_variables=["input", "history", "laws"],
            )
            # 获取相关法律条文
            laws = "\n".join(legal_bot_thinking.vectordb.get_similar_contents(query))
            # 获取对话历史
            history_messages = legal_bot_thinking.chat_history.get_session_history(session_id)
            history = "\n".join(
                [
                    f"{'Human' if index%2==0 else 'AI'}: {msg.content}"
                    for index, msg in enumerate(history_messages.messages)
                ]
            )
            # 流式输出思考链和回答
            reasoning_content = ""
            content = ""
            response = legal_bot_thinking.thinking_model.chat.completions.create(
                model=Config.LLM_CONFIG["thinking_model"],
                messages=[
                    {
                        "role": "user",
                        "content": prompt.format(input=query, history=history, laws=laws),
                    }
                ],
                stream=True,
            )
            flag = True  # 判断是否存在思考链
            for chunk in response:
                tmp_ans = ""
                if chunk.choices[0].delta.reasoning_content:
                    if flag:
                        flag = False
                    tmp_ans = chunk.choices[0].delta.reasoning_content or ""
                else:
                    if not flag:
                        flag = True
                    tmp_ans = chunk.choices[0].delta.content or ""
                reasoning_content += tmp_ans if not flag else ""
                content += tmp_ans if flag else ""
                yield {
                    "status": "thinking" if not flag else "answer",
                    "thinking": tmp_ans if not flag else "",
                    "answer": tmp_ans if flag else "",
                }
            # 将回答加入对话历史
            if exist_session_id:
                legal_bot_thinking.chat_history.add_message(session_id, {"human": query})
                legal_bot_thinking.chat_history.add_message(session_id, {"ai": content})
        except Exception as e:
            logging.error(f"Error in stream: {str(e)}")
            yield {
                "status": False,
                "thinking": "",
                "answer": "抱歉，系统出现了一些问题，请稍后再试。",
            }

    def invoke(self, query: str, session_id: str = None):
        try:
            if not session_id:
                session_id = str(uuid.uuid4())
            if not self.validate_input(query):
                return {
                    "status": False,
                    "thinking": "",
                    "answer": "输入内容不合法,请重新输入",
                }
            reasoning_content = ""
            content = ""
            for i in self.stream(query, session_id):
                if i.get("thinking"):
                    reasoning_content += i["thinking"]
                if i.get("answer"):
                    content += i["answer"]
            return {
                "status": True,
                "thinking": reasoning_content,
                "answer": content,
            }

        except Exception as e:
            logging.error(f"Error in invoke: {str(e)}")
            return {
                "status": False,
                "thinking": "",
                "answer": "抱歉，系统出现了一些问题，请稍后再试。",
            }

    def validate_input(self, query: str) -> bool:
        if not query or len(query.strip()) == 0:
            return False
        if len(query) > 1000:  # 限制输入长度
            return False
        if any(word in query for word in self.sensitive_words):  # 检查敏感词
            return False
        return True
