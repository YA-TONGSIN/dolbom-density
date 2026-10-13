from PIL import Image
import os
out=r'C:\Users\신운종\.openclaw\workspace\_judge'
names=['h_cj_dong','h_none','h_both']
ims=[Image.open(os.path.join(out,n+'.png')).crop((0,480,1280,1080)) for n in names]
w=1280;h=600
s=Image.new('RGB',(w,h*3),'white')
for i,im in enumerate(ims): s.paste(im,(0,h*i))
s.save(os.path.join(out,'combo.png'))
print('ok')
