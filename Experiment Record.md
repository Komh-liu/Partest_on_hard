## 2025/3/29
```shell
Error: cannot create std::vector larger than max_size()
```
注意到模型无法注意到显存和数据规模的关系从而调整策略
```bash
Segmentation fault (core dumped)
```
注意到生成的代码在边界逻辑上经常存在问题

## MPI和openmp的关系


## Todo
array扩大到一亿