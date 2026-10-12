import fs from 'fs'; import * as acorn from 'acorn';
const src=fs.readFileSync('../korea-assembly.html','utf8');
const i0=src.indexOf('<script>')+8, i1=src.lastIndexOf('</script>');
const js=src.slice(i0,i1);
const H=/[가-힣]/;
const ast=acorn.parse(js,{ecmaVersion:'latest',ranges:true,locations:true});
const out=[]; let regex=0;
(function walk(n,parent){ if(!n||typeof n.type!=='string') return;
  if(n.type==='Literal'&&typeof n.value==='string'&&H.test(n.value)){ out.push({v:n.value,s:n.start,e:n.end,line:n.loc.start.line,kind:'lit',pkey:parent&&parent.type==='Property'&&parent.key===n}); }
  if(n.type==='Literal'&&n.regex&&H.test(n.regex.pattern)) regex++;
  if(n.type==='TemplateElement'&&H.test(n.value.cooked)) out.push({v:n.value.cooked,s:n.start,e:n.end,line:n.loc.start.line,kind:'tpl'});
  for(const k in n){ if(k==='loc'||k==='range') continue; const c=n[k]; if(Array.isArray(c)) c.forEach(x=>walk(x,n)); else if(c&&typeof c.type==='string') walk(c,n); } })(ast,null);
// comments with Hangul are ignored
const uniq=new Map(); out.forEach(o=>{ if(!uniq.has(o.v)) uniq.set(o.v,{n:0,lines:new Set(),pkey:false}); const u=uniq.get(o.v); u.n++; u.lines.add(o.line); if(o.pkey) u.pkey=true; });
fs.writeFileSync('lits.json',JSON.stringify(out));
console.log('occurrences',out.length,'unique',uniq.size,'regex with hangul',regex,'chars',[...uniq.keys()].join('').length, 'propkeys', [...uniq.values()].filter(u=>u.pkey).length);
// html outside script
const html=src.slice(0,i0)+src.slice(i1);
const tn=[...html.replace(/data:[^)'"]+/g,'').matchAll(/>([^<>]*[가-힣][^<>]*)</g)].map(m=>m[1]); const at=[...html.matchAll(/(?:aria-label|title|placeholder|alt|content)="([^"]*[가-힣][^"]*)"/g)].map(m=>m[1]);
console.log('html text',tn.length,'attrs',at.length);
