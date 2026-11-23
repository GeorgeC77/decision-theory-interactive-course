/* All calculations stay local. Static first panel and PDF links survive script failure. */
(()=>{'use strict';
const M=window.Ch3,$=id=>document.getElementById(id),fmt=(x,d=3)=>{const n=Math.abs(Number(x))<1e-9?0:Number(x),digits=n!==0&&Math.abs(n)<.5*10**-d?Math.max(d,9):d;return n.toLocaleString('zh-CN',{maximumFractionDigits:digits});},esc=x=>String(x).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const probabilityText=(x,d=6)=>{const epsilon=10**-d;if(x>0&&x<epsilon)return '<'+epsilon.toFixed(d);if(x<1&&1-x<epsilon)return '>'+(1-epsilon).toFixed(d);return fmt(x,d);};
const value=id=>{const e=$(id);if(e.value.trim()===''||!e.validity.valid)throw Error(e.labels[0].textContent.trim()+'：请填写范围内的有效数值');const v=Number(e.value);if(!Number.isFinite(v))throw Error('请输入有限数值');return v;};
const table=(id,head,rows)=>{$(id).innerHTML='<table><thead><tr>'+head.map(x=>'<th>'+esc(x)+'</th>').join('')+'</tr></thead><tbody>'+rows.map(row=>'<tr>'+row.map(x=>'<td>'+esc(x)+'</td>').join('')+'</tr>').join('')+'</tbody></table>';};
const metrics=(id,rows)=>{$(id).innerHTML=rows.map(([label,v])=>'<div><span>'+esc(label)+'</span><strong>'+esc(v)+'</strong></div>').join('');};
const names=indices=>indices.map(i=>M.names[i]).join(' / ');
const colors=['#8a98a6','#244e79','#bb8637'];
function plot(id,series,xlabel,ylabel,marker){
 const pts=series.flatMap(s=>s.points),discrete=id==='ev-chart'||id==='sample-chart';let xmin=Math.min(...pts.map(p=>p[0])),xmax=Math.max(...pts.map(p=>p[0])),ymin=Math.min(0,...pts.map(p=>p[1])),ymax=Math.max(0,...pts.map(p=>p[1]));if(discrete)xmin=Math.min(0,xmin);if(xmin===xmax)xmax=xmin+1;if(ymin===ymax)ymax=ymin+1;const pad=(ymax-ymin)*.09;ymin-=pad;ymax+=pad;
 const X=x=>65+(x-xmin)/(xmax-xmin)*595,Y=y=>285-(y-ymin)/(ymax-ymin)*220;
 let s='<svg viewBox="0 0 720 360" role="img" aria-label="'+esc(ylabel+'随'+xlabel+'变化')+'"><rect width="720" height="360" fill="#fbfcfe"/>';
 for(let i=0;i<=4;i++){const y=ymin+(ymax-ymin)*i/4;s+=`<line x1="65" y1="${Y(y)}" x2="660" y2="${Y(y)}" stroke="#dce3e9"/><text x="57" y="${Y(y)+5}" text-anchor="end" font-size="13" fill="#586a7c">${fmt(y,2)}</text>`;}
 const ticks=[...new Set(Array.from({length:5},(_,i)=>{const x=xmin+(xmax-xmin)*i/4;return discrete?Math.round(x):x;}))];
 for(const x of ticks)s+=`<text class="plot-x-tick" x="${X(x)}" y="308" text-anchor="middle" font-size="13" fill="#586a7c">${fmt(x,2)}</text>`;
 s+=`<text x="65" y="23" font-size="14" fill="#586a7c">${esc(ylabel)}</text><text x="365" y="333" text-anchor="middle" font-size="14" fill="#586a7c">${esc(xlabel)}</text>`;
 series.forEach((t,i)=>{const color=t.color||colors[i%3];s+=`<polyline points="${t.points.map(p=>X(p[0])+','+Y(p[1])).join(' ')}" fill="none" stroke="${color}" stroke-width="3"/><text class="plot-series-label" x="${250+i*135}" y="23" font-size="13" style="fill:${color}">${esc(t.name)}</text>`;if(t.points.length===1)s+=`<circle cx="${X(t.points[0][0])}" cy="${Y(t.points[0][1])}" r="4" fill="${color}"/>`;});
 if(marker!==undefined&&marker>=xmin&&marker<=xmax)s+=`<line x1="${X(marker)}" x2="${X(marker)}" y1="65" y2="285" stroke="#8697a9" stroke-dasharray="5 5"/>`;
 $(id).innerHTML=s+'</svg>';
}
let model=null,latest={},step=0,selectedReport=0,activePanel='expectation';
function naturalFrequency(r){
 const report=r.reports[selectedReport],reportName=selectedReport?'差报告':'好报告';
 const groups=r.reports.flatMap((x,i)=>x.joint.map((p,j)=>({report:i,state:j,count:1000*p})));
 let svg='<svg viewBox="0 0 600 240" role="img" aria-label="'+esc(`每1000个情境的期望频数，非观测样本。当前突出${reportName}：高客流${fmt(report.joint[0]*1000,4)}，低客流${fmt(report.joint[1]*1000,4)}，合计${fmt(report.mass*1000,4)}。`)+'"><title>1000格自然频数图：每格代表1个情境的期望频数，可分割显示小数</title>';
 let start=0;
 for(const g of groups){
  const end=start+g.count,fill=g.state?'#bb8637':'#244e79';
  for(let cell=Math.floor(start);cell<Math.min(1000,Math.ceil(end-1e-9));cell++){
   const lo=Math.max(cell,start),hi=Math.min(cell+1,end);if(hi<=lo)continue;
   svg+=`<rect x="${cell%50*12+(lo-cell)*10}" y="${Math.floor(cell/50)*12}" width="${(hi-lo)*10}" height="10" fill="${fill}" opacity="${g.report===selectedReport?1:.16}"/>`;
  }
  start=end;
 }
 svg+='</svg>';
 const cells=groups.map(g=>`<div class="frequency-count ${g.report===selectedReport?'is-selected':''}" data-expected-count="${g.count}" data-report="${g.report}" data-state="${g.state}"><span><i class="state-key ${g.state?'low':'high'}" aria-hidden="true"></i>${g.state?'低':'高'}客流 · ${g.report?'差':'好'}报告</span><strong>${fmt(g.count,4)}</strong></div>`).join('');
 const posterior=report.posterior?`${fmt(report.joint[0]*1000,4)} ÷ ${fmt(report.mass*1000,4)} = ${fmt(report.posterior[0]*100,2)}%`:'0 ÷ 0：未定义';
 $('frequency').innerHTML=`<p class="frequency-prior">1000 个情境：高客流 <strong>${fmt(model.p[0]*1000,4)}</strong>，低客流 <strong>${fmt(model.p[1]*1000,4)}</strong>。每格为 1 个期望频数，小数用部分色格表示。</p><div class="frequency-grid">${svg}</div><div class="frequency-counts">${cells}</div><div class="posterior-reading" aria-live="polite"><span>${reportName}中，高客流占多少？</span><strong id="frequency-posterior" data-posterior="${report.posterior?report.posterior[0]:''}">${posterior}</strong><p>${report.posterior?`分母只数${reportName}的 ${fmt(report.mass*1000,4)} 个情境，不再是全部 1000 个。`:`P(${reportName})=0，此报告不会出现；后验不定义，对调查事前毛值的贡献为 0。`}</p></div>`;
 ['frequency-good','frequency-bad'].forEach((id,i)=>$(id).setAttribute('aria-pressed',String(i===selectedReport)));
}
function informationValue(r){
 const baseline=r.prior.best.value,perfect=r.prior.perfect,zero=x=>Math.abs(x)<1e-9?0:x;
 const lo=Math.min(0,zero(r.net)),rawHi=Math.max(0,baseline,r.gross,perfect),hi=rawHi===lo?lo+1:rawHi;
 const X=x=>(x-lo)/(hi-lo)*100,unit=x=>fmt(zero(x),4)+' 万元';
 const segment=(from,to,cls)=>`<span class="value-segment ${cls}" style="left:${X(Math.min(from,to))}%;width:${Math.abs(to-from)/(hi-lo)*100}%"></span>`;
 const rows=[
  ['baseline','无调查最佳 EMV',baseline,segment(0,baseline,'base'),`现在直接选：${names(r.prior.best.indices)}`],
  ['gross','调查后毛值',r.gross,segment(0,baseline,'base')+segment(baseline,r.gross,'sample'),`无调查最佳 EMV + EVSI = ${unit(baseline)} + ${unit(r.evsi)}`],
  ['net','调查后净值',r.net,segment(0,zero(r.net),r.net<0?'negative':'net'),`调查后毛值 − 调查费 = ${unit(r.gross)} − ${unit(r.cost)}`],
  ['perfect','完全信息下最佳值',perfect,segment(0,baseline,'base')+segment(baseline,perfect,'perfect'),`无调查最佳 EMV + EVPI = ${unit(baseline)} + ${unit(r.prior.evpi)}`]
 ];
 $('info-value').innerHTML='<p class="value-unit">共用金额轴 / 万元；虚线表示 0。蓝色实心为无调查基准，金色为 EVSI，绿色为 EVPI；调查净值用斜纹表示，负值改用红色。</p>'+rows.map(([key,label,v,bar,detail])=>`<div class="value-row" data-value-kind="${key}" data-value="${zero(v)}"><div class="value-label"><span>${label}</span><strong>${unit(v)}</strong></div><div class="value-track" aria-hidden="true">${bar}<i class="value-zero" style="left:${X(0)}%"></i></div><p>${esc(detail)}</p></div>`).join('')+`<div class="value-axis" aria-hidden="true"><span>${fmt(lo,4)}</span><span>${fmt(hi,4)} 万元</span></div><div class="value-conclusion" aria-live="polite"><strong>净改善 = EVSI − 调查费 = ${unit(r.evsi)} − ${unit(r.cost)} = ${unit(r.increment)}</strong><p>${r.prior.evpi<1e-9?'EVPI = 0：即使完全知道状态，也不能提高最优期望值；此时 EVSI 也为 0。':r.evsi<1e-9?'EVSI = 0：这项调查没有提高最优期望值，但完全信息仍可能有价值。':'EVSI 是这项调查带来的毛增量；EVPI 是完全信息的毛增量上限。'}${Math.abs(r.increment)<1e-9?' 净改善为 0，调查与不调查并列。':r.increment<0?' 净改善为负，应选择不调查。':' 净改善为正，按期望货币准则值得调查。'}</p></div>`;
}
function cafeInput(){const p=value('prior');return {p:[p,1-p],a:[[0,0],[value('small-high'),value('small-low')],[value('large-high'),value('large-low')]]};}
function expectation(){model=cafeInput();const {a,p}=model,r=M.evaluate(a,p),sim=M.simulate(a,p,value('runs'),value('seed'));latest.expectation={...model,...r,simulation:sim};$('prior-out').textContent=fmt(p[0]*100)+'%';metrics('ev-metrics',[['期望最优',names(r.best.indices)],['最优 EMV',fmt(r.best.value)+' 万'],['EVPI',fmt(r.evpi)+' 万']]);table('ev-table',['方案','EMV / 万元','SD / 万元','亏损概率','EOL / 万元','模拟均值'],a.map((_,i)=>[M.names[i],fmt(r.ev[i]),fmt(r.sd[i]),fmt(r.loss[i]*100)+'%',fmt(r.eol[i]),fmt(sim.means[i])]));plot('ev-chart',sim.paths.map((points,i)=>({name:M.names[i],points})),'独立抽样次数','累计样本均值 / 万元');$('ev-comment').textContent=`实际抽得高客流 ${sim.counts[0]} 次、低客流 ${sim.counts[1]} 次。理论期望不随种子改变；样本均值可能来回波动。`;}
function bayes(){
 if(!model)throw Error('请先修正期望实验中的输入');
 const s=value('sensitivity'),t=value('specificity'),cost=value('survey-cost'),r=M.bayes(model.a,model.p,[[s,1-t],[1-s,t]],cost);
 latest.bayes={sensitivity:s,specificity:t,...r};$('sensitivity-out').textContent=fmt(s*100)+'%';$('specificity-out').textContent=fmt(t*100)+'%';
 metrics('bayes-metrics',[['EVSI · 调查信息毛价值',fmt(r.evsi)+' 万元'],['EVPI · 完全信息上限',fmt(r.prior.evpi)+' 万元'],['调查费',fmt(cost)+' 万元'],['调查净改善',fmt(r.increment)+' 万元']]);
 $('bayes-comment').textContent=`调查后净价值 ${fmt(r.net)} 万元。`+(r.increment>1e-9?'按期望货币准则，值得调查。':r.increment< -1e-9?'费用超过信息毛价值，选择不调查。':'调查与不调查并列。')+' 同一模型应满足 0 ≤ EVSI ≤ EVPI。';
 naturalFrequency(r);informationValue(r);
 table('bayes-table',['报告','报告概率','后验 P(高)','后验 P(低)','最优行动','条件最优值 / 万元'],r.reports.map((x,i)=>[i===0?'好报告':'差报告',fmt(x.mass,5),x.posterior?fmt(x.posterior[0],6):'未定义',x.posterior?fmt(x.posterior[1],6):'未定义',x.best?names(x.best.indices):'不会出现',x.best?fmt(x.best.value,5):'—']));
}
function sensitivity(){if(!model)return;plot('sensitivity-chart',model.a.map((r,i)=>({name:M.names[i],points:Array.from({length:101},(_,j)=>[j/100,r[0]*j/100+r[1]*(1-j/100)])})),'高客流概率 p','EMV / 万元',model.p[0]);const intervals=M.sensitivity(model.a),merged=[];for(const item of intervals){const prev=merged.at(-1);if(prev&&String(prev.best)===String(item.best))prev.hi=item.hi;else merged.push({...item});}latest.sensitivity=merged;table('sensitivity-table',['概率开区间','最优方案','右端点最优方案'],merged.map(x=>[`${fmt(x.lo,6)} < p < ${fmt(x.hi,6)}`,names(x.best),names(M.evaluate(model.a,[x.hi,1-x.hi]).best.indices)]));$('sensitivity-comment').textContent='当前 p='+fmt(model.p[0],4)+'，最优：'+names(M.evaluate(model.a,model.p).best.indices)+'。p=0 时：'+names(M.evaluate(model.a,[0,1]).best.indices)+'；p=1 时：'+names(M.evaluate(model.a,[1,0]).best.indices)+'。开区间与端点并列情况分别显示。';}
function tree(){const cost=value('expand-cost'),r=M.tree(cost);latest.tree={cost,...r};$('expand-cost-out').textContent=fmt(cost);$('tree-stage').textContent=['0 / 3：先预测后7年的条件价值。','1 / 3：圆圈按条件概率加权；扩建费已从扩建候选值扣除。','2 / 3：小店前期好时，在扩建与保持中取较大值。','3 / 3：回到现在，加前3年收益、扣初始投资，比较完整策略。'][step];$('tree-next').disabled=step===3;
 const tx=(x,y,t,size=17)=>`<text x="${x}" y="${y}" text-anchor="middle" font-size="${size}" fill="#244e79">${esc(t)}</text>`;
 let svg='<svg viewBox="0 0 960 400" role="img" aria-label="例3-8分步回溯：中店或小店；小店前期好时可扩建"><g stroke="#94a7b8" stroke-width="2" fill="none"><path d="M100 190L330 65M100 190L330 240M330 240L570 185M330 240L570 340M570 185L790 145M570 185L790 245"/></g><rect class="tree-node" x="85" y="175" width="30" height="30"/><circle class="tree-chance" cx="330" cy="240" r="13"/><rect class="tree-node" x="555" y="170" width="30" height="30"/>';
 svg+=tx(200,87,'建中店')+tx(195,265,'建小店')+tx(439,186,'前期好 0.75')+tx(432,321,'前期差 0.25')+tx(697,135,'扩建')+tx(699,247,'保持');
 svg+=tx(330,58,step===3?'中店 '+fmt(r.medium):'中店：待回溯')+tx(812,168,step>=1?fmt(r.expand):'7×129−费用')+tx(812,275,step>=1?fmt(r.stayGood):'7×51.3')+tx(636,349,step>=1?fmt(r.stayBad):'7×7.8')+tx(577,108,step>=2?r.late.indices.map(i=>['扩建','保持'][i]).join(' / '):'等待比较')+tx(310,293,step===3?'小店 '+fmt(r.small):'等待回溯')+tx(116,366,step===3?'期初：'+r.root.indices.map(i=>['中店','小店'][i]).join(' / '):'金额：万元');
 $('tree-svg').innerHTML=svg+'</svg>';let rows=[];if(step>=1)rows.push(['后期条件期望',`扩建 ${fmt(r.expand)}；保持 ${fmt(r.stayGood)}；前期差后保持 ${fmt(r.stayBad)}`]);if(step>=2)rows.push(['后续决策',r.late.indices.map(i=>['扩建','保持'][i]).join(' / ')]);if(step>=3)rows.push(['完整小店策略',`136.5 + 0.75×${fmt(Math.max(r.expand,r.stayGood))} + 0.25×54.6 − 150 = ${fmt(r.small)}`],['中店策略','232.5 + 0.75×903 + 0.25×168 − 400 = 551.75']);table('tree-details',['步骤','计算'],rows);}
function sampling(){const n=value('sample-n'),fixed=value('sample-fixed'),unit=value('sample-unit'),r=M.sampling(n,fixed,unit),all=Array.from({length:41},(_,j)=>M.sampling(j,fixed,unit)),b=M.best(all.map(x=>x.increment));latest.sampling={n,fixed,unit,result:r,bestN:b.indices};metrics('sample-metrics',[['所选 n 的 EVSI',fmt(r.evsi,6)+' 元'],['所选 n 的净改善',fmt(r.increment,6)+' 元'],['0—40 的最优 n',b.indices.join(' / ')],['最大净改善',fmt(b.value,6)+' 元']]);$('sample-comment').textContent=`不抽样时直接买，期望净收益 1 元。所选方案成本 ${fmt(r.cost)} 元，抽样后净价值 ${fmt(r.net,6)} 元。`+(b.indices.includes(40)?'最优包含搜索上界40，需扩大范围检查。':'这里只比较给定的41种样本量。');plot('sample-chart',[{name:'EVSI',points:all.map(x=>[x.n,x.evsi]),color:'#244e79'},{name:'净改善',points:all.map(x=>[x.n,x.increment]),color:'#bb8637'}],'样本量 n','价值 / 元',n);table('sample-table',['缺陷数 X','概率','后验 θ=.2 / .1 / .05','行动','购买条件期望 / 元'],r.reports.map((x,i)=>[i,probabilityText(x.mass),x.posterior?x.posterior.map(v=>probabilityText(v,5)).join(' / '):'未定义',x.best?x.best.indices.map(j=>['不买','买'][j]).join(' / '):'不会出现',x.ev?fmt(x.ev[1],6):'—']));}
function utility(){const k=value('curvature'),r=M.utilityChoice(k);latest.utility={k,...r};$('curvature-out').textContent=fmt(k,1);plot('utility-chart',[{name:'当前效用',points:r.points,color:'#244e79'},{name:'线性参考',points:[[-10,0],[20,1]],color:'#bb8637'}],'结果 x / 万元','效用 u(x)');metrics('utility-metrics',[['风险态度',k>0?'厌恶风险':k<0?'偏好风险':'风险中性'],['风险方案 CE',fmt(r.ce[1],4)+' 万'],['风险溢价',fmt(5-r.ce[1],4)+' 万']]);table('utility-table',['方案','EMV','EU','CE / 万元'],['确定 5 万','20 / −10 各半'].map((s,i)=>[s,5,fmt(r.eu[i],6),fmt(r.ce[i],4)]));$('utility-comment').textContent='期望效用选择：'+r.best.indices.map(i=>['确定 5 万','有风险方案'][i]).join(' / ')+'。'+(k>0?'凹函数下，风险方案 E[u(V)] 小于 u(E[V])。':k<0?'凸函数下，此风险方案的确定等价高于期望值。':'线性时，期望效用与期望货币给出相同排序。');}
const quiz=[
 ['大店高/低损益16/−6，高客流概率0.4，EMV为？',['7.2','2.8','16'],1,'0.4×16+0.6×(−6)=2.8万元；期望不一定是实际可出现结果。'],
 ['决策树的机会节点应该怎样回溯？',['取最大值','加总所有分支','按该节点条件概率加权'],2,'可控行动取优；不可控状态按条件概率加权。'],
 ['P(好报告|高客流)=0.8意味着？',['好报告后高客流概率必为0.8','高客流时出现好报告的概率为0.8','总体准确率必为0.8'],1,'后验还需要先验和低客流时的报告概率。'],
 ['EVSI=1.6、调查费0.5，净改善为？',['1.1','2.1','1.6'],0,'信息毛价值扣一次费用；不能把EVPI或调查后总净价值混为净改善。'],
 ['在本章信息模型中，哪种结果必需复查？',['EVSI=0','净改善<0','EVSI>EVPI'],2,'同一模型、可忽略信息下0≤EVSI≤EVPI；成本可能让净改善为负。'],
 ['默认咖啡店p=0.5时怎么选？',['大店唯一最优','小店唯一最优','小店、大店并列'],2,'两者期望同为5万元，但风险特征不同。'],
 ['严格凹且递增效用下，非退化风险方案的CE怎样？',['小于EMV','等于EMV','大于EMV'],0,'先求期望效用，再求逆函数；Jensen不等式给出CE<EMV。'],
 ['最优抽样量比较中，n=0代表？',['不抽样，费用为0','支付固定费但不抽件','无效数据必须删除'],0,'必须允许不购买信息，否则可能被迫选择负净改善。']
];
function quizInit(){$('quiz-questions').innerHTML=quiz.map((q,i)=>`<fieldset class="quiz-item"><legend>${i+1}. ${esc(q[0])}</legend>${q[1].map((a,j)=>`<label><input type="radio" name="q${i}" value="${j}" required> ${esc(a)}</label>`).join('')}</fieldset>`).join('');$('quiz-form').addEventListener('submit',e=>{e.preventDefault();let score=0;const rows=quiz.map((q,i)=>{const answer=document.querySelector(`input[name="q${i}"]:checked`);if(!answer)return null;const ok=Number(answer.value)===q[2];if(ok)score++;return `<p>${i+1}. ${ok?'正确':'需修正'}：${esc(q[3])}</p>`;});if(rows.some(x=>x===null)){$('quiz-result').textContent='请完成全部8题后提交。';return;}$('quiz-result').innerHTML=`<strong>${score} / 8</strong>`+rows.join('');});$('quiz-form').addEventListener('reset',()=>{$('quiz-result').textContent='';});}
function safe(fn,id,clear=[]){try{fn();if(id)$(id).textContent='';return true;}catch(e){if(id)$(id).textContent=e.message;clear.forEach(x=>$(x).innerHTML='');return false;}}
const bayesClear=['bayes-metrics','bayes-table','frequency','info-value','bayes-comment'];
function shared(){const ok=safe(expectation,'ev-error',['ev-metrics','ev-chart','ev-table','ev-comment']);if(!ok){model=null;[...bayesClear,'sensitivity-chart','sensitivity-table','sensitivity-comment'].forEach(x=>$(x).innerHTML='');$('bayes-error').textContent='请先修正“期望与随机结果”中的输入。';return false;}const bayesOk=safe(bayes,'bayes-error',bayesClear);sensitivity();return bayesOk;}
function refreshForExport(){const sharedOk=shared(),treeOk=safe(tree,'tree-error',['tree-stage','tree-svg','tree-details']),sampleOk=safe(sampling,'sample-error',['sample-metrics','sample-chart','sample-table','sample-comment']),utilityOk=safe(utility,'utility-error',['utility-metrics','utility-chart','utility-table','utility-comment']);return sharedOk&&treeOk&&sampleOk&&utilityOk;}
function form(id,fn){$(id).addEventListener('input',fn);$(id).addEventListener('submit',e=>e.preventDefault());$(id).addEventListener('reset',()=>setTimeout(fn,0));}
function navigate(){let hash=location.hash.slice(1);if(hash==='main')hash=activePanel;if(!document.querySelector('.panel#'+CSSescape(hash)))hash='expectation';activePanel=hash;document.querySelectorAll('.panel').forEach(x=>x.hidden=x.id!==hash);document.querySelectorAll('.side-nav a').forEach(x=>{const yes=x.hash==='#'+hash;x.classList.toggle('active',yes);if(yes)x.setAttribute('aria-current','location');else x.removeAttribute('aria-current');});}
function CSSescape(s){return /^[a-z][a-z-]*$/.test(s)?s:'no-such-panel';}
try{
 form('ev-form',shared);form('bayes-form',()=>safe(bayes,'bayes-error',bayesClear));form('tree-form',()=>{step=0;safe(tree,'tree-error',['tree-stage','tree-svg','tree-details']);});form('sample-form',()=>safe(sampling,'sample-error',['sample-metrics','sample-chart','sample-table','sample-comment']));form('utility-form',()=>safe(utility,'utility-error',['utility-metrics','utility-chart','utility-table','utility-comment']));
 $('bayes-form').addEventListener('reset',()=>{selectedReport=0;});
 $('perfect-info').addEventListener('click',()=>{$('sensitivity').value='1';$('specificity').value='1';safe(bayes,'bayes-error',bayesClear);});$('no-info').addEventListener('click',()=>{$('sensitivity').value='.5';$('specificity').value='.5';safe(bayes,'bayes-error',bayesClear);});
 ['frequency-good','frequency-bad'].forEach((id,i)=>$(id).addEventListener('click',()=>{selectedReport=i;safe(bayes,'bayes-error',bayesClear);}));
 $('tree-next').addEventListener('click',()=>{step=Math.min(3,step+1);safe(tree,'tree-error',['tree-stage','tree-svg','tree-details']);});$('tree-hide').addEventListener('click',()=>{step=0;safe(tree,'tree-error',['tree-stage','tree-svg','tree-details']);});
 try{$('reflection').value=localStorage.getItem('decision-ch3-reflection')||'';}catch(_){$('note-status').textContent='此环境不能本机保存，可使用导出。';}
 $('save-note').addEventListener('click',()=>{try{localStorage.setItem('decision-ch3-reflection',$('reflection').value);$('note-status').textContent='已保存在本机此浏览器。';}catch(_){$('note-status').textContent='本机保存不可用，请导出记录。';}});
 $('export-record').addEventListener('click',()=>{const forms=[...document.querySelectorAll('input[type=number],input[type=range]')];if(forms.some(x=>!x.validity.valid||x.value==='')){$('note-status').textContent='请修正无效实验输入后导出，避免导出旧结果。';return;}if(!refreshForExport()){$('note-status').textContent='实验计算未完成，请修正错误后再导出。';return;}const blob=new Blob([JSON.stringify({chapter:3,savedAt:new Date().toISOString(),assumptions:'教学模拟；金额口径见各实验；未上传服务器',inputs:Object.fromEntries(forms.map(x=>[x.id,Number(x.value)])),results:latest,reflection:$('reflection').value},null,2)],{type:'application/json;charset=utf-8'});const url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download='第三章-实验记录.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);$('note-status').textContent='已准备实验记录下载。';});
 shared();tree();sampling();utility();quizInit();navigate();window.addEventListener('hashchange',navigate);$('runtime-status').hidden=true;
}catch(e){$('runtime-status').hidden=false;$('runtime-status').textContent='交互初始化未完成：'+e.message+'。可继续打开PDF课件，或重新完整解压教学包。';console.error(e);}
})();
