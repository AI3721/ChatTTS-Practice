import ex
import random
import itertools
import numpy as np
import gradio as gr
from collections import defaultdict
from tts import seed_min, seed_max, update_emb, refine_text, generate_audio

# 分割行
def split_line(text):
    line_list = []
    for line in text.split('\n'):
        if not line.strip():
            continue # 跳过空白行
        parts = []
        if line.find("::") != -1:
            parts = line.split("::")
        elif line.find("：") != -1:
            parts = line.split("：")
        if len(parts) != 2:
            continue # 跳过格式错误的行
        line_list.append({"role": parts[0], "text": parts[1]})
    return line_list
# 提取角色
def extract_roles(text):
    line_list = split_line(text)
    roles = dict.fromkeys([l["role"] for l in line_list])
    seeds = [random.randint(seed_min, seed_max) for _ in roles]
    return [[role, seed] for role, seed in zip(roles, seeds)]
# 生成音频
def generate_audio2(text, frame, temperature, top_P, top_K):
    # 批处理迭代器, 批处理大小默认为 5
    def batch(iterable, batch_size=5):
        it = iter(iterable)
        while True:
            batch = list(itertools.islice(it, batch_size))
            if not batch:
                break
            yield batch
    # 字典 {角色: 音色}
    role2seed = {row['角色']: row['音色'] for _,row in frame.iterrows()}
    print("【角色种子】", role2seed)
    # 按角色分组, 方便加速推理
    line_list = split_line(text)
    line_group = defaultdict(list)
    for line in line_list:
        line_group[line['role']].append(line)
    role2wavs = {role: [] for role in line_group}

    stream = False # 默认不使用流式输出
    text_refine = True # 默认使用文本细化
    for role, lines in line_group.items():
        audio_seed = role2seed[role] # 音色种子
        spk_emb = update_emb(audio_seed) # 音色编码
        text_seed = random.randint(seed_min, seed_max)
        for batch_lines in batch(lines):
            batch_texts = [batch_line['text'] for batch_line in batch_lines]
            batch_texts = refine_text(batch_texts, text_seed, text_refine, temperature, top_P, top_K)
            batch_wavs = next(generate_audio(batch_texts, audio_seed, stream, temperature, top_P, top_K, spk_emb, sample_emb=None, sample_text=None))
            if len(batch_lines) == 1: # 预防存在列表长度为1的批次
                batch_wavs=[batch_wavs[1]] # 选取有效数据
            role2wavs[role].extend(batch_wavs)
    # 按顺序重组
    all_wavs = []
    for line in line_list:
        wavs = role2wavs[line['role']]
        all_wavs.append(wavs.pop(0))
    # 返回采样频率以及合并后的完整音频
    yield 24000, np.concatenate(all_wavs)

######################################################################################################################

# 创建tts_more交互界面
def create_tts_more_block(temperature, top_p, top_k):
    with gr.Blocks() as tts_more_block:
        with gr.Column():
            with gr.Tab(label="有声小说"):
                with gr.Row():
                    with gr.Column(min_width=0, scale=2):
                        gr.Markdown("##### 输入小说")
                        input_text2 = gr.Textbox(
                            value=ex.input_text2, interactive=True,
                            label="", lines=18, max_lines=18, show_copy_button=True)
                        convert_btn = gr.Button("步骤①：格式转换")
                    with gr.Column(min_width=0, scale=3):
                        gr.Markdown("##### 输出剧本（格式：(角色::文本) 或 (角色：文本)")
                        output_text2 = gr.Textbox(
                            value=ex.output_text2, interactive=True,
                            label="", lines=18, max_lines=18, show_copy_button=True)
                        extract_btn = gr.Button("步骤②：角色提取")
                    with gr.Column(min_width=0, scale=2):
                        gr.Markdown("##### 设置角色")
                        output_frame = gr.DataFrame(
                            value=ex.output_frame, interactive=True,
                            height=378.5, row_count=9, col_count=(2, 'fixed'),
                            headers=["角色", "音色"], datatype=["str", "number"])
                        generate_btn2 = gr.Button("步骤③：音频生成")
                output_audio2 = gr.Audio(label="有声小说", interactive=False)
                # 响应事件
                extract_btn.click(fn=extract_roles, inputs=output_text2, outputs=output_frame)
                generate_btn2.click( # 可以通过可调参数区域的滑块来设置这里的参数
                    fn=generate_audio2,
                    inputs=[output_text2, output_frame, temperature, top_p, top_k],
                    outputs=output_audio2)
            
            with gr.Tab(label="克隆工厂"):
                gr.Button("功能添加中...")

    return tts_more_block
