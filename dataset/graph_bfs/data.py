import random

num_nodes = 1000000  # 节点数量
num_edges = 500000000  # 边数量

with open("data.txt", "w") as f:
    for _ in range(num_edges):
        u = random.randint(1, num_nodes)
        v = random.randint(1, num_nodes)
        f.write(f"{u} {v}\n")