"""Independent numerical reference. Run with env_Online_Lecture (NumPy/SciPy).
The web app uses its own small-model solver; this file verifies it independently.
"""
from pathlib import Path
import json
import numpy as np
from scipy.optimize import linprog

R=Path(__file__).resolve().parents[1]
RI={2:0,3:.52,4:.89,5:1.12}
def ahp(a):
    a=np.asarray(a,float);v,w=np.linalg.eig(a);i=np.argmax(v.real);lam=float(v[i].real);weights=w[:,i].real;weights/=weights.sum();ci=max(0,(lam-len(a))/(len(a)-1))
    return dict(weights=weights.tolist(),lambda_max=lam,ci=ci,cr=ci/RI[len(a)] if RI[len(a)] else 0)

def dea(data,o,bcc=False):
    d=np.asarray(data,float);n=len(d);x=d[:,:-1].T;y=d[:,-1:].T;m=x.shape[0]
    A=np.vstack([np.c_[x,-x[:,o]],np.c_[-y,np.zeros(1)]])
    b=np.r_[np.zeros(m),-y[:,o]]
    eq=np.array([[*np.ones(n),0]]) if bcc else None
    z=linprog(np.r_[np.zeros(n),1],A_ub=A,b_ub=b,A_eq=eq,b_eq=[1] if bcc else None,bounds=(0,None),method='highs');assert z.success,z.message
    theta=z.x[-1]
    c=(x/x[:,o,None]).sum(axis=0)-(y/y[:,o,None]).sum(axis=0)
    q=linprog(c,A_ub=np.vstack([x,-y]),b_ub=np.r_[theta*x[:,o],-y[:,o]],A_eq=np.ones((1,n)) if bcc else None,b_eq=[1] if bcc else None,bounds=(0,None),method='highs');assert q.success
    ins=theta*x[:,o]-x@q.x;outs=y@q.x-y[:,o]
    return dict(theta=float(theta),lambda_=q.x.tolist(),target=(d.T@q.x).tolist(),normalizedSlack=float(sum(ins/x[:,o])+sum(outs/y[:,o])))

def gp(cfg):
    goals=cfg['goals'];n=2+2*len(goals);A=[];b=[]
    for h in cfg['hard']:A.append(h['a']+[0]*(n-2));b.append(h['b'])
    E=[];f=[]
    for k,g in enumerate(goals):
        row=g['a']+[0]*(n-2);row[2+2*k]=1;row[3+2*k]=-1;E.append(row);f.append(g['target'])
    priorities=sorted(set(g['priority']for g in goals));vec=[]
    if cfg.get('mode','lex')=='weighted':priorities=[None]
    for p in priorities:
        c=np.zeros(n)
        for k,g in enumerate(goals):
            if p is not None and g['priority']!=p:continue
            if g['mode'] in ['under','exact']:c[2+2*k]=g['weight']
            if g['mode'] in ['over','exact']:c[3+2*k]=g['weight']
        z=linprog(c,A_ub=A,b_ub=b,A_eq=E,b_eq=f,bounds=(0,None),method='highs')
        if not z.success:return dict(feasible=False)
        vec.append(float(z.fun));E.append(c.tolist());f.append(float(z.fun))
    return dict(feasible=True,p=z.x[:2].tolist(),vector=vec)

def book_results():
    traffic=[[1,3,5,3,5],[1/3,1,3,1,3],[1/5,1/3,1,1/3,3],[1/3,1,3,1,3],[1/5,1/3,1/3,1/3,1]]
    local=[[[1,1,5],[1,1,5],[1/5,1/5,1]],[[1,3,5],[1/3,1,2],[1/5,1/2,1]],[[1,4,7],[1/4,1,4],[1/7,1/4,1]],[[1,1/2,1/3],[2,1,1],[3,1,1]],[[1,1/2,1/3],[2,1,1],[3,1,1]]]
    top=ahp(traffic);locals_=[ahp(a)for a in local];P=np.array([a['weights']for a in locals_]).T
    ex2top=ahp([[1,1/4,1/5],[4,1,2],[5,1/2,1]])
    ex2local=[ahp([[1,3,4,5,6],[1/3,1,2,4,3],[1/4,1/2,1,3,2],[1/5,1/4,1/3,1,3],[1/6,1/3,1/2,1/3,1]]),ahp([[1,1/5,1/4,1/6],[5,1,4,2],[4,1/4,1,1/2],[6,1/2,2,1]]),ahp([[1,3,2,3],[1/3,1,2,2],[1/2,1/2,1,1],[1/3,1/2,1,1]])]
    EP=np.column_stack([ex2local[0]['weights'],[0]+ex2local[1]['weights'],ex2local[2]['weights']+[0]])
    flood=np.array([[1,6,5,6,4,8,4,7],[3,7,5,6,4,2,3,8],[1,5,7,8,4,3,3,6],[1,4,7,8,5,2,3.3,6],[1,2,7,8,5,4,4,6],[1,8,5.9,4.3,6.6,7.4,7.7,2.7],[8,2.8,4,3.3,4.7,5.6,2.7,1],[6,8,1,1,1,5.3,8,1],[8,7,4,4,3,2,1,6],[2,2,7,6,5,4,8,1]])
    fw=np.array([.18,.13,.05,.09,.11,.15,.16,.07,.04,.02])
    paper=np.array([[19569,504,1952,86,1740,254],[4867,105,631,10,539.1,152],[14570,478,1334,9,9383,185.3],[10211,218,904,100,559.2,104],[10408,354,944,34,553.5,120.3],[1584,29,205,10,187.8,45.2],[4388,187,438,47,228.4,47.9],[8917,213,631,36,301.4,72]])
    X=paper[:,:4].T;Y=paper[:,4:].T;price=np.array([.11,.915,.11,1]);costs=[];radial=[]
    for o in range(8):
        c=price@X
        q=linprog(c,A_ub=-Y,b_ub=-Y[:,o],A_eq=np.ones((1,8)),b_eq=[1],bounds=(0,None),method='highs');assert q.success
        costs.append(float(q.fun/(price@X[:,o])))
        q=linprog([0]*8+[1],A_ub=np.vstack([np.c_[X,-X[:,o]],np.c_[-Y,np.zeros(2)]]),b_ub=np.r_[np.zeros(4),-Y[:,o]],A_eq=np.array([[1]*8+[0]]),b_eq=[1],bounds=(0,None),method='highs');assert q.success;radial.append(float(q.fun))
    return dict(traffic=dict(top=top,local=locals_,overall=(P@top['weights']).tolist()),exercise2=dict(top=ex2top,local=ex2local,overall=(EP@ex2top['weights']).tolist()),flood=dict(weights=fw.tolist(),scores=(fw@flood).tolist()),paper=dict(bcc_cost_efficiency=costs,bcc_radial_efficiency=radial))

if __name__=='__main__':
    out=book_results();destination=(R/'content/chapter-05-reference.json') if (R/'content').is_dir() else Path.cwd()/'chapter-05-reference.json';destination.write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(out,ensure_ascii=False,indent=2))
