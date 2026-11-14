#ifndef LINLIST_H
#define LINLIST_H

#include<stdio.h>
#include<stdlib.h>

typedef int DataType;
typedef struct Node{
    DataType data; 
    struct Node *next;
}SLNode;

void ListInitiate(SLNode **head);
int ListLength(SLNode *head);
int ListInsert(SLNode **head, int i, DataType x);
int ListDelete(SLNode *head, int i, DataType *x);
int ListGet(SLNode *head, int i, DataType *x);
void Destroy(SLNode **head);
int ListFind(SLNode *head, DataType x);

#endif