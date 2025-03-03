import os


class Config:
    # 模型配置
    LLM_CONFIG = {
        "temperature": 0,
        "model": os.getenv("LLM_MODEL"),
        "chat_model": os.getenv("LLM_CHAT_MODEL") or os.getenv("LLM_MODEL"),
        "thinking_model": os.getenv("LLM_THINKING_MODEL"),
        "api_key": os.getenv("OPENAI_API_KEY"),
        "base_url": os.getenv("OPENAI_BASE_URL"),
    }

    # 向量数据库配置
    VECTOR_DB_CONFIG = {
        "chunk_size": 500,
        "chunk_overlap": 50,
        "model_name": "BAAI/bge-small-zh-v1.5",
        "db_path": os.getenv("VECTOR_DB_FOLDER"),
    }
