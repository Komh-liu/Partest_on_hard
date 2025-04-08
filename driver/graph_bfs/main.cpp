#include "graph_bfs.h"
#include <fstream>
#include <sstream>
#include <algorithm>
#include <chrono>
#include <iostream>
#include <vector>
#include <string>
#include <numeric>

std::vector<int> loadFileToVector(const std::string& filename) {
    std::vector<int> result;
    std::ifstream file(filename);
    if (!file.is_open()) {
        std::cerr << "无法打开文件: " << filename << std::endl;
        return result;
    }
    std::string line;
    while (std::getline(file, line)) {
        std::istringstream iss(line);
        int num;
        while (iss >> num) {
            result.push_back(num);
        }
    }
    file.close();
    return result;
}
Graph loadGraphFromFile(const std::string& filename) {
    std::ifstream file(filename);
    Graph graph;

    if (!file.is_open()) {
        std::cerr << "无法打开文件: " << filename << std::endl;
        return {0, 0, nullptr, nullptr};
    }

    // 读取文件内容并构建CSR格式
    std::vector<int> tempEdges;
    std::vector<int> tempOffset;
    tempOffset.push_back(0);

    int maxVertex = 0;
    std::string line;
    while (std::getline(file, line)) {
        std::istringstream iss(line);
        int u, v;
        if (iss >> u >> v) {
            maxVertex = std::max({maxVertex, u, v});
            tempEdges.push_back(v);
            if (tempOffset.size() <= u + 1) {
                tempOffset.resize(u + 2);
            }
            tempOffset[u + 1]++;
        }
    }
    file.close();

    // 计算顶点偏移
    graph.numVertices = maxVertex + 1;
    graph.offset = new int[graph.numVertices + 1];
    std::partial_sum(tempOffset.begin(), tempOffset.end(), graph.offset);

    // 构建边数组
    graph.numEdges = graph.offset[graph.numVertices];
    graph.edges = new int[graph.numEdges];

    // 填充边数组
    std::vector<int> edgeIndex(graph.numVertices + 1, 0);
    for (int i = 0; i < tempEdges.size(); ++i) {
        int u = i / (graph.numVertices + 1); // 假设每行只包含两个顶点
        int idx = graph.offset[u] + edgeIndex[u];
        graph.edges[idx] = tempEdges[i];
        edgeIndex[u]++;
    }

    return graph;
}
int main(int argc, char* argv[]) {
    if (argc != 3) {
        std::cerr << "Usage: " << argv[0] << " <input_file> <result_file>" << std::endl;
        return 1;
    }

    std::string input_file = argv[1];
    std::string result_file = argv[2];
    Graph graph = loadGraphFromFile(input_file);

    if (graph.numVertices > 0) {
        int bfs_start_vertex = 214328887; // 修改变量名以避免冲突
        std::cout << "BFS starting from vertex " << bfs_start_vertex << ":\n";
        std::vector<int> bfs_result;
        std::vector<int> result = loadFileToVector(result_file);
        // 时间测量部分
        auto time_start = std::chrono::high_resolution_clock::now(); // 修改变量名
        bfs(graph, bfs_start_vertex,bfs_result);
        auto time_end = std::chrono::high_resolution_clock::now(); // 修改变量名

        // 清理内存
        delete[] graph.offset;
        delete[] graph.edges;

        // 输出运行时间
        std::cout << "Time: " 
                  << std::chrono::duration_cast<std::chrono::milliseconds>(time_end - time_start).count()
                  << "ms\n";
        if(result == bfs_result)
            std::cout << "验证成功";
    }
    return 0;
}