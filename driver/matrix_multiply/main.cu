#include "matrix_multiply.h"
#include <iostream>
#include <chrono>
#include <fstream>
#include <vector>

using Matrix = std::vector<int>;

// 加载矩阵函数
Matrix load_matrix(const std::string& filename, int& rows, int& cols) {
    std::ifstream file(filename);
    if (!file.is_open()) {
        std::cerr << "Failed to open file: " << filename << std::endl;
        exit(1);
    }

    file >> rows >> cols; // 读取矩阵的行数和列数

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
                file << i << " " << j << " " <<  value << std::endl;
            }
        }
    }
}

int main() {
    int N, M;
    Matrix A = load_matrix("/home/liu/Gitrepo/parwork/dataset/matrix_multiply/matrix_small.txt", N, M); // 加载矩阵
    Matrix result; // 初始化结果矩阵为空
    result.resize(N * N , 0);
    auto start = std::chrono::high_resolution_clock::now();
    matrix_multiply(A, N, M, result); // 统一函数调用
    auto end = std::chrono::high_resolution_clock::now();

    // 输出耗时和验证结果
    std::cout << "Time: " 
              << std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count()
              << "ms\n";
    save_matrix(result, N, N, "/home/liu/Gitrepo/parwork/driver/matrix_multiply/result.txt");

    return 0;
}