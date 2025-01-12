import os


class Config:
    # 模型配置
    LLM_CONFIG = {
        "temperature": 0,
        "model": os.environ["LLM_MODELEND"],
        "api_key": os.environ["OPENAI_API_KEY"],
        "base_url": os.environ["OPENAI_BASE_URL"],
    }

    # 向量数据库配置
    VECTOR_DB_CONFIG = {
        "chunk_size": 500,
        "chunk_overlap": 50,
        "model_name": "BAAI/bge-small-zh-v1.5",
        "db_path": os.environ["VECTOR_DB_FOLDER"],
    }
