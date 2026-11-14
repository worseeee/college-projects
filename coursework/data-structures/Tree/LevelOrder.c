#include <stdio.h>
#include <stdlib.h>

typedef char DataType;

typedef struct Node 
{        
    DataType data;	
    struct Node *leftChild;	
    struct Node *rightChild;
} BiTreeNode;

void Initiate(BiTreeNode **root)
{        
    *root = (BiTreeNode *)malloc(sizeof(BiTreeNode));
    (*root)->data = '#';  // 头结点数据域可以设置为特殊值
    (*root)->leftChild = NULL;
    (*root)->rightChild = NULL;
}

BiTreeNode *InsertLeftNode(BiTreeNode *curr, DataType x)
{       
    BiTreeNode *s, *t;
    if(curr == NULL) return NULL;
    t = curr->leftChild;
    s = (BiTreeNode *)malloc(sizeof(BiTreeNode));
    s->data = x;
    s->leftChild = t;
    s->rightChild = NULL;
    curr->leftChild = s;
    return curr->leftChild;	
}

BiTreeNode *InsertRightNode(BiTreeNode *curr, DataType x)
{       
    BiTreeNode *s, *t;
    if(curr == NULL) return NULL;
    t = curr->rightChild;
    s = (BiTreeNode *)malloc(sizeof(BiTreeNode));
    s->data = x;
    s->rightChild = t;  // 修正：原代码写成了 leftChild
    s->leftChild = NULL;
    curr->rightChild = s;
    return curr->rightChild;	
}

BiTreeNode *DeleteLeftTree(BiTreeNode *curr);
BiTreeNode *DeleteRightTree(BiTreeNode *curr);
void Destroy(BiTreeNode **root);

BiTreeNode *DeleteLeftTree(BiTreeNode *curr)
{        
    if(curr == NULL || curr->leftChild == NULL) return NULL;         
    Destroy(&curr->leftChild);
    curr->leftChild = NULL;
    return curr;
}

BiTreeNode *DeleteRightTree(BiTreeNode *curr)
{        
    if(curr == NULL || curr->rightChild == NULL) return NULL;         
    Destroy(&curr->rightChild);
    curr->rightChild = NULL;
    return curr;
}

void PreOrder(BiTreeNode *t, void Visit(DataType item))
{        
    if(t != NULL)
    {        
        Visit(t->data);
        PreOrder(t->leftChild, Visit);
        PreOrder(t->rightChild, Visit);
    }
}

void InOrder(BiTreeNode *t, void Visit(DataType item))
{
    if(t != NULL)
    {        
        InOrder(t->leftChild, Visit);
        Visit(t->data);
        InOrder(t->rightChild, Visit);
    }
}

void PostOrder(BiTreeNode *t, void Visit(DataType item))
{
    if(t != NULL)
    {        
        PostOrder(t->leftChild, Visit);
        PostOrder(t->rightChild, Visit);
        Visit(t->data);
    }
}

void Destroy(BiTreeNode **root)
{        
    if((*root) != NULL && (*root)->leftChild != NULL)
        Destroy(&(*root)->leftChild);
    if((*root) != NULL && (*root)->rightChild != NULL)
        Destroy(&(*root)->rightChild);
    free(*root);
    *root = NULL;  // 建议添加：防止悬空指针
}

BiTreeNode *Search(BiTreeNode *bt, DataType x)
{        
    BiTreeNode *p;
    if(bt == NULL) return NULL;	
    if(bt->data == x) return bt;
    if(bt->leftChild != NULL)
    {        
        p = Search(bt->leftChild, x);
        if(p != NULL) return p;	
    }
    if(bt->rightChild != NULL)
    {        
        p = Search(bt->rightChild, x);
        if(p != NULL) return p;	
    } 
    return NULL;
}

void Visit(DataType item)
{
    printf("%c ", item);
}

// 队列结构定义（用于层序遍历）
typedef struct QueueNode
{
    BiTreeNode *data;
    struct QueueNode *next;
} QueueNode;

typedef struct
{
    QueueNode *front;
    QueueNode *rear;
} Queue;

// 初始化队列
void InitQueue(Queue *q)
{
    q->front = q->rear = NULL;
}

// 判断队列是否为空
int IsEmpty(Queue *q)
{
    return q->front == NULL;
}

// 入队
void EnQueue(Queue *q, BiTreeNode *node)
{
    QueueNode *newNode = (QueueNode *)malloc(sizeof(QueueNode));
    newNode->data = node;
    newNode->next = NULL;
    
    if(q->rear == NULL)  // 队列为空
    {
        q->front = q->rear = newNode;
    }
    else
    {
        q->rear->next = newNode;
        q->rear = newNode;
    }
}

// 出队
BiTreeNode *DeQueue(Queue *q)
{
    if(IsEmpty(q)) return NULL;
    
    QueueNode *temp = q->front;
    BiTreeNode *node = temp->data;
    q->front = q->front->next;
    
    if(q->front == NULL)  // 队列变空
        q->rear = NULL;
    
    free(temp);
    return node;
}

// 层序遍历
void LevelOrder(BiTreeNode *root, void Visit(DataType item))
{
    if(root == NULL) return;
    
    Queue q;
    InitQueue(&q);
    
    // 根节点入队
    EnQueue(&q, root);
    
    while(!IsEmpty(&q))
    {
        // 出队并访问
        BiTreeNode *current = DeQueue(&q);
        Visit(current->data);
        
        // 左孩子入队
        if(current->leftChild != NULL)
            EnQueue(&q, current->leftChild);
        
        // 右孩子入队
        if(current->rightChild != NULL)
            EnQueue(&q, current->rightChild);
    }
}

// 层序遍历（带层次信息）
void LevelOrderWithLevel(BiTreeNode *root)
{
    if(root == NULL) return;
    
    Queue q;
    InitQueue(&q);
    EnQueue(&q, root);
    
    int level = 1;  // 当前层数
    
    while(!IsEmpty(&q))
    {
        int levelSize = 0;  // 当前层的节点数
        int i;
        // 计算当前层节点数
        QueueNode *temp = q.front;
        while(temp != NULL)
        {
            levelSize++;
            temp = temp->next;
        }
        
        printf("第%d层: ", level);
        
        // 处理当前层的所有节点
        for(i = 0; i < levelSize; i++)
        {
            BiTreeNode *current = DeQueue(&q);
            printf("%c ", current->data);
            
            if(current->leftChild != NULL)
                EnQueue(&q, current->leftChild);
            if(current->rightChild != NULL)
                EnQueue(&q, current->rightChild);
        }
        
        printf("\n");
        level++;
    }
}

int main()
{
    BiTreeNode *root, *p, *pp;
    
    // 初始化带头结点的二叉树
    Initiate(&root);
    
    // 构建二叉树
    p = InsertLeftNode(root, 'A');      // 根节点A
    p = InsertLeftNode(p, 'B');         // A的左孩子B
    p = InsertLeftNode(p, 'D');         // B的左孩子D
    p = InsertRightNode(p, 'G');        // D的右孩子G
    
    p = InsertRightNode(root->leftChild, 'C');  // A的右孩子C
    pp = InsertLeftNode(p, 'E');        // C的左孩子E
    InsertRightNode(p, 'F');            // C的右孩子F（注意这里用的是p，不是pp）
    
    // 打印树的结构（从头结点的左子树开始，即真正的根节点）
    printf("前序遍历: ");
    PreOrder(root->leftChild, Visit);
    printf("\n");
    
    printf("中序遍历: ");
    InOrder(root->leftChild, Visit);
    printf("\n");
    
    printf("后序遍历: ");
    PostOrder(root->leftChild, Visit);
    printf("\n");
    
    printf("层序遍历: ");
    LevelOrder(root->leftChild, Visit);
    printf("\n");
    
    printf("\n带层次的层序遍历:\n");
    LevelOrderWithLevel(root->leftChild);
    
    // 查找测试
    BiTreeNode *found = Search(root->leftChild, 'E');
    if(found != NULL)
        printf("\n找到节点: %c\n", found->data);
    
    // 释放内存
    Destroy(&root);
    
    return 0;
}
