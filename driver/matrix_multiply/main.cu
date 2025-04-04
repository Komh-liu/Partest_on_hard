#include "matrix_multiply.h"
#include <iostream>
#include <chrono>
#include <fstream>
#include <vector>
#include <string>
#include <ctime>
#include <filesystem>

using Matrix = std::vector<int>;

// 加载矩阵函数
Matrix load_matrix(const std::string& filename, int& rows, int& cols) {
    std::ifstream file(filename);
    if (!file.is_open()) {
        std::cerr << "Failed to open file: " << filename << std::endl;
        exit(1);
    }

    file >> rows >> cols; // 读取矩阵行数和列数

    Matrix matrix(rows * cols, 0); // 初始化为全零矩阵

    // 读取三元组形式的非零元素
    int i, j, value;
    while (file >> i >> j >> value) {
        if (i >= 0 && i < rows && j >= 0 && j < cols) {
            matrix[i * cols + j] = value;
        } else {
            std::cerr << "Invalid matrix coordinates: (" << i << ", " << j << ")" << std::endl;
        }
    }

    return matrix;
}

// 将矩阵保存为三元组形式
void save_matrix(const Matrix& matrix, int rows, int cols, const std::string& filename) {
    std::ofstream file(filename);
    if (!file.is_open()) {
        std::cerr << "Failed to open file: " << filename << std::endl;
        exit(1);
    }

    file << rows << " " << cols << std::endl; // 写入矩阵的行数和列数

    // 保存非零元素为三元组形式
    for (int i = 0; i < rows; ++i) {
        for (int j = 0; j < cols; ++j) {
            int value = matrix[i * cols + j];
            if (value != 0) {
                file << i << " " << j << " " << value << std::endl;
            }
        }
    }
}

// 比较两个文本文件是否相同
bool compare_text_files(const std::string& file1, const std::string& file2) {
    // 打开两个文件
    std::ifstream f1(file1);
    std::ifstream f2(file2);

    // 检查文件是否成功打开
    if (!f1.is_open() || !f2.is_open()) {
        std::cerr << "无法打开文件！" << std::endl;
        return false;
    }

    // 逐行读取并比较
    std::string line1, line2;
    bool same = true;

    while (true) {
        std::getline(f1, line1);
        std::getline(f2, line2);

        // 检查是否同时到达文件末尾
        if (f1.eof() && f2.eof()) {
            break;
        }

        // 如果一个文件到达末尾而另一个没有，行数不同
        if (f1.eof() != f2.eof()) {
            std::cerr << "文件行数不同！" << std::endl;
            same = false;
            break;
        }

        // 比较当前行
        if (line1 != line2) {
            std::cerr << "文件内容不同！" << std::endl;
            same = false;
            break;
        }
    }
    return same;
}

// 生成包含时间戳的文件名
std::string generate_filename_with_timestamp(const std::string& base_filename) {
    // 获取当前时间
    std::time_t now = std::time(nullptr);
    std::tm* now_tm = std::localtime(&now);

    // 格式化时间戳
    char timestamp_str[20];
    std::strftime(timestamp_str, sizeof(timestamp_str), "%Y%m%d_%H%M%S", now_tm);

    // 提取文件名（不包含路径）
    std::filesystem::path path(base_filename);
    std::string filename = path.filename().string();

    // 生成新文件名
    std::string new_filename = filename + "_" + timestamp_str + ".txt";

    // 返回新文件的完整路径
    return (path.parent_path() / new_filename).string();
}

// 将输入文件和输出文件的内容保存到新文件
void save_combined_file(const std::string& input_file, const std::string& output_file, const std::string& combined_file) {
    std::ofstream combined(combined_file);
    if (!combined.is_open()) {
        std::cerr << "Failed to open combined file: " << combined_file << std::endl;
        exit(1);
    }

    // 写入输入文件的内容
    // combined << "Input File Content:\n";
    std::ifstream input(input_file);
    std::string line;
    //while (std::getline(input, line)) {
    //    combined << line << "\n";
    //}
    input.close();

    // 写入输出文件的内容
    //combined << "\nOutput File Content:\n";
    std::ifstream output(output_file);
    while (std::getline(output, line)) {
        combined << line << "\n";
    }
    output.close();

    combined.close();
}

int main(int argc, char* argv[]) {
    if (argc != 3) {
        std::cerr << "Usage: " << argv[0] << " <input_file> <output_file>" << std::endl;
        return 1;
    }

    std::string input_file = argv[1];
    std::string output_file = argv[2];

    int N, M;
    Matrix A = load_matrix(input_file, N, M); // 加载矩阵
    Matrix result; // 初始化结果矩阵为空
    result.resize(N * N, 0);
    auto start = std::chrono::high_resolution_clock::now();
    matrix_multiply(A, N, M, result); // 统一函数调用
    auto end = std::chrono::high_resolution_clock::now();

    // 输出耗时和验证结果
    std::cout << "Time: " 
              << std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count()
              << "ms\n";

    // 保存结果到输出文件
    save_matrix(result, N, N, output_file);

    // 生成包含时间戳的文件名
    std::string combined_file = generate_filename_with_timestamp(output_file);

    // 保存输入文件和输出文件的内容到新文件
    save_combined_file(input_file, output_file, combined_file);

    //std::cout << "Combined file saved as: " << combined_file << std::endl;
    bool c_result = compare_text_files(combined_file, output_file);
    if(c_result)
       std::cout<<"验证成功"<<std::endl;
    else
        std::cout<<"验证失败"<<std::endl;
    return 0;
}