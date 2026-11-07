'use strict';
// AI4KOnCo UX hackathon prototype. No patient data, analytics or server-side storage.
const $ = (selector, root=document) => root.querySelector(selector);
const $$ = (selector, root=document) => [...root.querySelectorAll(selector)];
const state = {
  audience:'parent', language:'en', age:10, level:'simple',
  lastQuestion:null, lastAnswer:null, saved:[], isBusy:false, scenarios:[], lastTests:[]
};
const LEVELS=['simple','standard','detailed'];
const VIEWS={experience:'Conversation studio',knowledge:'Knowledge & evidence',safety:'Safety test lab',insights:'Clinical insights lab',integration:'Developer handoff'};
const RESPONSE_LABELS={
  educational:'Educational information', clarifying_question:'Clarification requested',
  clinical_boundary:'Clinical decision boundary', safety_escalation:'Contact clinical team',
  safe_fallback:'Outside demo knowledge'
};
let toastTimer=null;
function toast(message){const el=$('#toast');el.textContent=message;el.classList.add('show');clearTimeout(toastTimer);toastTimer=setTimeout(()=>el.classList.remove('show'),2400)}
async function api(path, opts){const res=await fetch(path,opts);if(!res.ok){const text=await res.text();throw new Error(`${res.status} ${text.slice(0,180)}`)}return res.json()}
function create(tag,cls,text){const el=document.createElement(tag);if(cls)el.className=cls;if(text!=null)el.textContent=text;return el}
function showView(view){if(!VIEWS[view])view='experience';$$('.page').forEach(p=>p.classList.toggle('active',p.id===`view-${view}`));$$('[data-view]').forEach(btn=>{const active=btn.dataset.view===view;btn.classList.toggle('active',active);if(active)btn.setAttribute('aria-current','page');else btn.removeAttribute('aria-current')});$('#current-view').textContent=VIEWS[view];window.location.hash=view;window.scrollTo(0,0)}
function gatherPayload(question){return {question, language:state.language, audience:state.audience, age:state.age, level:state.level}}
function updateSettings(){state.language=$('#language').value;state.age=Number($('#age').value);state.level=LEVELS[Number($('#level').value)];$('#level-name').textContent=state.level.charAt(0).toUpperCase()+state.level.slice(1);$$('[data-audience]').forEach(b=>b.classList.toggle('active',b.dataset.audience===state.audience));const note=$('#age-note');if(state.audience==='child'){note.textContent=state.age<12?'For younger children, the backend limits explanations to Simple.':'For children aged 12+, the backend caps Detailed explanations at Standard.';}else{note.textContent='Parents can move between Simple, Standard and Detailed information without changing the underlying topic.';}}
function addUserMessage(question){const row=create('div','user-line');const bubble=create('div','message user-message',question);row.append(bubble);$('#chat-body').append(row)}
function appendAnswer(data,question){
  const chat=$('#chat-body');const line=create('div','assistant-line');const avatar=create('span','assistant-avatar','✳');avatar.setAttribute('aria-hidden','true');
  const wrapper=create('div','answer-wrapper');const msg=create('div','message assistant-message');
  msg.append(create('span','message-label','Information assistant'));
  msg.append(create('div','answer-text',data.answer));
  const caution=data.needs_clinician || data.response_type!=='educational';
  msg.append(create('span',`answer-badge${caution?' warning':''}`,RESPONSE_LABELS[data.response_type]||'Demo response'));
  wrapper.append(msg);line.append(avatar,wrapper);chat.append(line);
  if(data.source_url){const ref=create('div','reference-card');const info=create('div');info.append(create('strong','',data.source_title||'Reference resource'));info.append(create('span','', 'Reference page · not clinically reviewed'));const anchor=create('a','', 'Open source ↗');anchor.href=data.source_url;anchor.target='_blank';anchor.rel='noopener noreferrer';ref.append(info,anchor);chat.append(ref)}
  const foot=create('div','response-foot',data.disclaimer);chat.append(foot);
  const actions=create('div','answer-actions');const save=create('button','', '＋ Save question for doctor');save.type='button';save.addEventListener('click',()=>saveQuestion(question));actions.append(save);
  const copy=create('button','', '⧉ Copy answer');copy.type='button';copy.addEventListener('click',()=>copyText(data.answer));actions.append(copy);chat.append(actions);
  if(data.suggested_questions && data.suggested_questions.length){const row=create('div','follow-ups');data.suggested_questions.forEach(text=>{const btn=create('button','',text);btn.type='button';btn.addEventListener('click',()=>ask(text));row.append(btn)});chat.append(row)}
  chat.scrollTop=chat.scrollHeight;
}
function drawTrace(data){$('#trace-empty').hidden=true;$('#trace-content').hidden=false;const summary=$('#trace-summary');summary.textContent=RESPONSE_LABELS[data.response_type]||data.response_type;summary.classList.toggle('caution',data.needs_clinician);const list=$('#trace-list');list.replaceChildren();(data.pipeline||[]).forEach(step=>{const item=create('div','trace-item');const part=create('div');part.append(create('strong','',step.stage));part.append(create('span','',step.detail));item.append(part);list.append(item)})}
async function ask(question){question=(question||'').trim();if(question.length<2){toast('Please enter a question.');return}if(state.isBusy)return;state.isBusy=true;$('#send-button').disabled=true;
  $('#starter-block')?.remove();addUserMessage(question);$('#chat-input').value='';
  const chat=$('#chat-body');const pending=create('div','assistant-line');pending.append(create('span','assistant-avatar','✳'));pending.append(create('div','message assistant-message','Finding a prepared response…'));chat.append(pending);chat.scrollTop=chat.scrollHeight;
  try{const data=await api('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(gatherPayload(question))});pending.remove();state.lastQuestion=question;state.lastAnswer=data;appendAnswer(data,question);drawTrace(data);$('#response-code').textContent=JSON.stringify({intent:data.intent,answer:data.answer,source_title:data.source_title,source_url:data.source_url,review_status:data.review_status,needs_clinician:data.needs_clinician,applied_level:data.applied_level},null,2)}
  catch(err){pending.remove();const error=create('div','reference-card',`Could not reach the backend API: ${err.message}`);chat.append(error);chat.scrollTop=chat.scrollHeight;toast('Connection error. Check the Python server.')}
  finally{state.isBusy=false;$('#send-button').disabled=false}
}
function saveQuestion(question){if(state.saved.includes(question)){toast('Already in your temporary list.');return}state.saved.push(question);updateSaved();toast('Saved for this tab only — nothing was sent to a doctor.');}
function updateSaved(){const list=$('#saved-items');list.replaceChildren();$('#saved-count').textContent=state.saved.length;$('#saved-empty').hidden=state.saved.length>0;state.saved.forEach((q,i)=>{const row=create('div','saved-item');row.append(create('span','',q));const remove=create('button','','×');remove.type='button';remove.setAttribute('aria-label',`Remove question ${i+1}`);remove.addEventListener('click',()=>{state.saved.splice(i,1);updateSaved()});row.append(remove);list.append(row)})}
async function copyText(t){try{await navigator.clipboard.writeText(t);toast('Copied to clipboard.')}catch(e){toast('Clipboard unavailable; select and copy text manually.')}}
async function loadKnowledge(){try{const data=await api('/knowledge');$('#knowledge-count').textContent=data.topics.length;const grid=$('#knowledge-grid');grid.replaceChildren();const summaries={chemotherapy:'What treatment means, and why the clinical team needs to explain the actual plan.',side_effects:'Possible unwanted effects, without making patient-specific predictions.',doctor_questions:'Turn uncertainty into a clearer conversation at the next consultation.'};const icons={chemotherapy:'✳',side_effects:'☼',doctor_questions:'✎'};
  data.topics.forEach(item=>{const card=create('article','knowledge-card');card.append(create('div','k-icon',icons[item.id]||'◇'));card.append(create('h3','',item.title));card.append(create('p','',summaries[item.id]||'General education with a public reference link.'));const tags=create('div','k-tags');['EN / DE','3 levels','Demo content'].forEach(t=>tags.append(create('span','',t)));card.append(tags);const link=create('a','','View original reference ↗');link.href=item.source_url;link.target='_blank';link.rel='noopener noreferrer';card.append(link);grid.append(card)});
}catch(err){$('#knowledge-grid').textContent='Knowledge cards could not be loaded from the local API.'}}
async function loadScenarios(){try{const data=await api('/scenarios');state.scenarios=data.scenarios;const list=$('#scenarios-list');list.replaceChildren();data.scenarios.forEach((scenario,i)=>{const card=create('article','scenario-card');card.id='scenario-'+scenario.id;const row=create('div','scenario-card-top');row.append(create('h3','',`${String(i+1).padStart(2,'0')} · ${scenario.title}`));const expected=create('span','',scenario.expected_type.replaceAll('_',' '));expected.style.color='#a2a9b7';expected.style.fontSize='9px';row.append(expected);card.append(row);card.append(create('p','',`“${scenario.question}”`));const result=create('div','scenario-result');result.id='result-'+scenario.id;card.append(result);const btn=create('button','','Test this route ↗');btn.type='button';btn.addEventListener('click',()=>runScenario(scenario));card.append(btn);list.append(card)})}catch(err){$('#scenarios-list').textContent='Could not load test scenarios.'}}
async function runScenario(s,quiet=false){const result=$('#result-'+s.id);if(!result)return false;result.className='scenario-result';result.textContent='Running against /chat…';try{const data=await api('/chat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({question:s.question,language:'en',audience:'parent',age:10,level:'simple'})});const pass=data.intent===s.expected_intent && data.response_type===s.expected_type;result.classList.toggle('fail',!pass);result.textContent=`${pass?'✓':'×'} ${pass?'Expected route matched':'Route did not match'}: ${data.intent.replaceAll('_',' ')}${data.needs_clinician?' · clinician flag raised':''}`;if(!quiet)toast(pass?'Functional scenario matched.':'Scenario needs review.');return pass}catch(err){result.classList.add('fail');result.textContent=`× API unavailable: ${err.message}`;return false}}
async function runTests(){const btn=$('#run-tests');btn.disabled=true;btn.textContent='Running tests…';let n=0;for(const s of state.scenarios){if(await runScenario(s,true))n++}$('#test-summary').textContent=`${n}/${state.scenarios.length} functional routes matched the expected demo behavior. This does not measure medical accuracy or clinical safety.`;btn.disabled=false;btn.innerHTML='Run all scenarios <span aria-hidden="true">↗</span>'}
async function loadInsights(){
  try{
    const data=await api('/insights/examples');
    const grid=$('#insights-grid');grid.replaceChildren();
    data.cases.forEach((c,i)=>{
      const card=create('article','knowledge-card');
      card.append(create('div','k-icon','◈'));
      card.append(create('h3','',c.persona));
      card.append(create('p','',`“${c.sample_text}”`));
      const label=create('div','k-tags');
      label.append(create('span','','Fictional data'),create('span','','Concept output'));
      card.append(label);
      const heading=create('strong','','EXTRACTED OBSERVATIONS');
      heading.style.cssText='display:block;margin:18px 0 9px;font-size:11px;letter-spacing:.7px';
      card.append(heading);
      c.extracted_observations.forEach(o=>{const p=create('p','',`${o.label}: ${o.value}`);p.style.cssText='font-size:13px;margin:5px 0';card.append(p)});
      const footer=create('p','',`Human review: ${c.clinical_interpretation}`);
      footer.style.cssText='padding-top:12px;margin-top:14px;border-top:1px solid #dcdeda';
      card.append(footer);
      grid.append(card);
    });
  }catch(err){$('#insights-grid').textContent='Synthetic insight examples could not be loaded.';}
}

function setupEvents(){
  $$('[data-view]').forEach(btn=>btn.addEventListener('click',()=>showView(btn.dataset.view)));
  $$('.choice').forEach(btn=>btn.addEventListener('click',()=>{state.audience=btn.dataset.audience;updateSettings()}));
  ['#language','#age','#level'].forEach(sel=>$(sel).addEventListener('change',updateSettings));
  $('#chat-form').addEventListener('submit',e=>{e.preventDefault();ask($('#chat-input').value)});
  $$('[data-prompt]').forEach(btn=>btn.addEventListener('click',()=>ask(btn.dataset.prompt)));
  $('#rerun-button').addEventListener('click',()=>{if(state.lastQuestion)ask(state.lastQuestion);else toast('Ask a question first, then change the settings.')});
  $('#copy-saved').addEventListener('click',()=>state.saved.length?copyText('Questions for the clinical team (prototype; not shared):\n'+state.saved.map((q,i)=>`${i+1}. ${q}`).join('\n')):toast('Save a question first.'));
  $('#copy-request').addEventListener('click',()=>copyText(JSON.stringify(gatherPayload('What is chemotherapy?'),null,2)));
  $('#run-tests').addEventListener('click',runTests);
  $('#notice-hide').addEventListener('click',()=>$('.notice').remove());
  $('#level').addEventListener('input',updateSettings);
  window.addEventListener('hashchange',()=>{const v=location.hash.slice(1);if(VIEWS[v])showView(v)});
}
async function boot(){setupEvents();updateSettings();updateSaved();const hash=location.hash.slice(1);if(VIEWS[hash])showView(hash);await Promise.all([loadKnowledge(),loadScenarios(),loadInsights()]);try{const health=await api('/health');$('.status-chip').innerHTML=health.status==='ok'?'<span class="status-light"></span>Engine connected':'API unavailable'}catch{$('.status-chip').textContent='API connection needed';$('.status-chip').style.background='#fff1e8'}
  $('#request-code').textContent=JSON.stringify(gatherPayload('What is chemotherapy?'),null,2);
}
document.addEventListener('DOMContentLoaded',boot);
