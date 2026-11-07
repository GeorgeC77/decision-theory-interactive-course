const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const M=require('../course-site/dist/assets/model.js');
const near=(a,b)=>assert.ok(Math.abs(a-b)<1e-8,`${a} != ${b}`);
const basic=M.carModel({oil:4,saving:40,burden:12.2});
near(basic.originalFuel,219);near(basic.shockedFuel,876);near(basic.newFuel,525.6);near(basic.maxPrice,3472);
near(M.carModel({oil:4,saving:40,burden:12.19}).maxPrice,3467);
assert.equal(M.carModel({oil:6,saving:0,burden:5}).feasible,false);
let carCases=0;for(const oil of [1,4,6])for(const saving of [0,40,80])for(const burden of [5,12.2,25]){const r=M.carModel({oil,saving,burden});near(r.maxPrice/5+r.newFuel,r.allowedAnnual);assert.equal(r.feasible,r.maxPrice>=0);carCases++;}
assert.ok(M.carModel({oil:4,saving:60,burden:12.2}).maxPrice>basic.maxPrice);
assert.ok(M.carModel({oil:5,saving:40,burden:12.2}).maxPrice<basic.maxPrice);
for(const input of [{oil:0,saving:40,burden:12.2},{oil:4,saving:101,burden:12.2},{oil:4,saving:40,burden:NaN}])assert.throws(()=>M.carModel(input));
let scenarios=0;for(const information of ['known','risk','unknown'])for(const multi of [false,true])for(const staged of [false,true])for(const strategic of [false,true]){const r=M.classify({information,multi,staged,strategic});assert.equal(r.tags.length,3);assert.equal(r.tags[1],multi?'多目标':'单目标');assert.equal(r.tags[2],staged?'序贯':'单项');assert.ok(r.explanation.length>15);scenarios++;}
assert.throws(()=>M.classify({information:'invalid',multi:false,staged:false,strategic:false}));
assert.equal(M.gradeQuiz([1,1,0,1,1]).score,5);assert.equal(M.gradeQuiz([1,1,null,1,1]).complete,false);
assert.equal(M.elements.length,6);assert.equal(M.principles.length,9);assert.equal(M.taxonomy.length,8);assert.equal(M.steps.length,5);assert.equal(M.canvas.length,10);
const slides=JSON.parse(fs.readFileSync(path.join(__dirname,'../content/chapter-01-slides.json'),'utf8'));
assert.equal(slides.length,30);assert.equal(slides.filter(s=>s.appendix).length,6);
console.log(JSON.stringify({car_parameter_cases:carCases,classification_cases:scenarios,default_price:basic.maxPrice,slides:slides.length,status:'passed'},null,2));
