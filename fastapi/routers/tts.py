import io
import sys
import torch
import zipfile
from models import ChatTTS
from typing import Optional
from pydantic import BaseModel
from fastapi import APIRouter, responses, UploadFile
from .utils import TorchSeedContext, clear_gpu_cache, load_audio
from .utils import get_logger, float_to_int16, pcm_arr_to_mp3_view

router = APIRouter()

logger = get_logger("TTS")

@router.on_event("startup")
async def startup_event():
    global chat
    chat = ChatTTS.Chat(get_logger("ChatTTS"))
    logger.info("Initializing ChatTTS...")
    if chat.load():
        logger.info("Models loaded successfully.")
    else:
        logger.error("Models load failed.")
        sys.exit(1)

class TTSParams(BaseModel):
    text_seed: int
    audio_seed: int
    text: list[str]
    stream: bool = False
    use_decoder: bool = True
    lang: Optional[str] = None
    skip_refine_text: bool = False
    refine_text_only: bool = False
    do_text_normalization: bool = True
    do_homophone_replacement: bool = False
    params_refine_text: ChatTTS.Chat.RefineTextParams
    params_infer_code: ChatTTS.Chat.InferCodeParams

@router.post("/tts")
async def tts(params: TTSParams):
    logger.info(f"Input text: {params.text}")
    # 设置speaker
    if params.audio_seed:
        torch.manual_seed(params.audio_seed)
        params.params_infer_code.spk_emb = chat.sample_random_speaker()
    # 文本细化
    if params.params_refine_text:
        torch.manual_seed(params.text_seed)
        text = chat.infer(text=params.text, skip_refine_text=False, refine_text_only=True)
        logger.info(f"Refined text: {text}")
    else:
        text = params.text
    # 文本转语音
    logger.info("Start inferring.")
    wavs = chat.infer(
        text=text,
        lang=params.lang,
        stream=params.stream,
        use_decoder=params.use_decoder,
        skip_refine_text=params.skip_refine_text,
        do_text_normalization=params.do_text_normalization,
        do_homophone_replacement=params.do_homophone_replacement,
        params_refine_text=params.params_refine_text,
        params_infer_code=params.params_infer_code,)
    logger.info("Inference completed.")
    # 音频压缩
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'a', zipfile.ZIP_DEFLATED, allowZip64=False) as f:
        for idx, wav in enumerate(wavs):
            f.writestr(f"{idx}.mp3", pcm_arr_to_mp3_view(wav))
    logger.info("Audio generation successful.")
    buf.seek(0)
    # 构建响应文件
    response = responses.StreamingResponse(content=buf, media_type="application/zip")
    response.headers["Content-Disposition"] = "attachment; filename=audio_files.zip"
    clear_gpu_cache()
    return response


@router.post("/tts/sas")
async def sas(file: UploadFile):
    sample_audio = load_audio(file.file, 24000)
    return chat.sample_audio_speaker(sample_audio)

class SeedParams(BaseModel):
    seed: int

@router.post("/tts/srs")
async def srs(params: SeedParams):
    with TorchSeedContext(params.seed):
        return chat.sample_random_speaker()

@router.post("/tts/reload")
async def reload():
    chat.unload()
    chat.load()
    return chat.coef

@router.post("/tts/interrupt")
async def interrupt():
    chat.interrupt()

class RefineParams(BaseModel):
    text: str | list[str]
    text_seed: int
    params_refine_text: ChatTTS.Chat.RefineTextParams

@router.post("/tts/refine")
async def refine(params: RefineParams):
    with TorchSeedContext(params.text_seed):
        clear_gpu_cache() # 清理缓存
        return chat.infer(
            text=params.text,
            refine_text_only=True,
            skip_refine_text=False,
            params_refine_text=params.params_refine_text)

class GenerateParams(BaseModel):
    text: str | list[str]
    audio_seed: int
    stream: bool = False
    params_infer_code: ChatTTS.Chat.InferCodeParams

def generator(params: GenerateParams):
    with TorchSeedContext(params.audio_seed):
        clear_gpu_cache() # 清理缓存
        wavs = chat.infer(
            text=params.text,
            stream=params.stream,
            skip_refine_text=True,
            params_infer_code=params.params_infer_code)
        if params.stream: # 流式响应
            for wav_list in wavs: # 这里wavs是迭代器
                wav = wav_list[0] # 这里列表长度为 1
                if wav is not None and len(wav) > 0:
                    yield float_to_int16(wav).tobytes()
        else: # 非流式响应，这里wavs是列表，其长度>=1
            yield float_to_int16(wavs).tolist()

@router.post("/tts/generate")
async def generate(params: GenerateParams):
    if params.stream: # 流式响应
        return responses.StreamingResponse(
            content=generator(params), media_type='audio/wav')
    else: # 非流式响应，返回列表数据
        return next(generator(params))
