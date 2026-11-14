song='''Oceans apart day after day. And I slowly go insane.
I hear your voice on the line.
But it does not stop the pain.
If I see you next to never.
How can we say forever?
Wherever you go whatever you do.
I will be right here waiting for you.
Whatever it takes or how my heart breaks!'''
for sign in ',.?!':
    song=song.replace(sign,' ')
words=song.split()
dict={}
for word in words:
    if word in dict:
        dict[word]+=1
    else:
        dict[word]=1
for key in dict.keys():
    print(key,dict[key])
