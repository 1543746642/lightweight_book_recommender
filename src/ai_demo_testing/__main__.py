import os

from dotenv import load_dotenv

load_dotenv()  # Make sure env vars are ready before anything else imports

# LangSmith now prefers the LANGCHAIN_* namespace. Mirror values if only legacy vars exist.
if not os.getenv("LANGCHAIN_PROJECT") and os.getenv("LANGSMITH_PROJECT"):
    os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGSMITH_PROJECT")

from ai_demo_testing.ui.chatbot import demo
from ai_demo_testing.utils.log import logger


def main():
    logger.debug(f"LANGCHAIN_TRACING_V2: {os.getenv('LANGCHAIN_TRACING_V2')}")
    logger.debug(f"LANGCHAIN_PROJECT: {os.getenv('LANGCHAIN_PROJECT')}")
    logger.debug(f"LANGCHAIN_API_KEY: {os.getenv('LANGCHAIN_API_KEY')}")
    demo.launch()


if __name__ == '__main__':
    main()
