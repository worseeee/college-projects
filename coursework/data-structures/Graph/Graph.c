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
    int i, j;
    
	G->numOfVerts = n;
    G->numOfEdges = 0;
    
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
    int i;
    
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
    int i;
    
	if(v < 0 || v >= G.numOfVerts)
        return -1;
    
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
    int i;
	if(v1 < 0 || v1 >= G.numOfVerts || v2 < 0 || v2 >= G.numOfVerts)
        return -1;
    
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
    int v;
	int visited[MaxVertices] = {0};  // 访问标记数组
    
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
    int v;
    
	int visited[MaxVertices] = {0};  // 访问标记数组
    Queue q;
    
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
    int i;
	// 初始化图
    Initiate(G, n);
    
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
    int i, j;
    
	printf("\n图的邻接矩阵表示：\n");
    printf("    ");
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
    int i, n = 5, e = 5;
    
    printf("========================================\n");
    printf("         图的遍历演示系统\n");
    printf("========================================\n");
    
    // 创建图
    CreatGraph(&g1, a, n, rcw, e);
    
    // 打印图的结构
    PrintGraph(g1);
    
    // 深度优先搜索
    printf("\n深度优先搜索序列: ");
    DepthFirstSearch(g1, Visit);
    
    // 广度优先搜索
    printf("\n广度优先搜索序列: ");
    BroadFirstSearch(g1, Visit);
    
    printf("\n\n========================================\n");
    
    // 测试：创建一个无向图
    printf("\n【测试：无向图】\n");
    AdjMWGraph g2;
    DataType a2[] = {'A', 'B', 'C', 'D'};
    int n2 = 4;
    Initiate(&g2, n2);
    
    // 插入顶点
    for(i = 0; i < n2; i++)
        g2.Vertices[i] = a2[i];
    
    // 插入无向边（双向）
    InsertEdge(&g2, 0, 1, 1);
    InsertEdge(&g2, 1, 0, 1);
    InsertEdge(&g2, 0, 2, 1);
    InsertEdge(&g2, 2, 0, 1);
    InsertEdge(&g2, 1, 3, 1);
    InsertEdge(&g2, 3, 1, 1);
    InsertEdge(&g2, 2, 3, 1);
    InsertEdge(&g2, 3, 2, 1);
    
    PrintGraph(g2);
    
    printf("\n深度优先搜索序列: ");
    DepthFirstSearch(g2, Visit);
    
    printf("\n广度优先搜索序列: ");
    BroadFirstSearch(g2, Visit);
    
    printf("\n\n");
    
    return 0;
}