import json
from openai import OpenAI
from config import CONFIG

def check_available_devices(hardware):
    # 检查可用设备
    available_devices = []
    if hardware.get("cpu", {}).get("available") == "True":
        available_devices.append({
            "type": "CPU",
            "cores": hardware["cpu"].get("cores", "N/A"),
            "cpu_memory": hardware.get("resources", {}).get("cpu_memory", "N/A")
        })
    if hardware.get("gpu", {}).get("available") == "True":
        available_devices.append({
            "type": "GPU",
            "cores": hardware["gpu"].get("cuda_cores", "N/A"),
            "memory": hardware["gpu"].get("memory", {})
        })
    return available_devices

def generate_code(config_path):
    # 读取任务描述文件
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    
    # 初始化一个全局的输出结构
    global_output = {
        "tasks": []
    }

    # 检查可用设备
    available_devices = check_available_devices(config["hardware"])
    available_devices_info = ", ".join([f"{device['type']}（核心数/线程数: {device.get('cores', 'N/A')}，内存: {device['memory'].get('size', 'N/A') if device['type'] == 'GPU' else device.get('cpu_memory', 'N/A')})" for device in available_devices])
    
    # 可选框架列表
    available_frameworks = [
        "OpenMP",
        #"TBB",
        #"CUDA",
        #"Serial"
    ]
    
    # 构建系统提示词
    system_prompt = f"""你是一个C++专家，需要根据以下配置生成优化的并行计算代码：
    - 任务类型: {config['task']['type']}
    - 函数签名: {config['task']['function_signature']}
    - 头文件和结构体定义(输出中省略): {config['task']['context']}
    - 硬件配置: CPU核心数: {config['hardware'].get('cpu', {}).get('cores', 'N/A')}, GPU显存: {config['hardware'].get('gpu', {}).get('memory', {}).get('size', 'N/A')}
    - 可用设备: {available_devices_info}
    - 可选框架: {', '.join(available_frameworks)}
    """
    
    # 构建用户提示词
    user_prompt = {
        "role": "user",
        "content": f"根据任务生成优化的并行计算代码：\n\n包含的头文件和结构体定义：\n{config['task']['context']}\n\n函数签名：\n{config['task']['function_signature']}\n\n请选择一个框架：{', '.join(available_frameworks)}"
    }

    # 初始化OpenAI客户端
    client = OpenAI(
        api_key=CONFIG["api_key"],
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
    )

    # 构造完整的消息列表
    messages = [
        {"role": "system", "content": system_prompt},
        user_prompt
    ]

    # 调用API
    completion = client.chat.completions.create(
        model=CONFIG["model"],
        messages=[
            {
                "role": "system",
                "content": f"请严格按以下格式输出代码：\n1. 代码必须用\n```cpp\n开始\n2. 用\n```\n结束\n3. 中间只包含C++代码\n4. 只输出{config['task']['function_signature']}的函数实现，禁止输出其他函数或结构体定义\n5. 禁止输出任何解释性文字或注释\n6. 在代码前指定所选择的框架（例如：选择的框架：OpenMP）"
            },
            *messages
        ],
        temperature=0.2,
        max_tokens=2500,
        stop=["\n```\n"]  # 设置停止标记为代码块结束符
    )

    # 提取代码内容并清理
    response_content = completion.choices[0].message.content
    response_lines = response_content.strip().split("\n")

    # 提取框架信息
    framework = "Serial"  # 默认框架
    code_lines = []
    for line in response_lines:
        if line.startswith("选择的框架："):
            framework = line.replace("选择的框架：", "").strip()
        else:
            code_lines.append(line)

    code_content = "\n".join(code_lines).strip()

    # 从代码内容检测框架
    if "#pragma omp" in code_content:
        framework = "OpenMP"
    elif "tbb::" in code_content:
        framework = "TBB"
    elif "__global__" in code_content:
        framework = "CUDA"

    # 确保代码内容只包含函数实现
    if code_content.startswith("```cpp") and code_content.endswith("```"):
        code_content = code_content[6:-3].strip()  # 去除代码块标记

    # 将当前任务的元数据和代码追加到全局输出结构中
    task_output = {
        "metadata": {
            "task_type": config["task"]["type"],
            "hardware": config["hardware"],
            "code": code_content,
            "framework": framework
        }
    }
    global_output["tasks"].append(task_output)

    # 打印生成的代码
    print("\n生成的代码：")
    print("-" * 50)
    print(code_content)
    print("-" * 50)

    print(f"选择的框架：{framework}")

    # 在所有任务完成后，将全局输出结构保存到同一个文件中
    with open("output.json", "w") as f:
        json.dump(global_output, f, indent=2, ensure_ascii=False)

    print("所有任务的代码生成完成，结果已保存到 output.json")

if __name__ == "__main__":
    generate_code("input.json")