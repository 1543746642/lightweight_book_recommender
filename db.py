# db.py
import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings

load_dotenv()

PERSIST_DIRECTORY = "chroma_mysql_like_db"


def get_or_create_db(documents=None):
    """自动判断是否创建或加载向量数据库"""

    embedding = OpenAIEmbeddings(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_API_BASE"),
        model="text-embedding-3-small"
    )

    # 如果目录已经存在 → 说明数据库已创建，直接加载
    if os.path.exists(PERSIST_DIRECTORY):
        print("检测到现有数据库 → 直接加载")
        db = Chroma(
            persist_directory=PERSIST_DIRECTORY,
            embedding_function=embedding
        )
        print(f"已加载，文档数量：{db._collection.count()}")
        return db

    # 否则 → 首次运行 → 创建数据库
    if documents is None:
        raise ValueError("数据库不存在，但未提供 documents 来创建数据库！")

    print("数据库不存在 → 正在创建并保存……")

    db = Chroma.from_documents(
        documents=documents,
        embedding=embedding,
        persist_directory=PERSIST_DIRECTORY
    )

    db.persist()
    print(f"数据库已创建并保存到：{PERSIST_DIRECTORY}")
    print(f"文档数量：{db._collection.count()}")

    return db
