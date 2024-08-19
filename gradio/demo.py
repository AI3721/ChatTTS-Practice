import gradio as gr
from tts import create_tts_block
from chat import create_chat_block

with gr.Blocks() as demo:
    gr.Markdown("<h1 style='text-align: center; font-size: 2em'>Chat 3721</h1>")
    with gr.Tab(label="文字转语音"):
        create_tts_block()
    with gr.Tab(label="对话机器人"):
        create_chat_block()

gr.close_all()
demo.launch(share=True)