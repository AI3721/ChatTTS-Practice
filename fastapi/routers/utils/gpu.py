import torch

# 清理GPU缓存
def clear_gpu_cache():
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.ipc_collect()