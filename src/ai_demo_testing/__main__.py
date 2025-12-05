import os

from dotenv import load_dotenv

load_dotenv()  # Make sure env vars are ready before anything else imports


from ai_demo_testing.ui.chatbot import demo
from ai_demo_testing.utils.log import logger


def main():
    demo.launch()


if __name__ == '__main__':
    main()
