import pymupdf
from PIL import Image
import os
out=r'C:\Users\신운종\.openclaw\workspace\_judge'
ims=[Image.open(os.path.join(out,f'pdf{i}.png')) for i in range(1,10)]
w,h=ims[0].size
for g in range(3):
    sheet=Image.new('RGB',(w, h*3),'white')
    for j in range(3):
        sheet.paste(ims[g*3+j],(0,h*j))
    sheet.save(os.path.join(out,f'pdfsheet{g+1}.png'))
print(w,h)
