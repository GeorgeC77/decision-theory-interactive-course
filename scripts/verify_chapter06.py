"""Independent numerical checks for browser-free pure model functions."""
from pathlib import Path
import json,subprocess,itertools,math
import numpy as np
from chapter06_reference import finite_mdp,enumerate_policies,references
R=Path(__file__).resolve().parents[1];rng=np.random.default_rng(20260917)
jobs=[];expected=[]
for h in range(1,7):
    for initial in [0,1]:
        c=dict(horizon=h,initial=initial,good=float(rng.integers(0,9)),worn=float(rng.integers(0,4)),cost=float(rng.integers(0,5)),terminal=float(rng.integers(0,8)))
        best=-1e9
        for acts in itertools.product([0,1],repeat=h):
            s=initial;v=0
            for a in acts:v+=([c['good'],c['worn']][s]if a==0 else -c['cost']);s=1 if a==0 else 0
            v+=c['terminal'] if s==0 else 0;best=max(best,v)
        jobs.append(['equipment',c]);expected.append(('equipment',best))
for k in range(25):
    P=rng.dirichlet([1,1],size=(2,2)).tolist();h=2 if k%2 else 3;initial=rng.dirichlet([1,1]).tolist();rewards=rng.uniform(-50,150,2).tolist();cost=float(rng.uniform(0,40));beta=[0,.7,1][k%3];terminal=rng.uniform(-20,40,2).tolist()
    c=dict(horizon=h,initial=initial,P=P,rewards=rewards,cost=cost,beta=beta,terminal=terminal)
    best,_=enumerate_policies(P,rewards,[0,cost],h,initial,beta,terminal)
    jobs.append(['mdp',c]);expected.append(('mdp',best))
for mode in ['money','cara']:
    for p,sens,spec in [(.5,.8,.8),(0,1,1),(1,0,1),(.55,51/55,.8),(.2,.5,.5),(.8,1,1),(1e-11,.7,.6)]:
        c=dict(prior=p,sensitivity=sens,specificity=spec,revenue=40,investment=20,cost=2,mode=mode,aversion=.05)
        u=(lambda x:x)if mode=='money'else(lambda x:-math.expm1(-.05*x))
        direct=[u(0),p*u(20)+(1-p)*u(-20)];values=[]
        # Sum four joint outcome cells for each of four complete conditional plans.
        for plan in itertools.product([0,1],repeat=2):
            v=0
            for good,pg in [(1,p),(0,1-p)]:
                for signal,ps in [(0,sens if good else 1-spec),(1,1-sens if good else spec)]:
                    net=(40*good-20 if plan[signal] else 0)-2;v+=pg*ps*u(net)
            values.append(v)
        jobs.append(['trial',c]);expected.append(('trial',[*direct,max(values)]))
ballots=[['A','B','C'],['B','C','A'],['C','A','B']]
for perm in itertools.permutations(ballots):jobs.append(['vote',perm]);expected.append(('vote',None))
jobs.append(['vote',[['A','B','C']]*3]);expected.append(('consensus',None))
jobs.append(['delegation',False,40]);expected.append(('delegation',60))
jobs.append(['delegation',True,12]);expected.append(('cycle',None))
js="const M=require('./course-site/dist/assets/ch6-model.js');let s='';process.stdin.on('data',c=>s+=c);process.stdin.on('end',()=>{const jobs=JSON.parse(s);console.log(JSON.stringify(jobs.map(([fn,...args])=>M[fn](...args))))});"
p=subprocess.run(['node','-e',js],input=json.dumps(jobs),capture_output=True,text=True,cwd=R,check=True)
results=json.loads(p.stdout)
for result,(kind,value)in zip(results,expected):
    if kind=='equipment':assert abs(result['optimal']['total']-value)<1e-8
    elif kind=='mdp':
        assert abs(result['value']-value)<1e-8
        assert abs(result['forecasts'][2]['total']-value)<1e-8
        for f in result['forecasts']:
            for row in f['rows']:assert abs(sum(row['dist'])-1)<1e-9 and min(row['dist'])>=0
    elif kind=='trial':assert np.allclose(result['all'],value,rtol=1e-10,atol=1e-10)
    elif kind=='vote':assert result['cycle']and result['borda']==[6,6,6]and result['W']==0 and result['condorcet']==[]
    elif kind=='consensus':assert result['W']==1 and result['condorcet']==[0]
    elif kind=='delegation':assert np.max(np.abs(np.array(result['rows'][-1])-value))<1e-5
    elif kind=='cycle':assert result['rows'][0][0]==result['rows'][2][0]!=result['rows'][1][0]
js=r"""
const M=require('./course-site/dist/assets/ch6-model.js'),d=M.defaults,c=M.clone;
const bad=[()=>M.equipment({...d.equipment,horizon:1.5}),()=>M.equipment({...d.equipment,cost:NaN}),()=>M.trial({...d.trial,prior:1.2}),()=>M.mdp({...d.mdp,P:[[[.8,.3],[.4,.6]],d.mdp.P[1]]}),()=>M.mdp({...d.mdp,initial:[-1,2]}),()=>M.vote([['A','A','C']]),()=>M.vote([])];
bad.forEach(f=>{let threw=false;try{f()}catch(_){threw=true}if(!threw)throw Error('Invalid input accepted')});
const z=M.equipment({...d.equipment,good:0,worn:0,cost:0,terminal:0});if(z.policy.slice(1).some(row=>row.some(a=>a.length!==2)))throw Error('Equipment tie lost');
const t=M.trial({...d.trial,cost:6});if(t.choices.length!==3)throw Error('Trial threshold ties lost');
const m=M.mdp({...d.mdp,cost:0,P:[d.mdp.P[0],d.mdp.P[0]]});if(m.policy.slice(1).some(row=>row.some(a=>a.length!==2)))throw Error('MDP tie lost');
const v=M.vote([...Array(4).fill(['A','B','C']),...Array(3).fill(['B','C','A']),...Array(2).fill(['C','B','A'])]);if(v.plurality[0]!==0||v.bordaWinners[0]!==1||v.condorcet[0]!==1)throw Error('Rule comparison mismatch');
const b=M.trial({...d.trial,prior:.55,sensitivity:51/55,specificity:.8,revenue:4,investment:1,cost:.3});if(Math.abs(b.tested-1.14)>1e-9||Math.abs(b.direct[1]-1.2)>1e-9)throw Error('Book trial units');
console.log('7 invalid cases, ties, distinct voting winners and book trial passed');
"""
print(subprocess.run(['node','-e',js],capture_output=True,text=True,cwd=R,check=True).stdout.strip())
book=references();assert book['ex6_1']['test_gross']==15000 and book['ex6_2']['total_tons']==182600
assert np.allclose(book['health_case']['year2'],[801.25,1345.5,849,504.25])
assert abs(book['exercise4_without_replacement']['initial_value']-.8)<1e-10
assert book['exercise4_without_replacement']['expected_samples']==1
print('Independent cases:',len(jobs),'passed; textbook source checks passed')
