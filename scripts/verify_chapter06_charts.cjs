// Execute the real pure SVG builder, without a browser or simulated DOM.
const fs=require('node:fs'),vm=require('node:vm'),assert=require('node:assert/strict');
const source=fs.readFileSync('course-site/dist/assets/ch6.js','utf8');
const start=source.indexOf('function chartSVG('),end=source.indexOf('\nfunction chart(target',start);
assert(start>=0&&end>start,'Pure SVG builder missing');
const E=x=>String(x).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const F=(x,n=4)=>Number.isFinite(x)?Number(x.toFixed(n)).toLocaleString('zh-CN',{maximumFractionDigits:n}):'—';
const render=vm.runInNewContext('('+source.slice(start,end)+')',{E,F});
const M=require('../course-site/dist/assets/ch6-model.js');
const b=M.equipment(M.defaults.equipment),m=M.mdp(M.defaults.mdp),t=M.trial(M.defaults.trial),v=M.vote(M.defaults.votes);
const cases=[
 ['equipment',b.V[0].map((_,s)=>({name:'state '+s,points:b.V.map((row,h)=>[h,row[s]])})),{}],
 ['trial',[{name:'EV',points:t.all.map((y,x)=>[x,y])}],{ticks:[[0,'stop'],[1,'act'],[2,'test']],stem:true}],
 ['votes',[{name:'first',points:v.first.map((y,x)=>[x,y])},{name:'Borda',points:v.borda.map((y,x)=>[x,y])}],{ticks:[[0,'A'],[1,'B'],[2,'C']],stem:true}],
];
for(const forecast of m.forecasts)for(let step=0;step<=3;step++)cases.push(['markov '+step,[0,1].map(s=>({name:'state '+s,points:forecast.rows.slice(0,step+1).map(row=>[row.t,row.dist[s]])})),{}]);
for(const cyclic of [false,true])for(const n of [0,1,12,40]){const d=M.delegation(cyclic,n);cases.push(['delegation '+n,[0,1,2].map(s=>({name:'member '+s,points:d.rows.map((row,x)=>[x,row[s]])})),{}]);}
cases.push(['negative values',[{name:'negative',points:[[0,-12],[1,-2]]}],{}]);
for(const[name,series,options]of cases){const svg=render(series,options);assert(svg.startsWith('<svg '),name);assert(svg.endsWith('</svg>'),name);assert(!/NaN|Infinity|undefined/.test(svg),name);assert.equal((svg.match(/<circle /g)||[]).length,series.reduce((n,s)=>n+s.points.length,0),name);}
const scalar=render([{name:'start',points:[[0,1]]}]);assert(scalar.includes('x="65" y="293"'),'Initial zero tick missing');
assert.equal(render([{name:'<script>',points:[[0,0],[1,1]]}]).includes('<script>'),false,'Labels must be escaped');
const html=fs.readFileSync('course-site/dist/ch6/index.html','utf8');assert(html.includes('ch6.js?v=20260919-1'),'Updated script URL missing');
console.log(cases.length+' SVG chart cases passed: all experiments, initial frame, every default forecast step, zero-round delegation, negative values, escaped labels.');
