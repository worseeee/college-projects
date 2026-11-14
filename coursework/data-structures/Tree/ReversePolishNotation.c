#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

// 表达式树节点定义
typedef struct ExprNode
{
    char data;  // 操作符或操作数
    struct ExprNode *left;
    struct ExprNode *right;
} ExprNode;

// 栈节点定义（用于构建表达式树）
typedef struct StackNode
{
    ExprNode *treeNode;
    struct StackNode *next;
} StackNode;

typedef struct
{
    StackNode *top;
} Stack;

// ============ 栈操作 ============
void InitStack(Stack *s)
{
    s->top = NULL;
}

int IsStackEmpty(Stack *s)
{
    return s->top == NULL;
}

void Push(Stack *s, ExprNode *node)
{
    StackNode *newNode = (StackNode *)malloc(sizeof(StackNode));
    newNode->treeNode = node;
    newNode->next = s->top;
    s->top = newNode;
}

ExprNode *Pop(Stack *s)
{
    if(IsStackEmpty(s)) return NULL;
    
    StackNode *temp = s->top;
    ExprNode *node = temp->treeNode;
    s->top = s->top->next;
    free(temp);
    return node;
}

// ============ 辅助函数 ============

// 判断是否为操作符
int IsOperator(char c)
{
    return (c == '+' || c == '-' || c == '*' || c == '/');
}

// 创建新节点
ExprNode *CreateNode(char data)
{
    ExprNode *node = (ExprNode *)malloc(sizeof(ExprNode));
    node->data = data;
    node->left = NULL;
    node->right = NULL;
    return node;
}

// ============ 核心功能1：根据后缀表达式构建表达式树 ============
ExprNode *BuildExpressionTree(char *postfix)
{
    Stack s;
    InitStack(&s);
    
    int i = 0;
    while(postfix[i] != '\0')
    {
        // 跳过空格
        if(postfix[i] == ' ')
        {
            i++;
            continue;
        }
        
        // 如果是数字
        if(isdigit(postfix[i]))
        {
            ExprNode *node = CreateNode(postfix[i]);
            Push(&s, node);
        }
        // 如果是操作符
        else if(IsOperator(postfix[i]))
        {
            ExprNode *node = CreateNode(postfix[i]);
            
            // 弹出两个操作数（注意顺序）
            node->right = Pop(&s);  // 右操作数
            node->left = Pop(&s);   // 左操作数
            
            Push(&s, node);
        }
        
        i++;
    }
    
    return Pop(&s);  // 最后栈中剩下的就是根节点
}

// ============ 核心功能2：中序遍历输出中缀表达式 ============
void InfixExpression(ExprNode *root)
{
    if(root == NULL) return;
    
    // 如果当前节点是操作符，需要加括号
    if(IsOperator(root->data))
    {
        printf("(");
        InfixExpression(root->left);
        printf(" %c ", root->data);
        InfixExpression(root->right);
        printf(")");
    }
    else  // 操作数直接输出
    {
        printf("%c", root->data);
    }
}

// ============ 核心功能3：计算表达式树的值 ============
double EvaluateExpressionTree(ExprNode *root)
{
    if(root == NULL) return 0;
    
    // 如果是叶子节点（操作数）
    if(root->left == NULL && root->right == NULL)
    {
        return (double)(root->data - '0');  // 字符转数字
    }
    
    // 递归计算左右子树
    double leftValue = EvaluateExpressionTree(root->left);
    double rightValue = EvaluateExpressionTree(root->right);
    
    // 根据操作符计算
    switch(root->data)
    {
        case '+': return leftValue + rightValue;
        case '-': return leftValue - rightValue;
        case '*': return leftValue * rightValue;
        case '/': 
            if(rightValue == 0)
            {
                printf("错误：除数为0!\n");
                return 0;
            }
            return leftValue / rightValue;
        default: return 0;
    }
}

// ============ 核心功能4：可视化显示树结构 ============
void PrintTree(ExprNode *root, int space)
{
    int i;
	
	if(root == NULL) return;
    
    space += 5;
    
    // 先打印右子树
    PrintTree(root->right, space);
    
    // 打印当前节点
    printf("\n");
    for(i = 5; i < space; i++)
        printf(" ");
    printf("%c\n", root->data);
    
    // 打印左子树
    PrintTree(root->left, space);
}

// ============ 辅助功能：前序、中序、后序遍历 ============
void PreOrder(ExprNode *root)
{
    if(root != NULL)
    {
        printf("%c ", root->data);
        PreOrder(root->left);
        PreOrder(root->right);
    }
}

void InOrder(ExprNode *root)
{
    if(root != NULL)
    {
        InOrder(root->left);
        printf("%c ", root->data);
        InOrder(root->right);
    }
}

void PostOrder(ExprNode *root)
{
    if(root != NULL)
    {
        PostOrder(root->left);
        PostOrder(root->right);
        printf("%c ", root->data);
    }
}

// ============ 释放树 ============
void DestroyTree(ExprNode *root)
{
    if(root != NULL)
    {
        DestroyTree(root->left);
        DestroyTree(root->right);
        free(root);
    }
}

// ============ 主函数 ============
int main()
{
    char postfix[100];
    
    printf("========================================\n");
    printf("    表达式树构建与求值系统\n");
    printf("========================================\n\n");
    
    printf("请输入后缀表达式（操作数和操作符之间用空格分隔）：\n");
    printf("支持的操作符: + - * /\n");
    printf("输入: ");
    
    fgets(postfix, 100, stdin);
    postfix[strcspn(postfix, "\n")] = 0;  // 去掉换行符
    
    printf("\n----------------------------------------\n");
    
    // 1. 构建表达式树
    ExprNode *root = BuildExpressionTree(postfix);
    
    if(root == NULL)
    {
        printf("表达式构建失败！\n");
        return -1;
    }
    
    printf("表达式树构建成功！\n\n");
    
    // 2. 输出中缀表达式
    printf("中缀表达式: ");
    InfixExpression(root);
    printf("\n\n");
    
    // 3. 计算表达式的值
    double result = EvaluateExpressionTree(root);
    printf("计算结果: %.2f\n\n", result);
    
    // 4. 显示树的结构
    printf("树的结构(逆时针旋转90度观看):\n");
    PrintTree(root, 0);
    printf("\n");
    
    // 5. 三种遍历方式
    printf("----------------------------------------\n");
    printf("前序遍历: ");
    PreOrder(root);
    printf("\n");
    
    printf("中序遍历: ");
    InOrder(root);
    printf("\n");
    
    printf("后序遍历: ");
    PostOrder(root);
    printf("\n");
    
    printf("========================================\n");
    
    // 释放内存
    DestroyTree(root);
    
    return 0;
}
