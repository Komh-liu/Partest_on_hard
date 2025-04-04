// main.cpp
#include "graph_bfs.h"
#include <fstream>
#include <sstream>
#include <algorithm> // 添加 std::max 所需的头文件
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
int main() {
    std::string filename = "data.txt"; // 假设图的边信息存储在 graph.txt 文件中
    Graph graph = loadGraphFromFile(filename);

    if (!graph.empty()) {
        int startVertex = 0; // 从顶点 0 开始进行 BFS
        std::cout << "BFS starting from vertex " << startVertex << ": ";
        bfs(graph, startVertex);
    }

    return 0;
}