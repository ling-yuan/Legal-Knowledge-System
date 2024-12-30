# # from legal_chatbot import leagal_bot

# # bot = leagal_bot()

# # ans = bot.get_response("如果我的老板没有给我发工资，我应该如何维权？")
# # print(ans)
# import os

# # model
# from langchain_community.llms.ctransformers import CTransformers
# from langchain_openai import ChatOpenAI  # ChatOpenAI模型
# from langchain_experimental.sql import SQLDatabaseChain

# # callbacks
# from langchain_core.callbacks import StreamingStdOutCallbackHandler

# # agent
# from langchain_community.agent_toolkits.sql.base import create_sql_agent
# from langchain.agents.agent_types import AgentType

# # tools
# from langchain_community.utilities import SQLDatabase
# from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit

# # prompt
# from langchain.prompts import PromptTemplate
# from legal_chatbot import MULTI_PROMPT_ROUTER_TEMPLATE as RounterTemplate
# from legal_chatbot import LAWYER_PROMPT_TEMPLATE as LawyerTemplate
# from legal_chatbot import EXPLAIN_PROMPT_TEMPLATE as ExplainTemplate
# from legal_chatbot import SUMMARY_PROMPT_TEMPLATE as SummaryTemplate

# # parser
# from langchain.chains.router.llm_router import RouterOutputParser

# # mysql
# import pymysql

# # fileloader
# from langchain_community.document_loaders import PyPDFLoader
# from langchain_community.document_loaders import Docx2txtLoader


# router_llm = ChatOpenAI(
#     model=os.environ["LLM_MODELEND"],
#     api_key=os.environ["OPENAI_API_KEY"],
#     base_url=os.environ["OPENAI_BASE_URL"],
#     temperature=0,
#     # verbose=True,
# )


# # 定义一个空列表来存储流式传输的块
# chunks = []

# # 使用模型的 stream 方法进行流式传输
# for chunk in router_llm.stream("what color is the sky?"):
#     chunks.append(chunk)
#     # 打印每个块的内容
#     print(chunk.content, end="|", flush=True)

# from legal_chatbot import leagal_bot

# bot = leagal_bot()

# ans = bot.get_response("如果我的老板没有给我发工资，我应该如何维权？")
# print(ans)
# import os

# # model
# from langchain_community.llms.ctransformers import CTransformers

# # callbacks
# from langchain_core.callbacks import StreamingStdOutCallbackHandler


# legal_llm = CTransformers(
#     model=os.environ.get("MODEL_PATH"),
#     model_type=os.environ.get("MODEL_TYPE"),
#     config={"temperature": 0.1, "gpu_layers": 500, "max_new_tokens": 1024, "stream": True},
#     callbacks=[StreamingStdOutCallbackHandler()],
# )
# import os
# import asyncio
# from typing import Generator

# # model
# from langchain_community.llms.ctransformers import CTransformers

# # callbacks
# from langchain_core.callbacks import StreamingStdOutCallbackHandler


# class CustomStreamingCallbackHandler(StreamingStdOutCallbackHandler):
#     def __init__(self):
#         super().__init__()
#         self.token_stream = asyncio.Queue()

#     async def on_llm_new_token(self, token: str, **kwargs) -> None:
#         # 将新的 token 放入队列中
#         await self.token_stream.put(token)
#         # 调用父类方法以保持原有功能
#         super().on_llm_new_token(token, **kwargs)

#     async def get_tokens(self):
#         # 使用 yield 关键字返回新的 token
#         while True:
#             token = await self.token_stream.get()
#             yield token


# # 初始化模型和自定义回调处理
# legal_llm = CTransformers(
#     model=os.environ.get("MODEL_PATH"),
#     model_type=os.environ.get("MODEL_TYPE"),
#     config={"temperature": 0.1, "gpu_layers": 500, "max_new_tokens": 1024, "stream": True},
#     callbacks=[CustomStreamingCallbackHandler()],
# )

# # 获取自定义回调处理实例
# custom_callback = legal_llm.callbacks[0]


# # 异步获取预测结果
# async def get_prediction():
#     prediction_task = asyncio.create_task(legal_llm("what color is the sky?"))
#     token_generator = await custom_callback.get_tokens()
#     async for token in token_generator:
#         print(token, end="|", flush=True)


# # 运行异步获取预测结果函数
# asyncio.run(get_prediction())

from legal_chatbot import leagal_bot

bot = leagal_bot()
session_id = "user1234"
while True:
    user_input = input("User: ")
    if user_input.lower() == "quit":
        break
    elif user_input.lower() == "history":
        print("History: ", leagal_bot.get_session_history(session_id), "\n------------------------------\n")
        continue
    bot_response = bot.invoke(user_input, session_id)
    print("Bot: ", bot_response, "\n------------------------------\n")
