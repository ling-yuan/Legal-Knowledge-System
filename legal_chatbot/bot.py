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


# llm = CTransformers(
#     model=os.environ.get("MODEL_PATH"),
#     model_type=os.environ.get("MODEL_TYPE"),
#     config={"max_new_tokens": 10240, "temperature": 0.1, "gpu_layers": 500},
#     callbacks=[StreamingStdOutCallbackHandler()],
# )
llm = ChatOpenAI(
    model=os.environ["LLM_MODELEND"],
    api_key=os.environ["OPENAI_API_KEY"],
    base_url=os.environ["OPENAI_BASE_URL"],
    temperature=0,
    verbose=True,
)

db = SQLDatabase.from_uri("mysql://root:root@localhost:3306/graduation_project")
agent_executor = create_sql_agent(
    llm=llm,
    toolkit=SQLDatabaseToolkit(db=db, llm=llm),
    verbose=True,
    agent_type=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
)

response = agent_executor.invoke("婚姻有关的规定有多少？")
print(response)
