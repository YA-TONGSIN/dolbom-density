import io,os
h=open('build/index.html',encoding='utf-8').read()
out=r'C:\Users\신운종\.openclaw\workspace\_judge'
def mk(name, js):
    inj = "<script>window.addEventListener('load',function(){setTimeout(function(){"+js+"},300);});</script>"
    open(os.path.join(out,name),'w',encoding='utf-8').write(h.replace('</body>', inj+'</body>'))
# 1) 화성시 + 검색 '화성효나눔'
mk('h_hwaseong.html', "location.hash='#'+encodeURIComponent('경기도')+'/'+encodeURIComponent('화성시');fromHash();document.getElementById('q').value='화성효나눔';render();")
# 2) 남동구 + 검색 '행복나눔'
mk('h_namdong_dup.html', "location.hash='#'+encodeURIComponent('인천광역시')+'/'+encodeURIComponent('남동구');fromHash();document.getElementById('q').value='행복나눔';render();")
# 3) 관악구 + 비용 토글 ON + 등급 선택
mk('h_fee.html', "location.hash='#'+encodeURIComponent('서울특별시')+'/'+encodeURIComponent('관악구');fromHash();var f=document.getElementById('feeon');f.checked=true;f.dispatchEvent(new Event('change'));var g=document.getElementById('grade');if(g){g.selectedIndex=1;g.dispatchEvent(new Event('change'));}render();")
# 4) 없는 검색어
mk('h_none.html', "location.hash='#'+encodeURIComponent('서울특별시')+'/'+encodeURIComponent('관악구');fromHash();document.getElementById('q').value='zzqq없는이름';render();")
# 5) 청주시 읍면동 선택
mk('h_cj_dong.html', "location.hash='#'+encodeURIComponent('충청북도')+'/'+encodeURIComponent('청주시')+'/'+encodeURIComponent('가경동');fromHash();render();")
# 6) 전국 최악 - 등급필터+중앙값 동시
mk('h_both.html', "location.hash='#'+encodeURIComponent('서울특별시')+'/'+encodeURIComponent('관악구');fromHash();document.getElementById('only').checked=true;document.getElementById('onlyab').checked=true;document.getElementById('only').dispatchEvent(new Event('change'));document.getElementById('onlyab').dispatchEvent(new Event('change'));render();")
print("ok")
