from langchain_ollama import OllamaLLM
from langchain_community.llms.openai import OpenAI  # 如果你还用 OpenAI

from ai_demo_testing.service.testcase_sevice import callback_handler


class LLMFactory:
    def __init__(self):
        self.llm = None

    def create_llm(self, name):
        if name == 'llama':
            # 最新写法：使用 OllamaLLM
            self.llm = OllamaLLM(
                model="llama3.1:8b",
                base_url="http://localhost:11434",
                callbacks=[callback_handler],
                verbose=True
            )
        elif name == 'openai':
            self.llm = OpenAI()  # 这里保持原样
        return self.llm

    def get_llm(self):
        return self.llm
