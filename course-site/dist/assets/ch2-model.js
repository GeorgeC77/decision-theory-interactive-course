/* All monetary arrays use t=0 first and year-end flows afterwards. */
(function(root){'use strict';
const finite=(x,name)=>{if(!Number.isFinite(x))throw new Error(name+'须为有限数值');return x;};
function rate(r){finite(r,'折现率');if(r<=-1)throw new Error('折现率必须大于 -100%');}
function flows(fs){if(!Array.isArray(fs)||fs.length<2||fs.length>61)throw new Error('请输入 2—61 个现金流（含第 0 期）');fs.forEach(x=>finite(x,'现金流'));}
function npv(fs,r){flows(fs);rate(r);return fs.reduce((a,x,t)=>a+x/Math.pow(1+r,t),0);}
function pvRows(fs,r){flows(fs);rate(r);let cum=0;return fs.map((cf,t)=>{const pv=cf/Math.pow(1+r,t);cum+=pv;return {t,cf,pv,cumulative:cum};});}
function annuityFactor(r,n){rate(r);if(!Number.isInteger(n)||n<1||n>60)throw new Error('期数须为 1—60 的整数');return r===0?n:-Math.expm1(-n*Math.log1p(r))/r;}
function series(I,A,n,S=0,G=0){[I,A,S,G].forEach(x=>finite(x,'输入'));if(I<0)throw new Error('初始投资不得为负');annuityFactor(0,n);return [-I,...Array.from({length:n},(_,j)=>A+j*G+(j===n-1?S:0))];}
function irr(fs){flows(fs);if(!(fs[0]<0&&fs.slice(1).every(x=>x>=0)&&fs.slice(1).some(x=>x>0)))return {value:null,reason:'现金流不满足“期初流出、后续非负且有流入”，可能有多个 IRR 或无 IRR；本工具不强报单一数值。'};
let lo=-1+Number.EPSILON/2,hi=1;
if(npv(fs,lo)<0)return {value:null,reason:'IRR 太接近 −100%，超出可表示的数值精度，请用 NPV 评价。'};while(npv(fs,hi)>0&&hi<1048576)hi=hi*2+1;
if(npv(fs,hi)>0)return {value:null,reason:'根超出数值求解范围，请用 NPV 评价。'};
for(let k=0;k<140;k++){const mid=(lo+hi)/2;if(npv(fs,mid)>0)lo=mid;else hi=mid;}return {value:(lo+hi)/2,reason:'常规现金流的唯一 IRR'};}
function payback(fs,r=0){const rows=pvRows(fs,r);if(fs[0]>=0)return null;for(let t=1;t<rows.length;t++){if(rows[t-1].cumulative<0&&rows[t].cumulative>=0&&rows[t].pv>0)return t-1-rows[t-1].cumulative/rows[t].pv;}return null;}
function metrics(fs,r){const value=npv(fs,r),n=fs.length-1,initial=-fs[0];return {npv:value,nav:value/annuityFactor(r,n),irr:irr(fs),staticPayback:payback(fs),dynamicPayback:payback(fs,r),npvr:initial>0?value/initial:null};}
function breakEven({price,variable,fixed,capacity,quantity,target=0}){[price,variable,fixed,capacity,quantity,target].forEach(x=>finite(x,'输入'));if([price,variable,fixed,capacity,quantity,target].some(x=>x<0))throw new Error('本实验参数不得为负');const margin=price-variable,profit=margin*quantity-fixed;const q=margin>0?fixed/margin:(fixed===0?0:null);return {margin,profit,revenue:price*quantity,cost:fixed+variable*quantity,breakEven:q,targetQuantity:margin>0?(fixed+target)/margin:(fixed===0&&target===0?0:null),reachable:q!==null&&q<=capacity,overCapacity:quantity>capacity,utilization:capacity>0&&q!==null?q/capacity:null};}
const budgetProjects=[['A',200,120],['B',120,54],['C',40,5],['D',90,22.5],['E',130,28.6],['F',360,64.8],['G',30,4.2],['H',150,57]].map(([id,cost,value])=>({id,cost,value}));
function portfolio(budget,projects=budgetProjects){finite(budget,'预算');if(budget<0||projects.length>20)throw new Error('预算须非负，项目最多 20 个');const choices=[];for(let mask=0;mask<2**projects.length;mask++){let cost=0,value=0,ids=[];projects.forEach((p,j)=>{if(mask&(1<<j)){cost+=p.cost;value+=p.value;ids.push(p.id);}});if(cost<=budget+1e-9)choices.push({cost,value,ids});}choices.sort((a,b)=>b.value-a.value||a.cost-b.cost);return {best:choices[0],feasibleCount:choices.length,top:choices.slice(0,5)};}
function greedy(budget,criterion='ratio'){let cost=0,value=0,ids=[];[...budgetProjects].sort((a,b)=>criterion==='ratio'?b.value/b.cost-a.value/a.cost:b.value-a.value).forEach(p=>{if(cost+p.cost<=budget){cost+=p.cost;value+=p.value;ids.push(p.id);}});return {cost,value,ids};}
function compare(key,r){const preset=presets[key];if(!preset)throw new Error('未知方案');const a=metrics(preset.a,r),b=metrics(preset.b,r),delta=preset.b.map((v,i)=>v-preset.a[i]);const best=Math.max(0,a.npv,b.npv),tol=1e-8;const winners=[];if(Math.abs(best)<tol)winners.push('不投资');if(Math.abs(a.npv-best)<tol)winners.push('A');if(Math.abs(b.npv-best)<tol)winners.push('B');return {a,b,delta,deltaNpv:npv(delta,r),deltaIrr:irr(delta),winners};}
const presets={
 cafe:{title:'校园咖啡店（教学模拟）',a:series(20,7,5,2),b:series(30,9.5,5,3),labels:['A 小规模','B 较大规模'],note:'同为 5 年，万元；每年净现金流分别为 7、9.5，期末残值分别为 2、3。需求与成本暂按已知。'},
 table:{title:'教材例 2-15 · 按表 2-6',a:series(20,5.8,10),b:series(30,7.2,10),labels:['A：教材 X','B：教材 Y'],note:'按 p.40 表格：Y 每年 7.2 万元；正文算式却用了 7.8，需区分。'},
 worked:{title:'教材例 2-15 · 按正文算式',a:series(20,5.8,10),b:series(30,7.8,10),labels:['A：教材 X','B：教材 Y'],note:'按 p.40—41 正文：Y 每年 7.8 万元。本工具不把该数值当作已证实的勘误。'}
};
const timingFlows=[7000,9016,10850,12516,14000,15316];
function timing(r){rate(r);const values=timingFlows.map((v,t)=>v/(1+r)**t),best=Math.max(...values);return {values,years:values.map((v,t)=>Math.abs(v-best)<1e-7?t:-1).filter(t=>t>=0)};}
const api={npv,pvRows,annuityFactor,series,irr,payback,metrics,breakEven,portfolio,greedy,budgetProjects,compare,presets,timing,timingFlows};
if(typeof module!=='undefined'&&module.exports)module.exports=api;root.Ch2Model=api;
})(typeof globalThis!=='undefined'?globalThis:this);
