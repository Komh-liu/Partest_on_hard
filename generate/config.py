CONFIG = {
    "api_key": "sk-02d5dbd0219246a38fb9b22bf31613b1",
    "model": "qwen2.5-coder-3b-instruct",
    "devices": {
        "cpu": {
            "type": "CPU",
            "cores": 16,
            "memory": "32GB",
            "available": True,
        },
        "gpu": {
            "type": "GPU",
            "compute_capability": 8.0,  # CUDA compute capability
            "memory": "16GB",
            "threads_per_block": 1024,
            "available": True,
        }
    }
}