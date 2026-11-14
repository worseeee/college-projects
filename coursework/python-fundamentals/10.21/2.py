x=input("请输入：")
cnt_num=0
cnt_char=0
cnt_else=0
for i in range(0,len(x)):
    m=ord(x[i])
    if 48<=m<=57:
        cnt_num+=1
    elif 65<=m<=90 or 97<=m<=122:
        cnt_char+=1
    else:
        cnt_else+=1
print("数字有%d个"%(cnt_num))
print("字母有%d个"%(cnt_char))
print("其他符号有有%d个"%(cnt_else))
