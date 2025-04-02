#include "array_sum.h"
#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <string>
#include <cuda_runtime.h>  // CUDA 运行时头文件
#include <chrono>

// 加载数组从文件
std::vector<int> load_array_from_file(const std::string& filename) {
    std::vector<int> arr;
    std::ifstream file(filename);
    std::string line;

    if (!file.is_open()) {
        std::cerr << "无法打开文件: " << filename << std::endl;
        exit(1);
    }

    while (std::getline(file, line)) {
        std::istringstream iss(line);
        int num;
        while (iss >> num) {
            arr.push_back(num);
        }
    }

    file.close();
    return arr;
}

int load_result_from_file(const std::string& filename) {
    int result;
    std::ifstream file(filename);
    std::string line;

    if (!file.is_open()) {
        std::cerr << "无法打开文件: " << filename << std::endl;
        exit(1);
    }

    while (std::getline(file, line)) {
        std::istringstream iss(line);
        int num;
        iss >> result;
    }

    file.close();
    return result;
}

// 主函数
int main(int argc, char* argv[]) {
    if (argc != 3) {
        std::cerr << "Usage: " << argv[0] << " <input_file> <result_file>" << std::endl;
        return 1;
    }

    std::string input_file = argv[1];
    std::string result_file = argv[2];

    // 从文件加载数组
    std::vector<int> arr = load_array_from_file(input_file);
    int result = load_result_from_file(result_file);

    // 调用统一接口函数
    auto start = std::chrono::high_resolution_clock::now();
    int sum = array_sum(arr);
    std::cout << "数组的和是: " << sum << std::endl; // 统一函数调用
    auto end = std::chrono::high_resolution_clock::now();

    // 输出耗时和验证结果
    std::cout << "Time: " 
              << std::chrono::duration_cast<std::chrono::milliseconds>(end - start).count()
              << "ms\n";
    if(result == sum)
        std::cout << "验证成功" << std::endl;
    return 0;
}