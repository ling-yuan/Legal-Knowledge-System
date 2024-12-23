import os

# model
from langchain_community.llms.ctransformers import CTransformers
from langchain_openai import ChatOpenAI  # ChatOpenAI模型
from langchain_experimental.sql import SQLDatabaseChain

# callbacks
from langchain_core.callbacks import StreamingStdOutCallbackHandler

# agent
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain.agents.agent_types import AgentType

# tools
from langchain_community.utilities import SQLDatabase
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit

# prompt
from langchain.prompts import PromptTemplate
from legal_chatbot import MULTI_PROMPT_ROUTER_TEMPLATE as RounterTemplate
from legal_chatbot import LAWYER_PROMPT_TEMPLATE as LawyerTemplate
from legal_chatbot import EXPLAIN_PROMPT_TEMPLATE as ExplainTemplate
from legal_chatbot import SUMMARY_PROMPT_TEMPLATE as SummaryTemplate

# parser
from langchain.chains.router.llm_router import RouterOutputParser

# mysql
import pymysql

# fileloader
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import Docx2txtLoader


class leagal_bot:

    def __init__(self):
        self.router_llm = ChatOpenAI(
            model=os.environ["LLM_MODELEND"],
            api_key=os.environ["OPENAI_API_KEY"],
            base_url=os.environ["OPENAI_BASE_URL"],
            temperature=0,
            # verbose=True,
        )
        self.legal_llm = CTransformers(
            model=os.environ.get("MODEL_PATH"),
            model_type=os.environ.get("MODEL_TYPE"),
            config={"temperature": 0.1, "gpu_layers": 500},
            callbacks=[StreamingStdOutCallbackHandler()],
        )

    def get_response(self, question):
        prompt_template = self.__get_intention(question)
        data = self.__get_data(question)
        response = self.__get_legal_response(question, prompt_template, data)
        return response

    def __get_intention(self, question):
        prompt_dicts = [
            {
                "key": "lawyer",
                "description": "适合回答法律适用、程序或策略的相关问题",
                "template": LawyerTemplate,
            },
            {
                "key": "explain",
                "description": "适合回答相关法律条文或概念的问题",
                "template": ExplainTemplate,
            },
        ]
        destinations = [f"{p['key']}: {p['description']}" for p in prompt_dicts]
        router_template = RounterTemplate.format(destinations="\n".join(destinations))
        router_prompt = PromptTemplate(
            template=router_template,
            input_variables=["input"],
        )
        chain = router_prompt | self.router_llm | RouterOutputParser()
        answer = chain.invoke(question)
        destination = answer["destination"]
        if destination == "lawyer":
            return prompt_dicts[0].get("template", LawyerTemplate)
        elif destination == "explain":
            return prompt_dicts[1].get("template", LawyerTemplate)
        else:
            return prompt_dicts[0].get("template", LawyerTemplate)

    def __get_data(self, question):
        summary_prompt = PromptTemplate(
            template=SummaryTemplate,
            input_variables=["input"],
        )
        chain = summary_prompt | self.router_llm
        answer = chain.invoke(question).content
        name, file_name = query_db(answer)
        if file_name:
            return read_file(file_name)
        else:
            return "无"

    def __get_legal_response(self, question, prompt_template, data):
        prompt = PromptTemplate(
            template=prompt_template,
            input_variables=["input", "laws"],
        )
        print(prompt.format(input=question, laws=data))
        chain = prompt | self.legal_llm
        answer = chain.invoke({"input": question, "laws": data})
        return answer


def query_db(key_words: list[str] | str):
    key_words = key_words if isinstance(key_words, list) else key_words.split(",")
    key_words = [i.strip() for i in key_words]
    # 连接数据库
    db = pymysql.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ["DB_PORT"]),
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"],
        charset="utf8",
    )
    # 创建游标
    cursor = db.cursor()
    # 查询语句
    search_ans = []
    for key_word in key_words:
        sql = f'SELECT name, id, filetype FROM law_information WHERE name LIKE "%{key_word}%" and lawtype = "法律" AND status = "有效" ORDER BY id DESC'
        cursor.execute(sql)
        results = cursor.fetchall()
        for row in results:
            search_ans.append(row)
    # 关闭游标和数据库连接
    cursor.close()
    db.close()
    if len(search_ans) > 0:
        return search_ans[0][0], search_ans[0][1] + "." + search_ans[0][2]
    else:
        return "未找到相关法律条文", None


def read_file(file_name: str):
    file_path = os.environ.get("DATA_FILE_FOLDER") + file_name
    ans = ""
    if file_name.endswith(".pdf"):
        loader = PyPDFLoader(file_path)
        documents = loader.load()
        for doc in documents:
            ans += doc.page_content
        ans = ans.replace("\n\n", "\n")
    elif file_name.endswith(".docx"):
        loader = Docx2txtLoader(file_path)
        documents = loader.load()
        for doc in documents:
            ans += doc.page_content
        ans = ans.replace("\n\n", "\n")
    elif file_name.endswith(".doc"):
        loader = Docx2txtLoader(file_path.replace("doc", "docx"))
        documents = loader.load()
        for doc in documents:
            ans += doc.page_content
        ans = ans.replace("\n\n", "\n")
    elif file_name.endswith(".html"):
        t = ""
        with open(file_path, "r", encoding="utf-8") as f:
            t = f.read()
        ans = t
        ans = ans.replace("\n\n", "\n")
    return ans
