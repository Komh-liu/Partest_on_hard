// graph.cpp
#include "graph.h"
#include <fstream>
#include <sstream>
#include <string>
#include <algorithm> // 添加 std::max 所需的头文件

// 从文件中加载图

// BFS 算法
void bfs(const Graph& graph, int start) {
    int numVertices = graph.size();
    std::vector<bool> visited(numVertices, false);
    std::queue<int> q;

    visited[start] = true;
    q.push(start);

    while (!q.empty()) {
        int vertex = q.front();
        q.pop();
        std::cout << vertex << " ";

        for (int neighbor : graph[vertex]) {
            if (!visited[neighbor]) {
                visited[neighbor] = true;
                q.push(neighbor);
            }
        }
    }
    std::cout << std::endl;
}