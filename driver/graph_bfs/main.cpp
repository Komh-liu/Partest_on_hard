// main.cpp
#include "graph_bfs.h"
#include <fstream>
#include <sstream>
#include <algorithm> // 添加 std::max 所需的头文件
#include <chrono>    // 添加 std::chrono 所需的头文件

Graph loadGraphFromFile(const std::string& filename) {
    std::ifstream file(filename);
    if (!file.is_open()) {
        std::cerr << "无法打开文件: " << filename << std::endl;
        return {};
    }

    int maxVertex = 0;
    std::vector<std::pair<int, int>> edges;
    std::string line;
    while (std::getline(file, line)) {
        std::istringstream iss(line);
        int u, v;
        if (iss >> u >> v) {
            edges.emplace_back(u, v);
            maxVertex = std::max({maxVertex, u, v});
        }
    }
    file.close();

    Graph graph(maxVertex + 1);
    for (const auto& edge : edges) {
        int u = edge.first;
        int v = edge.second;
        graph[u].push_back(v);
        graph[v].push_back(u); // 无向图
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
    //std::string filename = "data.txt";
    Graph graph = loadGraphFromFile(input_file);

    if (!graph.empty()) {
        int startVertex = 0; // 从顶点 0 开始进行 BFS
        std::cout << "BFS starting from vertex " << startVertex << ": ";

        // 记录开始时间
        auto start = std::chrono::high_resolution_clock::now();

        bfs(graph, startVertex);

        // 记录结束时间
        auto end = std::chrono::high_resolution_clock::now();

        // 计算并输出执行时间
        std::chrono::duration<double, std::milli> duration = end - start;
        std::cout << "\nTime: " << duration.count() << "ms\n";
    }
    //std::cout << "BFS starting from vertex " << ": ";
    return 0;
}