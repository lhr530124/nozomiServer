#coding:utf8
f = open('nk.txt').readlines()
words = []
for l in f:
    words.append(l[:-1])
    #print l[:-1]
#words = [
#'fuck',
#'干你妹啊',
#]

#wordTree = wordTree.append(0)
#构造违禁词树
def create_word_tree(words_list):
    wordTree = [None for i in range(0,256)]
    #wordTree.append(0)
    wordTree = [wordTree,0]
    for word in words_list:

        # 每个单词对应一个tree
        tree = wordTree[0]
        for i  in range(0,len(word)):
            little = word[i]
            index = ord(little)
            # 已经到最后一个字母了
            #一个节点 有多种状态 
            # 有子树 
            # 终止 
            # 有子树 并且可以终止
            if i ==  len(word) -1:
                tree[index] = 1
            else:
                #新生节点
                if tree[index] == None:
                    tree[index] = [[None for x in range(0,256)], 0]
                #终止节点
                elif tree[index] == 1:
                    tree[index] = [[None for x in range(0,256)], 1]
                #节点加入过了 重复
                    
                tree = tree[index][0]

    return wordTree
#True 表示包含有敏感词
def checkWord(string, tree):
    temp = tree
    result = ''
    words = []
    word = []
    a = 0
    while a < len(string):
        index = ord(string[a])
        temp = temp[0][index]
        #没有匹配的回溯到单词开始 
        if temp == None:
            temp = tree
            a = a-len(word)
            word = []
        #完美匹配 从该单词下一个位置开始匹配
        elif temp == 1 or temp[1] == 1:
            word.append(index)
            words.append(word)
            a = a-len(word)+1
            word = []
            temp = tree
            return True
        #匹配过程中
        else:
            word.append(index)
        #下一个字符
        a = a+1
    return False
    
def search(string,tree):
    temp = tree
    result = ''
    words = []
    word = []
    a = 0
    while a < len(string):
        index = ord(string[a])
        temp = temp[0][index]
        #没有匹配的回溯到单词开始 
        if temp == None:
            temp = tree
            a = a-len(word)
            word = []
        #完美匹配 从该单词下一个位置开始匹配
        elif temp == 1 or temp[1] == 1:
            word.append(index)
            words.append(word)
            a = a-len(word)+1
            word = []
            temp = tree
        #匹配过程中
        else:
            word.append(index)
        #下一个字符
        a = a+1
    return words
    
    """
    for little in string:
        index = ord(little)
        temp = temp[0][index]
        #遍历到当前状态 但是没有找到 从头开始么？ 
        #不对 fufuck 这个时候 可能ufuc 是关键字呢？ 不应该回到头部 当前状态进行不下去了 需要回溯到某个位置 不定状态机 

        #没有匹配关键字 从头开始找
        if temp == None:
            temp = tree
            print 'can not find', index
            result += chr(index)
            word = []
        #关键字匹配成功
        elif temp == 1 or temp[1] == 1:
            word.append(index)
            words.append(word)
            a = 
        else:
            result += chr(index)
            print 'append', index
        if temp == 1:
            return string.replace(result,'*')
    return result
    """


tree = create_word_tree(words)

def blockWord(string):
    words = search(string, tree)
    for w in words:
        nw = ''
        for k in w:
            nw += chr(k)
        string = string.replace(nw, '*')
    return string

#print tree
#print tree[0][229][0][185][0][178][0][228][0][189][0][160][0][229][0][166]
#print tree[229][185][178][228][189][160][229][166][185]
#print tree[0][102][0][117]
#print translate('fufuck fuck fadsf  ',tree)
#res = translate('阿扁 是谁啊?', tree)
#print len(res)
#for r in res:
#    print ord(r)
#print res

if __name__ == '__main__':
    mystr = 'fufuck fuck you now'
    words = search(mystr, tree)
    print words
    for w in words:
        nw = ''
        for k in w:
            nw += chr(k)
        mystr = mystr.replace(nw, '*')
    print mystr

    nstr = 'fuck fuck world'
    res = checkWord(nstr, tree)
    print res

