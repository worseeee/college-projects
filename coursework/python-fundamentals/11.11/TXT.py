f=open(r'E:\college\Python\11.11\TXT.txt','r',encoding='utf-8')
txt=f.read()
f.close()
print(txt)
def change(t):
    newtxt=''
    for char in t:
        if 'a'<=char<='z':
            newtxt+=chr(ord(char)-32)
        elif 'A'<=char<='Z':
            newtxt+=chr(ord(char)+32)
        else:
            newtxt+=char
    return newtxt
newtxt=change(txt)
print(newtxt)
f=open(r'E:\college\Python\11.11\newTXT.txt','w',encoding='utf-8')
f.write(newtxt)
f.close()
