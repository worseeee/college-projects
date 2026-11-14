#include <stdio.h>
#include <stdlib.h>

#define MaxVertices 100  // 最大顶点数
#define INFINITY 65535   // 无穷大

typedef char DataType;

// ============ 邻接矩阵图的结构定义 ============
typedef struct
{
    int fromVex;    // 边的起始顶点
    int toVex;      // 边的终止顶点
    int weight;     // 边的权重
} RowColWeight;

typedef struct
{
    DataType Vertices[MaxVertices];           // 顶点数组
    int Edge[MaxVertices][MaxVertices];       // 邻接矩阵
    int numOfVerts;                            // 当前顶点数
    int numOfEdges;                            // 当前边数
} AdjMWGraph;

// ============ 队列实现（用于广度优先搜索）============
typedef struct QNode
{
    int data;
    struct QNode *next;
} QueueNode;

typedef struct
{
    QueueNode *front;
    QueueNode *rear;
} Queue;

void InitQueue(Queue *q)
{
    q->front = q->rear = NULL;
}

int IsQueueEmpty(Queue *q)
{
    return q->front == NULL;
}

void EnQueue(Queue *q, int value)
{
    QueueNode *newNode = (QueueNode *)malloc(sizeof(QueueNode));
    newNode->data = value;
    newNode->next = NULL;
    
    if(q->rear == NULL)
    {
        q->front = q->rear = newNode;
    }
    else
    {
        q->rear->next = newNode;
        q->rear = newNode;
    }
}

int DeQueue(Queue *q)
{
    if(IsQueueEmpty(q))
    {
        printf("队列为空!\n");
        return -1;
    }
    
    QueueNode *temp = q->front;
    int value = temp->data;
    q->front = q->front->next;
    
    if(q->front == NULL)
        q->rear = NULL;
    
    free(temp);
    return value;
}

// ============ 图的基本操作 ============

// 初始化图
void Initiate(AdjMWGraph *G, int n)
{
    G->numOfVerts = n;
    G->numOfEdges = 0;
    
    int i = 0, j = 0;
    // 初始化邻接矩阵（无边用INFINITY表示）
    for(i = 0; i < n; i++)
    {
        for(j = 0; j < n; j++)
        {
            if(i == j)
                G->Edge[i][j] = 0;  // 自己到自己距离为0
            else
                G->Edge[i][j] = INFINITY;  // 初始无边
        }
    }
}

// 插入顶点
void InsertVertex(AdjMWGraph *G, DataType vertex)
{
    G->Vertices[G->numOfVerts] = vertex;
    G->numOfVerts++;
}

// 插入边
void InsertEdge(AdjMWGraph *G, int v1, int v2, int weight)
{
    if(v1 < 0 || v1 >= G->numOfVerts || v2 < 0 || v2 >= G->numOfVerts)
    {
        printf("错误：顶点索引超出范围!\n");
        return;
    }
    
    G->Edge[v1][v2] = weight;
    // 如果是无向图，取消下面注释
    // G->Edge[v2][v1] = weight;
    
    G->numOfEdges++;
}

// 查找顶点位置
int LocateVertex(AdjMWGraph *G, DataType vertex)
{
    int i = 0;
	for(i = 0; i < G->numOfVerts; i++)
    {
        if(G->Vertices[i] == vertex)
            return i;
    }
    return -1;
}

// 获取第一个邻接点
int GetFirstAdjVex(AdjMWGraph G, int v)
{
    if(v < 0 || v >= G.numOfVerts)
        return -1;
    
    int i = 0;
	for(i = 0; i < G.numOfVerts; i++)
    {
        if(G.Edge[v][i] > 0 && G.Edge[v][i] < INFINITY)
            return i;
    }
    return -1;
}

// 获取下一个邻接点
int GetNextAdjVex(AdjMWGraph G, int v1, int v2)
{
    if(v1 < 0 || v1 >= G.numOfVerts || v2 < 0 || v2 >= G.numOfVerts)
        return -1;
    
    int i = 0;
    for(i = v2 + 1; i < G.numOfVerts; i++)
    {
        if(G.Edge[v1][i] > 0 && G.Edge[v1][i] < INFINITY)
            return i;
    }
    return -1;
}

// ============ 图的遍历算法 ============

// 访问函数
void Visit(DataType item)
{
    printf("%c ", item);
}

// 深度优先搜索的递归函数
void DFS(AdjMWGraph G, int v, int visited[])
{
    visited[v] = 1;  // 标记为已访问
    Visit(G.Vertices[v]);
    
    // 遍历所有邻接点
    int w = GetFirstAdjVex(G, v);
    while(w != -1)
    {
        if(!visited[w])
            DFS(G, w, visited);
        w = GetNextAdjVex(G, v, w);
    }
}

// 深度优先搜索
void DepthFirstSearch(AdjMWGraph G, void (*Visit)(DataType))
{
    int visited[MaxVertices] = {0};  // 访问标记数组
    int v = 0;
    // 遍历所有顶点，确保非连通图也能遍历完
    for(v = 0; v < G.numOfVerts; v++)
    {
        if(!visited[v])
            DFS(G, v, visited);
    }
}

// 广度优先搜索
void BroadFirstSearch(AdjMWGraph G, void (*Visit)(DataType))
{
    int visited[MaxVertices] = {0};  // 访问标记数组
    Queue q;
    int v = 0;
    
    // 遍历所有顶点
    for(v = 0; v < G.numOfVerts; v++)
    {
        if(!visited[v])
        {
            InitQueue(&q);
            visited[v] = 1;
            Visit(G.Vertices[v]);
            EnQueue(&q, v);
            
            while(!IsQueueEmpty(&q))
            {
                int u = DeQueue(&q);
                int w = GetFirstAdjVex(G, u);
                
                while(w != -1)
                {
                    if(!visited[w])
                    {
                        visited[w] = 1;
                        Visit(G.Vertices[w]);
                        EnQueue(&q, w);
                    }
                    w = GetNextAdjVex(G, u, w);
                }
            }
        }
    }
}

// ============ 创建图 ============
void CreatGraph(AdjMWGraph *G, DataType a[], int n, RowColWeight rcw[], int e)
{
    // 初始化图
    Initiate(G, n);
    
    int i = 0;
    // 插入顶点
    for(i = 0; i < n; i++)
    {
        G->Vertices[i] = a[i];
    }
    
    // 插入边
    for(i = 0; i < e; i++)
    {
        InsertEdge(G, rcw[i].fromVex, rcw[i].toVex, rcw[i].weight);
    }
}

// ============ 辅助函数：打印图 ============
void PrintGraph(AdjMWGraph G)
{
    printf("\n图的邻接矩阵表示：\n");
    printf("    ");
    int i = 0, j = 0;
	for(i = 0; i < G.numOfVerts; i++)
        printf("%c    ", G.Vertices[i]);
    printf("\n");
    
    for(i = 0; i < G.numOfVerts; i++)
    {
        printf("%c  ", G.Vertices[i]);
        for(j = 0; j < G.numOfVerts; j++)
        {
            if(G.Edge[i][j] == INFINITY)
                printf("∞    ");
            else
                printf("%-4d ", G.Edge[i][j]);
        }
        printf("\n");
    }
    
    printf("\n顶点数: %d, 边数: %d\n", G.numOfVerts, G.numOfEdges);
}

// ============ 核心功能：计算各顶点的入度 ============

/**
 * 函数功能：计算有向图中每个顶点的入度
 * 
 * 算法思路：
 * 对于邻接矩阵，Edge[i][j]表示从顶点i到顶点j的边
 * 因此，要计算顶点j的入度，我们需要统计第j列中所有有效边的数量
 * 
 * 具体步骤：
 * 1. 遍历邻接矩阵的每一列（代表每个顶点）
 * 2. 对于第j列，遍历该列的所有行
 * 3. 统计Edge[i][j]中有效边的数量（非0且非INFINITY）
 * 4. 该数量即为顶点j的入度
 * 
 * @param G 有向图
 * @param inDegree 存储各顶点入度的数组（需要提前分配空间）
 */
void GetInDegree(AdjMWGraph G, int inDegree[])
{
    // 首先将所有顶点的入度初始化为0
    // 这一步很重要，确保我们从一个干净的状态开始计数
    int i = 0, j = 0;
	for(i = 0; i < G.numOfVerts; i++)
    {
        inDegree[i] = 0;
    }
    
    // 外层循环遍历每一列，每一列对应一个顶点
    // j代表目标顶点（边的终点）
    for(j = 0; j < G.numOfVerts; j++)
    {
        // 内层循环遍历第j列的每一行
        // i代表起始顶点（边的起点）
        for(i = 0; i < G.numOfVerts; i++)
        {
            // 判断是否存在从顶点i到顶点j的边
            // 条件1: Edge[i][j] != 0，排除自环为0的情况
            // 条件2: Edge[i][j] != INFINITY，排除无边的情况
            // 注意：即使i==j（自环），如果有边也要计入入度
            if(G.Edge[i][j] != 0 && G.Edge[i][j] != INFINITY)
            {
                // 找到一条指向顶点j的边，入度加1
                inDegree[j]++;
            }
        }
    }
}

/**
 * 函数功能：打印各顶点的入度信息
 * 这个辅助函数让结果更加直观易读
 * 
 * @param G 有向图
 * @param inDegree 各顶点的入度数组
 */
void PrintInDegree(AdjMWGraph G, int inDegree[])
{
    printf("\n========== 各顶点的入度 ==========\n");
    printf("顶点\t入度\n");
    printf("----\t----\n");
    
    int i = 0;
    for(i = 0; i < G.numOfVerts; i++)
    {
        printf(" %c\t %d\n", G.Vertices[i], inDegree[i]);
    }
    
    // 计算并显示统计信息
    int maxInDegree = 0;
    int minInDegree = G.numOfVerts;
    int totalInDegree = 0;
    
    for(i = 0; i < G.numOfVerts; i++)
    {
        totalInDegree += inDegree[i];
        if(inDegree[i] > maxInDegree)
            maxInDegree = inDegree[i];
        if(inDegree[i] < minInDegree)
            minInDegree = inDegree[i];
    }
    
    printf("----------------------------------\n");
    printf("统计信息：\n");
    printf("  最大入度: %d\n", maxInDegree);
    printf("  最小入度: %d\n", minInDegree);
    printf("  平均入度: %.2f\n", (double)totalInDegree / G.numOfVerts);
    printf("  总边数: %d (验证：入度之和应等于边数)\n", totalInDegree);
    printf("==================================\n");
}

/**
 * 扩展功能：同时计算入度和出度
 * 
 * 出度的计算方式：统计每一行中有效边的数量
 * 这样可以一次遍历得到完整的度数信息
 * 
 * @param G 有向图
 * @param inDegree 存储入度的数组
 * @param outDegree 存储出度的数组
 */
void GetDegrees(AdjMWGraph G, int inDegree[], int outDegree[])
{
    // 初始化所有度数为0
    int i = 0, j = 0;
	for(i = 0; i < G.numOfVerts; i++)
    {
        inDegree[i] = 0;
        outDegree[i] = 0;
    }
    
    // 一次遍历同时计算入度和出度
    for(i = 0; i < G.numOfVerts; i++)
    {
        for(j = 0; j < G.numOfVerts; j++)
        {
            if(G.Edge[i][j] != 0 && G.Edge[i][j] != INFINITY)
            {
                outDegree[i]++;  // 顶点i的出度加1（第i行）
                inDegree[j]++;   // 顶点j的入度加1（第j列）
            }
        }
    }
}

// ============ 主函数 ============
int main(void)
{
    AdjMWGraph g1;
    DataType a[] = {'A', 'B', 'C', 'D', 'E'};
    RowColWeight rcw[] = {
        {0, 1, 10},  // A->B, 权重10
        {0, 4, 20},  // A->E, 权重20
        {1, 3, 30},  // B->D, 权重30
        {2, 1, 40},  // C->B, 权重40
        {3, 2, 50}   // D->C, 权重50
    };
    int n = 5, e = 5;
    
    printf("========================================\n");
    printf("       图的遍历与入度计算演示\n");
    printf("========================================\n");
    
    // 创建图
    CreatGraph(&g1, a, n, rcw, e);
    
    // 打印图的结构
    PrintGraph(g1);
    
    // ============ 测试入度计算功能 ============
    printf("\n【功能演示：计算各顶点的入度】\n");
    
    int inDegree[MaxVertices];
    GetInDegree(g1, inDegree);
    PrintInDegree(g1, inDegree);
    
    // ============ 测试同时计算入度和出度 ============
    printf("\n【扩展功能：同时计算入度和出度】\n");
    
    int outDegree[MaxVertices];
    GetDegrees(g1, inDegree, outDegree);
    
    printf("\n顶点\t入度\t出度\n");
    printf("----\t----\t----\n");
    
	int i = 0;
	for(i = 0; i < g1.numOfVerts; i++)
    {
        printf(" %c\t %d\t %d\n", 
               g1.Vertices[i], inDegree[i], outDegree[i]);
    }
    
    // 深度优先搜索
    printf("\n\n【图的遍历】\n");
    printf("深度优先搜索序列: ");
    DepthFirstSearch(g1, Visit);
    
    // 广度优先搜索
    printf("\n广度优先搜索序列: ");
    BroadFirstSearch(g1, Visit);
    
    printf("\n\n========================================\n");
    
    // ============ 额外测试：更复杂的图 ============
    printf("\n【测试案例2：更复杂的有向图】\n");
    AdjMWGraph g2;
    DataType a2[] = {'A', 'B', 'C', 'D', 'E', 'F'};
    RowColWeight rcw2[] = {
        {0, 1, 1},   // A->B
        {0, 2, 1},   // A->C
        {1, 2, 1},   // B->C
        {1, 3, 1},   // B->D
        {2, 4, 1},   // C->E
        {3, 4, 1},   // D->E
        {3, 5, 1},   // D->F
        {4, 5, 1},   // E->F
        {5, 2, 1}    // F->C (形成环)
    };
    int n2 = 6, e2 = 9;
    
    CreatGraph(&g2, a2, n2, rcw2, e2);
    PrintGraph(g2);
    
    // 计算入度
    int inDegree2[MaxVertices], outDegree2[MaxVertices];
    GetDegrees(g2, inDegree2, outDegree2);
    
    printf("\n顶点\t入度\t出度\t说明\n");
    printf("----\t----\t----\t----------------\n");
    
	for(i = 0; i < g2.numOfVerts; i++)
    {
        printf(" %c\t %d\t %d\t", 
               g2.Vertices[i], inDegree2[i], outDegree2[i]);
        
        // 添加说明
        if(inDegree2[i] == 0)
            printf("源点（无入边）");
        else if(outDegree2[i] == 0)
            printf("汇点（无出边）");
        else if(inDegree2[i] == outDegree2[i])
            printf("平衡点");
        
        printf("\n");
    }
    
    printf("\n");
    
    return 0;
}