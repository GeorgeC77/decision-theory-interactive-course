const assert=require('node:assert/strict'),fs=require('node:fs'),path=require('node:path');
const {JSDOM}=require('../tmp/ch2-dom-test/node_modules/jsdom');
const M=require('../course-site/dist/assets/ch2-model.js');
let checks=0;function check(value,message){assert.ok(value,message);checks++;}
check(Math.abs(M.irr([-1000000,.0001]).value-(-.9999999999))<1e-12,'IRR near -100% must not clamp to the old bracket');
check(M.irr([-1e20,1]).value===null,'An unrepresentable IRR must not become a fabricated rate');
check(M.payback([-1e-12,1e-13])===null,'An investment still unrecovered at the horizon has no payback');
check(Math.abs(M.payback([-1e-12,2e-12])-.5)<1e-12,'Payback must not depend on currency scale');
check(M.breakEven({price:6,variable:6,fixed:0,capacity:10,quantity:2,target:0}).targetQuantity===0,'A zero profit target with zero costs is attainable');
function boot(n,deck=false,inject=false){const file=`course-site/dist/ch${n}/${deck?'slides':'index'}.html`;const dom=new JSDOM(fs.readFileSync(file,'utf8'),{url:'https://course.local/',runScripts:'outside-only'});const w=dom.window;w.URL.createObjectURL=()=> 'blob:test';w.URL.revokeObjectURL=()=>{};w.HTMLAnchorElement.prototype.click=function(){};for(const s of w.document.querySelectorAll('script[src]')){const f=path.resolve(path.dirname(file),s.getAttribute('src').split('?')[0]);w.eval(fs.readFileSync(f,'utf8'));if(inject&&/-model\.js$/.test(f)){w['Ch'+n][n===5?'scoreLocations':'equipment']=()=>{throw Error('Injected calculation failure');};}}return dom;}
for(let n=1;n<=6;n++){const dom=boot(n,true),w=dom.window,d=w.document;for(const hash of ['#1.5','#-4','#Infinity','#NaN','#999999','#2']){w.location.hash=hash;w.dispatchEvent(new w.HashChangeEvent('hashchange'));check(d.querySelectorAll('.slide.active').length===1,`ch${n}: exactly one slide for ${hash}`);}dom.window.close();}
for(const n of [5,6]){const dom=boot(n,false,true),d=dom.window.document;check(/计算暂停/.test(d.getElementById('runtime-status').textContent),`ch${n}: failed experiments must not announce ready`);check(d.getElementById(n===5?'u-results':'b-results').hidden,`ch${n}: failed result is hidden`);check(!d.getElementById(n===5?'a-results':'t-results').hidden,`ch${n}: independent experiment remains usable`);dom.window.close();}
(async()=>{
for(const n of [5,6]){
 const dom=boot(n),w=dom.window,d=w.document,$=id=>d.getElementById(id),blobs=[];
 w.URL.createObjectURL=blob=>{blobs.push(blob);return 'blob:test';};
 const input=$(n===5?'u-0-0':'b-good'),original=input.value;
 input.value='';input.dispatchEvent(new w.Event('input',{bubbles:true}));
 check(/计算暂停/.test($('runtime-status').textContent),`ch${n}: invalid input updates global status`);
 $('export-record').click();check(blobs.length===0,`ch${n}: invalid records are not exported`);
 input.value=original;input.dispatchEvent(new w.Event('input',{bubbles:true}));
 check(/四个实验已就绪/.test($('runtime-status').textContent),`ch${n}: corrected input recovers automatically`);
 $('export-record').click();check(blobs.length===1,`ch${n}: valid records export once`);
 const text=await new Promise((resolve,reject)=>{const r=new w.FileReader();r.onload=()=>resolve(r.result);r.onerror=reject;r.readAsText(blobs[0]);});
 const data=JSON.parse(text);check(data.chapter===n,`ch${n}: export chapter`);
 const fields=n===5?['utility','ahp','dea','gp']:['equipment','trial','mdp','committee','delegation'];
 for(const field of fields)check(data[field]&&typeof data[field]==='object',`ch${n}: complete exported ${field}`);
 $('quiz-form').dispatchEvent(new w.Event('submit',{bubbles:true,cancelable:true}));
 check(/0 \/ /.test($('quiz-result').textContent),`ch${n}: unanswered questions cannot earn credit`);
 const answers=n===5?[1,2,1,1,0,1,1,1]:[1,0,2,0,1,2];
 answers.forEach((v,i)=>{d.querySelector(`input[name=q${i}][value="${v}"]`).checked=true;});
 $('quiz-form').dispatchEvent(new w.Event('submit',{bubbles:true,cancelable:true}));
 check($('quiz-result').textContent.includes(`${answers.length} / ${answers.length}`),`ch${n}: fully correct quiz`);
 $('quiz-form').reset();check($('quiz-result').textContent==='',`ch${n}: quiz reset removes score`);
 if(n===6){
  let tick=null;w.setInterval=fn=>{tick=fn;return 1;};w.clearInterval=()=>{tick=null;};
  $('m-play').click();check(typeof tick==='function','MDP animation starts');
  for(let i=0;i<3;i++){const step=tick;check(typeof step==='function','MDP has a pending animation frame');step();}
  check($('m-step').value==='3'&&tick===null,'MDP stops at its horizon');
  $('m-start').click();check($('m-step').value==='0','MDP returns to initial distribution');
 }
 dom.window.close();
}
console.log(JSON.stringify({checks,status:'passed'}));
})().catch(e=>{console.error(e);process.exitCode=1;});
