#include <cuda_runtime.h>
#include <vector>
#include <iostream>

using Matrix = std::vector<int>;

__global__ void matrixMultiplyKernel(const int* A, int* result, int N, int M) {
    int row = blockIdx.y * blockDim.y + threadIdx.y;
    int col = blockIdx.x * blockDim.x + threadIdx.x;

    if (row < N && col < N) {
        int sum = 0;
        for (int k = 0; k < M; ++k) {
            sum += A[row * M + k] * A[col * M + k];  // 假设是 A * A^T
        }
        result[row * N + col] = sum;
    }
}

void matrix_multiply(const Matrix& A, int N, int M, Matrix& result) {
    // 检查矩阵是否为空
    if (A.empty() || N == 0 || M == 0) {
        std::cerr << "Error: Matrix is empty." << std::endl;
        return;
    }

    size_t sizeA = N * M * sizeof(int);
    size_t sizeResult = N * N * sizeof(int); // 结果矩阵的大小是 N x N

    int* d_A;
    int* d_result;
    cudaMalloc(&d_A, sizeA);
    cudaMalloc(&d_result, sizeResult);

    // 检查CUDA错误
    cudaError_t cudaStatus = cudaGetLastError();
    if (cudaStatus != cudaSuccess) {
        std::cerr << "CUDA malloc failed: " << cudaGetErrorString(cudaStatus) << std::endl;
        return;
    }

    // 直接拷贝连续的一维主机数据到设备
    cudaMemcpy(d_A, A.data(), sizeA, cudaMemcpyHostToDevice);

    // 检查CUDA错误
    cudaStatus = cudaGetLastError();
    if (cudaStatus != cudaSuccess) {
        std::cerr << "CUDA memcpy to device failed: " << cudaGetErrorString(cudaStatus) << std::endl;
        return;
    }

    dim3 threadsPerBlock(16, 16);
    dim3 numBlocks((N + threadsPerBlock.x - 1) / threadsPerBlock.x, (N + threadsPerBlock.y - 1) / threadsPerBlock.y);

    // 调用内核函数进行矩阵乘法
    matrixMultiplyKernel<<<numBlocks, threadsPerBlock>>>(d_A, d_result, N, M);

    // 检查CUDA错误
    cudaStatus = cudaGetLastError();
    if (cudaStatus != cudaSuccess) {
        std::cerr << "CUDA kernel launch failed: " << cudaGetErrorString(cudaStatus) << std::endl;
        return;
    }

    // 将结果从设备复制回主机
    result.resize(N * N);
    cudaMemcpy(result.data(), d_result, sizeResult, cudaMemcpyDeviceToHost);

    // 检查CUDA错误
    cudaStatus = cudaGetLastError();
    if (cudaStatus != cudaSuccess) {
        std::cerr << "CUDA memcpy from device failed: " << cudaGetErrorString(cudaStatus) << std::endl;
        return;
    }

    cudaFree(d_A);
    cudaFree(d_result);
}