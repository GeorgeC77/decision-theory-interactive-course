(function(root){'use strict';
const EPS=1e-9, clone=x=>JSON.parse(JSON.stringify(x));
function finite(x,name){if(typeof x!=='number'||!Number.isFinite(x))throw Error(name+'必须是有限数值');return x;}
function range(x,a,b,name){finite(x,name);if(x<a||x>b)throw Error(name+'须在 '+a+' 至 '+b+' 之间');return x;}
function integer(x,a,b,name){range(x,a,b,name);if(!Number.isInteger(x))throw Error(name+'须为整数');}
function winners(v){const m=Math.max(...v);return v.map((x,i)=>Math.abs(x-m)<=EPS*Math.max(1,Math.abs(m))?i:-1).filter(i=>i>=0);}
function dot(a,b){return a.reduce((s,x,i)=>s+x*b[i],0);}
function distribution(d){d.forEach(x=>range(x,0,1,'概率'));if(Math.abs(d.reduce((a,b)=>a+b,0)-1)>1e-8)throw Error('每行概率之和必须为1');}
function advance(d,P){return d.map((_,j)=>d.reduce((s,x,i)=>s+x*P[i][j],0));}
const defaults={
 equipment:{horizon:3,good:5,worn:1,cost:2,terminal:0,initial:0},
 trial:{prior:.5,sensitivity:.8,specificity:.8,revenue:40,investment:20,cost:2,mode:'money',aversion:.05},
 mdp:{horizon:3,initial:[1,0],P:[[[.8,.2],[.4,.6]],[[.9,.1],[.7,.3]]],rewards:[100,30],cost:15,beta:1,terminal:[0,0]},
 votes:[['A','B','C'],['B','C','A'],['C','A','B']]
};
function equipment(c){integer(c.horizon,1,6,'阶段数');integer(c.initial,0,1,'初始状态');['good','worn','cost','terminal'].forEach(k=>range(c[k],0,100,k));
 const V=[[c.terminal,0]],policy=[],Q=[];
 for(let h=1;h<=c.horizon;h++){const q=[0,1].map(s=>[(s===0?c.good:c.worn)+V[h-1][1],-c.cost+V[h-1][0]]);Q[h]=q;V[h]=q.map(x=>Math.max(...x));policy[h]=q.map(winners);}
 function path(greedy){let s=c.initial,total=0;const rows=[];for(let t=1;t<=c.horizon;t++){const h=c.horizon-t+1,options=greedy?winners([s===0?c.good:c.worn,-c.cost]):policy[h][s],a=options[0],r=a===0?(s===0?c.good:c.worn):-c.cost;rows.push({t,state:s,action:a,reward:r,tied:options.length>1});total+=r;s=a===0?1:0;}total+=s===0?c.terminal:0;return{rows,total,final:s};}
 return{V,Q,policy,optimal:path(false),greedy:path(true)};
}
function trial(c){['prior','sensitivity','specificity'].forEach(k=>range(c[k],0,1,k));['revenue','investment','cost'].forEach(k=>range(c[k],0,100,k));range(c.aversion,.001,.2,'风险厌恶系数');if(!['money','cara'].includes(c.mode))throw Error('未知效用模式');
 const u=x=>c.mode==='money'?x:-Math.expm1(-c.aversion*x), p=c.prior;
 const joint=[[p*c.sensitivity,(1-p)*(1-c.specificity)],[p*(1-c.sensitivity),(1-p)*c.specificity]];
 const gross=post=>[0,post*c.revenue-c.investment];
 const branch=joint.map((j,i)=>{const prob=j[0]+j[1];if(prob===0)return{signal:i,prob:0,posterior:null,choices:[],q:null};const post=j[0]/prob,q=[u(-c.cost),post*u(c.revenue-c.investment-c.cost)+(1-post)*u(-c.investment-c.cost)];return{signal:i,prob,posterior:post,q,choices:winners(q),money:gross(post)};});
 const direct=[u(0),p*u(c.revenue-c.investment)+(1-p)*u(-c.investment)];
 const tested=branch.reduce((s,b)=>s+b.prob*(b.q?Math.max(...b.q):0),0);
 const all=[...direct,tested], evsi=branch.reduce((s,b)=>s+b.prob*(b.money?Math.max(...b.money):0),0)-Math.max(...gross(p));
 const policies=[];for(let a=0;a<2;a++)for(let b=0;b<2;b++){const actions=[a,b];policies.push({actions,value:branch.reduce((s,z,i)=>s+z.prob*(z.q?z.q[actions[i]]:0),0),money:branch.reduce((s,z,i)=>s+z.prob*(z.posterior===null?0:(actions[i]?z.posterior*c.revenue-c.investment-c.cost:-c.cost)),0)});}
 return{branch,direct,tested,all,choices:winners(all),evsi,policies,mode:c.mode};
}
function mdp(c){integer(c.horizon,1,12,'期数');distribution(c.initial);if(c.initial.length!==2||c.P.length!==2)throw Error('本实验固定两个状态、两种行动');c.P.forEach(p=>{if(p.length!==2||p.some(r=>r.length!==2))throw Error('转移矩阵须为2×2');p.forEach(distribution);});c.rewards.forEach(x=>range(x,-200,200,'期末收益'));range(c.cost,0,100,'广告费');range(c.beta,0,1,'折现因子');c.terminal.forEach(x=>range(x,-200,200,'终值'));if(c.terminal.length!==2||c.rewards.length!==2)throw Error('收益和终值须有两个分量');
 const V=[c.terminal.slice()],Q=[],policy=[];
 for(let h=1;h<=c.horizon;h++){const q=[0,1].map(s=>[0,1].map(a=>dot(c.P[a][s],c.rewards.map((r,j)=>r+c.beta*V[h-1][j]))-a*c.cost));Q[h]=q;V[h]=q.map(x=>Math.max(...x));policy[h]=q.map(winners);}
 function forecast(mode){let d=c.initial.slice(),total=0;const rows=[{t:0,dist:d.slice(),reward:0}],actions=[];for(let t=1;t<=c.horizon;t++){const h=c.horizon-t+1,act=[0,1].map(s=>mode==='optimal'?policy[h][s][0]:mode),p=[0,1].map(s=>c.P[act[s]][s]),nd=advance(d,p),reward=dot(nd,c.rewards)-c.cost*dot(d,act);total+=c.beta**(t-1)*reward;actions.push(act);rows.push({t,dist:nd.slice(),reward});d=nd;}total+=c.beta**c.horizon*dot(d,c.terminal);return{rows,total,actions};}
 const forecasts=[forecast(0),forecast(1),forecast('optimal')];
 return{V,Q,policy,forecasts,value:dot(c.initial,V[c.horizon])};
}
function vote(ballots){if(ballots.length<1||ballots.length>60)throw Error('请输入1至60份排序');const names=['A','B','C'],first=[0,0,0],borda=[0,0,0],pair=names.map(()=>[0,0,0]),rankSums=[0,0,0];ballots.forEach(b=>{if(b.length!==3||new Set(b).size!==3||b.some(x=>!names.includes(x)))throw Error('每行须恰好包含 A、B、C，各一次');first[names.indexOf(b[0])]++;names.forEach((a,i)=>{const r=b.indexOf(a);borda[i]+=3-r;rankSums[i]+=r+1;names.forEach((z,j)=>{if(r<b.indexOf(z))pair[i][j]++;});});});
 const condorcet=names.map((_,i)=>i).filter(i=>names.every((_,j)=>j===i||pair[i][j]>pair[j][i]));
 const cycle=(pair[0][1]>pair[1][0]&&pair[1][2]>pair[2][1]&&pair[2][0]>pair[0][2])||(pair[1][0]>pair[0][1]&&pair[2][1]>pair[1][2]&&pair[0][2]>pair[2][0]);
 const m=ballots.length,mean=m*2,W=12*rankSums.reduce((s,r)=>s+(r-mean)**2,0)/(m*m*(27-3));
 return{first,borda,pair,condorcet,cycle,plurality:winners(first),bordaWinners:winners(borda),absolute:first.map((n,i)=>n>m/2?i:-1).filter(i=>i>=0),W,rankSums,n:m};
}
function delegation(cyclic=false,steps=12){integer(steps,0,40,'迭代次数');const P=cyclic?[[0,1,0],[1,0,0],[1,0,0]]:[[0,2/3,1/3],[.5,0,.5],[1/3,2/3,0]];let values=[20,60,100];const rows=[values.slice()];for(let t=0;t<steps;t++){values=P.map(r=>dot(r,values));rows.push(values.slice());}return{P,rows,limit:cyclic?null:60};}
const api={defaults,clone,equipment,trial,mdp,vote,delegation,advance,winners};if(typeof module!=='undefined'&&module.exports)module.exports=api;else root.Ch6=api;
})(typeof window==='undefined'?globalThis:window);
