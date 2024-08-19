import datetime
from fastapi import APIRouter
from pydantic import BaseModel
from .utils import clear_gpu_cache
from transformers import AutoTokenizer, AutoModelForCausalLM, GenerationConfig

router = APIRouter()

class ChatParams(BaseModel):
    prompt: str
    top_p: float = 0.7
    temperature: float = 0.9
    max_new_tokens: int = 1024
    history: list[tuple[str, str]]

@router.on_event("startup")
async def startup_event():
    global model, tokenizer
    model_path = "models/Qwen-7B-Chat"
    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(model_path, trust_remote_code=True).eval()
    model.generation_config = GenerationConfig.from_pretrained(model_path, trust_remote_code=True)

@router.post("/chat")
async def chat(params: ChatParams):
    # 调用模型生成回答
    answer, history = model.chat(
        tokenizer,
        query=params.prompt,
        history=params.history,
        top_p=params.top_p,
        temperature=params.temperature,
        max_new_tokens=params.max_new_tokens)
    # 获取当前时间
    now = datetime.datetime.now()
    time = now.strftime("%Y-%m-%d %H:%M:%S")
    # 构建响应文件
    response = {
        "time": time,
        "answer": answer,
        "history": history}
    # 打印日志
    print(f"【{time}】 Q: {params.prompt}  A: {answer}")
    clear_gpu_cache()
    return response