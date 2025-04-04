import json
import subprocess
import os
import tempfile
import shutil

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
    elif framework =='MPI':
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
    # print(absolute_test_folder_path)
    # 检查文件夹是否存在
    if not os.path.exists(absolute_test_folder_path):
        print(f"文件夹 {absolute_test_folder_path} 不存在，跳过此任务。")
        return

    # 复制整个f"{task_type}"文件夹到临时文件夹
    temp_test_folder_path = os.path.join(temp_dir, relative_test_folder_path)
    shutil.copytree(absolute_test_folder_path, temp_test_folder_path)

    # 记录复制的文件夹路径
    # print(f"测试文件夹已复制到: {temp_test_folder_path}")
    # list_files_in_directory(temp_test_folder_path)  # 列出复制后的文件夹中的文件

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
        # print(main_cpp_path)
        compile_command = f"g++ {main_cpp_path} -o {os.path.join(temp_dir, 'main')} -I{temp_dir}"

    compile_result = subprocess.run(compile_command, shell=True, capture_output=True, text=True, cwd=temp_dir)

    # 检查编译是否成功
    if compile_result.returncode != 0:
        print("编译失败！")
        print("错误信息：")
        print(compile_result.stderr)
        return
    parent_path = os.path.dirname(current_dir)
    # 运行测试代码
    input_file = os.path.join(parent_path, 'dataset', task_type, 'data.txt')
    output_file = os.path.join(parent_path, 'driver', task_type, 'result.txt')
    run_command = f"./{os.path.basename(os.path.join(temp_dir, 'main'))} {input_file} {output_file}"
    run_result = subprocess.run(run_command, shell=True, capture_output=True, text=True, cwd=temp_dir)

    # 检查运行结果
    if run_result.returncode != 0:
        print("测试代码运行失败！")
        print("错误信息：")
        print(run_result.stderr)
    else:
        print("测试代码运行成功！")
        print("输出结果：")
        print(run_result.stderr)
        print(run_result.stdout)

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