from pathlib import Path

from langchain_core.callbacks import StdOutCallbackHandler
from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain_chroma import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_classic import hub
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langsmith import traceable
from ai_demo_testing.utils.log import logger

callback_handler = StdOutCallbackHandler()

@traceable
class TestCaseService:
    def __init__(self):
        # 1LLM
        self.llm = OllamaLLM(
            model="llama3.1:8b",
            base_url="http://localhost:11434"
        )

        # 2Prompt
        prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一个非常有帮助的机器人，可以使用中文回复问题"),
            ("user", "{input}"),
        ])

        # RAG prompt
        rag_prompt = hub.pull("rlm/rag-prompt")
        logger.debug(f"RAG Prompt模板: {rag_prompt}")
        logger.debug(f"RAG Prompt输入变量: {rag_prompt.input_variables}")

        # Chroma向量库
        self.db = Chroma(
            embedding_function=OllamaEmbeddings(model="nomic-embed-text:v1.5"),
            persist_directory=str(Path(__file__).parent.parent / "chroma_store")
        )

        # 上传文档
        self.upload()
        
        # 检查向量库状态
        try:
            collection_count = self.db._collection.count()
            logger.info(f"向量库中共有 {collection_count} 个文档块")
            if collection_count == 0:
                logger.warning("⚠️ 向量库为空！RAG 将无法检索到任何内容")
        except Exception as e:
            logger.error(f"检查向量库状态时出错: {e}")
        
        # 创建检索器，设置检索参数
        retriever = self.db.as_retriever(
            search_kwargs={"k": 4}  # 检索前4个最相关的文档
        )
        logger.debug(f"检索器配置: k=4 (检索前4个最相关文档)")

        # 格式化函数
        def format_docs(docs):
            formatted = "\n\n".join(doc.page_content for doc in docs)
            logger.debug(f"检索到的文档数量: {len(docs)}")
            logger.debug(f"格式化后的context长度: {len(formatted)} 字符")
            if formatted:
                logger.debug(f"Context内容预览: {formatted[:500]}...")
            else:
                logger.warning("检索到的context为空！")
            return formatted

        # 保存 retriever 和 rag_prompt 用于调试
        self.retriever = retriever
        self.rag_prompt = rag_prompt

        # RAG 链
        self.rag_chain = (
                {"context": retriever | format_docs, "question": RunnablePassthrough()}
                | rag_prompt
                | self.llm
                | StrOutputParser()
        )

        # 普通问答链
        self.chain = prompt | self.llm

    @traceable(name="manual_gen", run_type="chain")
    def manual_gen(self, query):
        logger.debug(f"manual_gen 收到查询: {query}")
        
        # 先检查检索结果
        retrieved_docs = self.retriever.invoke(query)
        formatted_context = "\n\n".join(doc.page_content for doc in retrieved_docs)
        logger.debug(f"检索到的文档数量: {len(retrieved_docs)}, context长度: {len(formatted_context)} 字符")
        
        result = self.rag_chain.invoke(query)
        logger.debug(f"RAG 链返回结果: {result[:200] if result else 'None'}...")
        return result

    @traceable(name="auto_gen", run_type="chain")
    def auto_gen(self, query):
        logger.debug(f"auto_gen 收到查询: {query}")
        
        # 检查向量库状态
        try:
            collection_count = self.db._collection.count()
            logger.debug(f"向量库中总文档数: {collection_count}")
            if collection_count == 0:
                logger.error(" 向量库为空！无法进行检索。请检查文档是否正确加载。")
                return "错误：向量库为空，无法检索相关信息。请先确保文档已正确加载到向量库。"
        except Exception as e:
            logger.error(f"检查向量库时出错: {e}")
        
        # 先检查检索结果
        try:
            retrieved_docs = self.retriever.invoke(query)
            logger.debug(f"检索到的文档数量: {len(retrieved_docs)}")
            
            if len(retrieved_docs) == 0:
                logger.warning(" 检索器没有返回任何文档！可能的原因：")
                logger.warning("  1. 查询与文档内容不匹配")
                logger.warning("  2. 向量库中没有相关文档")
                logger.warning("  3. 检索参数设置不当")
            else:
                for i, doc in enumerate(retrieved_docs[:3]):  # 只显示前3个
                    logger.debug(f"文档 {i+1} 内容预览: {doc.page_content[:200]}...")
                    if hasattr(doc, 'metadata'):
                        logger.debug(f"文档 {i+1} 元数据: {doc.metadata}")
        except Exception as e:
            logger.error(f"检索文档时出错: {e}")
            return f"错误：检索文档时出错 - {str(e)}"
        
        # 手动构建输入以查看 prompt
        formatted_context = "\n\n".join(doc.page_content for doc in retrieved_docs)
        logger.debug(f"格式化后的context长度: {len(formatted_context)} 字符")
        if formatted_context:
            logger.debug(f"Context内容预览: {formatted_context[:500]}...")
        else:
            logger.warning("检索到的context为空！RAG可能无法正常工作")
        
        # 查看格式化后的最终 prompt
        try:
            formatted_prompt = self.rag_prompt.format(context=formatted_context, question=query)
            logger.debug(f"=== 最终发送给LLM的Prompt ===")
            logger.debug(formatted_prompt)
            logger.debug(f"=== Prompt结束 ===")
        except Exception as e:
            logger.error(f"格式化prompt时出错: {e}")
            logger.debug(f"Prompt模板需要的变量: {self.rag_prompt.input_variables}")
        
        # 调用 RAG 链
        result = self.rag_chain.invoke(query)
        logger.debug(f"RAG 链返回结果: {result[:200] if result else 'None'}...")
        return result

    def upload(self):
        """
        支持本地文件夹导入文档到向量库
        """
        # 检查向量库中是否已有数据
        try:
            collection_count = self.db._collection.count()
            logger.debug(f"向量库中已有文档数量: {collection_count}")
            if collection_count > 0:
                logger.info(f"向量库已有 {collection_count} 个文档，跳过重复加载")
                return
        except Exception as e:
            logger.debug(f"检查向量库时出错（可能是新库）: {e}")
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=20,
        )

        all_documents = []
        
        def read_files(glob):
            logger.debug(f"加载文件模式: {glob}")
            try:
                docs = DirectoryLoader(
                    str(Path(__file__).parent.parent / "data"),
                    glob=glob,
                    loader_cls=TextLoader,
                    loader_kwargs={"encoding": "utf-8"}
                ).load()
                logger.debug(f"加载了 {len(docs)} 个文档")
                if docs:
                    documents = text_splitter.split_documents(docs)
                    logger.debug(f"分割后得到 {len(documents)} 个文档块")
                    all_documents.extend(documents)
                else:
                    logger.warning(f"没有找到匹配 {glob} 的文件")
            except Exception as e:
                logger.error(f"加载文件时出错 {glob}: {e}")

        read_files("**/*.txt")
        read_files("**/*.md")
        
        if not all_documents:
            logger.warning(" 没有加载到任何文档！请检查 data 目录下是否有 .txt 或 .md 文件")
            return
        
        # 使用 add_documents 将文档添加到现有的向量库
        logger.info(f"正在将 {len(all_documents)} 个文档块添加到向量库...")
        try:
            self.db.add_documents(all_documents)
            logger.info(f" 成功添加 {len(all_documents)} 个文档块到向量库")
            
            # 验证添加是否成功
            collection_count = self.db._collection.count()
            logger.debug(f"向量库中现在有 {collection_count} 个文档")
        except Exception as e:
            logger.error(f"添加文档到向量库时出错: {e}")
            raise


testcase_service = TestCaseService()
