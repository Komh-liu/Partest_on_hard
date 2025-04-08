CONFIG = {
    #"model": "qwen2.5-coder-3b-instruct",
    # "model": "qwen-coder-plus",
    # "model": "deepseek-r1",
    "model": "deepseek-v3",
    "devices": {
        "cpu": {
            "type": "CPU",
            "cores": 16,
            "memory": "32GB",
            "available": True,
        },
        "gpu": {
            "type": " NVIDIA GPU RTX 3090",
            "compute_capability": 8.0,  # CUDA compute capability
            "memory": "24GB",
            "threads_per_block": 1024,
            "available": True,
        }
    }
}