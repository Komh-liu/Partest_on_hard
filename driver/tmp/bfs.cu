#include <cuda_runtime.h>
#include <iostream>

// BFS 内核函数：并行处理当前层的节点
__global__ void bfs_kernel(const int* d_offset, const int* d_edges,
                          int* d_visited, int* d_current, int* d_next,
                          int* current_size, int* next_size) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx < *current_size) {
        int u = d_current[idx];
        int start = d_offset[u];
        int end = d_offset[u + 1];

        // 遍历当前节点的所有邻居
        for (int i = start; i < end; ++i) {
            int v = d_edges[i];
            // 原子操作标记访问，确保每个节点只被处理一次
            if (atomicExch(&d_visited[v], 1) == 0) {
                int pos = atomicAdd(next_size, 1);  // 原子操作分配位置
                d_next[pos] = v;
            }
        }
    }
}

// BFS 主函数
void bfs(const CUDAGraph& graph, int start) {
    // 分配设备内存
    int *d_offset, *d_edges, *d_visited;
    int *d_current, *d_next;
    int *d_current_size, *d_next_size;

    cudaMalloc(&d_offset, (graph.numVertices + 1) * sizeof(int));
    cudaMalloc(&d_edges, graph.numEdges * sizeof(int));
    cudaMalloc(&d_visited, graph.numVertices * sizeof(int));
    cudaMalloc(&d_current, graph.numVertices * sizeof(int));
    cudaMalloc(&d_next, graph.numVertices * sizeof(int));
    cudaMallocManaged(&d_current_size, sizeof(int));
    cudaMallocManaged(&d_next_size, sizeof(int));

    // 拷贝图数据到设备
    cudaMemcpy(d_offset, graph.offset, (graph.numVertices + 1) * sizeof(int), cudaMemcpyHostToDevice);
    cudaMemcpy(d_edges, graph.edges, graph.numEdges * sizeof(int), cudaMemcpyHostToDevice);

    // 初始化 visited 数组和当前层
    cudaMemset(d_visited, 0, graph.numVertices * sizeof(int));
    int one = 1;
    cudaMemcpy(&d_visited[start], &one, sizeof(int), cudaMemcpyHostToDevice);  // 标记起始节点
    *d_current_size = 1;
    *d_next_size = 0;
    cudaMemcpy(d_current, &start, sizeof(int), cudaMemcpyHostToDevice);

    // 打印起始节点
    std::cout << "BFS Order: " << start << " ";

    // 循环处理每一层
    while (*d_current_size > 0) {
        // 配置内核参数
        dim3 block(256);
        dim3 grid((*d_current_size + block.x - 1) / block.x);

        // 启动内核
        bfs_kernel<<<grid, block>>>(d_offset, d_edges, d_visited,
                                   d_current, d_next, d_current_size, d_next_size);
        cudaDeviceSynchronize();

        // 交换 current 和 next，并重置 next_size
        std::swap(d_current, d_next);
        *d_current_size = *d_next_size;
        *d_next_size = 0;

        // 打印当前层的节点
        if (*d_current_size > 0) {
            int* current_layer = new int[*d_current_size];
            cudaMemcpy(current_layer, d_current, *d_current_size * sizeof(int), cudaMemcpyDeviceToHost);
            for (int i = 0; i < *d_current_size; ++i) {
                std::cout << current_layer[i] << " ";
            }
            delete[] current_layer;
        }
    }
    std::cout << std::endl;

    // 释放设备内存
    cudaFree(d_offset);
    cudaFree(d_edges);
    cudaFree(d_visited);
    cudaFree(d_current);
    cudaFree(d_next);
    cudaFree(d_current_size);
    cudaFree(d_next_size);
}