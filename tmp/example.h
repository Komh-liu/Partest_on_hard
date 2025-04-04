// single_thread_impl.h （单线程实现）
#include "matrix_multiply.h"


#include <iostream>
#include <vector>
#include <thread>
#include <algorithm>

using Matrix = std::vector<std::vector<int>>;

void matrix_multiply(const Matrix& A, Matrix& result) {
    int rowsA = A.size();
    int colsA = A[0].size();
    int colsResult = colsA; // 结果矩阵的列数等于A的行数

    if (result.empty() || result.size() != rowsA || result[0].size() != colsResult) {
        result.resize(rowsA, std::vector<int>(colsResult));
    }

    for (int i = 0; i < rowsA; ++i) {
        for (int j = 0; j < colsResult; ++j) {
            result[i][j] = 0;
            for (int k = 0; k < colsA; ++k) {
                result[i][j] += A[i][k] * A[k][j];
            }
        }
    }
}