#include<stdio.h>
#include<stdlib.h>
#include<malloc.h>

typedef int DataType;
typedef struct Node{
	DataType data; 
	struct Node *next;
}SLNode;

void ListInitiate(SLNode **head){
	*head = (SLNode *)malloc(sizeof(SLNode));
	(*head)->next = NULL;
}

int ListLength(SLNode *head){
	SLNode *p = head;
	int size = 0;
	while(p->next != NULL){
		p = p->next;
		size ++;
	}
	return size;
}

int ListInsert(SLNode *head, int i, DataType x){
	SLNode *p, *q; 
	int j;
	p = head; 
	j = -1;
	while(p->next != NULL && j < i-1){
		p = p -> next; 
		j ++;
	}
	if(j != i-1){
		printf("插入位置参数错！");
		return 0;
	}
	q = (SLNode *)malloc(sizeof(SLNode));
	q -> data = x; 
	q -> next = p -> next; 
	p -> next = q;
	return 1;
}

int ListGet(SLNode *head, int i, DataType *x){
	SLNode *p;
	int j;
	p = head;
	j = -1;
	while (p->next != NULL && j < i){
		p = p->next;
		j ++;
	}
	if (j != i){
		printf("取元素位置参数错！");
		return 0;
	}
	*x = p->data;
	return 1;
}

void LinlistSort(SLNode *head){
	SLNode *curr, *pre, *p, *q;
	p = head->next; head->next = NULL;
	while (p != NULL){
		curr = head->next; pre = head;
		while (curr != NULL && curr->data >= p->data){
			pre = curr;
			curr = curr->next;
		}
		q = p; p = p->next;
		q->next = pre->next; pre->next = q;
	}
}

void main(void){
    SLNode *head;
	int i, x;
	ListInitiate(&head);
	for (i = 0; i < 10; i ++){
		ListInsert(head, i, i + 1);
	}
	printf("排序前：");
	for (i = 0; i < ListLength(head); i ++){
		ListGet(head, i, &x);
		printf("%d ", x);
	}
	printf("\n");
	printf("排序后：");
	LinlistSort(head);
	for (i = 0; i < ListLength(head); i ++){
		ListGet(head, i, &x);
		printf("%d ", x);
	}
}