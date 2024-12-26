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


def clean_documents(documents: list[Document]):
    """
    清洗文档
    """
    import re

    character_list = [
        ("\u3000", "", False),
        ("－\d+－", "", True),
        ("- \d+ -", "", True),
    ]
    for doc in documents:
        for char in character_list:
            if not char[2]:
                doc.page_content = doc.page_content.replace(char[0], char[1])
            else:
                doc.page_content = re.sub(char[0], char[1], doc.page_content)
    return documents


def read_file(file_name: str):
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
            return clean_documents(documents)
        elif file_name.endswith(".docx"):
            loader = Docx2txtLoader(file_path)
            documents = loader.load()
            # for doc in documents:
            #     ans += doc.page_content
            # ans = ans.replace("\n\n", "\n")
            return clean_documents(documents)
        elif file_name.endswith(".doc"):
            loader = Docx2txtLoader(file_path.replace("doc", "docx"))
            documents = loader.load()
            # for doc in documents:
            #     ans += doc.page_content
            # ans = ans.replace("\n\n", "\n")
            return clean_documents(documents)
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
            return clean_documents(documents)
    except Exception as e:
        print(f"Error reading file {file_name}: {e}")
        return None


def creat_vector_db(chunk_size: int = 500, chunk_overlap: int = 50):
    """
    创建向量数据库
    """
    # 文本分割器
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        # separators=["\n\n", "\n", " ", ""],
        is_separator_regex=False,
        length_function=len,
        keep_separator=False,
    )
    # 读取文件
    retults = get_law_info()
    documents = []
    for result in retults:
        file_name = result[0] + "." + result[-1]
        file_documents = read_file(file_name)
        if file_documents is not None:
            documents.extend(file_documents)
    # 切割文本
    documents = text_splitter.split_documents(documents)

    # 嵌入模型
    embedding = HuggingFaceEmbeddings(model_name="BAAI/bge-small-zh-v1.5")
    # 创建向量数据库
    chroma = Chroma(
        persist_directory=os.getenv("VECTOR_DB_FOLDER"),
        embedding_function=embedding,
    )
    chroma.reset_collection()
    # 批量添加文档到向量数据库
    # sub_num = 1000
    # doc_len = len(documents)
    # for i in range(0, doc_len, sub_num):
    #     s = i
    #     e = i + sub_num if i + sub_num < doc_len else doc_len
    #     chroma.add_documents(documents[s:e])
    #     print(f"已添加 {e} / {doc_len} 个文档")
    doc_len = len(documents)
    for i in tqdm.tqdm(range(0, doc_len)):
        chroma.add_documents(documents[i : i + 1])

    # 保存向量数据库
    # chroma.persist()


def ask_question():
    # 嵌入模型
    embedding = HuggingFaceEmbeddings(model_name="BAAI/bge-small-zh-v1.5")
    # 读取向量数据库
    vectordb = Chroma(persist_directory=os.getenv("VECTOR_DB_FOLDER"), embedding_function=embedding)
    # 读取问题
    question = input("请输入您的问题：")
    # 查询向量数据库
    response = vectordb.similarity_search(question)
    # 返回结果
    return response


# 类 用于从向量数据库中获取文本相似的内容
class VectorDB:
    def __init__(self, db_path=""):
        # 嵌入模型
        self.embedding = HuggingFaceEmbeddings(model_name="BAAI/bge-small-zh-v1.5")
        # 读取向量数据库
        self.vectordb = Chroma(
            persist_directory=db_path or os.getenv("VECTOR_DB_FOLDER"),
            embedding_function=self.embedding,
        )

    def get_similar_documents(self, question):
        # 查询向量数据库
        response = self.vectordb.similarity_search(question)
        # 返回结果
        return response

    def get_similar_contents(self, question):
        # 查询向量数据库
        response = self.vectordb.similarity_search(question)
        # 返回结果
        return [doc.page_content.replace("\n\n", "\n") for doc in response]

    def as_retriever(self, *args, **kwargs):
        return self.vectordb.as_retriever(*args, **kwargs)


if __name__ == "__main__":
    # creat_vector_db(300, 10)
    # ask_question()
    vdb = VectorDB()
    ans = [f"-< {i} >-" for i in vdb.get_similar_contents("我想知道，如果我的雇主没有支付工资，我应该如何维权？")]
    print(*ans, sep="\n---------------------------------------------------\n")
    pass
