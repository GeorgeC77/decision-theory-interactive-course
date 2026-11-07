const assert=require('node:assert/strict'),M=require('../course-site/dist/assets/ch4-model.js');let checks=0;
const close=(a,b)=>{assert.ok(Math.abs(a-b)<1e-7,`${a} != ${b}`);checks++;},eq=(a,b)=>{assert.deepEqual(a,b);checks++;};
let r=M.evaluate(M.presets.cafe.matrix);eq(Object.values(r.criteria).map(c=>c.indices),[[2],[0],[2],[1],[1]]);eq(r.baseline,[20,7,2]);eq(r.regrets,[[14,2,0],[8,0,4],[0,1,12],[20,7,2]]);close(r.criteria.hurwicz.value,8);close(r.criteria.laplace.value,17/3);
eq(M.evaluate(M.presets.cafe.matrix,'benefit',.4).criteria.hurwicz.indices,[0,1]);eq(M.evaluate(M.presets.cafe.matrix,'benefit',.5).criteria.hurwicz.indices,[1,2]);eq(M.frontier(M.presets.cafe.matrix).points.map(p=>p.alpha),[0,.4,.5,1]);
const w=M.presets.watch.matrix;eq(M.frontier(w).points.map(x=>x.alpha),[0,.5,2/3,1]);eq(M.evaluate(w,'benefit',0).criteria.hurwicz.indices,[0,3]);eq(M.evaluate(w,'benefit',.5).criteria.hurwicz.indices,[0,2]);eq(M.evaluate(w,'benefit',2/3).criteria.hurwicz.indices,[1,2]);close(M.evaluate(w,'benefit',.7).criteria.hurwicz.value,3600);
r=M.evaluate(M.presets.cost.matrix,'cost');eq(r.baseline,[21,24,20]);eq(r.criteria.regret.scores,[16,20,17]);eq(r.criteria.optimistic.indices,[0]);eq(r.criteria.pessimistic.indices,[2]);eq(r.criteria.regret.indices,[0]);
r=M.evaluate(M.presets.regret.matrix);eq(r.criteria.regret.scores,[160,170,180]);eq(r.criteria.regret.indices,[0]);r=M.evaluate(M.presets.equal.matrix);eq(r.criteria.laplace.scores,[8.75,25,10]);
r=M.evaluate(M.presets.auto.matrix,'benefit',.7);r.criteria.hurwicz.scores.forEach((x,i)=>close(x,[30218,25865,30978][i]));eq(r.criteria.regret.scores,[3200,7590,200]);
// Build the bookshop matrix independently from sales, procurement, and salvage cash flows.
const q=[50,100,150,200],book=q.map(n=>q.map(d=>8*Math.min(n,d)+2*Math.max(0,n-d)-5*n));eq(book,M.presets.books.matrix);r=M.evaluate(book);eq(r.criteria.laplace.indices,[1,2]);eq(r.criteria.regret.indices,[1,2]);eq(r.criteria.regret.scores,[450,300,300,450]);
const ex45=[[152,70,-60,-150],[100,45,-13,-53],[118,63,-45,-98]];r=M.evaluate(ex45,'benefit',.65);r.criteria.hurwicz.scores.forEach((v,i)=>close(v,[46.3,46.45,42.4][i]));eq(r.criteria.hurwicz.indices,[1]);eq(r.criteria.regret.scores,[97,52,45]);eq(r.criteria.regret.indices,[2]);eq(r.criteria.laplace.scores,[3,19.75,9.5]);
const before=M.evaluate(M.presets.partition.matrix),after=M.evaluate(M.presets.split.matrix);eq(before.criteria.laplace.indices,[0]);eq(after.criteria.laplace.indices,[1]);for(const k of ['optimistic','pessimistic','hurwicz','regret'])eq(before.criteria[k].indices,after.criteria[k].indices);eq(before.criteria.regret.indices,[0]);eq(M.evaluate(M.presets.alternative.matrix).criteria.regret.indices,[1]);
// Model invariants for all supplied cases and both semantics across alpha.
for(const p of Object.values(M.presets))for(const kind of ['benefit','cost'])for(let i=0;i<=20;i++){
 const a=p.matrix,alpha=i/20,x=M.evaluate(a,kind,alpha),neg=M.evaluate(a.map(r=>r.map(v=>-v)),kind==='benefit'?'cost':'benefit',alpha),perm=M.evaluate(a.map(r=>[...r].reverse()),kind,alpha),affine=M.evaluate(a.map(r=>r.map(v=>3*v+7)),kind,alpha);
 for(const k of Object.keys(x.criteria)){eq(x.criteria[k].indices,neg.criteria[k].indices);eq(x.criteria[k].indices,perm.criteria[k].indices);eq(x.criteria[k].indices,affine.criteria[k].indices);}
 for(let j=0;j<a[0].length;j++){close(Math.min(...x.regrets.map(r=>r[j])),0);assert.ok(x.regrets.every(r=>r[j]>=0));}
 if(i===0)eq(x.criteria.hurwicz.indices,x.criteria.pessimistic.indices);if(i===20)eq(x.criteria.hurwicz.indices,x.criteria.optimistic.indices);
 const f=M.frontier(a,kind);for(const seg of f.segments){const mid=(seg.lo+seg.hi)/2;eq(seg.indices,M.evaluate(a,kind,mid).criteria.hurwicz.indices);}
}
eq(M.evaluate([[0,0],[0,0]]).criteria.regret.indices,[0,1]);eq(M.frontier([[1,1],[1,1]]).segments[0].indices,[0,1]);eq(M.evaluate([[1],[2]]).criteria.regret.indices,[1]);eq(M.best([1e9,1e9-.1]).indices,[0]);
for(const bad of [[],[[1],[1,2]],[[NaN]],[[Infinity]],[[1e10]]])assert.throws(()=>M.evaluate(bad));assert.throws(()=>M.evaluate([[1]],'benefit',1.01));assert.throws(()=>M.evaluate([[1]],'wrong',.5));
console.log(JSON.stringify({chapter:4,checks,status:'passed',cases:Object.keys(M.presets).length}));
