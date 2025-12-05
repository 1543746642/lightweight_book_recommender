import logging
import sys

# 1. 定义一个标准格式
# %(levelname)s: 日志级别（DEBUG, INFO, ERROR等）
# %(message)s: 日志内容
# %(pathname)s: 完整的文件路径名
# %(lineno)d: 产生日志调用的行号
# (注意：这里的格式是许多IDE默认识别为跳转链接的关键！)
LOG_FORMAT = '%(pathname)s:%(lineno)d: [%(levelname)s] - %(message)s'


def setup_logging():
    """配置logging模块，设置输出到控制台，并应用自定义格式。"""

    # 获取根 Logger 实例
    logger = logging.getLogger()

    # 设置最低输出级别为 DEBUG，确保所有级别信息都被捕获
    logger.setLevel(logging.DEBUG)

    # 创建一个控制台处理器 (Handler)，将日志发送到标准错误流 (stderr)
    # sys.stderr 是默认的控制台输出流
    console_handler = logging.StreamHandler(sys.stderr)

    # 设置 Handler 的输出级别（例如，只在控制台输出 INFO 及以上的日志）
    # 这里为了演示，我们设置为 DEBUG
    console_handler.setLevel(logging.DEBUG)

    # 创建格式化器 (Formatter) 并应用我们定义的格式
    formatter = logging.Formatter(LOG_FORMAT)

    # 将格式化器设置给处理器
    console_handler.setFormatter(formatter)

    # 将处理器添加到 Logger
    if not logger.handlers:
        logger.addHandler(console_handler)


def main():
    """主函数，演示不同级别的日志输出。"""

    # 确保 logging 已配置
    setup_logging()

    logging.debug("这是一条DEBUG级别的消息，用于详细的调试信息。")
    logging.info("这是一条INFO级别的消息，程序正常运行的关键信息。")

    try:
        result = 10 / 0  # 制造一个错误
    except ZeroDivisionError as e:
        # 使用 exc_info=True 可以将当前的异常信息也输出到日志中
        logging.error("程序执行时发生了一个错误。", exc_info=True)

    logging.warning("这是一条WARNING级别的消息，需要注意但不是致命问题。")
    

if __name__ == '__main__':
    main()