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
	(*head)->next = *head;
}

int ListLength(SLNode *head){
	SLNode *p = head;
	int size = 0;
	while(p->next != head){
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
	while(p->next != head && j < i-1){
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

int ListDelete(SLNode *head, int i, DataType *x){
    SLNode *p, *s; 
    int j;
    p = head;
    j = -1;
    while(p->next != NULL && j < i-1){
        p = p->next;
        j++;
    }
    if (j != i-1){
        printf("删除位置参数错！");  // 修正错误信息
        return 0; 
    }
    s = p->next;
    *x = s->data;
    p->next = p->next->next;
    free(s);
    return 1;
}

int ListGet(SLNode *head, int i, DataType *x){
	SLNode *p;
	int j;
	p = head;
	j = -1;
	while (p->next != head && j < i){
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
	while (p != head){
		curr = head->next; pre = head;
		while (curr != head && curr->data >= p->data){
			pre = curr;
			curr = curr->next;
		}
		q = p; p = p->next;
		q->next = pre->next; pre->next = q;
	}
}

int main(void){
    SLNode *head;
	int i, x;
	ListInitiate(&head);
	for (i = 0; i < 10; i ++){
		ListInsert(head, i, i + 1);
	}
	printf("插入元素后的链表：");
	for (i = 0; i < ListLength(head); i ++){
		ListGet(head, i, &x);
		printf("%d ", x);
	}
	printf("\n");
	ListDelete(head, 3, &x);
	printf("删除元素后的链表：");
	for (i = 0; i < ListLength(head); i ++){
	    ListGet(head, i, &x);
		printf("%d ", x);
	}
	printf("\n");
	printf("链表的元素个数：%d", ListLength(head));
	printf("\n");
}
