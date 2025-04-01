#include "matrix_multiply.h"
#include <iostream>
#include <chrono>
#include <fstream>
#include <vector>
Matrix load_matrix(const std::string& filename) {
    std::ifstream file(filename);
    if (!file.is_open()) {
        std::cerr << "Failed to open file: " << filename << std::endl;
        exit(1);
    }

    int rows, cols;
    file >> rows >> cols; // 读取矩阵的行数和列数
    std::cout << "Matrix size: " << rows << " x " << cols << std::endl;
    Matrix matrix(rows, std::vector<int>(cols, 0)); // 初始化为全零矩阵

    // 读取三元组形式的非零元素
    int i, j, value;
    while (file >> i >> j >> value) {
        if (i >= 0 && i < rows && j >= 0 && j < cols) {
            matrix[i][j] = value;
        } else {
            std::cerr << "Invalid matrix coordinates: (" << i << ", " << j << ")" << std::endl;
        }
    }

    return matrix;
}

// 将矩阵保存为三元组形式
void save_matrix(const Matrix& matrix, const std::string& filename) {
    std::ofstream file(filename);
    if (!file.is_open()) {
        std::cerr << "Failed to open file: " << filename << std::endl;
        exit(1);
    }

    int rows = matrix.size();
    if (rows == 0) {
        std::cerr << "Matrix is empty." << std::endl;
        return;
    }

    int cols = matrix[0].size();
    // file << rows << " " << cols << std::endl; // 写入矩阵的行数和列数

    // 保存非零元素为三元组形式
    for (int i = 0; i < rows; ++i) {
        for (int j = 0; j < cols; ++j) {
            if (matrix[i][j] != 0) {
                file << i << " " << j << " " << matrix[i][j] << std::endl;
                //std::cout << "once" << std::endl;
            }
        }
    }
    //std::cout << "Matrix size: " << rows << " x " << cols << std::endl;
}
int main() {
    Matrix A = load_matrix("/home/liu/Gitrepo/parwork/dataset/matrix_multiply/matrix_small.txt"); // 加载矩阵
    Matrix result(A.size(), std::vector<int>(A.size()));
    result.resize(A[0].size(), std::vector<int>(A[0].size(), 0)); // 初始化结果矩阵为 m x m 的零矩阵
    // 使用std::fill填充矩阵为全0
    for (auto& row : result) {
        std::fill(row.begin(), row.end(), 0);
    }

    auto start = std::chrono::high_resolution_clock::now();
    matrix_multiply(A, result); // 统一函数调用
    auto end = std::chrono::high_resolution_clock::now();

    // 输出耗时和验证结果
    std::cout << "Time: " 
              << std::chrono::duration_cast<std::chrono::milliseconds>(end-start).count()
              << "ms\n";
    save_matrix(result, "/home/liu/Gitrepo/parwork/driver/matrix_multiply/result.txt");
}