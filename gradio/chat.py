import requests
import gradio as gr

api = "http://127.0.0.1:7788"

def get_chat_response(prompt, history=[], temperature=0.5):
    json = {"prompt": prompt, "history": history, "temperature": temperature}
    response = requests.post(url=api+'/chat', json=json)
    return response.json()['answer']

def respond(prompt, chatbot, temperature):
    answer = get_chat_response(prompt, chatbot, temperature)
    chatbot.append([prompt, answer])
    return "", chatbot

def create_chat_block():
    with gr.Blocks() as chat_block:
        with gr.Column():
            # gr.Markdown("<h1 style='text-align: center; font-size: 2em'>Chat Bot</h1>")
            chatbot = gr.Chatbot(label="AI 3721", avatar_images=['image/ME.png', 'image/AI.png'])
            temperature = gr.Slider(label="Temperature", minimum=0.1, maximum=1.0, value=0.9)
            prompt = gr.Textbox(label="Prompt", lines=3, max_lines=3, autofocus=True)

            with gr.Row():
                clear_btn = gr.ClearButton(components=[prompt, chatbot], value="清空")
                submit_btn = gr.Button("提交", variant='primary')

            submit_btn.click(fn=respond,inputs=[prompt, chatbot, temperature], outputs=[prompt, chatbot])
            prompt.submit(fn=respond,inputs=[prompt, chatbot, temperature], outputs=[prompt, chatbot])
    
    return chat_block