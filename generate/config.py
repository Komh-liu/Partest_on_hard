CONFIG = {
    #"model": "qwen2.5-coder-3b-instruct",
    "model": "deepseek-r1",
    "devices": {
        "cpu": {
            "type": "CPU",
            "cores": 16,
            "memory": "32GB",
            "available": True,
        },
        "gpu": {
            "type": " NVIDIA GPU RTX 3060",
            "compute_capability": 8.0,  # CUDA compute capability
            "memory": "16GB",
            "threads_per_block": 1024,
            "available": True,
        }
    }
}