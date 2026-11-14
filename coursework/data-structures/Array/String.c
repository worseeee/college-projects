#include <stdio.h>
#include <malloc.h>
#include <string.h>
typedef struct{
	char *str;
	int maxLength;
	int length;
}DString;

void Initiate(DString *S, int max, char *string){
	int i, m;
	
	S->length = strlen(string);
	if (S->length > max){
		m = S->length;
	}
	else {
		m = max;
	}
	S->str = (char *)malloc(sizeof(char)*m);
	
	for (i = 0; i < S->length; i ++){
		S->str[i] = string[i];
	}
}

int Insert(DString *S, int pos, DString T){
	int i;
	char *p;
	if (pos < 0){
		printf("参数pos出错！");
		return 0;
	}
	else {
		if (S->length + T.length > S->maxLength){
			p = (char *)realloc(S->str, (S->length + T.length)*sizeof(char));
		}
		for (i = S->length - 1; i >= pos; i --){
			S->str[i + T.length] = S->str[i];
		}
		for (i = 0; i < T.length; i ++){
			S->str[pos + i] = T.str[i];
		}
		S->length = S->length + T.length;
		return 1;
	}
}

int Delete(DString *S, int pos, int len){
	int i;
	if (S->length <= 0){
		printf("数组中未存放字符无元素可删！\n");
		return 0;
	}
	else if (pos < 0 || len < 0 || pos + len > S->length){
		printf("参数pos和len不合法");
		return 0;
	}
	else {
		for (i = pos + len; i <= S->length - 1; i ++){
			S->str[i - len] = S->str[i];
		}
		S->length = S->length - len;
		return 1;
	}
}

int SubString(DString *S, int pos, int len, DString *T){
	int i;
	if (pos < 0 || len < 0 || pos + len > S->length){
		printf("参数pos和len出错！");
		return 0; 
	}
	else {
		for (i = 0; i < len; i ++){
			T->str[i] = S->str[pos + i];
			T->length = len;
			return 1;
		}
	}
}

void Destroy(DString *S){
	free(S->str);
	S->maxLength = 0;
	S->length = 0;
}

int Encryption(DString *S, DString *T){
	int i, index;
	char ch;
	for (i = 0; i < S->length; i ++){
		ch = S->str[i];
		index = ch - 'a';
		S->str[i] = T->str[index];
	}
}

int Decryption(DString *S, DString *T, DString *R){
	int i, index;
	char ch;
	for (i = 0; i < S->length; i ++){
		ch = S->str[i];
		char *result = strchr(R->str, ch);
		int index = result - R->str;
		S->str[i] = T->str[index];
	}
}
int main(){
	DString Doc, Sec, doC, seC;
	int i, max1 = 50, max2 = 50, max3 = 50, max4 = 50;
	char *doc[50], *DOC[50];
	char *sec = "ngzqtcobmuhelkpdawxfyivrsj";
	char *SEC = "abcdefghijklmnopqrstuvwxyz";
	printf("请输入需加密文本：\n");
	scanf("%s", doc);
	Initiate(&Doc, max1, doc);
	Initiate(&Sec, max2, sec);
	printf("加密后为：\n");
	Encryption(&Doc, &Sec);
	for (i = 0; i < Doc.length; i ++){
		printf("%c", Doc.str[i]);
	}
	printf("\n");
	printf("请输入需解密文本：\n");
	scanf("%s", DOC);
	Initiate(&doC, max3, DOC);
	Initiate(&seC, max4, SEC);
	printf("解密后为：\n");
	Decryption(&doC, &seC, &Sec);
	for (i = 0; i < doC.length; i ++){
		printf("%c", doC.str[i]);
	}
	printf("\n");
}