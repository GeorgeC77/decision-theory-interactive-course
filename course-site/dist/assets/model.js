(function(root){
'use strict';
const elements=[
 {key:'actor',name:'决策者',text:'创业团队代表学校运营这家咖啡店，并负责作出选择。',explain:'决策者是作出选择并承担相应责任的主体；可以是个人，也可以是群体。'},
 {key:'goal',name:'决策目标',text:'在可持续经营的前提下，提高师生购买咖啡的便利程度。',explain:'目标描述希望达到的状态；尚未给出具体的比较规则。'},
 {key:'action',name:'决策方案',text:'开固定小店、设置移动售卖点，或者暂缓投资。',explain:'方案是决策者可选择的行动。暂缓或维持现状也可以是备选方案。'},
 {key:'state',name:'自然状态',text:'新学期的实际需求可能高，也可能低。',explain:'在本模型里，需求状态不能由团队直接指定；它与团队选择的行动不同。'},
 {key:'result',name:'决策结果',text:'在低需求状态下，固定小店可能出现经营亏损。',explain:'结果由方案和状态共同决定。此处是结果描述，尚不是评价它的准则。'},
 {key:'criterion',name:'决策准则',text:'在满足预算与场地约束的方案中，优先选择预期净收益较高者。',explain:'准则说明用什么价值标准比较方案。此示例需要后续概率与收益估计支撑。'}
];
const taxonomy=[['决策主体的身份','个人决策 / 组织决策','看所服务的目标与身份，不只看签字人数。'],['问题性质','战略 / 管理 / 业务决策','长期方向、组织资源、日常运作。'],['重复性与规范性','程序化 / 非程序化','是否有成熟的常规处理程序；与是否使用代码不同。'],['自然状态与信息','确定型 / 非确定型','教材在非确定型下区分竞争型、风险型、不确定型。'],['过程连续性','单项 / 序贯','一次行动，或前后相互关联的一系列行动。'],['目标数量','单目标 / 多目标','是否需要同时权衡多个目标。'],['量化程度','定性 / 定量','多数现实问题需要两者结合。'],['对象性质','政治 / 经济 / 军事 / 文化教育等','按决策所处理的领域分类。']];
const principles=[['信息准全','关键数据是否准确、充分？缺失了什么？'],['效益','方案本身和分析过程的投入产出是否合理？'],['系统','局部与整体、当前与长远利益是否协调？'],['科学','方法、数据与推理是否能够接受检验？'],['可行','资源、技术和制度条件是否允许实施？'],['选优','用什么准则比较？现实中是否采用满意标准？'],['行动','谁在何时做什么，资源从哪里来？'],['反馈','如何检查结果，何时修正或重新决策？'],['民主','是否吸收相关人员、专家与执行者的意见？']];
const steps=[['分析问题','界定现实与期望之间的差距，检验原因，避免把“排队长”直接等同于“必须扩店”。'],['确定目标','目标要有针对性、具体明确、兼顾需要与可能，并写清资源约束和目标层次。'],['拟定方案','寻找方案 → 设计实施细节 → 估计可能结果。保留可行的不同选择，不能只为既定结论找证据。'],['选择方案','依据目标和准则比较方案。可以选最优方案，也可在信息与资源限制下寻找满意方案。'],['实施方案','明确责任、资源与进度，检查执行与结果；根据反馈修订方案，必要时追踪决策。']];
const events={routine:'首先检查排班、设备和流程，属于一般执行反馈或局部修正；仅凭一个班次出餐慢，尚不足以认定需要根本性追踪决策。',environment:'客观条件发生重大变化，原选址基础失效。应回到问题与约束，重新生成和比较可行方案，属于追踪决策。',error:'原决策依据可能存在重大错误。先回溯统计口径，再更新需求估计、目标和方案；若错误足以改变方案基础，应进行追踪决策。'};
const canvas=[
 ['actor','决策者','谁有选择权？为谁的目标负责？','创业团队代表学校提出并执行方案，学校负责场地审批。'],
 ['goal','决策目标','希望改变什么？主要与次要目标是什么？','在可持续经营前提下改善购买便利性；同时控制噪声影响。'],
 ['action','备选方案','至少两个可行选择，可包含维持现状。','固定小店、移动售卖点、暂缓投资。'],
 ['state','自然状态','哪些关键条件不能由你直接指定？','高需求或低需求；期初尚无可靠概率。'],
 ['result','决策结果','说明方案在不同状态下的后果。','分别估计收益、等待时间与服务覆盖；当前数据不足，不先填写无依据的数字。'],
 ['criterion','决策准则','怎样评价和比较？说明立场与依据。','先检查预算与场地约束，再比较经营可持续性和服务效果；具体权重由相关方讨论。'],
 ['constraints','硬约束','预算、时间、场地等。','教学假设：总投资不超过 20 万元；开学前完成审批；符合场地和噪声要求。'],
 ['evidence','事实与假设','分开写已核实事实和暂定假设。','已知：本任务给定预算约束。假设：售卖点可获审批，需求分为高低两种。需实际核实。'],
 ['gaps','信息缺口','最值得收集哪些证据？','分时段独立客流、购买意愿、租金报价、审批条件及周边替代服务。'],
 ['triggers','追踪触发条件','写两条可观察的变化，并说明回到哪一步。','场地被取消：回到问题与约束；发现客流统计重大重复计数：回溯数据并重估方案结果。']
];
const quiz=[
 {q:'“开固定店”与“下学期需求低”分别属于什么？',options:['都是决策方案','方案与自然状态','目标与准则'],correct:1,explain:'固定店是可选择的行动；在这里需求是模型中不能直接指定的外部状态。'},
 {q:'一个新型选址问题由 AI 生成代码求解，因此它一定是程序化决策。',options:['正确，用了程序就属于程序化','错误，要看是否重复且有规范流程'],correct:1,explain:'教材的“程序化”依据重复性和处理程序规范性分类，与是否写代码不同。'},
 {q:'开店既考虑利润又考虑便利性，并先试营业再扩张，可以同时属于：',options:['多目标与序贯决策','只属于多目标','只属于序贯'],correct:0,explain:'目标数量与过程连续性是不同维度，标签可以同时成立。'},
 {q:'场地政策改变，使原址无法继续使用。最需要做的是：',options:['因已经投入很多而保持原计划','重新审视约束并开展追踪决策','只增加广告投入'],correct:1,explain:'客观条件发生重大变化，需要回溯原依据，比较在当前约束下的新方案。'},
 {q:'油价与油耗数据算得很精确，就能证明汽车开发方案一定成功。',options:['正确，精确计算足够','错误，还要检验假设、可行性和市场反应'],correct:1,explain:'定量结论以模型和输入为条件，必须与定性分析及实施反馈结合。'}
];
function classify(s){if(!['known','risk','unknown'].includes(s.information))throw Error('无效的信息类型');for(const k of ['multi','staged','strategic'])if(typeof s[k]!=='boolean')throw Error('情境开关必须为布尔值');const names={known:'确定型',risk:'风险型',unknown:'不确定型'};const desc={known:'在所设模型中，方案对应结果已确定，可以直接比较可行方案。',risk:'存在多个可能状态，并有可用概率信息；可考虑期望值、决策树和效用分析。',unknown:'存在多个可能状态，但缺乏可靠概率；需要声明采用哪种不确定型准则。'};let tags=[s.strategic?'竞争型（策略互动）':names[s.information],s.multi?'多目标':'单目标',s.staged?'序贯':'单项'];let methods=[s.strategic?'竞争者的回应需要显式建模，联系教材第七章。':s.information==='known'?'连接第二章：确定型比较。':s.information==='risk'?'连接第三章：风险与信息分析。':'连接第四章：准则与立场。'];if(s.multi)methods.push('第五章：指标体系与多目标权衡。');if(s.staged)methods.push('第六章：观察后的条件行动。');return{tags,explanation:s.strategic?'竞争者的行动会影响结果，不能把主动回应简单当作固定自然状态。关于客流的信息仍是：'+names[s.information]+'情境。':desc[s.information],methods:methods.join(' '),caveat:'分类用于识别模型结构，不自动决定最优行动。概率可估计也不代表估计完全可靠。'};}
function carModel({oil,saving,burden}){if(!Number.isFinite(oil)||oil<1||oil>6||!Number.isFinite(saving)||saving<0||saving>80||!Number.isFinite(burden)||burden<5||burden>25)throw Error('参数超出实验范围');const income=10000,life=5;const originalFuel=365*3*.2;const shockedFuel=originalFuel*oil;const newFuel=shockedFuel*(1-saving/100);const allowedAnnual=income*burden/100;const maxPrice=life*(allowedAnnual-newFuel);return{originalFuel,shockedFuel,newFuel,allowedAnnual,maxPrice,feasible:maxPrice>=0,baseCarPercent:10,baseFuelPercent:originalFuel/income*100,shockFuelPercent:shockedFuel/income*100,newFuelPercent:newFuel/income*100,newCarPercent:Math.max(0,(allowedAnnual-newFuel)/income*100)};}
function gradeQuiz(answers){if(!Array.isArray(answers)||answers.length!==quiz.length)throw Error('答案数量不正确');return{score:answers.reduce((n,a,i)=>n+(a===quiz[i].correct?1:0),0),total:quiz.length,complete:answers.every((a,i)=>Number.isInteger(a)&&a>=0&&a<quiz[i].options.length)};}
const api={elements,taxonomy,principles,steps,events,canvas,quiz,classify,carModel,gradeQuiz};root.CourseModel=api;if(typeof module!=='undefined'&&module.exports)module.exports=api;
})(typeof globalThis!=='undefined'?globalThis:this);
