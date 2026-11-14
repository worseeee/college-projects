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
    pp = InsertLeftNode(p, 'E');         // C的左孩子E
    InsertRightNode(p, 'F');           // E的右孩子F
    
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
    
    // 查找测试
    BiTreeNode *found = Search(root->leftChild, 'E');
    if(found != NULL)
        printf("\n找到节点: %c\n", found->data);
    
    // 释放内存
    Destroy(&root);
    
    return 0;
}
