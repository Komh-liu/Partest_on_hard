import json
import subprocess
import os
import tempfile
import shutil
import time
import re  # 导入正则表达式模块
import glob  # 用于文件匹配

def list_files_in_directory(directory):
    """列出指定目录中的所有文件和文件夹"""
    files = os.listdir(directory)
    print(f"目录内容 ({directory}):")
    for file in files:
        print(f"  {file}")

def extract_and_compile(metadata, current_dir, temp_dir):
    framework = metadata['framework']
    task_type = metadata['task_type']  # 获取任务类型
    # 创建头文件路径
    if framework == 'Serial':
        header_file_name = 'single_thread_impl.h'
    elif framework == 'OpenMP':
        header_file_name = 'openmp_impl.h'
    elif framework == 'CUDA':
        header_file_name = 'cuda_impl.cu'
    elif framework == 'MPI':
        header_file_name = 'mpi_impl.h'
    else:
        # 这里可以根据需要添加更多框架的处理
        header_file_name = 'single_thread_impl.h'

    header_file_path = os.path.join(temp_dir, header_file_name)

    # 使用头文件保护机制避免重复定义
    code_content = metadata['code'].strip().replace("```cpp", "").replace("```", "")
    protected_code = f"#ifndef {header_file_name.replace('.', '_').upper()}\n#define {header_file_name.replace('.', '_').upper()}\n{code_content}\n#endif // {header_file_name.replace('.', '_').upper()}"

    # 将目标代码写入头文件
    with open(header_file_path, 'w') as header_file:
        header_file.write(protected_code)

    # 定义相对路径的测试文件夹
    relative_test_folder_path = task_type

    # 计算测试文件夹的绝对路径
    absolute_test_folder_path = os.path.join(current_dir, relative_test_folder_path)
    # 检查文件夹是否存在
    if not os.path.exists(absolute_test_folder_path):
        print(f"文件夹 {absolute_test_folder_path} 不存在，跳过此任务。")
        return

    # 复制整个f"{task_type}"文件夹到临时文件夹
    temp_test_folder_path = os.path.join(temp_dir, relative_test_folder_path)
    shutil.copytree(absolute_test_folder_path, temp_test_folder_path)

    # 根据framework选择头文件包含
    include_line = f'#include "{header_file_name}"'

    # 修改main.cpp以包含正确的头文件
    if framework == 'CUDA':
        main_cpp_path = os.path.join(temp_test_folder_path, 'main.cu')
    else:
        main_cpp_path = os.path.join(temp_test_folder_path, 'main.cpp')
    if not os.path.exists(main_cpp_path):
        print(f"文件 {main_cpp_path} 不存在，跳过此任务。")
        return

    with open(main_cpp_path, 'r') as main_file:
        lines = main_file.readlines()

    new_lines = []
    found_include = False
    for line in lines:
        if line.startswith("#include"):
            if not found_include:
                # new_lines.append(f'{include_line}\n')
                found_include = True
        new_lines.append(line)

    with open(main_cpp_path, 'w') as main_file:
        main_file.writelines(new_lines)

    # 根据框架调整编译命令
    if framework == 'OpenMP':
        compile_command = f"g++ -std=c++17 {main_cpp_path} -o {os.path.join(temp_dir, 'main')} -I{temp_dir} -fopenmp -DUSE_OPENMP"
        print("g++ OpenMP编译")
    elif framework == 'CUDA':
        main_cu_path = os.path.join(temp_test_folder_path, 'main.cu')
        compile_command = f"nvcc -std=c++17 {main_cu_path} -o {os.path.join(temp_dir, 'main')} -I{temp_dir} -lcudart -DUSE_CUDA"
        print("nvcc CUDA编译")
    elif framework == 'MPI':
        compile_command = f"mpicxx -std=c++17 {main_cpp_path} -o {os.path.join(temp_dir, 'main')} -I{temp_dir} -DUSE_MPI"
        print("mpicxx MPI编译")
    else:
        print("g++编译")
        compile_command = f"g++ -std=c++17 {main_cpp_path} -o {os.path.join(temp_dir, 'main')} -I{temp_dir}"

    # 检查main.c是否存在
    print(f"检查main.c是否存在: {os.path.exists(os.path.join(temp_dir, 'main.c'))}")
    
    print(f"编译命令: {compile_command}")
    compile_result = subprocess.run(compile_command, shell=True, capture_output=True, text=True, cwd=temp_dir)

    # 检查编译是否成功
    if compile_result.returncode != 0:
        print("编译失败！")
        print("错误信息：")
        print(compile_result.stderr)
        log_content = f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {framework} - {task_type} - 编译失败 - 运行时长: N/A\n"
        with open('log.txt', 'a') as log_file:
            log_file.write(log_content)
        return

    # 检查可执行文件是否存在
    executable_path = os.path.join(temp_dir, 'main')
    if os.path.exists(executable_path):
        print(f"可执行文件存在: {executable_path}")
        # 添加执行权限
        os.chmod(executable_path, 0o755)
        print("已添加执行权限")
    else:
        print(f"可执行文件不存在: {executable_path}")
        return

    parent_path = os.path.dirname(current_dir)
    
    # 获取所有数据集文件
    dataset_dir = os.path.join(parent_path, 'dataset', task_type)
    if not os.path.exists(dataset_dir):
        print(f"数据集目录 {dataset_dir} 不存在，跳过此任务。")
        return
    
    # 获取所有txt文件
    txt_files = [f for f in os.listdir(dataset_dir) if f.endswith('.txt')]
    
    if not txt_files:
        print(f"数据集目录 {dataset_dir} 中没有.txt文件，跳过此任务。")
        return
    
    print(f"找到 {len(txt_files)} 个测试文件: {', '.join(txt_files)}")
    
    # 确保driver中的输出目录存在
    driver_output_dir = os.path.join(parent_path, 'driver', task_type)
    os.makedirs(driver_output_dir, exist_ok=True)
    
    # 依次测试每个文件
    for txt_file in txt_files:
        print(f"\n开始测试文件: {txt_file}")
        input_file = os.path.join(dataset_dir, txt_file)
        
        # 寻找格式为 "result_<txt_file>" 的文件
        result_file_pattern = f"result_{txt_file}"
        result_file_path = os.path.join(driver_output_dir, result_file_pattern)
        
        # 检查结果文件是否存在
        if not os.path.exists(result_file_path):
            print(f"验证结果文件 {result_file_path} 不存在，跳过此测试文件。")
            continue
        
        # 使用现有的结果文件作为输出文件
        output_file = result_file_path
        print(f"使用验证文件: {output_file}")
            
        # 使用绝对路径的可执行文件
        absolute_executable = os.path.abspath(os.path.join(temp_dir, 'main'))
        run_command = f"{absolute_executable} {input_file} {output_file}"
        print(f"执行完整命令: {run_command}")
        
        start_time = time.time()
        
        try:
            # 使用subprocess代替os.system以便捕获更多错误信息
            run_result = subprocess.run(run_command, shell=True, capture_output=True, text=True, timeout=300)  # 设置超时时间为300秒（5分钟）
        except subprocess.TimeoutExpired:
            print(f"测试文件 {txt_file} 运行超时！")
            log_content = f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {framework} - {task_type} - {txt_file} - 运行超时 - 运行时长: {int((time.time() - start_time) * 1000)}ms\n"
            with open("log.txt", 'a') as log_file:
                log_file.write(log_content)
            continue  # 继续测试下一个文件

        end_time = time.time()
        runtime = (end_time - start_time) * 1000  # 转换为毫秒

        # 检查运行结果
        if run_result.returncode != 0:
            print(f"测试文件 {txt_file} 运行失败！")
            print("错误信息：")
            print(run_result.stderr)
            print("标准输出：")
            print(run_result.stdout)
            log_content = f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {framework} - {task_type} - {txt_file} - 运行失败 - 运行时长: {runtime:.2f}ms\n"
        else:
            print(f"测试文件 {txt_file} 运行成功！")
            print("输出结果：")
            print(run_result.stdout)
            # 提取运行时间和验证成功与否的信息
            time_match = re.search(r"Time: (\d+)ms", run_result.stdout)
            success_match = re.search(r"验证成功", run_result.stdout)
            time_info = time_match.group(1) if time_match else f"{runtime:.0f}"
            success_info = "验证成功" if success_match else "验证失败"
            log_content = f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {framework} - {task_type} - {txt_file} - 运行成功 - 运行时间: {time_info}ms - {success_info}\n"

        with open("log.txt", 'a') as log_file:
            log_file.write(log_content)

    # 清理临时文件夹
    shutil.rmtree(temp_dir)

# 定义JSON文件路径
json_file_path = 'output.json'

# 获取当前脚本所在的绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))

# 读取JSON文件内容
with open(json_file_path, 'r') as file:
    data = json.load(file)

# 遍历所有任务
for task in data['tasks']:
    # 提取任务的元数据
    metadata = task['metadata']

    # 创建临时文件夹
    temp_dir = tempfile.mkdtemp()

    # 提取和编译
    extract_and_compile(metadata, current_dir, temp_dir)
