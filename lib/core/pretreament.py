import nltk
import re
import json
import os


class pretreament(object):
    def __init__(self,script_path):
        self.script_path = script_path


        with open(F"{self.script_path}/json/zgrab2.json", 'r',  encoding = 'utf-8') as f:
            for line in f.readlines():
                line = line.strip()   # 使用strip函数去除空行
                if len(line) != 0:

                    # 先提取ip
                    lines = json.loads(line)
                    ip = lines['ip']
                    # print(ip)
                    data = str(lines['data'])

                    # 对数据进行处理
                    data = re.sub(r'\\[n|r|t|v|f|s|S|cx]','', data)     # 删除不可打印字符
                    data = re.sub(r'<[^<]+?>','', data)                 # 删除http标签
                    data = data.replace('@','')                         # 删除标点符号
                    data = data.replace('\\"','@')
                    data = re.sub(r'[\s+\!\\\/=|_@$&#%^*(+\')]+','',data)
                    data = data.replace("\"","$").replace(",","%").replace('[','#').replace(']','&')

                    # 分词
                    word = nltk.word_tokenize(data)
                    free = ["$", "%", '#', '&', '{', '}', ':']
                    word = [w for w in word if not w in free]           # 删除之前用来替换符号的字符

                    # 删除停止词
                    stop_words = set(nltk.corpus.stopwords.words('english'))
                    filtered_sentence = [w for w in word if not w in stop_words]

                    # 与ip合成新的json格式文件
                    predata = {"ip":ip, "data":filtered_sentence}
                    with open(F"{self.script_path}/json/fo.json","a", encoding = 'utf-8') as f:
                        f.write(json.dumps(predata) + '\n')
