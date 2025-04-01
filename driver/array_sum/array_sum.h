// array_sum.h （统一接口）
#pragma once
#include <vector>

// 定义数组类型
using Array = std::vector<int>;

// 统一函数声明（核心唯一接口）
int array_sum(const Array& arr);

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