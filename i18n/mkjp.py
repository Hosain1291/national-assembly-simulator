import subprocess,sys
s=open('../korea-assembly-ja.html',encoding='utf-8').read()
ch=set(c for c in s if ord(c)>=0x20 and not 0xD800<=ord(c)<=0xDFFF and not 0xAC00<=ord(c)<=0xD7A3)
ch|=set(chr(c) for c in range(0x3040,0x3100))|set(chr(c) for c in range(0x20,0x7f))|set('、。「」『』・ー〜（）！？：；％')
open('fonts_ja/chars.txt','w',encoding='utf-8').write(''.join(sorted(ch)))
for n in ('Regular','Medium','SemiBold','Bold','ExtraBold'):
  subprocess.run(['pyftsubset','../pretjp/package/dist/web/static/woff2/PretendardJP-%s.woff2'%n,'--text-file=fonts_ja/chars.txt','--flavor=woff2','--output-file=fonts_ja/pjp-%s.woff2'%n,'--layout-features=*'],check=True,stderr=subprocess.DEVNULL)
