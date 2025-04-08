# 打开文件，如果文件不存在则创建，如果存在则覆盖
with open("numbers.txt", "w") as file:
    # 遍历从1到10000的数字
    for i in range(1, 10001):
        # 将每个数字写入文件，每个数字占一行
        file.write(str(i) + " ")

print("数字1到10000已成功写入numbers.txt文件中。")