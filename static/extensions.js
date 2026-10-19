'use strict';
// All user and model strings are rendered as text nodes, including saved case files.
let versionSequence = 0;
function currentVersion() { return state.current?.versions?.at(-1); }
function invalidated(message) {
  if (state.result) state.current.priorSummary = state.result.report.summary.statement;
  state.priorSummary = state.current.priorSummary || null;
  state.result = null; state.current.lastResult = null; state.current.excluded = [...state.excluded];
  $('#report-area').classList.add('hidden'); $('#welcome').classList.remove('hidden');
  $('#export-btn').disabled = true; $('#answer').replaceChildren();
  renderCounts(); renderSources(); syncExtendedControls(); tell(message);
}
function syncExtendedControls() {
  const ready = !!state.current;
  for (const id of ['#add-evidence-btn', '#bundle-btn', '#tour-btn', '#restore-btn']) $(id).disabled = state.busy || !ready;
  $('#print-brief-btn').disabled = state.busy || !state.result;
  if (ready) $('#scope-status').textContent = `${activeSources().length}/${state.current.sources.length} sources in scope · ${state.current.versions?.length || 0} versions in this tab`;
  document.querySelectorAll('.scope-toggle, .review-trigger, .review-save, .history-control, .export-print').forEach(node => { node.disabled = state.busy; });
  document.querySelectorAll('.review-trigger').forEach(node => { node.disabled = state.busy || !state.config?.ai_available; });
}
function recordVersion() {
  const versions = state.current.versions ||= [];
  versions.push({ id: `${Date.now()}-${++versionSequence}`, recorded_at: new Date().toISOString(),
    sources: copy(activeSources()), result: copy(state.result), annotations: {}, review: null });
  if (versions.length > 10) versions.shift();
  syncExtendedControls();
}
function smallHeading(title, note) {
  const head = el('div', 'feature-heading'); head.append(el('h2', '', title), el('p', 'muted', note)); return head;
}
function metric(value, label) { const node = el('div', 'metric'); node.append(el('strong', '', value), el('span', '', label)); return node; }
function renderEvidenceMap(target) {
  const analysis = state.result.analysis;
  target.append(smallHeading('See what supports what.', 'Each connection is a citation in this report. A source being cited often does not make it more reliable.'));
  const metrics = el('div', 'metrics');
  metrics.append(metric(`${analysis.cited_source_count}/${analysis.sources.length}`, 'sources cited'), metric(analysis.claims.length, 'report claims'), metric(analysis.single_source_claim_ids.length, 'single-source claims'));
  target.append(metrics);
  if (analysis.uncited_source_ids.length) target.append(el('p', 'notice', 'Not cited in this report: ' + analysis.uncited_source_ids.join(', ') + '. Check whether important context was missed.'));
  if (analysis.diagnostics.duplicate_body_groups.length) target.append(el('p', 'notice', 'Repeated source text detected: ' + analysis.diagnostics.duplicate_body_groups.map(ids => ids.join(' / ')).join('; ') + '. Repetition is not independent corroboration.'));
  const tableWrap = el('div', 'matrix-wrap'); const table = el('table', 'evidence-matrix');
  const caption = el('caption', 'sr-only', 'Claim-to-source citation matrix'); table.append(caption);
  const head = el('thead'); const row = el('tr'); row.append(el('th', '', 'Claim / source'));
  for (const source of analysis.sources) { const cell = el('th'); const button = el('button', 'matrix-source', source.source_id); button.addEventListener('click', () => openSource(source.source_id)); cell.append(button); row.append(cell); }
  head.append(row); table.append(head); const body = el('tbody');
  for (const claim of analysis.claims) {
    const tr = el('tr'); const title = el('th', '', claim.title); title.scope = 'row'; title.title = claim.statement; tr.append(title);
    for (const source of analysis.sources) {
      const cell = el('td'); const ref = claim.evidence.find(e => e.source_id === source.source_id);
      if (ref) { const link = el('button', 'evidence-dot', '●'); link.setAttribute('aria-label', `${claim.title}: inspect ${source.source_id}`); link.title = ref.quote; link.addEventListener('click', () => openSource(ref.source_id, ref.quote)); cell.append(link); }
      else cell.append(el('span', 'no-link', '—'));
      tr.append(cell);
    }
    body.append(tr);
  }
  table.append(body); tableWrap.append(table); target.append(tableWrap);
  const scope = el('section', 'actions'); scope.append(el('h3', '', 'Evidence sensitivity experiment'), el('p', '', 'Exclude one record, then rerun. This tests dependence on available evidence; it does not prove real-world causality. Custom subsets require Live AI. Cedar without its correction also has an authored replay.'));
  for (const source of state.current.sources) {
    const label = el('label', 'scope-row'); const checkbox = el('input', 'scope-toggle'); checkbox.type = 'checkbox'; checkbox.checked = !state.excluded.has(source.id); checkbox.disabled = state.busy;
    checkbox.addEventListener('change', () => {
      if (state.busy) return;
      if (!checkbox.checked && activeSources().length <= 1) { checkbox.checked = true; return tell('Keep at least one source in scope.', true); }
      if (checkbox.checked) state.excluded.delete(source.id); else state.excluded.add(source.id);
      invalidated('Evidence scope changed. The previous version is preserved. Investigate again to compare conclusions.');
    });
    label.append(checkbox, el('span', '', `${source.id} · ${source.title}`)); scope.append(label);
  }
  target.append(scope);
}
function sourceChanges(before, after) {
  const a = new Map(before.map(s => [s.id, s])); const b = new Map(after.map(s => [s.id, s]));
  return { added: [...b.keys()].filter(id => !a.has(id)), removed: [...a.keys()].filter(id => !b.has(id)),
    modified: [...b.keys()].filter(id => a.has(id) && !sameSources([a.get(id)], [b.get(id)])) };
}
function versionCard(version, label) {
  const node = el('article', 'version-card'); node.append(el('span', 'eyebrow', label), badge(version.result.report.summary.kind), el('h3', '', version.result.report.summary.title), el('p', '', version.result.report.summary.statement), el('small', 'muted', `${version.sources.length} sources · ${version.result.meta.model}`));
  const list = el('ul', 'version-commitments'); for (const item of version.result.report.commitments) list.append(el('li', '', `${item.owner} · ${item.status.replaceAll('_', ' ')} · ${item.promise} · prerequisite ${item.condition_status || "unknown"} · ${item.status_reason || "Not assessed"}`)); node.append(list); return node;
}
function renderHistory(target) {
  const versions = state.current.versions || [];
  target.append(smallHeading('A conclusion has a history.', 'Compare complete snapshots. Added or removed text is not automatically a new fact. Versions are retained in this tab; save a case file before reloading.'));
  if (versions.length < 2) { target.append(el('p', 'notice', 'One version so far. Add evidence or change the source scope, then investigate again to create a comparison.')); if (versions.length) target.append(versionCard(versions[0], 'CURRENT VERSION')); return; }
  const controls = el('div', 'compare-controls');
  const left = el('select', 'history-control'); left.setAttribute('aria-label', 'Earlier version'); const right = el('select', 'history-control'); right.setAttribute('aria-label', 'Later version');
  versions.forEach((version, i) => { for (const select of [left, right]) { const option = el('option', '', `Version ${i+1} · ${dateTime(version.recorded_at)}`); option.value = i; select.append(option); } });
  left.value = versions.length-2; right.value = versions.length-1; controls.append(left, el('span', '', '→'), right); target.append(controls);
  const display = el('div'); target.append(display);
  function compare() {
    display.replaceChildren(); const before = versions[Number(left.value)], after = versions[Number(right.value)];
    const change = sourceChanges(before.sources, after.sources);
    const metrics = el('div', 'metrics'); metrics.append(metric(change.added.length, 'sources added'), metric(change.removed.length, 'sources removed'), metric(change.modified.length, 'sources edited')); display.append(metrics);
    const summary = el('p', 'notice', `Summary ${before.result.report.summary.statement === after.result.report.summary.statement ? 'unchanged' : 'changed'}. Added: ${change.added.join(', ') || 'none'}. Removed: ${change.removed.join(', ') || 'none'}. Edited: ${change.modified.join(', ') || 'none'}.`); display.append(summary);
    const columns = el('div', 'compare-grid'); columns.append(versionCard(before, `VERSION ${Number(left.value)+1}`), versionCard(after, `VERSION ${Number(right.value)+1}`)); display.append(columns);
  }
  left.addEventListener('change', compare); right.addEventListener('change', compare); compare();
}
function renderReview(target) {
  const version = currentVersion();
  target.append(smallHeading('Challenge the interpretation.', 'A second AI pass checks whether the sources support each claim. Human decisions below are recorded separately and never silently rewrite the report.'));
  const header = el('section', 'review-panel'); const button = el('button', 'button primary review-trigger', version?.review ? 'Run review again ↗' : 'Run AI evidence review ↗');
  button.disabled = state.busy || !state.config.ai_available;
  button.addEventListener('click', runReview);
  header.append(button, el('p', 'muted', state.config.ai_available ? `Uses ${state.config.review_model}. Sends this report and its selected sources to the configured AI provider in a separate API call.` : 'Configure a server API key to enable semantic review. Human review works without one.'));
  target.append(header);
  if (version?.review) {
    const review = version.review; const stats = el('div', 'metrics review-metrics');
    for (const [name, count] of Object.entries(review.counts)) stats.append(metric(count, name));
    target.append(stats, el('p', 'notice', review.note));
    const claimMap = new Map(state.result.analysis.claims.map(c => [c.id,c]));
    for (const item of review.review.assessments) {
      const card = el('article', 'review-assessment'); card.append(badge(item.verdict), el('h3', '', claimMap.get(item.claim_id)?.title || item.claim_id), el('p', '', item.explanation), citations(item.evidence)); target.append(card);
    }
    if (review.review.missing_context.length) { const missing = el('section', 'actions'); missing.append(el('h3', '', 'Questions raised by the reviewer')); const list = el('ul'); for (const question of review.review.missing_context) list.append(el('li', '', question)); missing.append(list); target.append(missing); }
  }
  target.append(el('h2', 'section-title', 'Your review decisions'));
  target.append(el('p', 'muted', 'Local reviewer notes, not authenticated approvals. Save the case file to retain them across sessions.'));
  for (const claim of state.result.analysis.claims.filter(c => c.section === 'summary' || c.section === 'findings' || c.section === 'commitments')) {
    const card = el('article', 'human-review'); card.append(el('h3', '', claim.title), citations(claim.evidence));
    const decision = el('select'); decision.setAttribute('aria-label', `Review status for ${claim.title}`);
    for (const [value,label] of [['unreviewed','Not reviewed'],['accepted','Accepted by me'],['needs_follow_up','Needs follow-up'],['disputed','Disputed by me']]) { const option = el('option','',label); option.value=value; decision.append(option); }
    decision.value = version?.annotations?.[claim.id]?.status || 'unreviewed';
    const note = el('textarea'); note.rows=2; note.maxLength=2000; note.placeholder='Why? What should be verified next?'; note.setAttribute('aria-label', `Reviewer note for ${claim.title}`); note.value=version?.annotations?.[claim.id]?.note || '';
    const save = el('button', 'button secondary review-save', 'Save my review'); save.addEventListener('click', () => { if (state.busy || !version) return; version.annotations[claim.id] = { status:decision.value, note:note.value, recorded_at:new Date().toISOString() }; tell('Your review was saved in this version. Download the case file to preserve it.'); });
    card.append(decision,note,save);target.append(card);
  }
}
async function runReview() {
  if (state.busy || !state.result || !state.config.ai_available) return;
  setBusy(true); tell('The second AI pass is checking every claim against the sources. It will not overwrite the investigation.');
  try {
    const result=await api('/api/review',{project:state.current.project,sources:activeSources(),report:state.result.report});
    currentVersion().review=result; renderReport(); tell('Evidence review complete. Inspect partial, unsupported and uncertain assessments before relying on the report.');
  } catch(error){tell(error.message,true);} finally{setBusy(false);}
}
function importFormatChanged() { $('#import-metadata').classList.toggle('hidden',$('#import-format').value==='json'); }
function saveCaseFile() {
  if (!state.current || state.busy) return;
  const data={format:'caselens-case-file',version:2,saved_at:new Date().toISOString(),project:state.current.project,sources:state.current.sources,
    excluded:[...state.excluded],versions:state.current.versions || []};
  download(`${state.current.project.id}-case-file.json`,JSON.stringify(data,null,2),'application/json');
  tell('Case file downloaded with source records, report versions and reviewer notes. Keep it somewhere appropriate for that data.');
}
async function restoreCaseFile(file) {
  if (!file || state.busy) return;
  setBusy(true);
  try {
    if(file.size>8000000)throw new Error('Case files are limited to 8 MB.');
    const data=JSON.parse(await file.text());
    if(data.format!=='caselens-case-file'||data.version!==2||!Array.isArray(data.versions)||data.versions.length>10)throw new Error('This is not a supported CaseLens case file.');
    const base=await api('/api/normalize',{project:data.project,sources:data.sources});
    const versions=[];
    tell('Restoring sources and rechecking each saved report. Imported AI-origin labels will not be trusted.');
    for(const saved of data.versions){
      if(!saved||typeof saved!=='object'||!saved.result?.report)throw new Error('A saved version is incomplete.');
      const result=await api('/api/inspect',{project:base.project,sources:saved.sources,report:saved.result.report});
      const annotations={}; const validIds=new Set(result.analysis.claims.map(c=>c.id));
      if(saved.annotations&&typeof saved.annotations==='object')for(const [key,value]of Object.entries(saved.annotations)){
        if(validIds.has(key)&&value&&['unreviewed','accepted','needs_follow_up','disputed'].includes(value.status)&&typeof value.note==='string'&&value.note.length<=2000) annotations[key]={status:value.status,note:value.note,recorded_at:'Imported; author unverified'};
      }
      versions.push({id:`import-${Date.now()}-${++versionSequence}`,recorded_at:result.meta.generated_at,sources:saved.sources,result,annotations,review:null});
    }
    const excluded=Array.isArray(data.excluded)?data.excluded.filter(id=>base.sources.some(s=>s.id===id)):[];
    if(excluded.length===base.sources.length)throw new Error('A restored case must retain at least one included source.');
    const item={project:base.project,sources:base.sources,excluded,versions,imported:true,tag:'Restored case file',description:'Saved source context restored. Imported report provenance was rechecked; origin and reviewer identity are unverified.'};
    const included=base.sources.filter(s=>!excluded.includes(s.id)); const latest=versions.at(-1);
    if(latest&&sameSources(included,latest.sources))item.lastResult=latest.result;
    const existing=state.cases.findIndex(c=>c.project.id===base.project.id);
    if(existing>=0)state.cases[existing]=item;else state.cases.push(item);
    selectCase(existing>=0?existing:state.cases.length-1);
    tell('Case restored. Imported reports are labeled origin-unverified. Run a new investigation for a fresh analysis; old AI reviews must be rerun.');
  }catch(error){tell(error.message,true);}finally{setBusy(false);$('#restore-file').value='';}
}
function sameSources(a,b){const normalize=list=>JSON.stringify(list.map(s=>({id:s.id,project_id:s.project_id,kind:s.kind,author:s.author,sent_at:s.sent_at,title:s.title,body:s.body})).sort((x,y)=>x.id.localeCompare(y.id)));return normalize(a)===normalize(b);}
$('#import-format').addEventListener('change',importFormatChanged);
$('#bundle-btn').addEventListener('click',saveCaseFile);
$('#print-brief-btn').addEventListener('click',exportPrintableBrief);
$('#restore-btn').addEventListener('click',()=>$('#restore-file').click());
$('#restore-file').addEventListener('change',event=>restoreCaseFile(event.target.files[0]));
$('#tour-btn').addEventListener('click',()=>$('#tour-dialog').showModal());
$('#tour-start').addEventListener('click',()=>{if(state.busy)return;const index=state.cases.findIndex(c=>c.project.id==='cedar');if(index>=0)selectCase(index);$('#tour-dialog').close();});
$('#add-evidence-btn').addEventListener('click',()=>{if(state.busy)return;$('#evidence-error').textContent='';$('#evidence-time').value=new Date().toISOString();$('#evidence-dialog').showModal();});
$('#evidence-form').addEventListener('submit',async event=>{
  event.preventDefault();if(state.busy)return;
  const source={id:$('#evidence-id').value.trim(),project_id:state.current.project.id,kind:$('#evidence-kind').value,author:$('#evidence-author').value.trim(),sent_at:$('#evidence-time').value.trim(),title:$('#evidence-title').value.trim(),body:$('#evidence-body').value};
  setBusy(true);$('#evidence-save').disabled=true;
  try{const result=await api('/api/normalize',{project:state.current.project,sources:[...state.current.sources,source]});state.current.sources=result.sources;$('#evidence-dialog').close();$('#evidence-form').reset();invalidated('New evidence added. Previous versions are preserved. Select Live AI to investigate the expanded source set.');}
  catch(error){$('#evidence-error').textContent=error.message;}finally{setBusy(false);$('#evidence-save').disabled=false;}
});
window.enhancements={recordVersion,syncControls:syncExtendedControls,importFormatChanged,
  decorateSource(panel,source){
    const button=el('button','button secondary scope-toggle',state.excluded.has(source.id)?'Include in investigation':'Exclude & test dependence');button.disabled=state.busy;
    button.addEventListener('click',()=>{if(state.busy)return;if(state.excluded.has(source.id))state.excluded.delete(source.id);else{if(activeSources().length<=1)return tell('Keep at least one source in scope.',true);state.excluded.add(source.id);}invalidated('Evidence scope changed. Rerun to create a comparable version, or reopen this source to restore it.');openSource(source.id);});panel.append(button);
  },
  onSelect(){state.current.versions||=[];syncExtendedControls();},
  render(tab,target){if(tab==='map')renderEvidenceMap(target);else if(tab==='history')renderHistory(target);else if(tab==='review')renderReview(target);}
};
if(state.current)window.enhancements.onSelect();

function escapeHtml(value){return String(value).replace(/[&<>"']/g,char=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));}
function exportPrintableBrief(){
  if(!state.result||state.busy)return;
  const {report,meta}=state.result;const e=escapeHtml;
  const refs=items=>'<ul class="refs">'+items.map(ref=>`<li><a href="#${e(ref.source_id)}">${e(ref.source_id)}</a> — “${e(ref.quote)}”</li>`).join('')+'</ul>';
  const review=currentVersion()?.review;
  let content=`<header><div class="brand">CASELENS / INVESTIGATION BRIEF</div><h1>${e(state.current.project.title)}</h1><p>${e(state.current.project.customer)} · ${e(meta.generated_at)}</p><p>Engine: ${e(meta.model)}</p></header><aside>${e(meta.limitation)}</aside><h2>Executive summary</h2><h3>${e(report.summary.title)}</h3><p><b>${e(report.summary.kind)}</b> · ${e(report.summary.statement)}</p>${refs(report.summary.evidence)}<h2>Timeline</h2>`;
  for(const item of report.timeline)content+=`<article><small>${e(item.occurred_at)} · ${e(item.actor)}</small><h3>${e(item.title)}</h3><p>${e(item.statement)}</p>${refs(item.evidence)}</article>`;
  content+='<h2>Commitments</h2>';
  for(const item of report.commitments)content+=`<article><h3>${e(item.promise)}</h3><p>Owner: ${e(item.owner)} · Due: ${e(item.due)} · Status: ${e(item.status)}</p><p>Prerequisite: ${e(item.condition || "Not assessed")} · ${e(item.condition_status || "unknown")}</p><p>${e(item.status_reason || "Not assessed")}</p>${refs(item.evidence)}</article>`;
  content+='<h2>Findings</h2>';
  for(const item of report.findings)content+=`<article><h3>${e(item.title)}</h3><p><b>${e(item.kind)}</b> · ${e(item.statement)}</p>${refs(item.evidence)}</article>`;
  content+='<h2>Recommended next steps</h2><ol>'+report.next_actions.map(action=>`<li>${e(action)}</li>`).join('')+'</ol>';
  if(review){content+='<h2>Second-pass AI review</h2><aside>'+e(review.note)+'</aside>';for(const assessment of review.review.assessments)content+=`<p><b>${e(assessment.claim_id)} · ${e(assessment.verdict)}</b>: ${e(assessment.explanation)}</p>${refs(assessment.evidence)}`;}
  const notes=currentVersion()?.annotations||{};
  if(Object.keys(notes).length){content+='<h2>Human review notes</h2><p>Local notes; reviewer identity is not authenticated.</p>';for(const [id,note]of Object.entries(notes))content+=`<p><b>${e(id)} · ${e(note.status)}</b>: ${e(note.note)}</p>`;}
  content+='<h2 class="newpage">Original evidence</h2>';
  for(const source of activeSources())content+=`<article id="${e(source.id)}"><h3>${e(source.id)} · ${e(source.title)}</h3><small>${e(source.kind)} · ${e(source.author)} · ${e(source.sent_at)}</small><pre>${e(source.body)}</pre></article>`;
  content+=`<footer>Source fingerprint: ${e(meta.fingerprint)}<br>Quotes verify provenance, not semantic truth. No external actions were performed.</footer>`;
  const html=`<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'"><title>${e(state.current.project.title)} — CaseLens</title><style>body{max-width:860px;margin:50px auto;padding:0 28px;font:15px/1.75 Arial,sans-serif;color:#23392f}header{border-bottom:3px solid #25543e;padding-bottom:24px}.brand{font-size:10px;letter-spacing:3px;color:#65815b}h1{font:42px/1.2 Georgia,serif}h2{font:28px Georgia,serif;margin-top:38px;color:#25543e}h3{font-size:17px;margin-bottom:8px}article{border-bottom:1px solid #dce3d8;padding:12px 0}aside{background:#edf3e7;padding:18px;font-size:12px;margin-top:24px}.refs,small,footer{font-size:11px;color:#5a6e55}.refs{padding-left:20px}a{color:#25543e}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:13px/1.7 Arial,sans-serif;background:#f5f7f1;padding:16px}footer{border-top:1px solid #dce3d8;margin-top:40px;padding-top:20px;overflow-wrap:anywhere}@media print{body{margin:0;max-width:none;font-size:11pt;padding:0}h1{font-size:27pt}h2{font-size:20pt;break-after:avoid}h3{break-after:avoid}.newpage{break-before:page}a{text-decoration:none}aside{border:1px solid #b8cbb0}article{break-inside:auto}@page{size:A4;margin:20mm}}</style></head><body>${content}</body></html>`;
  download(`${state.current.project.id}-printable-brief.html`,html,'text/html');tell('Printable brief downloaded. Open it in a browser and use Print → Save as PDF. It includes the original source records.');
}
