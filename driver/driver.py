import json
import subprocess
import os
import tempfile
import shutil

def extract_and_compile(metadata, current_dir, temp_dir):
    # 创建头文件路径
    header_file_path = os.path.join(temp_dir, 'single_thread_impl.h')

    # 使用头文件保护机制避免重复定义
    code_content = metadata['code'].strip().replace("```cpp", "").replace("```", "")
    protected_code = f"#ifndef SINGLE_THREAD_IMPL_H\n#define SINGLE_THREAD_IMPL_H\n{code_content}\n#endif // SINGLE_THREAD_IMPL_H"

    # 将目标代码写入头文件
    with open(header_file_path, 'w') as header_file:
        header_file.write(protected_code)

    # 定义相对路径的测试文件夹
    relative_test_folder_path = 'matrix_multiply'

    # 计算测试文件夹的绝对路径
    absolute_test_folder_path = os.path.join(current_dir, relative_test_folder_path)

    # 检查文件夹是否存在
    if not os.path.exists(absolute_test_folder_path):
        print(f"文件夹 {absolute_test_folder_path} 不存在，跳过此任务。")
        return

    # 复制整个matrix_multiply文件夹到临时文件夹
    temp_test_folder_path = os.path.join(temp_dir, relative_test_folder_path)
    shutil.copytree(absolute_test_folder_path, temp_test_folder_path)

    # 根据framework选择头文件包含
    if metadata['framework'] == 'Serial':
        include_line = '#include "single_thread_impl.h"'
    elif metadata['framework'] == 'OpenMP':
        include_line = '#include "openmp_impl.h"'
    elif metadata['framework'] == 'MPI':
        include_line = '#include "mpi_impl.h"'
    else:
        print(f"不支持的框架: {metadata['framework']}，跳过此任务。")
        return

    # 修改main.cpp以包含正确的头文件
    main_cpp_path = os.path.join(temp_test_folder_path, 'main.cpp')
    if not os.path.exists(main_cpp_path):
        print(f"文件 {main_cpp_path} 不存在，跳过此任务。")
        return

    with open(main_cpp_path, 'r') as main_file:
        lines = main_file.readlines()

    new_lines = []
    for line in lines:
        if line.startswith('#include "matrix_multiply.h"'):
            new_lines.append(f'{include_line}\n')
        else:
            new_lines.append(line)

    with open(main_cpp_path, 'w') as main_file:
        main_file.writelines(new_lines)

    # 根据框架选择编译命令
    executable_path = os.path.join(temp_dir, 'main')
    if metadata['framework'] == 'Serial':
        compile_command = f"g++ {main_cpp_path} -o {executable_path} -I{temp_dir}"
    elif metadata['framework'] == 'OpenMP':
        compile_command = f"g++ -DUSE_OPENMP {main_cpp_path} -o {executable_path} -I{temp_dir} -fopenmp"
    elif metadata['framework'] == 'MPI':
        compile_command = f"mpicxx -DUSE_MPI {main_cpp_path} -o {executable_path} -I{temp_dir}"
    else:
        print(f"不支持的框架: {metadata['framework']}，跳过此任务。")
        return

    # 编译测试代码
    compile_result = subprocess.run(compile_command, shell=True, capture_output=True, text=True, cwd=temp_dir)

    # 检查编译是否成功
    if compile_result.returncode != 0:
        print("编译失败！")
        print("错误信息：")
        print(compile_result.stderr)
        return

    # 运行测试代码
    run_command = f"./{os.path.basename(executable_path)}"
    run_result = subprocess.run(run_command, shell=True, capture_output=True, text=True, cwd=temp_dir)

    # 检查运行结果
    if run_result.returncode != 0:
        print("测试代码运行失败！")
        print("错误信息：")
        print(run_result.stderr)
    else:
        print("测试代码运行成功！")
        print("输出结果：")
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