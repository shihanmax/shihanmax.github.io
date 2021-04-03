
import os
import re


def handle(file):
    # 替换文件中的qiniu图片超链接
    content = open(file).read()

    content = re.sub(r"http://shihanmax\.top", "http://qiniu.shihanmax.top", content)
    
    with open("new-" + file, "w") as fwt:
        fwt.write(content)
    print("Done!")
    
    
targets = []
for i in os.listdir():
    if i.endswith(".md"):
        targets.append(i)

for i in targets:
    handle(i)
