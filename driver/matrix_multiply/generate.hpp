#ifndef GENERATE_HPP
#define GENERATE_HPP

#include <vector>
#include <unordered_map>

// 定义三元组结构体
struct Triplet {
    int row;
    int col;
    float value;
};

// 计算矩阵与它转置的乘积
std::unordered_map<int, std::unordered_map<int, float>> multiplyWithTranspose(const std::vector<Triplet>& matrix, int rows, int cols) {
    std::unordered_map<int, std::unordered_map<int, float>> result;
    for (size_t i = 0; i < matrix.size(); ++i) {
        for (size_t j = 0; j < matrix.size(); ++j) {
            if (matrix[i].col == matrix[j].col) {
                int row = matrix[i].row;
                int col = matrix[j].row;
                float prod = matrix[i].value * matrix[j].value;
                result[row][col] += prod;
            }
        }
    }
    return result;
}    

#endif // GENERATE_HPP    