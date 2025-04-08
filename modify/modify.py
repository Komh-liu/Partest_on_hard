import json
from openai import OpenAI
from config import CONFIG
import os

def load_data_with_validation(original_path, modifications_path):
    """带校验的数据加载：确保任务数量和标识匹配"""
    with open(original_path, "r") as f:
        original_data = json.load(f)
    with open(modifications_path, "r") as f:
        modifications = json.load(f)
    
    # 校验任务数量一致
    if len(original_data["tasks"]) != len(modifications["tasks"]):
        raise ValueError("原始任务数与修改需求数量不匹配")
    
    # 校验任务类型对应
    for orig_task, mod_task in zip(original_data["tasks"], modifications["tasks"]):
        if orig_task["metadata"]["task_type"] != mod_task.get("task_type"):
            raise ValueError(f"任务类型不匹配: {orig_task['metadata']['task_type']} vs {mod_task.get('task_type')}")

    return original_data, modifications

def generate_context_prompt(original_code, requirements, errors):
    """构建强调代码继承性的提示模板"""
    return f"""
    请基于以下原始代码进行修改（不要重写）：
    ```cpp
    {original_code}
    ```
    
    修改需求：
    - 优化目标：{requirements}
    - 已知问题：{errors if errors else '无'}
    
    修改要求：
    1. 保持原有框架和核心逻辑
    2. 只修改必要部分并添加注释说明
    3. 保留原有API接口
    4. 用// MODIFIED: 标注修改位置
    """

def process_single_task(client, orig_task, mod_task):
    """处理单个任务的完整流程"""
    # 检查修改要求是否为 none
    if mod_task["requirements"].lower() == "none":
        print(f"任务 {orig_task['metadata']['task_type']} 的修改要求为 none，跳过该任务。")
        return orig_task["metadata"]["code"]
    
    # 构建强化提示
    system_prompt = f"""你是一个资深C++工程师，需要根据问题描述修改现有并行代码。注意：
    - 原始框架：{orig_task['metadata']['framework']}
    - 硬件配置：{json.dumps(orig_task['metadata']['hardware'], indent=2)}
    - 必须保持原有并行化策略"""
    
    user_prompt = generate_context_prompt(
        orig_task["metadata"]["code"],
        mod_task["requirements"],
        mod_task.get("errors")
    )
    
    # API调用
    completion = client.chat.completions.create(
        model=CONFIG["model"],
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
            {"role": "system", "content": "输出要求：\n1. 使用相同代码框架\n2. 只输出最终代码\n3. 用注释标注修改点\n4. 不要添加额外解释"}
        ],
        temperature=0.1,
        max_tokens=2500
    )
    
    # 提取并校验代码
    response = completion.choices[0].message.content
    if "```cpp" in response:
        code = response.split("```cpp\n")[-1].split("\n```")[0].strip()
    else:
        code = response.strip()  # 容错处理
    
    # 验证代码继承性
    if not any(keyword in code for keyword in ["omp parallel", "MPI_", "cuda"]):
        raise RuntimeError("生成的代码可能丢失原有并行化特征")
    
    return code

def generate_modified_code(original_path, modifications_path):
    """带严格校验的修改流程"""
    original_data, modifications = load_data_with_validation(original_path, modifications_path)
    client = OpenAI(api_key=os.getenv('DASHSCOPE_API_KEY'),
                   base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")
    
    modified_output = {"tasks": []}
    for orig_task, mod_task in zip(original_data["tasks"], modifications["tasks"]):
        try:
            new_code = process_single_task(client, orig_task, mod_task)
            modified_task = {
                "metadata": orig_task["metadata"].copy(),
                "modification_record": {
                    "requirements": mod_task["requirements"],
                    "error_info": mod_task.get("errors", "")
                }
            }
            modified_task["metadata"]["code"] = new_code
            modified_output["tasks"].append(modified_task)
        except Exception as e:
            print(f"处理任务 {orig_task['metadata']['task_type']} 失败: {str(e)}")
            modified_output["tasks"].append(orig_task)  # 保留原始代码
    
    with open("output_modified.json", "w") as f:
        json.dump(modified_output, f, indent=2, ensure_ascii=False)
    print("代码修改完成，结果已保存到 output_modified.json")

if __name__ == "__main__":
    generate_modified_code("output.json", "modifications.json")