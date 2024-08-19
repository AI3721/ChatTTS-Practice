import ex
import random
import requests
import numpy as np
import gradio as gr

api = "http://127.0.0.1:7788"
has_interrupted = False
seed_max = 99999999
seed_min = 1
speakers = {
    "Default": {"seed": 21},
    "Speaker1": {"seed": 1111},
    "Speaker2": {"seed": 2222},
    "Speaker3": {"seed": 3333},
    "Speaker4": {"seed": 4444},
    "Speaker5": {"seed": 5555},
    "Speaker6": {"seed": 6666},
    "Speaker7": {"seed": 7777},
    "Speaker8": {"seed": 8888},
    "Speaker9": {"seed": 9999},
}


# 更换sample
def change_sample(sample_audio):
    if sample_audio is None:
        return ""
    file = open(sample_audio, 'rb')
    files = {'file': ('audio.wav', file.read())}
    response = requests.post(url=api+'/tts/sas', files=files)
    return response.json()
# 更新spk_emb
def update_emb(audio_seed):
    json = {"seed": audio_seed}
    response = requests.post(url=api+'/tts/srs', json=json)
    return response.json()
# 更新dvae_coef
def update_dvae(coef):
    if not has_interrupted:
        return coef
    response = requests.post(url=api+'/tts/reload')
    return response.json()
# 中断生成
def interrupt():
    global has_interrupted
    has_interrupted = True
    requests.post(url=api+'/tts/interrupt')
# 细化文本
def refine_text(text, text_seed, text_refine, temperature, top_P, top_K):
    if not text or not text_refine:
        return text
    # 自定义的文本正则优化方法
    from norm import normalize
    if isinstance(text, list):
        text = [normalize(t) for t in text]
    else:
        text = normalize(text)
    params_refine_text = {"temperature": temperature, "top_P": top_P, "top_K": top_K}
    json = {"text": text, "text_seed": text_seed, "params_refine_text": params_refine_text}
    response = requests.post(url=api+'/tts/refine', json=json)
    if len(response.json()) == 1: # 不显示中括号['']
        return response.json()[0]
    return response.json()
# 生成音频
def generate_audio(text, audio_seed, stream, temperature, top_P, top_K, spk_emb, sample_emb, sample_text):
    if not text or not spk_emb.startswith("蘁淰"):
        return None
    params_infer_code = {"temperature": temperature, "top_P": top_P, "top_K": top_K, "spk_emb": spk_emb}
    if sample_emb and sample_text:
        params_infer_code["spk_emb"] = None
        params_infer_code["spk_smp"] = sample_emb
        params_infer_code["txt_smp"] = sample_text
    json = {"text": text, "audio_seed": audio_seed, "stream": stream, "params_infer_code": params_infer_code}
    response = requests.post(url=api+'/tts/generate', json=json, stream=stream)
    if stream:
        for content in response.iter_content(48000):
            yield 24000, np.frombuffer(content, dtype=np.int16)
    elif len(response.json()) == 1: # 只有一段音频返回
        yield 24000, np.array(response.json()[0], dtype=np.int16)
    else: # 因为在TTS生成的多元数组中短音频会自动补零
        def drop_fill(list):
            while list[-1]==0: # 所以要去除多余的零
                list.pop()
            if len(list) < 24000: # 防止短音频太短
                add = [0]*((24000-len(list))//2)
                list = add + list + add
            return list
        yield [np.array(drop_fill(wav), dtype=np.int16) for wav in response.json()]


# 更换speaker
def change_speaker(speaker):
    return speakers.get(speaker)["seed"]
# 随机speaker
def random_speaker():
    return gr.update(value=random.choices(list(speakers.keys()))[0])
# 随机种子
def random_seed():
    return gr.update(value=random.randint(seed_min, seed_max))
# 更换按钮
def change_button(generate_btn, interrupt_btn, is_visible):
    interrupt_btn = gr.update(visible=not is_visible)
    generate_btn = gr.update(visible=is_visible)
    return generate_btn, interrupt_btn
# 设置生成前按钮
def set_button_before(generate_btn, interrupt_btn):
    global has_interrupted
    has_interrupted = False
    return change_button(generate_btn, interrupt_btn, is_visible=has_interrupted)
# 设置生成后按钮
def set_button_after(generate_btn, interrupt_btn):
    global has_interrupted
    has_interrupted = True
    return change_button(generate_btn, interrupt_btn, is_visible=has_interrupted)

####################################################################################################

# 创建tts交互界面
def create_tts_block():
    with gr.Blocks() as tts_block:
        with gr.Column():
            # gr.Markdown("<h1 style='text-align: center; font-size: 2em'>Chat TTS</h1>")
            # Input
            with gr.Row():
                with gr.Column(min_width=0, scale=2):
                    with gr.Tab(label="Input Text"):
                        input_text = gr.Textbox(label="", lines=12, max_lines=12, show_copy_button=True, interactive=True, value=ex.input_text)
                    with gr.Tab(label="Sample Text"):
                        sample_text = gr.Textbox(label="", lines=12, max_lines=12, show_copy_button=True, interactive=True)
                with gr.Column(min_width=0, scale=1):
                    with gr.Tab(label="Sample Audio"):
                        sample_audio = gr.Audio(label="", type="filepath", waveform_options=gr.WaveformOptions(sample_rate=24000))
                    with gr.Tab(label="Emb"):
                        sample_emb = gr.Textbox(label="", lines=12, max_lines=12, show_copy_button=True, interactive=True)
            # 可调参数
            with gr.Accordion(label="可调参数：点击这里，可以尝试生成不同音色的声音！", open=False):
                # Checkbox
                with gr.Row():
                    auto_play = gr.Checkbox(label="Auto Play", value=False, interactive=True)
                    stream_mode = gr.Checkbox(label="Stream Mode", value=False, interactive=True)
                    text_refine = gr.Checkbox(label="Text Refine", value=True, interactive=True)
                # Slider
                with gr.Row():
                    temperature = gr.Slider(label="Temperature", minimum=0, maximum=1.0, step=0.01, value=0.3, interactive=True)
                    top_p = gr.Slider(label="top_P", minimum=0, maximum=1.0, step=0.05, value=0.7, interactive=True)
                    top_k = gr.Slider(label="top_K", minimum=0, maximum=20, step=1, value=10, interactive=True)
                # Tab
                with gr.Row():
                    with gr.Column(min_width=0):
                        with gr.Tab(label="Speaker"):
                            speaker = gr.Dropdown(show_label=False, choices=speakers.keys(), value="Default", interactive=True)
                        speaker_btn = gr.Button("\U0001F3B2")
                    with gr.Column(min_width=0):
                        with gr.Tab(label="Audio Seed"):
                            audio_seed = gr.Number(show_label=False, minimum=seed_min, maximum=seed_max, value=21, interactive=True)
                        with gr.Tab(label="Emb"):
                            spk_emb = gr.Textbox(show_label=False, max_lines=1, value=update_emb(audio_seed.value), interactive=True)
                        audio_seed_btn = gr.Button("\U0001F3B2")
                    with gr.Column(min_width=0):
                        with gr.Tab(label="Text Seed"):
                            text_seed = gr.Number(show_label=False, minimum=seed_min, maximum=seed_max, value=21, interactive=True)
                        with gr.Tab(label="DVAE"):
                            dvae_coef = gr.Textbox(show_label=False, max_lines=1, interactive=True)
                        text_seed_btn = gr.Button("\U0001F3B2")
                reload_btn = gr.Button("Reload (Update DVAE)")
            # Button
            generate_btn = gr.Button("Generate", variant="primary")
            interrupt_btn = gr.Button("Interrupt", variant="stop", visible=False)
            output_text = gr.Textbox(label="Output Text", lines=4, max_lines=4, show_copy_button=True)
            # 响应事件
            sample_audio.change(fn=change_sample, inputs=sample_audio, outputs=sample_emb)
            speaker_btn.click(fn=random_speaker, outputs=speaker)
            speaker.change(fn=change_speaker, inputs=speaker, outputs=audio_seed)
            audio_seed_btn.click(fn=random_seed, outputs=audio_seed)
            audio_seed.change(fn=update_emb, inputs=audio_seed, outputs=spk_emb)
            text_seed_btn.click(fn=random_seed, outputs=text_seed)
            reload_btn.click(fn=update_dvae, inputs=dvae_coef, outputs=dvae_coef)
            interrupt_btn.click(fn=interrupt)
            # output
            @gr.render(inputs=[auto_play, stream_mode])
            def make_audio(autoplay, streaming):
                output_audio = gr.Audio(
                    autoplay=autoplay, streaming=streaming,
                    label="Output Audio", interactive=False,
                    format='mp3' if not streaming else 'wav',
                    waveform_options=gr.WaveformOptions(sample_rate=24000))
                generate_btn.click(
                    fn=set_button_before, 
                    inputs=[generate_btn, interrupt_btn],
                    outputs=[generate_btn, interrupt_btn]
                ).then(
                    fn=refine_text,
                    inputs=[input_text, text_seed, text_refine, temperature, top_p, top_k],
                    outputs=output_text
                ).then(
                    fn=generate_audio,
                    inputs=[output_text, audio_seed, stream_mode, temperature, top_p, top_k, spk_emb, sample_emb, sample_text],
                    outputs=output_audio
                ).then(
                    fn=set_button_after,
                    inputs=[generate_btn, interrupt_btn],
                    outputs=[generate_btn, interrupt_btn]
                )
            # 更多玩法
            with gr.Accordion(label="更多玩法：点击这里，可以体验更多新奇有趣的玩法！", open=False):
                from tts_more import create_tts_more_block
                create_tts_more_block(temperature, top_p, top_k)
    
    return tts_block