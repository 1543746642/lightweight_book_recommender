import logging
import sys

# 1. 定义一个标准格式
# %(levelname)s: 日志级别（DEBUG, INFO, ERROR等）
# %(message)s: 日志内容
# %(pathname)s: 完整的文件路径名
# %(lineno)d: 产生日志调用的行号
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

    # 设置 Handler 的输出级别
    console_handler.setLevel(logging.DEBUG)

    # 创建格式化器 (Formatter) 并应用
    formatter = logging.Formatter(LOG_FORMAT)

    # 将格式化器设置给处理器
    console_handler.setFormatter(formatter)

    # 将处理器添加到 Logger
    if not logger.handlers:
        logger.addHandler(console_handler)


