#include "graph_bfs.h"
#include <fstream>
#include <fstream>
#include <sstream>
#include <algorithm>

CUDAGraph loadCUDAGraphFromFile(const std::string& filename) {
    std::ifstream file(filename);
    CUDAGraph graph;
    std::vector<std::vector<int>> tempGraph;

    if (!file.is_open()) {
        std::cerr << "无法打开文件: " << filename << std::endl;
        return {0, 0, nullptr, nullptr};
    }

    // 读取数据到临时邻接表
    int maxVertex = 0;
    std::string line;
    while (std::getline(file, line)) {
        std::istringstream iss(line);
        int u, v;
        if (iss >> u >> v) {
            maxVertex = std::max({maxVertex, u, v});
            if (tempGraph.size() <= maxVertex) tempGraph.resize(maxVertex + 1);
            tempGraph[u].push_back(v);
            tempGraph[v].push_back(u);
        }
    }
    file.close();

    // 转换为CSR格式
    graph.numVertices = tempGraph.size();
    graph.offset = new int[graph.numVertices + 1];
    graph.offset[0] = 0;
    
    for (int i = 0; i < tempGraph.size(); ++i) {
        graph.offset[i+1] = graph.offset[i] + tempGraph[i].size();
    }
    
    graph.numEdges = graph.offset[tempGraph.size()];
    graph.edges = new int[graph.numEdges];
    
    int idx = 0;
    for (const auto& list : tempGraph) {
        for (int v : list) {
            graph.edges[idx++] = v;
        }
    }

    return graph;
}

int main() {
    std::string filename = "data.txt";
    CUDAGraph graph = loadCUDAGraphFromFile(filename);

    if (graph.numVertices > 0) {
        int start = 0;
        std::cout << "CUDA BFS starting from vertex " << start << ":\n";
        bfs(graph, start);
        
        // 清理内存
        delete[] graph.offset;
        delete[] graph.edges;
    }

    return 0;
}