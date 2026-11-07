"""Independent NumPy / SciPy calculations. Run with env_Online_Lecture.
All textbook values are transcribed from printed pp.167-194.
"""
from pathlib import Path
import itertools,json,math
import numpy as np
from scipy.optimize import linprog

def stationary(P):
    P=np.array(P,float);n=len(P)
    return np.linalg.lstsq(np.vstack([P.T-np.eye(n),np.ones(n)]),np.r_[np.zeros(n),1],rcond=None)[0]

def finite_mdp(P,R,cost,horizon,beta=1,terminal=None):
    P=np.array(P,float);R=np.array(R,float);n=P.shape[1]
    # R[s,j] is earned after the transition, cost[a] is charged once in that period.
    if R.ndim==1:R=np.tile(R,(n,1))
    V=[np.zeros(n) if terminal is None else np.array(terminal,float)];pol=[]
    for _ in range(horizon):
        Q=(P*(R+beta*V[-1])[None,:,:]).sum(axis=2)-np.array(cost)[:,None]
        V.append(Q.max(axis=0));pol.append(Q.argmax(axis=0))
    return np.array(V),np.array(pol)

def enumerate_policies(P,R,cost,horizon,initial,beta=1,terminal=None):
    # Exhaust all state-contingent policies and propagate probability mass forwards.
    P=np.array(P,float);R=np.array(R,float);n=P.shape[1]
    if R.ndim==1:R=np.tile(R,(n,1))
    terminal=np.zeros(n) if terminal is None else np.array(terminal,float)
    best=-np.inf;arg=None
    for actions in itertools.product(range(len(P)),repeat=horizon*n):
        d=np.array(initial,float);v=0
        for t in range(horizon):
            a=actions[t*n:(t+1)*n];Q=np.array([P[a[s],s]for s in range(n)])
            v+=beta**t*sum(d[s]*(Q[s]@R[s]-cost[a[s]])for s in range(n));d=d@Q
        v+=beta**horizon*(d@terminal)
        if v>best+1e-10:best=v;arg=actions
    return best,arg

def group_mix(U):
    U=np.array(U,float);ar=U.mean(axis=2);geo=np.sqrt(U.prod(axis=2));v=((ar+geo)/2).mean(axis=0)
    return {'arithmetic':ar.tolist(),'geometric':geo.tolist(),'v':v.tolist(),'e':(v/v.sum()).tolist(),'order':(np.argsort(-v)+1).tolist()}

def finite_sampling(totals,prior,fee,terminal_values,N=100):
    """Without replacement; sampled units remain in the delivered box.
    State=(observed successes, observed failures). Hypergeometric posterior.
    Stopping alternatives are given by terminal_values(posterior).
    """
    V={};policy={};prob={}
    def choose(n,k):return math.comb(n,k) if 0<=k<=n else 0
    for n in range(N,-1,-1):
        for good in range(n+1):
            bad=n-good
            w=np.array([p*choose(k,good)*choose(N-k,bad)for k,p in zip(totals,prior)],float)
            if w.sum()==0:continue
            w/=w.sum();stop=terminal_values(w);opts=list(stop)
            if n<N:
                pg=sum(w[i]*(k-good)/(N-n)for i,k in enumerate(totals));prob[good,bad]=pg
                cont=-fee
                if pg>0:cont+=pg*V[good+1,bad]
                if pg<1:cont+=(1-pg)*V[good,bad+1]
                opts.append(cont)
            V[good,bad]=max(opts);policy[good,bad]=[i for i,x in enumerate(opts)if abs(x-max(opts))<1e-9]
    expected={(0,0):1.};samples=0
    for n in range(N):
        for good in range(n+1):
            state=(good,n-good);mass=expected.get(state,0)
            if mass and policy[state][0]==2:
                samples+=mass;pg=prob[state]
                for next_state,p in [((good+1,n-good),pg),((good,n-good+1),1-pg)]:expected[next_state]=expected.get(next_state,0)+mass*p
    return {'initial_value':V[0,0],'initial_actions':policy[0,0],'expected_samples':samples,'reachable_states':len(V),'after_success':{'value':V[1,0],'actions':policy[1,0]},'after_failure':{'value':V[0,1],'actions':policy[0,1]}}

def references():
    p=np.array([.4,.3,.3]);L=np.array([[.4,.3,.3],[.2,.4,.4],[.4,.5,.1]])
    payoff=np.array([[40000,20000,-30000],[30000,30000,-20000],[10000,10000,10000]])
    joint=p[:,None]*L;signal=joint.sum(axis=0);post=joint.T/signal[:,None];ev=post@payoff.T
    ex61={'signals':signal.tolist(),'posterior':post.tolist(),'branch_ev':ev.tolist(),'no_test_gross':float(max(payoff@p)),'test_gross':float(signal@ev.max(axis=1)),'test_net':float(signal@ev.max(axis=1)-600-4000),'no_test_net':11000,'outside':8000}
    # Original capital stays in its selected scheme; annual profit of ALL installed capital is reinvested.
    objective=-np.array([8000,12000,6000,9000,4000,6000,2000,3000],float)
    A=[];b=[]
    for t in range(4):
        row=np.zeros(8);row[2*t:2*t+2]=1
        for j in range(t):row[2*j:2*j+2]=[-.5,-.2]
        A.append(row);b.append(10 if t==0 else 0)
    lp=linprog(objective,A_eq=A,b_eq=b,bounds=(0,None),method='highs')
    P=np.array([[.5,.5,0],[0,.5,.5],[.75,.25,0]])
    market=np.array([[[.8,.15,.05],[.2,.45,.35],[.3,.4,.3]],[[.9,.05,.05],[.1,.8,.1],[.1,.15,.75]],[[.9,.05,.05],[.1,.8,.1],[.1,.15,.75]]])
    adv=np.array([[[.8,.2],[.4,.6]],[[.9,.1],[.7,.3]]]);V,pol=finite_mdp(adv,[100,30],[0,15],3)
    fixed=[sum(np.array([1,0])@np.linalg.matrix_power(adv[a],t)@np.array([100,30])-15*a for t in range(1,4))for a in range(2)]
    health=np.array([[.8,.1,.06,.04],[.05,.75,.15,.05],[0,.05,.75,.2],[0,0,0,1]])
    ex5=np.array([[.8,.1,.1],[.07,.9,.03],[.15,.25,.6]]);d5=np.array([.3,.45,.25])
    ex6=[np.array([[.8,.2],[.7,.3]]),np.array([[.7,.3],[.8,.2]])]
    # Exercise 7, rows = previous state; columns = resulting state.
    P7=np.array([[[.8,.2],[.4,.6]],[[.7,.3],[.5,.5]]]);R7=np.array([[200,-20],[100,-60]])
    V7,pol7=finite_mdp(P7,R7,[0,0],2)
    fixed7=[sum(np.array([0,1])@np.linalg.matrix_power(P7[a],t)@(P7[a]*R7).sum(axis=1) for t in range(2))for a in range(2)]
    long=[]
    for acts in itertools.product(range(2),repeat=2):
        Q=np.array([P7[acts[s],s]for s in range(2)]);pi=stationary(Q);long.append({'actions':acts,'average_reward':float(pi@(Q*R7).sum(axis=1))})
    g=820/7;bias=np.array([1360/7,0]);average_Q=(P7*(R7+bias)[None,:,:]).sum(axis=2)
    assert np.allclose(average_Q.max(axis=0),g+bias)
    return {'ex6_1':ex61,'ex6_2':{'allocation':lp.x.reshape(4,2).tolist(),'total_tons':float(-lp.fun)},
      'ex6_3':{'trial':11400,'direct':12000,'max_trial_cost':2400},
      'ex6_4':{'trial_utility':.6*.85*.98+.4*.6,'direct_drill_utility':.55+.45*.27,'direct_stop_utility':.68},
      'ex6_5':{'P2':(P@P).tolist(),'d1':(np.ones(3)/3@P).tolist(),'d2':(np.ones(3)/3@P@P).tolist(),'stationary':stationary(P).tolist()},
      'ex6_6_literal_matrices':{'stationary':[stationary(q).tolist()for q in market],'net_profit':[float(stationary(q)[0]*1000-c)for q,c in zip(market,[150,40,30])]},
      'ex6_7_8':{'fixed':fixed,'V':V.tolist(),'policy_remaining_horizon':pol.tolist(),'enumerated':enumerate_policies(adv,[100,30],[0,15],3,[1,0])[0]},
      'ex6_9':{'weights':stationary([[0,2/3,1/3],[.5,0,.5],[1/3,2/3,0]]).tolist()},
      'ex6_10':group_mix([[[1,5],[2,4],[3,3],[4,2],[5,1]],[[2,4],[3,1],[5,2],[4,5],[1,3]]]),
      'health_case':{'year1':(np.array([1000,2000,500,0])@health).tolist(),'year2':(np.array([1000,2000,500,0])@health@health).tolist()},
      'exercise1_independent_sampling':{'outside_profit':800,'supplier_profit':600,'expected_price_adjustment':sum(p*(8*(1-q)**2-12*2*q*(1-q)-32*q*q)for p,q in zip([.3,.4,.3],[.2,.3,.4]))},
      'exercise2':{'direct':15.4,'pilot':16.41,'survey':14.4},
      'exercise3_without_replacement':finite_sampling([10,50,90],[.2,.7,.1],2,lambda w:[0,float(w@np.array([-100,0,100]))]),
      'exercise4_without_replacement':finite_sampling([90,10],[.5,.5],.1,lambda w:[float(w[0]),float(w[1])]),
      'exercise5':{'d1':(d5@ex5).tolist(),'P2':(ex5@ex5).tolist(),'d2':(d5@ex5@ex5).tolist(),'stationary':stationary(ex5).tolist()},
      'exercise6':{'year3_profit_probability':[float((np.linalg.matrix_power(q,3))[1,0])for q in ex6]},
      'exercise7_8':{'fixed_two_year':fixed7,'adaptive_two_year':V7.tolist(),'policies':pol7.tolist(),'stationary_policies':long,'average_optimality_certificate':{'g':g,'bias':bias.tolist(),'Q_by_action_state':average_Q.tolist(),'max_residual':float(np.max(np.abs(average_Q.max(axis=0)-g-bias))) }},
      'exercise9':group_mix([[[1,4],[2,1],[3,2],[4,3]],[[3,2],[1,3],[4,1],[2,4]],[[2,4],[3,3],[1,1],[4,2]]])}

if __name__=='__main__':
    r=references();target=Path(__file__).resolve().with_name('chapter-06-reference.json') if Path(__file__).parent.name=='downloads' else Path(__file__).resolve().parents[1]/'content/chapter-06-reference.json'
    target.write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(r,ensure_ascii=True,indent=2))
