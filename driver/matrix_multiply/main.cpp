#include <iostream>
#include <fstream>
#include <vector>
#include <unordered_map>
#include <omp.h>
#include <chrono>
#include <sys/resource.h>
#include <sys/time.h>

// 假设 multiplyWithTranspose 在 generate.hpp 中定义
#include "generate.hpp"

// 定义三元组结构体
struct Triplet {
    int row;
    int col;
    float value;
};

// 读取稀疏矩阵的三元组表示
std::vector<Triplet> readSparseMatrix(const std::string& filename) {
    std::vector<Triplet> matrix;
    std::ifstream file(filename);
    if (file.is_open()) {
        int row, col;
        float value;
        while (file >> row >> col >> value) {
            matrix.push_back({row, col, value});
        }
        file.close();
    }
    return matrix;
}

// 将结果保存到文件中
void saveResult(const std::unordered_map<int, std::unordered_map<int, float>>& result, const std::string& filename) {
    std::ofstream file(filename);
    if (file.is_open()) {
        for (const auto& rowPair : result) {
            int row = rowPair.first;
            for (const auto& colPair : rowPair.second) {
                int col = colPair.first;
                float value = colPair.second;
                file << row << " " << col << " " << value << std::endl;
            }
        }
        file.close();
    }
}

// 获取 CPU 时间
double getCPUTime() {
    struct rusage ru;
    getrusage(RUSAGE_SELF, &ru);
    return (double)ru.ru_utime.tv_sec + (double)ru.ru_utime.tv_usec / 1000000.0;
}

// 获取内存使用情况
long getMemoryUsage() {
    struct rusage ru;
    getrusage(RUSAGE_SELF, &ru);
    return ru.ru_maxrss;
}

int main() {
    int rows = 100;
    int cols = 100;
    std::string inputFilename = "matrix_small.txt";
    std::string outputFilename = "result.txt";

    // 读取稀疏矩阵
    std::vector<Triplet> matrix = readSparseMatrix(inputFilename);

    // 记录开始时间
    auto start_time = std::chrono::high_resolution_clock::now();
    double start_cpu_time = getCPUTime();
    long start_memory = getMemoryUsage();

    // 计算矩阵与它转置的乘积
    std::unordered_map<int, std::unordered_map<int, float>> product = multiplyWithTranspose(matrix, rows, cols);

    // 记录结束时间
    auto end_time = std::chrono::high_resolution_clock::now();
    double end_cpu_time = getCPUTime();
    long end_memory = getMemoryUsage();

    // 计算时间和内存使用情况
    auto duration = std::chrono::duration_cast<std::chrono::milliseconds>(end_time - start_time).count();
    double cpu_time = end_cpu_time - start_cpu_time;
    long memory_usage = end_memory - start_memory;

    // 保存结果到文件
    saveResult(product, outputFilename);

    std::cout << "矩阵乘法完成，结果已保存到 " << outputFilename << std::endl;
    std::cout << "测试消耗时间: " << duration << " 毫秒" << std::endl;
    std::cout << "CPU 占用时间: " << cpu_time << " 秒" << std::endl;
    std::cout << "内存占用: " << memory_usage << " KB" << std::endl;

    return 0;
}