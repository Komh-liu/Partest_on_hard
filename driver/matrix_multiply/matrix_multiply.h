// matrix_multiply.h （统一接口）
#pragma once
#include <vector>

using Matrix = std::vector<std::vector<int>>;

// 统一函数声明（核心唯一接口）
void matrix_multiply(const Matrix& A, Matrix& result);

// 根据不同编译选项包含实现
#if defined(USE_OPENMP)
#include "openmp_impl.h"
#elif defined(USE_MPI)
#include "mpi_impl.h"
#else
#include "single_thread_impl.h"
#endif