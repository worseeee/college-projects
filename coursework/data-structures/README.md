# 数据结构与算法练习

线性表、栈、队列、树、图、最短路与迷宫

**性质**：课程练习 / 小型工具。

## 功能与实现

- 线性表、栈、队列、树、图、最短路与迷宫。
- 各文件按独立练习保留，不将单文件练习计作完整系统项目。

## 目录与入口

- `Array/Array1D.c`
- `Array/Array2D.c`
- `Array/String.c`
- `Graph/Dijkstra.c`
- `Graph/Graph.c`
- `Graph/In_Degree.c`
- `List/LinList.c`
- `List/LinList.h`
- `List/LinListSort.c`
- `List/Locate.c`
- `List/Location/main.c`
- `List/ReLinList.c`
- `Print/Print.c`
- `Print/Queue.c`
- `Print/main.c`
- `Queue/ReQueue.c`
- `Recursive/Maze.c`
- `Stack/bag.c`
- 其余文件见当前目录（共 22 个源码/设计文件）。

## 环境与运行

使用 GCC/Clang 或课程指定 C 编译器，按每个含 main 的练习独立构建。多文件练习同时编译其依赖源文件，避免把所有同名 main 链接到一个程序。

```bash
gcc -Wall -Wextra -o exercise <entry.c> <required-source.c>
```

## 验证范围与复现说明

- 本次只做发布整理与静态检查，未将所有练习逐一运行。
- 输入文本、真实账号和生成文件未发布；课程参考实现保持学习材料性质。

## 资料与来源

保留源码中的课程、厂商与开源来源标注。依赖与权重按各自许可另行获取。

[返回项目总览](../../README.md)
