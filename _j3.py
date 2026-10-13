import re
h=open('build/index.html',encoding='utf-8').read()
print("LEN",len(h))
i=h.find('15058856')
while i>=0:
    print("---@",i,"---")
    print(h[max(0,i-600):i+400].replace("\n"," | "))
    i=h.find('15058856',i+1)
