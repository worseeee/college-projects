#include <stdio.h>
#include <stdlib.h>
#include <malloc.h>

int **Array2D(int row, int col){
	int **a, i;
	a = (int **)malloc(row * sizeof(int *));
	for (i = 0; i < row; i ++){
		a[i] = (int *)malloc(col * sizeof(int));
	}
	return a;
}

int DeArray2D(int **a, int row){
	int i;
	for (i = 0; i < row; i ++){
		free(a[i]);
	}
	free(a);
}

int main(){
	int i, j, m;
	int row = 3, col = 4, **a;
	a = Array2D(row, col);
	m = 1;
	for (i = 0; i < row; i ++){
		for (j = 0; j < col; j ++){
			a[i][j] = m;
			m ++;
		}
	}
	for (i = 0; i < row; i ++){
		for (j = 0; j < col; j ++){
			printf("%5d",a[i][j]);
		}
		printf("\n");
	}
	DeArray2D(a, row);
}
