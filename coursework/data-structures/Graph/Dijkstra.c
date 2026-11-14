#include <stdio.h>
#include <stdlib.h>
#include <limits.h>

#define MaxVertices 100   // 最大顶点数
#define INFINITY 65535    // 表示无穷大，用于表示两点间无直接路径

typedef char VertexType;  // 顶点数据类型

// 邻接矩阵图的结构定义
typedef struct {
    VertexType vertices[MaxVertices];     // 顶点数组
    int edge[MaxVertices][MaxVertices];   // 邻接矩阵，存储边的权重
    int numVertices;                       // 顶点数
    int numEdges;                          // 边数
} MGraph;

// ============ 图的基本操作 ============

// 初始化图
void InitGraph(MGraph *G) {
    G->numVertices = 0;
    G->numEdges = 0;
    
    int i = 0, j = 0;
    // 初始化邻接矩阵：对角线为0，其他位置为无穷大
    for (i = 0; i < MaxVertices; i++) {
        for (j = 0; j < MaxVertices; j++) {
            if (i == j)
                G->edge[i][j] = 0;
            else
                G->edge[i][j] = INFINITY;
        }
    }
}

// 添加顶点
void AddVertex(MGraph *G, VertexType v) {
    if (G->numVertices >= MaxVertices) {
        printf("顶点数已达上限！\n");
        return;
    }
    G->vertices[G->numVertices] = v;
    G->numVertices++;
}

// 添加边（有向图）
void AddEdge(MGraph *G, int from, int to, int weight) {
    if (from < 0 || from >= G->numVertices || to < 0 || to >= G->numVertices) {
        printf("顶点索引超出范围！\n");
        return;
    }
    
    // 只设置一个方向，因为是有向图
    G->edge[from][to] = weight;
    G->numEdges++;
}

// 查找顶点的索引
int LocateVertex(MGraph *G, VertexType v) {
	int i = 0;
    for (i = 0; i < G->numVertices; i++) {
        if (G->vertices[i] == v)
            return i;
    }
    return -1;
}

// 打印邻接矩阵
void PrintGraph(MGraph *G) {
    printf("\n========== 图的邻接矩阵表示 ==========\n");
    printf("      ");
    
    int i = 0, j = 0;
    for (i = 0; i < G->numVertices; i++) {
        printf("%4c ", G->vertices[i]);
    }
    printf("\n");
    
    for (i = 0; i < G->numVertices; i++) {
        printf("  %c   ", G->vertices[i]);
        for (j = 0; j < G->numVertices; j++) {
            if (G->edge[i][j] == INFINITY)
                printf("  ∞  ");
            else
                printf("%4d ", G->edge[i][j]);
        }
        printf("\n");
    }
    printf("======================================\n");
}

// ============ Dijkstra算法核心实现 ============

/**
 * Dijkstra算法求单源最短路径
 * 
 * 算法思想：
 * 1. 维护两个集合：已找到最短路径的顶点集S，和未确定的顶点集V-S
 * 2. 维护一个距离数组dist[]，记录源点到各顶点的当前最短距离
 * 3. 每次从V-S中选择dist值最小的顶点u加入S
 * 4. 更新u的所有邻接点v的距离：如果dist[u]+edge[u][v] < dist[v]，则更新dist[v]
 * 5. 重复步骤3-4，直到所有顶点都加入S或剩余顶点不可达
 * 
 * @param G 图的邻接矩阵表示
 * @param start 源点索引
 * @param dist 输出参数：存储源点到各顶点的最短距离
 * @param path 输出参数：存储最短路径树（每个顶点的前驱）
 */
void Dijkstra(MGraph *G, int start, int dist[], int path[]) {
    // visited数组标记顶点是否已找到最短路径
    // visited[i]=1表示顶点i已确定最短路径，加入集合S
    int visited[MaxVertices] = {0};
    int i = 0, v = 0, count = 1;
    
    // 第一步：初始化
    // 设置源点到各顶点的初始距离和路径前驱
    for (i = 0; i < G->numVertices; i++) {
        dist[i] = G->edge[start][i];  // 初始距离为源点到该点的直接距离
        
        // 初始化路径前驱
        // 如果源点可以直接到达顶点i，则i的前驱是源点
        // 否则前驱设为-1表示不可达
        if (dist[i] < INFINITY)
            path[i] = start;
        else
            path[i] = -1;
    }
    
    // 源点到自己的距离为0，且源点已确定最短路径
    dist[start] = 0;
    visited[start] = 1;
    path[start] = -1;  // 源点没有前驱
    
    // 第二步：迭代寻找最短路径
    // 需要处理n-1个顶点（源点已处理）
    for (count = 1; count < G->numVertices; count++) {
        
        // 在未访问的顶点中找到距离源点最近的顶点
        int minDist = INFINITY;
        int u = -1;  // 距离最近的顶点
        
        for (i = 0; i < G->numVertices; i++) {
            // 如果顶点i未访问，且距离比当前最小距离更小
            if (!visited[i] && dist[i] < minDist) {
                minDist = dist[i];
                u = i;
            }
        }
        
        // 如果找不到可达的未访问顶点，说明剩余顶点都不可达，算法结束
        if (u == -1)
            break;
        
        // 标记顶点u为已访问（加入集合S）
        visited[u] = 1;
        
        // 第三步：通过顶点u更新其邻接点的距离
        // 这是算法的核心：松弛操作（Relaxation）
        for (v = 0; v < G->numVertices; v++) {
            // 对于u的每个邻接点v（edge[u][v]不为无穷大）
            // 如果v未访问，且通过u到达v的路径更短
            if (!visited[v] && G->edge[u][v] < INFINITY) {
                // 计算通过u到达v的新距离
                int newDist = dist[u] + G->edge[u][v];
                
                // 如果新距离更短，则更新
                if (newDist < dist[v]) {
                    dist[v] = newDist;
                    path[v] = u;  // 更新v的前驱为u
                }
            }
        }
    }
}

// ============ 辅助函数：打印路径 ============

/**
 * 递归打印从源点到目标点的路径
 * 
 * 思路：从目标点开始，沿着path数组逆向追溯到源点
 * 使用递归可以正向打印路径
 * 
 * @param G 图
 * @param path 路径数组（记录每个顶点的前驱）
 * @param start 源点
 * @param end 目标点
 */
void PrintPath(MGraph *G, int path[], int start, int end) {
    // 递归终止条件：到达源点
    if (end == start) {
        printf("%c", G->vertices[start]);
        return;
    }
    
    // 如果目标点不可达（前驱为-1）
    if (path[end] == -1) {
        printf("不可达");
        return;
    }
    
    // 递归打印前驱节点到源点的路径
    PrintPath(G, path, start, path[end]);
    
    // 打印当前节点
    printf(" -> %c", G->vertices[end]);
}

/**
 * 打印Dijkstra算法的完整结果
 * 包括最短距离和完整路径
 */
void PrintDijkstraResult(MGraph *G, int start, int dist[], int path[]) {
    printf("\n========== 最短路径结果 ==========\n");
    printf("源点: %c\n\n", G->vertices[start]);
    printf("目标点\t最短距离\t最短路径\n");
    printf("------\t--------\t----------------------------------\n");
    
    int i = 0;
    for (i = 0; i < G->numVertices; i++) {
        // 跳过源点自己
        if (i == start)
            continue;
        
        printf("  %c\t", G->vertices[i]);
        
        if (dist[i] == INFINITY) {
            printf("  ∞\t\t不可达\n");
        } else {
            printf("%6d\t\t", dist[i]);
            PrintPath(G, path, start, i);
            printf("\n");
        }
    }
    printf("==================================\n");
}

// ============ 测试函数 ============

// 创建测试图1：考研常见的标准测试用例
void CreateTestGraph1(MGraph *G) {
    InitGraph(G);
    
    // 添加顶点
    char vertices[] = {'A', 'B', 'C', 'D', 'E'};
    int i = 0;
    for (i = 0; i < 5; i++) {
        AddVertex(G, vertices[i]);
    }
    
    // 添加有向边
    // 这个图的结构是一个典型的带权有向图
    AddEdge(G, 0, 1, 10);  // A -> B: 10
    AddEdge(G, 0, 3, 30);  // A -> D: 30
    AddEdge(G, 0, 4, 100); // A -> E: 100
    AddEdge(G, 1, 2, 50);  // B -> C: 50
    AddEdge(G, 2, 4, 10);  // C -> E: 10
    AddEdge(G, 3, 2, 20);  // D -> C: 20
    AddEdge(G, 3, 4, 60);  // D -> E: 60
}

// 创建测试图2：包含不可达顶点的情况
void CreateTestGraph2(MGraph *G) {
    InitGraph(G);
    
    // 添加顶点
    char vertices[] = {'A', 'B', 'C', 'D', 'E', 'F'};
    int i = 0;
    for (i = 0; i < 6; i++) {
        AddVertex(G, vertices[i]);
    }
    
    // 添加有向边
    AddEdge(G, 0, 1, 5);   // A -> B: 5
    AddEdge(G, 0, 2, 3);   // A -> C: 3
    AddEdge(G, 1, 3, 6);   // B -> D: 6
    AddEdge(G, 2, 1, 1);   // C -> B: 1
    AddEdge(G, 2, 3, 5);   // C -> D: 5
    AddEdge(G, 2, 4, 6);   // C -> E: 6
    AddEdge(G, 3, 4, 2);   // D -> E: 2
    // 注意：F是孤立顶点，从A不可达
}

// ============ 主函数 ============
int main() {
    MGraph G;
    int dist[MaxVertices];
    int path[MaxVertices];
    
    printf("========================================\n");
    printf("    Dijkstra单源最短路径算法演示\n");
    printf("========================================\n");
    
    // 测试案例1：标准有向图
    printf("\n【测试案例1：标准有向带权图】\n");
    CreateTestGraph1(&G);
    PrintGraph(&G);
    
    // 从顶点A（索引0）开始计算最短路径
    int startVertex = 0;
    Dijkstra(&G, startVertex, dist, path);
    PrintDijkstraResult(&G, startVertex, dist, path);
    
    // 测试案例2：包含不可达顶点
    printf("\n\n【测试案例2：包含不可达顶点的图】\n");
    CreateTestGraph2(&G);
    PrintGraph(&G);
    
    startVertex = 0;
    Dijkstra(&G, startVertex, dist, path);
    PrintDijkstraResult(&G, startVertex, dist, path);
    
    // 交互式测试：允许用户选择起点
    printf("\n\n【交互测试】\n");
    printf("使用测试案例1的图，请输入源点（A-E）: ");
    char startChar;
    scanf(" %c", &startChar);
    
    CreateTestGraph1(&G);  // 重新创建图1
    int startIndex = LocateVertex(&G, startChar);
    
    if (startIndex != -1) {
        Dijkstra(&G, startIndex, dist, path);
        PrintDijkstraResult(&G, startIndex, dist, path);
    } else {
        printf("输入的顶点不存在！\n");
    }
    
    // 算法复杂度说明
    printf("\n========================================\n");
    printf("【算法复杂度分析】\n");
    printf("时间复杂度: O(V2)\n");
    printf("  - 外层循环: V-1次\n");
    printf("  - 内层查找最小距离: O(V)\n");
    printf("  - 更新邻接点: O(V)\n");
    printf("空间复杂度: O(V2)\n");
    printf("  - 邻接矩阵: O(V2)\n");
    printf("  - 辅助数组: O(V)\n");
    printf("\n优化方案:\n");
    printf("使用优先队列(最小堆)可以将时间复杂度\n");
    printf("降低到 O((V+E)logV)\n");
    printf("========================================\n");
    
    return 0;
}