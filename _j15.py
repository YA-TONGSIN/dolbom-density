import os
h=open('build/index.html',encoding='utf-8').read()
out=r'C:\Users\신운종\.openclaw\workspace\_judge'
js=("<script>window.addEventListener('load',function(){setTimeout(function(){"
    "location.hash='#'+encodeURIComponent('\uc138\uc885\ud2b9\ubcc4\uc790\uce58\uc2dc')+'/'+encodeURIComponent('\uace0\uc6b4\ub3d9');fromHash();"
    "var s=document.getElementById('sgg');var o=[].map.call(s.options,function(x){return x.text;}).join(' / ');"
    "var d=document.getElementById('dong');var dd=[].map.call(d.options,function(x){return x.text;}).join(' / ');"
    "var p=document.createElement('div');p.style.cssText='background:#ffe;border:2px solid #c00;padding:10px;font:15px monospace;white-space:pre-wrap';"
    "p.textContent='[\uc2dc\u00b7\uad70\u00b7\uad6c \uc635\uc158] '+o+'\\n[\uc74d\uba74\ub3d9 \uc635\uc158] '+dd+'\\n[\uc74d\uba74\ub3d9\uce78 hidden] '+document.getElementById('dongwrap').hidden;"
    "document.body.prepend(p);},900);});</script>")
open(os.path.join(out,'sj2.html'),'w',encoding='utf-8').write(h.replace('</body>', js+'</body>'))
print('ok')
