import pymupdf, os
d=pymupdf.open('발표자료.pdf')
print("pages:",d.page_count)
out=r'C:\Users\신운종\.openclaw\workspace\_judge'
for i in range(d.page_count):
    d[i].get_pixmap(dpi=78).save(os.path.join(out,f'pdf{i+1}.png'))
    t=d[i].get_text().replace('\n',' | ')
    print(f"--- p{i+1} ---")
    print(t[:1400])
