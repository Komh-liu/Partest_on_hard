#include <iostream>
#include <fstream>
#include <vector>
#include <tuple>
#include <cuda_runtime.h>

// Function to read the sparse matrix from a file
std::vector<std::tuple<int, int, float>> readSparseMatrix(const std::string& filename) {
    std::ifstream file(filename);
    if (!file.is_open()) {
        throw std::runtime_error("Failed to open file");
    }

    std::vector<std::tuple<int, int, float>> matrix;
    int item1, item2;
    float value;
    while (file >> item1 >> item2 >> value) {
        matrix.push_back({item1, item2, value});
    }
    file.close();
    return matrix;
}

// Function to write the result to a file
void writeResultToFile(const std::vector<std::tuple<int, int, float>>& result, const std::string& filename) {
    std::ofstream file(filename);
    if (!file.is_open()) {
        throw std::runtime_error("Failed to open file");
    }

    for (const auto& [item1, item2, value] : result) {
        file << item1 << " " << item2 << " " << value << "\n";
    }
    file.close();
}

// CUDA kernel to perform matrix multiplication
__global__ void multiplyMatricesKernel(
    const std::tuple<int, int, float>* A,
    const std::tuple<int, int, float>* AT,
    std::tuple<int, int, float>* C,
    int numElements
) {
    int idx = blockIdx.x * blockDim.x + threadIdx.x;
    if (idx >= numElements) return;

    int item1 = std::get<0>(A[idx]);
    int item2 = std::get<1>(A[idx]);
    float value = std::get<2>(A[idx]);

    // Find matching elements in AT
    for (int j = 0; j < numElements; ++j) {
        if (std::get<0>(AT[j]) == item2) {
            int resultItem1 = item1;
            int resultItem2 = std::get<1>(AT[j]);
            float resultValue = value * std::get<2>(AT[j]);

            // Find if the result position already exists
            bool found = false;
            for (int k = 0; k < numElements; ++k) {
                if (std::get<0>(C[k]) == resultItem1 && std::get<1>(C[k]) == resultItem2) {
                    std::get<2>(C[k]) += resultValue;
                    found = true;
                    break;
                }
            }
            if (!found) {
                C[numElements + idx] = {resultItem1, resultItem2, resultValue};
            }
        }
    }
}

int main() {
    try {
        // Read the sparse matrix from file
        std::vector<std::tuple<int, int, float>> A = readSparseMatrix("matrix.txt");

        // Transpose matrix A
        std::vector<std::tuple<int, int, float>> AT;
        for (const auto& [item1, item2, value] : A) {
            AT.push_back({item2, item1, value});
        }

        // Allocate memory on GPU
        std::tuple<int, int, float>* d_A;
        std::tuple<int, int, float>* d_AT;
        std::tuple<int, int, float>* d_C;
        size_t size = A.size() * sizeof(std::tuple<int, int, float>);

        cudaMalloc(&d_A, size);
        cudaMalloc(&d_AT, size);
        cudaMalloc(&d_C, size * 2); // Allocate extra space for results

        cudaMemcpy(d_A, A.data(), size, cudaMemcpyHostToDevice);
        cudaMemcpy(d_AT, AT.data(), size, cudaMemcpyHostToDevice);

        // Launch kernel
        int blockSize = 256;
        int numBlocks = (A.size() + blockSize - 1) / blockSize;
        multiplyMatricesKernel<<<numBlocks, blockSize>>>(d_A, d_AT, d_C, A.size());

        // Copy result back to host
        std::vector<std::tuple<int, int, float>> C(A.size() * 2);
        cudaMemcpy(C.data(), d_C, size * 2, cudaMemcpyDeviceToHost);

        // Write result to file
        writeResultToFile(C, "result.txt");

        // Free GPU memory
        cudaFree(d_A);
        cudaFree(d_AT);
        cudaFree(d_C);

        std::cout << "Matrix multiplication completed successfully." << std::endl;

    } catch (const std::exception& e) {
        std::cerr << "Error: " << e.what() << std::endl;
    }

    return 0;
}