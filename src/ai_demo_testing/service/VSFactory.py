from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma
from pathlib import Path

class VSFactory:
    def create(self, name):
        if name == 'chroma':
            # 最新写法，支持向量库持久化
            db = Chroma(
                embedding_function=OllamaEmbeddings(model="nomic-embed-text:v1.5"),
                persist_directory=str(Path(__file__).parent.parent / "chroma_store")
            )
            return db
        else:
            return None
