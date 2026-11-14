#include <stdio.h>
#include <stdlib.h>
#include <stdbool.h>

#define MAX_SIZE 6  // 队列最大容量为5，牺牲一个单元

typedef struct {
    int data[MAX_SIZE];
    int front;      // 队头指针
    int rear;       // 队尾指针
} ReQueue;

// 初始化队列
void initQueue(ReQueue *queue) {
    queue->front = 0;
    queue->rear = 0;
}

// 判断队列是否为空
bool isEmpty(ReQueue *queue) {
    return queue->front == queue->rear;
}

// 判断队列是否已满
bool isFull(ReQueue *queue) {
    return (queue->rear + 1) % MAX_SIZE == queue->front;
}

// 入队操作
bool enqueue(ReQueue *queue, int value) {
    if (isFull(queue)) {
        printf("队列已满，无法入队元素 %d\n", value);
        return false;
    }
    
    queue->data[queue->rear] = value;
    queue->rear = (queue->rear + 1) % MAX_SIZE;
    printf("入队成功: %d\n", value);
    return true;
}

// 出队操作
bool dequeue(ReQueue *queue, int *value) {
    if (isEmpty(queue)) {
        printf("队列为空，无法出队\n");
        return false;
    }
    
    *value = queue->data[queue->front];
    queue->front = (queue->front + 1) % MAX_SIZE;
    printf("出队成功: %d\n", *value);
    return true;
}

// 获取队头元素
bool getFront(ReQueue *queue, int *value) {
    if (isEmpty(queue)) {
        return false;
    }
    *value = queue->data[queue->front];
    return true;
}

// 获取队列元素个数
int getSize(ReQueue *queue) {
    return (queue->rear - queue->front + MAX_SIZE) % MAX_SIZE;
}

// 打印队列状态
void printQueue(ReQueue *queue) {
    printf("队列状态: ");
    if (isEmpty(queue)) {
        printf("空队列\n");
        return;
    }
    
    int i = queue->front;
    while (i != queue->rear) {
        printf("%d ", queue->data[i]);
        i = (i + 1) % MAX_SIZE;
    }
    printf("\n");
}

// 主函数
int main() {
    ReQueue queue;
    int value;
    int i;
    
    // 初始化队列
    initQueue(&queue);
    printf("=== 循环队列测试 ===\n");
    
    // 测试入队
    printf("\n1. 测试入队操作:\n");
    for (i = 1; i <= 6; i++) {
        enqueue(&queue, i * 10);
        printf("当前队列大小: %d\n", getSize(&queue));
    }
    
    // 打印队列状态
    printf("\n2. 当前队列内容:\n");
    printQueue(&queue);
    
    // 测试出队
    printf("\n3. 测试出队操作:\n");
    for (i = 0; i < 3; i++) {
        dequeue(&queue, &value);
        printf("当前队列大小: %d\n", getSize(&queue));
    }
    
    // 再次入队测试循环特性
    printf("\n4. 再次入队测试循环特性:\n");
    for (i = 6; i <= 8; i++) {
        enqueue(&queue, i * 10);
        printf("当前队列大小: %d\n", getSize(&queue));
    }
    
    printf("\n5. 最终队列内容:\n");
    printQueue(&queue);
    
    // 获取队头元素
    if (getFront(&queue, &value)) {
        printf("队头元素: %d\n", value);
    }
    
    return 0;
}
