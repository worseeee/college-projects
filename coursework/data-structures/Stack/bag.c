#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

// 节点结构定义
typedef struct {
    int level;      // 当前决策层级
    int profit;     // 当前总价值
    int weight;     // 当前总重量
    double bound;   // 上界值
} Node;

// 优先队列结构定义
typedef struct {
    Node* nodes;    // 节点数组
    int size;       // 当前队列大小
    int capacity;   // 队列容量
} PriorityQueue;

// 物品结构定义
typedef struct {
    int weight;
    int value;
    double ratio;
} Item;

// 优先队列操作函数
PriorityQueue* createPriorityQueue(int capacity) {
    PriorityQueue* pq = (PriorityQueue*)malloc(sizeof(PriorityQueue));
    pq->capacity = capacity;
    pq->size = 0;
    pq->nodes = (Node*)malloc(capacity * sizeof(Node));
    return pq;
}

bool isPriorityQueueEmpty(PriorityQueue* pq) {
    return pq->size == 0;
}

// 上浮操作（插入时）
void swim(PriorityQueue* pq, int index) {
    while (index > 0) {
        int parent = (index - 1) / 2;
        if (pq->nodes[parent].bound >= pq->nodes[index].bound) {
            break;
        }
        // 交换节点
        Node temp = pq->nodes[parent];
        pq->nodes[parent] = pq->nodes[index];
        pq->nodes[index] = temp;
        index = parent;
    }
}

// 下沉操作（删除时）
void sink(PriorityQueue* pq, int index) {
    while (2 * index + 1 < pq->size) {
        int left = 2 * index + 1;
        int right = left + 1;
        int largest = index;
        
        if (pq->nodes[left].bound > pq->nodes[largest].bound) {
            largest = left;
        }
        if (right < pq->size && pq->nodes[right].bound > pq->nodes[largest].bound) {
            largest = right;
        }
        if (largest == index) {
            break;
        }
        
        // 交换节点
        Node temp = pq->nodes[index];
        pq->nodes[index] = pq->nodes[largest];
        pq->nodes[largest] = temp;
        index = largest;
    }
}

void enqueue(PriorityQueue* pq, Node node) {
    if (pq->size >= pq->capacity) {
        // 动态扩容
        pq->capacity *= 2;
        pq->nodes = realloc(pq->nodes, pq->capacity * sizeof(Node));
    }
    
    pq->nodes[pq->size] = node;
    swim(pq, pq->size);
    pq->size++;
}

Node dequeue(PriorityQueue* pq) {
    if (isPriorityQueueEmpty(pq)) {
        Node empty = {-1, -1, -1, -1};
        return empty;
    }
    
    Node maxNode = pq->nodes[0];
    pq->size--;
    pq->nodes[0] = pq->nodes[pq->size];
    sink(pq, 0);
    
    return maxNode;
}

void freePriorityQueue(PriorityQueue* pq) {
    free(pq->nodes);
    free(pq);
}

// 比较函数（按价值密度降序排序）
int compare(const void* a, const void* b) {
    Item* item1 = (Item*)a;
    Item* item2 = (Item*)b;
    
    if (item1->ratio < item2->ratio) return 1;
    if (item1->ratio > item2->ratio) return -1;
    return 0;
}

// 计算上界函数
double calculateBound(Node u, int n, int capacity, Item* items) {
    if (u.weight >= capacity) return 0;
    
    double bound = u.profit;
    int j = u.level + 1;
    int totalWeight = u.weight;
    
    // 按价值密度继续添加物品
    while (j < n && totalWeight + items[j].weight <= capacity) {
        totalWeight += items[j].weight;
        bound += items[j].value;
        j++;
    }
    
    // 如果还有剩余空间，添加部分物品
    if (j < n) {
        bound += (capacity - totalWeight) * items[j].ratio;
    }
    
    return bound;
}

// 使用优先队列实现的01背包算法
int knapsackWithPriorityQueue(int capacity, Item* items, int n) {
    int i;
	// 按价值密度排序
    for (i = 0; i < n; i++) {
        items[i].ratio = (double)items[i].value / items[i].weight;
    }
    qsort(items, n, sizeof(Item), compare);
    
    PriorityQueue* pq = createPriorityQueue(1000);
    int maxProfit = 0;
    
    // 创建根节点并入队
    Node root = {-1, 0, 0, 0};
    root.bound = calculateBound(root, n, capacity, items);
    enqueue(pq, root);
    
    int nodesExplored = 0;  // 用于统计探索的节点数
    
    while (!isPriorityQueueEmpty(pq)) {
        // 取出上界最大的节点
        Node current = dequeue(pq);
        nodesExplored++;
        
        // 如果当前节点的上界已经小于已知最优解，剪枝
        if (current.bound <= maxProfit) {
            continue;
        }
        
        // 如果这是叶子节点，更新最大价值
        if (current.level == n - 1) {
            if (current.profit > maxProfit) {
                maxProfit = current.profit;
            }
            continue;
        }
        
        // 考虑下一个物品
        int nextLevel = current.level + 1;
        
        // 情况1：包含下一个物品
        Node include = {
            nextLevel,
            current.profit + items[nextLevel].value,
            current.weight + items[nextLevel].weight,
            0
        };
        
        if (include.weight <= capacity) {
            if (include.profit > maxProfit) {
                maxProfit = include.profit;
            }
            include.bound = calculateBound(include, n, capacity, items);
            if (include.bound > maxProfit) {
                enqueue(pq, include);
            }
        }
        
        // 情况2：不包含下一个物品
        Node exclude = {
            nextLevel,
            current.profit,
            current.weight,
            0
        };
        
        exclude.bound = calculateBound(exclude, n, capacity, items);
        if (exclude.bound > maxProfit) {
            enqueue(pq, exclude);
        }
    }
    
    printf("探索节点数: %d\n", nodesExplored);
    freePriorityQueue(pq);
    return maxProfit;
}

// 测试函数
int main() {
    int capacity = 50;
    int i;
    Item items[] = {
        {10, 60},
        {20, 100},
        {30, 120},
        {5, 30},
        {15, 80},
        {25, 110},
        {35, 150}
    };
    int n = sizeof(items) / sizeof(items[0]);
    
    printf("背包容量: %d\n", capacity);
    printf("物品列表:\n");
    for (i = 0; i < n; i++) {
        printf("物品%d: 重量=%d, 价值=%d, 密度=%.2f\n", 
               i+1, items[i].weight, items[i].value, 
               (double)items[i].value / items[i].weight);
    }
    
    printf("\n使用优先队列的算法:\n");
    int maxValue = knapsackWithPriorityQueue(capacity, items, n);
    printf("最大价值: %d\n", maxValue);
    
    return 0;
}