#include <iostream>
#include <cuda_runtime.h>

// CUDA 内核函数
__global__ void addKernel(int *a, int *b, int *c) {
    int i = blockIdx.x * blockDim.x + threadIdx.x;
    c[i] = a[i] + b[i];
}

int main() {
    const int arraySize = 10;
    const int blockSize = 1;
    const int gridSize = arraySize / blockSize;

    // 在主机上分配内存
    int h_a[arraySize], h_b[arraySize], h_c[arraySize];
    for (int i = 0; i < arraySize; i++) {
        h_a[i] = i;
        h_b[i] = i * 2;
    }

    // 在设备上分配内存
    int *d_a, *d_b, *d_c;
    cudaMalloc((void**)&d_a, arraySize * sizeof(int));
    cudaMalloc((void**)&d_b, arraySize * sizeof(int));
    cudaMalloc((void**)&d_c, arraySize * sizeof(int));

    // 将数据从主机复制到设备
    cudaMemcpy(d_a, h_a, arraySize * sizeof(int), cudaMemcpyHostToDevice);
    cudaMemcpy(d_b, h_b, arraySize * sizeof(int), cudaMemcpyHostToDevice);

    // 启动 CUDA 内核
    addKernel<<<gridSize, blockSize>>>(d_a, d_b, d_c);

    // 将结果从设备复制回主机
    cudaMemcpy(h_c, d_c, arraySize * sizeof(int), cudaMemcpyDeviceToHost);

    // 打印结果
    for (int i = 0; i < arraySize; i++) {
        std::cout << h_c[i] << " ";
    }
    std::cout << std::endl;

    // 释放设备内存
    cudaFree(d_a);
    cudaFree(d_b);
    cudaFree(d_c);

    return 0;
}