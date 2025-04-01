#include "array_sum.h"
#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <string>
#include <cuda_runtime.h>  // CUDA 运行时头文件

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

// 主函数
int main() {
    // 从文件加载数组
    std::vector<int> arr = load_array_from_file("/home/liu/Gitrepo/parwork/dataset/array_sum/data.txt");

    // 调用统一接口函数
    int sum = array_sum(arr);

    // 输出结果
    std::cout << "数组的和是: " << sum << std::endl;

    return 0;
}