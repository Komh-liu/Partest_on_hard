#include "graph_bfs.h"
#include <fstream>
#include <sstream>
#include <algorithm>
#include <chrono>

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

int main(int argc, char* argv[]) {
    if (argc != 3) {
        std::cerr << "Usage: " << argv[0] << " <input_file> <result_file>" << std::endl;
        return 1;
    }

    std::string input_file = argv[1];
    std::string result_file = argv[2];
    CUDAGraph graph = loadCUDAGraphFromFile(input_file);

    if (graph.numVertices > 0) {
        int bfs_start_vertex = 0; // 修改变量名以避免冲突
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