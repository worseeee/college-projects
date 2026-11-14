#include<stdio.h>

typedef struct node{
	int id;
	char *text;
	struct node *next;
}Task;

typedef struct{
	Task *front;
	Task *rear;
}Queue;

int PrintTaskAppend(Queue *taskmanager, int id, char *text){
	Task *p;
	p = (Task *)malloc(sizeof(Task));
	p->text = (char *)malloc(strlen(text)+1);
	strcpy(p->text, text);
	p->id = tid;
	p->next = NULL;
	if (taskmanager->rear != NULL){
		taskmanager->rear->next = p;
		taskmanager->rear = p;
	}
	if (taskmanager->front == NULL){
		taskmanager->front = p;
	}
}

int PrintTaskDelete(Queue *taskmanager){
	Task *p = taskmanager->front;
	if (p == NULL){
		return 0;
	}
	else {
		printf("Task id: %d\n", p->id)id;
		printf("Task context: %s\n", p->text)text;
	}
	taskmanager->front = taskmanager->front->next;
	if (taskmanager->front == NULL){
		taskmanager->rear = NULL;
	}
	free(p->text);
	free(p);
	return 1;
}