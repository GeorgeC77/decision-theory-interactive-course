const assert=require('node:assert/strict'),M=require('../course-site/dist/assets/ch3-model.js');let count=0;
function close(x,y,eps=1e-8){assert.ok(Math.abs(x-y)<eps,`${x} != ${y}`);count++;}
let r=M.evaluate(M.cafe,[.6,.4]);r.ev.forEach((v,i)=>close(v,[0,5.6,7.2][i]));close(r.evpi,3.2);close(Math.min(...r.eol),r.evpi);close(r.loss[2],.4);
r=M.bayes(M.cafe,[.6,.4],[[.8,.2],[.2,.8]],.5);close(r.reports[0].mass,.56);close(r.reports[0].posterior[0],6/7);close(r.reports[1].posterior[0],3/11);close(r.gross,8.8);close(r.evsi,1.6);close(r.increment,1.1);
// Independent textbook fixtures (3-9, 3-10, comprehensive production, oil case).
r=M.bayes([[15,1,-6],[0,0,0]],[.25,.3,.45],[[.65,.25,.1],[.25,.45,.15],[.1,.3,.75]],.6);close(r.gross,2.91);close(r.net,2.31);
r=M.bayes([[15000,-5000],[0,0]],[.8,.2],[[.95,.1],[.05,.9]]);close(r.gross,11300);close(r.evsi,300);close(r.prior.evpi,1000);
r=M.bayes([[40000,20000,-30000],[30000,30000,-20000],[10000,10000,10000]],[.6,.3,.1],[[.6,.2,.2],[.3,.6,.3],[.1,.2,.5]],500);close(r.gross,27800);close(r.evsi,800);close(r.net,27300);
r=M.bayes([[100,-30],[20,10]],[.3,.7],[[.8,.4],[.2,.6]],5);close(r.gross,21);close(r.increment,3);close(r.prior.evpi,24);
// Information properties across extreme and interior priors/likelihoods.
for(let p=0;p<=10;p++)for(let s=0;s<=10;s++)for(let t=0;t<=10;t++){
 const b=M.bayes(M.cafe,[p/10,1-p/10],[[s/10,1-t/10],[1-s/10,t/10]],.5);assert.ok(b.evsi>=-1e-8&&b.evsi<=b.prior.evpi+1e-8);count++;
 close(b.reports.reduce((z,x)=>z+x.mass,0),1);b.reports.filter(x=>x.posterior).forEach(x=>close(x.posterior.reduce((z,v)=>z+v,0),1));
 if(s===t&&s===10)close(b.evsi,b.prior.evpi);if(s+t===10)close(b.evsi,0);
}
r=M.bayes(M.cafe,[.6,.4],[[0,0],[1,1]]);assert.equal(r.reports[0].posterior,null);assert.equal(r.reports[0].best,null);
r=M.tree(210);close(r.expand,693);close(r.stayGood,359.1);close(r.stayBad,54.6);close(r.medium,551.75);close(r.small,519.9);assert.deepEqual(M.tree(100).root.indices,[1]);assert.deepEqual(M.tree(600).late.indices,[1]);close(M.tree(543.9).expand,359.1);
for(const k of [-5,-3,-.1,0,.1,3,5]){r=M.utilityChoice(k);close(M.utility(-10,k),0);close(M.utility(20,k),1);close(r.ce[0],5);r.points.forEach(([x,u])=>close(M.inverse(u,k),x));if(k>0)assert.ok(r.ce[1]<5);if(k<0)assert.ok(r.ce[1]>5);if(k===0)close(r.ce[1],5);}
// Enumerate all 2^n observation sequences independently of binomial formula.
for(let n=0;n<=9;n++){let gross=0;for(let mask=0;mask<2**n;mask++){let joint=[.5,.3,.2];for(let t=0;t<n;t++)joint=joint.map((x,i)=>x*((mask>>t)&1?[.2,.1,.05][i]:1-[.2,.1,.05][i]));gross+=Math.max(0,joint[0]*-5+joint[1]*5+joint[2]*10);}close(M.sampling(n).gross,gross);}
close(M.sampling(4).evsi,.5891625);close(M.sampling(0,10,10).cost,0);for(let n=0;n<=40;n++)close(M.sampling(n).reports.reduce((s,x)=>s+x.mass,0),1);
r=M.simulate(M.cafe,[.6,.4],1000,2026);assert.deepEqual(r,M.simulate(M.cafe,[.6,.4],1000,2026));close(r.counts.reduce((x,y)=>x+y),1000);r.means.forEach((x,i)=>close(x,(r.counts[0]*M.cafe[i][0]+r.counts[1]*M.cafe[i][1])/1000));close(M.simulate(M.cafe,[0,1],10,0).means[2],-6);
assert.throws(()=>M.evaluate(M.cafe,[.6,.5]));assert.throws(()=>M.evaluate([[1]],[.5,.5]));assert.throws(()=>M.sampling(4.5));assert.throws(()=>M.bayes(M.cafe,[.6,.4],[[.8,.2],[.8,.8]]));assert.throws(()=>M.utility(21,3));assert.throws(()=>M.simulate(M.cafe,[.6,.4],1,-1));
close(M.sensitivity([[50,-20],[-15,100]])[0].hi,24/37);
console.log(`Chapter 3 mathematical checks passed (${count} numeric/property checks plus assertions).`);
