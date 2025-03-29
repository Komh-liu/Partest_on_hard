#include <iostream>
#include <fstream>
#include <vector>
#include <unordered_map>
#include <omp.h>

// 定义三元组结构体
struct Triplet {
    int row;
    int col;
    float value;
};

// 读取稀疏矩阵的三元组表示
std::vector<Triplet> readSparseMatrix(const std::string& filename) {
    std::vector<Triplet> matrix;
    std::ifstream file(filename);
    if (file.is_open()) {
        int row, col;
        float value;
        while (file >> row >> col >> value) {
            matrix.push_back({row, col, value});
        }
        file.close();
    }
    return matrix;
}

// 计算矩阵与它转置的乘积
std::unordered_map<int, std::unordered_map<int, float>> multiplyWithTranspose(const std::vector<Triplet>& matrix, int rows, int cols) {
    std::unordered_map<int, std::unordered_map<int, float>> result;
    int numThreads = omp_get_max_threads();
    #pragma omp parallel for num_threads(numThreads)
    for (size_t i = 0; i < matrix.size(); ++i) {
        for (size_t j = 0; j < matrix.size(); ++j) {
            if (matrix[i].col == matrix[j].col) {
                int row = matrix[i].row;
                int col = matrix[j].row;
                float prod = matrix[i].value * matrix[j].value;
                #pragma omp critical
                {
                    result[row][col] += prod;
                }
            }
        }
    }
    return result;
}

// 将结果保存到文件中
void saveResult(const std::unordered_map<int, std::unordered_map<int, float>>& result, const std::string& filename) {
    std::ofstream file(filename);
    if (file.is_open()) {
        for (const auto& rowPair : result) {
            int row = rowPair.first;
            for (const auto& colPair : rowPair.second) {
                int col = colPair.first;
                float value = colPair.second;
                file << row << " " << col << " " << value << std::endl;
            }
        }
        file.close();
    }
}

int main() {
    int rows = 18528;
    int cols = 123628;
    std::string inputFilename = "matrix.txt";
    std::string outputFilename = "result.txt";

    // 读取稀疏矩阵
    std::vector<Triplet> matrix = readSparseMatrix(inputFilename);

    // 计算矩阵与它转置的乘积
    std::unordered_map<int, std::unordered_map<int, float>> product = multiplyWithTranspose(matrix, rows, cols);

    // 保存结果到文件
    saveResult(product, outputFilename);

    std::cout << "矩阵乘法完成，结果已保存到 " << outputFilename << std::endl;

    return 0;
}    