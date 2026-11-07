const assert=require('node:assert/strict');
const fs=require('node:fs');
const M=require('../course-site/dist/assets/ch2-model.js');
let checks=0;const near=(a,b,t=1e-8)=>{assert.ok(Math.abs(a-b)<t,`${a} != ${b}`);checks++;};
near(M.npv([-100,110],.1),0);near(M.npv([-100,60,60],.1),4.13223140495866);
near(M.npv([-20,7,7,7,7,9],0),17);near(M.annuityFactor(0,5),5);
for(const r of [0,1e-12,.05,.15,.4])for(const n of [1,2,5,30])near(M.annuityFactor(r,n),Array.from({length:n},(_,i)=>(1+r)**(-i-1)).reduce((a,b)=>a+b,0),1e-7);
assert.deepEqual(M.series(100,10,4,5,-1),[-100,10,9,8,12]);checks++;
near(M.irr([-100,110]).value,.1);near(M.irr([-100,50]).value,-.5);near(M.irr([-100,20,30,20,40,40]).value,.13473216365726992);
for(const fs of [[-100,230,-132],[100,100],[-100,0,0]]){assert.equal(M.irr(fs).value,null);checks++;}
near(M.npv([-100,230,-132],.1),0);near(M.npv([-100,230,-132],.2),0);
for(const [name,p] of Object.entries(M.presets)){for(const cf of [p.a,p.b]){const ir=M.irr(cf).value;near(M.npv(cf,ir),0,1e-7);}for(const r of [0,.08,.12,.4]){const v=M.compare(name,r);near(v.deltaNpv,v.b.npv-v.a.npv);}}
near(M.compare('cafe',.08).a.npv,9.3101366536141);near(M.compare('cafe',.08).b.npv,9.972494943343067);
assert.deepEqual(M.compare('table',.12).winners,['A']);assert.deepEqual(M.compare('worked',.12).winners,['B']);assert.deepEqual(M.compare('cafe',.4).winners,['不投资']);checks+=3;
near(M.payback([-20,7,7,7,7,9]),20/7);near(M.payback([-20,7,7,7,7,9],.08),3.380999314285715);assert.equal(M.payback([-100,10,10]),null);checks++;
near(M.payback([-6000,-4000,3000,3500,5000,4500,4000]),3.7);
const base={price:18,variable:6,fixed:24000,capacity:4000,quantity:3000,target:12000};let b=M.breakEven(base);near(b.breakEven,2000);near(b.targetQuantity,3000);near(b.profit,12000);
assert.equal(M.breakEven({...base,capacity:1800}).reachable,false);assert.equal(M.breakEven({...base,price:6}).breakEven,null);assert.equal(M.breakEven({...base,price:5}).breakEven,null);assert.equal(M.breakEven({...base,fixed:0,price:6}).breakEven,0);assert.equal(M.breakEven({...base,capacity:0}).overCapacity,true);checks+=5;
// Independent dynamic programming cross-check for all budget-slider values.
for(let budget=0;budget<=1000;budget+=10){const dp=Array(budget+1).fill(0);for(const p of M.budgetProjects)for(let c=budget;c>=p.cost;c--)dp[c]=Math.max(dp[c],dp[c-p.cost]+p.value);const result=M.portfolio(budget);near(result.best.value,dp[budget],1e-7);assert.ok(result.best.cost<=budget);checks++;}
assert.deepEqual(M.portfolio(600).best.ids,['A','B','E','H']);near(M.portfolio(600).best.value,259.6);near(M.greedy(600).value,257.7);near(M.greedy(600,'npv').value,189.8);
assert.deepEqual(M.timing(.1).years,[4]);assert.deepEqual(M.timing(0).years,[5]);checks+=2;
near(M.npv(M.series(250,43,15,20),.1),81.84925975864273);near(M.npv([-48,13.8,13.8,13.8,25.8],.12),1.5416379243023641);
for(const fn of [()=>M.npv([-100,100],-1),()=>M.npv([-100,NaN],.1),()=>M.series(1,1,1.5),()=>M.series(1,1,0),()=>M.portfolio(-1),()=>M.breakEven({...base,price:-1})]){assert.throws(fn);checks++;}
// Static contract: every literal DOM reference must exist in authored HTML.
const html=fs.readFileSync('course-site/dist/ch2/index.html','utf8'),js=fs.readFileSync('course-site/dist/assets/ch2.js','utf8');
const ids=new Set([...html.matchAll(/\bid="([^"]+)"/g)].map(x=>x[1]));
for(const m of js.matchAll(/\$\('([^']+)'\)/g)){assert.ok(ids.has(m[1]),'Missing element: '+m[1]);checks++;}
console.log(JSON.stringify({chapter:2,checks,status:'passed',budgetIndependentCheck:'dynamic programming for 101 budgets'}));
