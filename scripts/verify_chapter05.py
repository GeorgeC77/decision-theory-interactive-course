"""Cross-check the browser-independent JS models against NumPy/SciPy.
No browser/DOM testing. Deterministic fixtures include degeneracy and edge cases.
"""
from pathlib import Path
import json,subprocess,copy
import numpy as np
from chapter05_reference import ahp,dea,gp
R=Path(__file__).resolve().parents[1];rng=np.random.default_rng(20260917)
fixtures={'ahp':[],'dea':[],'gp':[]}
for n in [3,4]:
    for k in range(16):
        A=np.ones((n,n))
        for i in range(n):
            for j in range(i+1,n):A[i,j]=float(rng.choice([1/9,1/5,1/3,1/2,1,2,3,5,9]));A[j,i]=1/A[i,j]
        fixtures['ahp'].append(A.tolist())
for data in [[[1,3,1],[3,1,1],[3,3,2],[4,2,1]],[[1,1,1],[1,2,1],[2,1,1],[2,2,1]],[[1,1,1]]*4]+[rng.uniform(.1,40,size=(4,3)).round(3).tolist()for _ in range(20)]:
    for bcc in [False,True]:
        for o in range(4):fixtures['dea'].append({'data':data,'o':o,'bcc':bcc})
textile={'hard':[{'a':[1,0],'b':70},{'a':[0,1],'b':45},{'a':[1,1],'b':115}], 'goals':[{'a':[1,1],'target':80,'mode':'under','priority':1,'weight':1},{'a':[1,1],'target':90,'mode':'over','priority':2,'weight':1},{'a':[1,0],'target':70,'mode':'under','priority':3,'weight':5},{'a':[0,1],'target':45,'mode':'under','priority':3,'weight':3},{'a':[1,1],'target':80,'mode':'over','priority':4,'weight':1}]}
for mode in ['lex','weighted']:
    for k in range(25):
        cfg=copy.deepcopy(textile);cfg['mode']=mode
        if k:
            cfg['hard'][2]['b']=float(rng.integers(30,121))
            for g in cfg['goals']:
                g['target']=float(rng.integers(0,131));g['priority']=int(rng.integers(1,5));g['weight']=float(rng.integers(1,10));g['mode']=str(rng.choice(['under','over','exact']))
        fixtures['gp'].append(cfg)
bad=copy.deepcopy(textile);bad['hard'][0]['b']=-1;fixtures['gp'].append(bad)
source="""const fs=require('fs'),m=require('./course-site/dist/assets/ch5-model.js'),f=JSON.parse(fs.readFileSync(0,'utf8'));process.stdout.write(JSON.stringify({ahp:f.ahp.map(a=>m.ahp(a)),dea:f.dea.map(x=>m.dea(x.data,x.o,x.bcc)),gp:f.gp.map(x=>m.gp(x))}));"""
p=subprocess.run(['node','-e',source],cwd=R,input=json.dumps(fixtures),capture_output=True,text=True,encoding='utf-8',check=True);out=json.loads(p.stdout);checks=0
def near(a,b,tol=2e-6):
    global checks
    np.testing.assert_allclose(a,b,rtol=tol,atol=tol);checks+=1
for A,r in zip(fixtures['ahp'],out['ahp']):
    ref=ahp(A);near(r['weights'],ref['weights']);near(r['lambda'],ref['lambda_max']);near(r['cr'],ref['cr'])
for f,r in zip(fixtures['dea'],out['dea']):
    ref=dea(f['data'],f['o'],f['bcc']);near(r['theta'],ref['theta']);near(r['normalizedSlack'],ref['normalizedSlack'])
    D=np.array(f['data']);target=D.T@r['lambda'];near(target,r['target']);assert np.all(target[:2]<=r['theta']*D[f['o'],:2]+1e-6);assert target[2]>=D[f['o'],2]-1e-6
    if f['bcc']:near(sum(r['lambda']),1)
for f,r in zip(fixtures['gp'],out['gp']):
    ref=gp(f);assert r['feasible']==ref['feasible'];checks+=1
    if r['feasible']:near(r['vector'],ref['vector']);assert all(np.dot(h['a'],r['p'])<=h['b']+1e-6 for h in f['hard'])
js="""const m=require('./course-site/dist/assets/ch5-model.js'),assert=require('assert');let checks=0;const near=(a,b)=>{assert(Math.abs(a-b)<1e-7);checks++;};
for(let k=0;k<=20;k++)for(let j=0;j<=20;j++)for(const rule of ['add','distance','replace','product','mixed']){const v=m.combine(k/20,j/20,rule,.6);assert(v>=-1e-10&&v<=1+1e-10);if(k<20)assert(m.combine((k+1)/20,j/20,rule,.6)>=v-1e-10);checks++;}
for(const rule of ['add','distance','replace','product','mixed']){near(m.combine(0,0,rule),0);near(m.combine(1,1,rule),1);}
const r=m.scoreLocations(m.presets.locations);near(r.scores[0],.6533333333333333);near(r.scores[1],.67);assert.deepEqual(r.winners,[1]);
const b=m.scoreLocations(m.presets.locations,13/29);assert.deepEqual(b.winners,[1,2]);const c=m.scoreLocations(m.presets.locations,29/45);assert.deepEqual(c.winners,[0,1]);checks+=2;
near(m.utility(30,0,15),1);near(m.utility(15,0,12,'cost'),0);
const d=m.dea(m.presets.dea,3);near(d.theta,.6);near(d.target[0],2.4);near(d.target[1],1.2);assert(m.dea(m.presets.weak,1).weakOnly);
for(let i=0;i<4;i++){const base=m.dea(m.presets.dea,i);const changed=m.dea(m.presets.dea.map(r=>[r[0]*10,r[1]*.5,r[2]*7]),i);near(base.theta,changed.theta);}
const g=m.gp(m.presets.textile);near(g.p[0],70);near(g.p[1],20);const gw=m.gp({...m.presets.textile,mode:'weighted'});near(gw.p[0],70);near(gw.p[1],45);assert(m.gp(m.presets.exercise5).ties.length>1);
for(const f of [()=>m.ahp([[1,3],[1,1]]),()=>m.dea([[0,1,1],[1,1,1]]),()=>m.scoreLocations([[NaN,2,3],[1,2,3],[1,2,3]]),()=>m.utility(1,0,0)]){assert.throws(f);checks++;}
process.stdout.write(String(checks));"""
p=subprocess.run(['node','-e',js],cwd=R,capture_output=True,text=True,check=True);checks+=int(p.stdout)
summary={'independent_ahp_matrices':len(fixtures['ahp']),'independent_dea_models':len(fixtures['dea']),'independent_goal_programs':len(fixtures['gp']),'numeric_assertions':checks,'status':'passed','method':'JS model vs NumPy eigenvectors and SciPy HiGHS; property and boundary checks'}
(R/'tmp/chapter05-numerical-checks.json').write_text(json.dumps(summary,indent=2),encoding='utf-8');print(json.dumps(summary,indent=2))
