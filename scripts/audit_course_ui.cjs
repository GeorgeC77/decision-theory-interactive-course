// Integration audit of real chapter scripts in jsdom; no browser rendering claim.
const {JSDOM,VirtualConsole}=require('../tmp/ch2-dom-test/node_modules/jsdom');
const fs=require('node:fs'),path=require('node:path');
const findings=[],counts={boots:0,navigation:0,selects:0,numbers:0,buttons:0,decks:0};
function boot(n,deck=false){const file=`course-site/dist/ch${n}/${deck?'slides':'index'}.html`,errors=[],vc=new VirtualConsole();vc.on('jsdomError',e=>errors.push(e.message));vc.on('error',e=>errors.push(String(e)));const dom=new JSDOM(fs.readFileSync(file,'utf8'),{url:`https://course.local/ch${n}/${deck?'slides':'index'}.html`,runScripts:'outside-only',virtualConsole:vc});const w=dom.window,d=w.document;w.URL.createObjectURL=()=> 'blob:audit';w.URL.revokeObjectURL=()=>{};const downloads=[];w.HTMLAnchorElement.prototype.click=function(){downloads.push(this.download);};for(const script of d.querySelectorAll('script[src]')){const f=path.resolve(path.dirname(file),script.getAttribute('src').split('?')[0]);try{w.eval(fs.readFileSync(f,'utf8'));}catch(e){errors.push(e.stack);}}return{dom,w,d,errors,downloads};}
function check(ctx,label){const{d,errors}=ctx;for(const e of errors.splice(0))findings.push({label,error:e});const status=d.getElementById('runtime-status');if(status&&!status.hidden&&/暂未就绪|未能|未初始化/.test(status.textContent))findings.push({label,error:status.textContent});for(const svg of d.querySelectorAll('svg')){if(svg.closest('[hidden]'))continue;for(const e of svg.querySelectorAll('*'))for(const a of e.attributes){if(['d','points','x','y','cx','cy','width','height','x1','x2','y1','y2'].includes(a.name)&&/NaN|Infinity|undefined/.test(a.value))findings.push({label,error:'Invalid SVG coordinate '+a.name+'='+a.value});}}}
function fire(ctx,e){e.dispatchEvent(new ctx.w.Event('input',{bubbles:true}));e.dispatchEvent(new ctx.w.Event('change',{bubbles:true}));}
(async()=>{for(let n=1;n<=6;n++){
 let c=boot(n);counts.boots++;check(c,`ch${n} initial`);
 for(const e of c.d.querySelectorAll('[id$="-error"]'))if(e.textContent.trim())findings.push({label:`ch${n} initial error`,error:e.textContent});
 for(const a of c.d.querySelectorAll('.side-nav a')){if(!a.hash)continue;c.w.location.hash=a.hash;c.w.dispatchEvent(new c.w.HashChangeEvent('hashchange'));check(c,`ch${n} nav ${a.hash}`);counts.navigation++;}
 // Each control starts in a clean page to keep changes independent.
 const selects=[...c.d.querySelectorAll('select[id]')].map(e=>[e.id,[...e.options].map(o=>o.value)]);
 c.dom.window.close();
 for(const[id,values]of selects){c=boot(n);for(const v of values){const e=c.d.getElementById(id);if(!e)continue;e.value=v;fire(c,e);check(c,`ch${n} ${id}=${v}`);counts.selects++;}c.dom.window.close();}
 c=boot(n);const inputs=[...c.d.querySelectorAll('input[type=number][id],input[type=range][id]')].map(e=>[e.id,e.min,e.max]);c.dom.window.close();
 for(const[id,min,max]of inputs){c=boot(n);for(const value of [...new Set([min,max].filter(x=>x!==''))]){const e=c.d.getElementById(id);if(!e)continue;e.value=value;fire(c,e);check(c,`ch${n} ${id}=${value}`);counts.numbers++;}c.dom.window.close();}
 c=boot(n);for(const b of [...c.d.querySelectorAll('button[id]')]){if(/play|fullscreen/.test(b.id))continue;try{b.click();await new Promise(r=>setTimeout(r,1));check(c,`ch${n} button ${b.id}`);}catch(e){findings.push({label:`ch${n} button ${b.id}`,error:e.stack});}counts.buttons++;}c.dom.window.close();
 c=boot(n,true);for(const id of ['next','prev','notes-button']){c.d.getElementById(id)?.click();check(c,`ch${n} deck ${id}`);}for(const key of ['End','Home','ArrowRight']){c.d.dispatchEvent(new c.w.KeyboardEvent('keydown',{key,bubbles:true}));check(c,`ch${n} deck ${key}`);}counts.decks++;c.dom.window.close();
 console.log('Audited chapter',n);
 }
const result={counts,findings};fs.mkdirSync('tmp',{recursive:true});fs.writeFileSync('tmp/course-ui-audit.json',JSON.stringify(result,null,2));console.log(JSON.stringify(result,null,2));if(findings.length)process.exitCode=1;
})().catch(e=>{console.error(e);process.exitCode=1;});
