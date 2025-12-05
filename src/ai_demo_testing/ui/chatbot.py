import gradio as gr


from ai_demo_testing.service.testcase_sevice import testcase_service

def respond(message, history):
    history.append((message, "收到啦"))
    return "", history

def manual_gen(chat_history):
    if chat_history is None:
        chat_history = []
    message = '请为测试人宠物商店生成测试用例，使用等价类、边界值等方法保证测试用例实现尽量充分的对功能进行测试'
    # message = '你收到了html代码吗？'
    r = testcase_service.manual_gen(message)
    chat_history.append({'role': 'user', 'content': message})

    chat_history.append({'role': 'assistant', 'content': r})
    return chat_history

def auto_gen(message, chat_history):
    if chat_history is None:
        chat_history = []
    if message == '':
        message = '请为测试人宠物商店生成自动化测试用例，使用pytest+selenium测试'
    # message = '你收到了html代码吗？'
    r = testcase_service.auto_gen(message)
    chat_history.append({'role': 'user', 'content': message})

    chat_history.append({'role': 'assistant', 'content': r})
    return chat_history, chat_history


with gr.Blocks() as demo:
    # main headline
    gr.Markdown("# 我的chatbot")

    with gr.Row():
        with gr.Column(scale=1):
            # 左侧侧边栏 + accordion
            with gr.Accordion("帮助信息", open=True):
                gr.Markdown("测试")
                gr.Markdown("测试")
                gr.Markdown("测试")
            with gr.Accordion("<UNK>", open=True):
                gr.Markdown("1")
                gr.Markdown("2")
                gr.Markdown("3")

        with gr.Column(scale=3):
            with gr.Tabs():
                with gr.Tab("Chatbot"):
                    chatbot = gr.Chatbot()
                    msg = gr.Textbox(label="输入信息")

                    with gr.Row():
                        with gr.Column(scale=1):
                            clear = gr.ClearButton([msg, chatbot])
                            # 按空格时触发
                            msg.submit(respond, [msg, chatbot], [msg, chatbot])

                        with gr.Column(scale=2):
                            
                            testcase_gen_btn = gr.Button("业务测试用例生成")
                            testcase_gen_btn.click(manual_gen, chatbot, chatbot)
                        with gr.Column(scale=3):
                            auto_gen_btn = gr.Button("自动化测试用例生成")
                            auto_gen_btn.click(auto_gen, [msg, chatbot], [chatbot, chatbot])


                with gr.Tab("Testcase"):
                    with gr.Accordion("Testcase详情", open=True):
                        gr.Markdown("""
                        - 测试
                        - 幸运
                        """)
                    gr.Button("执行Testcase")
                    gr.Textbox(label="Testcase输出结果")
