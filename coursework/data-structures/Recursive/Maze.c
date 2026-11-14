#include <stdio.h>
#include <stdlib.h>

typedef struct{               	//路口的结构体定义
	int left;		//向左方向
	int forward;	//向前方向
	int right;		//向右方向
} InterSection;

typedef struct{               	//迷宫的结构体定义
	int mazeSize;	//路口个数
	InterSection *intSec;	//路口集合
	int Exit;		//出口
} Maze;
  
int TravMaze(Maze *m, int currSetValue)
{        //用回溯算法搜索迷宫m的所有分支，参数currSetValue为当前所处路口
          // currSetValue>0表示有路径存在，可以继续探索发现一条路径
	if(currSetValue>0) {
		if(currSetValue==m->Exit) {
			printf("%d <== ", currSetValue); return 1; }
		else if(TravMaze(m, m->intSec[currSetValue].left)==1){
			printf("%d <== ", currSetValue); return 1; }
	    else if(TravMaze(m, m->intSec[currSetValue].forward)==1){
			printf("%d <== ", currSetValue); return 1; }
	    else if(TravMaze(m, m->intSec[currSetValue].right)==1){
            printf("%d <== ", currSetValue); return 1; }
	}
    return 0;
}

void CreatMaze(char *filename, Maze *m)
{        //按文件Filename中存放的数据创建迷宫m
	FILE *fp; int i;
	fp=fopen(filename, "r");
	if(!fp) {
		printf("数据文件无法打开!"); return; };
	fscanf(fp, "%d", &m->mazeSize);
 	m->intSec=(InterSection *)malloc(sizeof(InterSection)*(m->mazeSize+1));
    for(i=1; i<=m->mazeSize; i++)
		fscanf(fp, "%d%d%d", &m->intSec[i].left, &m->intSec[i].forward,   
			&m->intSec[i].right); 
	fscanf(fp, "%d%d%d", &m->Exit);
	fclose(fp);
}

int main(void)
{        
	Maze m;
 	int start=1;
  	CreatMaze("maze.txt", &m);
 	if(TravMaze(&m, start))
 		printf("\n此迷宫的一条通路如上所示!"); 
  	else
  		printf("\n此迷宫无通路!");
}
