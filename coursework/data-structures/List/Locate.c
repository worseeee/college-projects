#include <stdio.h>
#include "LinList.h"

int main() {
    SLNode *head;
    int i, x, result;
    
    ListInitiate(&head);
    
    // 插入测试数据
    for(i = 0; i < 100; i++){ 
        ListInsert(&head, i, i+1);
    }
    
    printf("链表长度: %d\n", ListLength(head));
    printf("请输入查找元素: ");
    scanf("%d", &x);
    
    result = ListFind(head, x);
    if (result != -1){
        printf("该元素序号为：%d\n", result);
    } else {
        printf("未找到该元素\n");
    }
    
    // 释放内存
    Destroy(&head);
    return 0;
}