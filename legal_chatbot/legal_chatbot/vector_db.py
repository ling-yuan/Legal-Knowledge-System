import os
import tqdm
import pymysql
from lxml import etree

# fileloader
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import Docx2txtLoader

# vectorstore
# from langchain_community.vectorstores import Chroma
from langchain_chroma import Chroma

# embeddings
from langchain_huggingface import HuggingFaceEmbeddings

# text_splitter
from langchain.text_splitter import RecursiveCharacterTextSplitter

# config
from .config import Config


def get_law_info():
    """
    从数据库中获取法律信息
    """
    # 获取数据库连接参数
    db_host = os.getenv("DB_HOST")
    db_port = int(os.getenv("DB_PORT"))
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_NAME")
    db_charset = os.getenv("DB_CHARSET")

    # 建立数据库连接
    conn = pymysql.connect(
        host=db_host, port=db_port, user=db_user, password=db_password, database=db_name, charset=db_charset
    )

    # 创建游标对象
    cursor = conn.cursor()

    # 执行查询
    sql = "SELECT * FROM law_information"
    cursor.execute(sql)

    # 获取所有数据
    results = cursor.fetchall()

    return results


def clean_documents(documents: list[Document], title: str):
    """
    清洗文档
    """
    import re

    character_list = [
        ("\u3000", "", False),  # 全角空格
        ("目录", "", False),  # 目录
        ("^第[一二三四五六七八九十]*?分?[章节编].*?$", "", True),  # 章节号
        ("－\d+－", "", True),  # 章节号
        ("－ \d+ －", "", True),  # 章节号
        ("- \d+ -", "", True),  # 章节号
        ("—\d+—", "", True),  # 章节号
        ("\n{3,}", "\n", True),  # 多个换行符替换为两个换行符
        (f"^{title}", "", True),  # 标题
    ]
    for doc in documents:
        for char in character_list:
            if not char[2]:
                doc.page_content = doc.page_content.replace(char[0], char[1])
            else:
                doc.page_content = re.sub(char[0], char[1], doc.page_content, flags=re.MULTILINE)
    return documents


def read_file(file_name: str, title: str):
    """
    读取文件内容
    """
    try:
        file_path = os.environ.get("DATA_FILE_FOLDER") + file_name
        if file_name.endswith(".pdf"):
            loader = PyPDFLoader(file_path)
            documents = loader.load()
            # for doc in documents:
            #     ans += doc.page_content
            # ans = ans.replace("\n\n", "\n")
            return clean_documents(documents, title)
        elif file_name.endswith(".docx"):
            loader = Docx2txtLoader(file_path)
            documents = loader.load()
            # for doc in documents:
            #     ans += doc.page_content
            # ans = ans.replace("\n\n", "\n")
            return clean_documents(documents, title)
        elif file_name.endswith(".doc"):
            loader = Docx2txtLoader(file_path.replace("doc", "docx"))
            documents = loader.load()
            # for doc in documents:
            #     ans += doc.page_content
            # ans = ans.replace("\n\n", "\n")
            return clean_documents(documents, title)
        elif file_name.endswith(".html"):
            t = ""
            with open(file_path, "r", encoding="utf-8") as f:
                t = f.read()
            tree = etree.HTML(t)
            texts = tree.xpath("//span/text()")
            for text in texts:
                t += text + "\n"
            doc = Document(page_content=t)
            documents = [doc]
            return clean_documents(documents, title)
    except Exception as e:
        print(f"Error reading file {file_name}: {e}")
        return None


def creat_vector_db(chunk_size: int = None, chunk_overlap: int = None):
    """
    创建向量数据库
    """
    # 文本分割器
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size or Config.VECTOR_DB_CONFIG["chunk_size"],
        chunk_overlap=chunk_overlap or Config.VECTOR_DB_CONFIG["chunk_overlap"],
        separators=["第[^\n]*条"],
        is_separator_regex=True,
        length_function=len,
        keep_separator=True,
    )

    # 读取文件
    results = get_law_info()
    documents = []
    for result in results:
        file_name = result[0] + "." + result[-1]
        file_documents = read_file(file_name, result[2])
        if file_documents is not None:
            # 切割文本
            for doc in text_splitter.split_documents(file_documents):
                doc.page_content = f"《{result[2]}》\n" + doc.page_content
                doc.page_content = doc.page_content.replace("\n\n", "\n")
                documents.append(doc)

    # 嵌入模型
    embedding = HuggingFaceEmbeddings(
        model_name=Config.VECTOR_DB_CONFIG["model_name"],
    )

    # 创建向量数据库
    chroma = Chroma(
        persist_directory=Config.VECTOR_DB_CONFIG["db_path"],
        embedding_function=embedding,
    )
    chroma.reset_collection()

    # 批量添加文档到向量数据库
    doc_len = len(documents)
    for i in tqdm.tqdm(range(0, doc_len)):
        chroma.add_documents(documents[i : i + 1])


# 类 用于从向量数据库中获取文本相似的内容
class VectorDB:

    embedding = HuggingFaceEmbeddings(
        model_name=Config.VECTOR_DB_CONFIG["model_name"],
    )

    vectordb = Chroma(
        persist_directory=Config.VECTOR_DB_CONFIG["db_path"],
        embedding_function=embedding,
        collection_metadata={"hnsw:space": "cosine"},
    )

    retriever = vectordb.as_retriever()

    def __init__(self, db_path=""):
        # 嵌入模型
        self.embedding = VectorDB.embedding
        # 读取向量数据库
        if db_path:
            self.vectordb = Chroma(
                persist_directory=db_path,
                embedding_function=self.embedding,
            )
            self.retriever = self.vectordb.as_retriever()
        else:
            self.vectordb = VectorDB.vectordb
            self.retriever = VectorDB.retriever

        # 添加缓存机制
        self._cache = {}
        self._cache_size = 1000

    def get_similar_documents(self, question):
        # 查询向量数据库
        response = self.vectordb.similarity_search(question)
        # 返回结果
        return response

    def get_similar_contents(self, question):
        # 检查缓存
        if question in self._cache:
            return self._cache[question]

        # 查询向量数据库
        response = self.vectordb.similarity_search(question)
        results = [doc.page_content.replace("\n\n", "\n") for doc in response]

        # 更新缓存
        if len(self._cache) >= self._cache_size:
            self._cache.pop(next(iter(self._cache)))
        self._cache[question] = results

        return results


if __name__ == "__main__":
    # creat_vector_db(200, 10)
    # # ask_question()
    vdb = VectorDB()
    while True:
        question = input("请输入您的问题：")
        if question == "exit":
            break
        ans = vdb.get_similar_contents(question)
        print(*ans, sep="\n------------\n")
