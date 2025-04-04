// graph.h
#pragma once
#include <vector>
#include <queue>
#include <iostream>
#include <unordered_set>

#if defined(USE_CUDA)
#include <cuda_runtime.h>

// 使用条件编译防止重复定义
#ifndef CUDA_GRAPH_DEFINED
#define CUDA_GRAPH_DEFINED
struct CUDAGraph {
    int numVertices;
    int numEdges;
    int* offset;    // 顶点邻接表偏移数组
    int* edges;     // 邻接顶点数据数组
};
#endif // CUDA_GRAPH_DEFINED

void bfs(const CUDAGraph& graph, int start); 
#else
// 定义图的邻接表表示
using Graph = std::vector<std::vector<int>>;
void bfs(const Graph& graph, int start);
#endif

// 根据不同编译选项包含实现
#if defined(USE_OPENMP)
#include "openmp_impl.h"
#elif defined(USE_MPI)
#include "mpi_impl.h"
#elif defined(USE_CUDA)
#include "cuda_impl.cu"  // 仍然直接包含.cu文件
#else
#include "single_thread_impl.h"
#endif