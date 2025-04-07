import json
from openai import OpenAI
from config import CONFIG
import os


def check_available_devices(hardware):
    # 检查可用设备
    available_devices = []
    
    # 检查多个CPU
    if "cpus" in hardware:
        for cpu in hardware["cpus"]:
            if cpu.get("available") == "True":
                available_devices.append({
                    "type": "CPU",
                    "cores": cpu.get("cores", "N/A"),
                    "threads": cpu.get("threads", "N/A"),
                    "frequency": cpu.get("frequency", "N/A")
                })
    
    # 检查GPU
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
    
    # 构建可用设备信息
    available_devices_info = []
    for device in available_devices:
        if device["type"] == "CPU":
            device_info = f"CPU（核心数: {device['cores']}, 线程数: {device['threads']}, 频率: {device['frequency']})"
        else:
            device_info = f"GPU（CUDA核心数: {device['cores']}, 显存: {device['memory'].get('size', 'N/A')})"
        available_devices_info.append(device_info)
    
    available_devices_info = ", ".join(available_devices_info)

    # 可选框架列表
    available_frameworks = [
        "Serial",
        "OpenMP",
        "MPI",
        # "CUDA",
    ]

    # 遍历所有任务
    for task in config["tasks"]:
        # 构建系统提示词
        system_prompt = f"""你是一个C++专家，需要根据以下配置生成优化的并行计算代码：
        - 任务类型: {task['type']}
        - 硬件配置: {available_devices_info}
        - 可用框架: {', '.join(available_frameworks)}
        请根据硬件信息和任务需求，从可选框架中选择最合适的一个来生成代码。
        """

        # 构建用户提示词
        user_prompt_content = f"根据任务生成优化的并行计算代码：\n\n"

        # 根据可能选择的框架准备不同的函数签名和上下文
        for framework in available_frameworks:
            if framework == "CUDA":
                function_signature = task["function_signatures"]["CUDA"]
                context = task["contexts"]["CUDA"]
            else:
                function_signature = task["function_signatures"]["other"]
                context = task["contexts"]["other"]
            user_prompt_content += f"如果选择 {framework} 框架：\n包含的头文件和结构体定义：\n{context}\n\n函数签名：\n{function_signature}\n\n"

        user_prompt = {
            "role": "user",
            "content": user_prompt_content
        }

        # 初始化OpenAI客户端
        client = OpenAI(
            api_key=os.getenv('DASHSCOPE_API_KEY'),
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
                    "content": f"请严格按以下格式输出代码：\n1. 代码必须用\n```cpp\n开始\n2. 用\n```\n结束\n3. 中间只包含C++代码\n4. 只输出所选框架对应的函数实现，不输出prompt给出的结构体定义,如果框架是mpi需要先进行MPI_INIT\n5. 禁止输出任何解释性文字或注释\n6. 在代码前指定所选择的框架（例如：选择的框架：<框架名称>）\n7. 尽可能根据硬件条件减小资源消耗"
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
        framework = None
        code_lines = []
        for line in response_lines:
            if line.startswith("选择的框架："):
                framework = line.split("：")[1]
            else:
                code_lines.append(line)

        code_content = "\n".join(code_lines).strip()

        # 确保代码内容只包含函数实现
        if code_content.startswith("```cpp") and code_content.endswith("```"):
            code_content = code_content[6:-3].strip()  # 去除代码块标记
        print(f"选择的框架：{framework}")
        print("*"*50)
        print(f"代码实现：\n{code_content}")
        print("*"*50)
        # 将当前任务的元数据和代码追加到全局输出结构中
        task_output = {
            "metadata": {
                "task_type": task["type"],
                "hardware": config["hardware"],
                "code": code_content,
                "framework": framework
            }
        }
        global_output["tasks"].append(task_output)

    # 在所有任务完成后，将全局输出结构保存到同一个文件中
    with open("output.json", "w") as f:
        json.dump(global_output, f, indent=2, ensure_ascii=False)

    print("所有任务的代码生成完成，结果已保存到 output.json")


if __name__ == "__main__":
    generate_code("input.json")