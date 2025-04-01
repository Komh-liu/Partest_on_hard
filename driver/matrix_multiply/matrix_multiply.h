// matrix_multiply.h （统一接口）
#pragma once
#include <vector>

// 为不同框架提供不同的类型定义和函数声明
#if defined(USE_CUDA)
// CUDA 版本使用一维向量表示矩阵
using Matrix = std::vector<int>;
// CUDA 版本的函数声明
void matrix_multiply(const Matrix& A, int N, int M, Matrix& result);
#else
// 其他版本使用二维向量表示矩阵
using Matrix = std::vector<std::vector<int>>;
// 其他版本的函数声明
void matrix_multiply(const Matrix& A, Matrix& result);
#endif

// 根据不同编译选项包含实现
#if defined(USE_OPENMP)
#include "openmp_impl.h"
#elif defined(USE_MPI)
#include "mpi_impl.h"
#elif defined(USE_CUDA)
#include "cuda_impl.cu"
#else
#include "single_thread_impl.h"
#endif