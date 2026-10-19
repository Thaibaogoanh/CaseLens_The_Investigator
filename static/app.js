'use strict';
const $ = selector => document.querySelector(selector);
const state = { cases: [], current: null, config: null, result: null, tab: 'overview', filter: 'all', selected: null, busy: false, priorSummary: null, excluded: new Set() };
function activeSources() { return state.current.sources.filter(source => !state.excluded.has(source.id)); }
const copy = value => JSON.parse(JSON.stringify(value));
function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}
function dateTime(value) {
  return new Date(value).toLocaleString('en-GB', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit', timeZone: 'UTC', hour12: false }) + ' UTC';
}
function tell(message, error = false) {
  $('#message').textContent = message;
  $('#message').classList.remove('hidden');
  $('#message').classList.toggle('error', error);
}
function clearMessage() { $('#message').classList.add('hidden'); }
async function api(path, body) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), 110000);
  try {
    const response = await fetch(path, { method: body ? 'POST' : 'GET', signal: controller.signal,
      headers: body ? { 'Content-Type': 'application/json', ...(window.personalAI && ['/api/investigate','/api/ask','/api/review'].includes(path) ? {'X-AI-Key':window.personalAI.key,'X-AI-Provider':window.personalAI.provider,'X-AI-Model':window.personalAI.model} : {}) } : {}, body: body ? JSON.stringify(body) : undefined });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'The request could not be completed.');
    return data;
  } catch (error) {
    if (error.name === 'AbortError') throw new Error('The request timed out. Please try again with fewer sources.');
    throw error;
  } finally { clearTimeout(timeout); }
}
function setBusy(value) {
  state.busy = value;
  for (const selector of ['#run-btn', '#welcome-run', '#import-btn', '#mode', '#ask-btn', '#supplement-btn']) $(selector).disabled = value;
  document.querySelectorAll('.case-item').forEach(node => { node.disabled = value; });
  $('#export-btn').disabled = value || !state.result;
  $('#ask-btn').disabled = value || !state.result || !state.config?.ai_available;
  $('#question').disabled = value || !state.result || !state.config?.ai_available;
  $('#main').setAttribute('aria-busy', String(value));
  window.enhancements?.syncControls();
}
function renderCases() {
  $('#case-list').replaceChildren();
  state.cases.forEach((item, index) => {
    const active = item.project.id === state.current?.project.id;
    const button = el('button', 'case-item' + (active ? ' active' : ''));
    button.setAttribute('aria-current', active ? 'true' : 'false');
    button.append(el('span', 'case-index', `CASE ${String(index + 1).padStart(2, '0')}`), el('strong', '', item.project.title), el('small', '', item.project.customer));
    button.addEventListener('click', () => { if (!state.busy) selectCase(index); });
    $('#case-list').append(button);
  });
  $('#case-count').textContent = String(state.cases.length).padStart(2, '0');
}
function selectCase(index) {
  state.current = state.cases[index]; state.result = state.current.lastResult || null; state.selected = null; state.priorSummary = state.current.priorSummary || null; state.tab = 'overview';
  state.excluded = new Set(state.current.excluded || []);
  state.filter = 'all'; $('#source-search').value = ''; $('#answer').replaceChildren();
  $('#project-customer').textContent = state.current.project.customer;
  $('#project-title').textContent = state.current.project.title;
  $('#project-description').textContent = state.current.description || 'Imported context, ready for an evidence-linked investigation.';
  $('#case-number').textContent = `CASE ${String(index + 1).padStart(2, '0')}`;
  $('#question').value = state.current.question || '';
  $('#mode').value = state.current.imported ? 'live' : 'sample';
  $('#source-detail').classList.add('hidden');
  $('#report-area').classList.add('hidden'); $('#welcome').classList.remove('hidden');
  $('#export-btn').disabled = true;
  $('#run-btn').disabled = false;
  updateTabs(); renderCases(); renderCounts(); renderSources(); modeNote(); clearMessage(); updateSupplement();
  window.enhancements?.onSelect();
  if (state.result) renderReport();
}
function renderCounts() {
  const strip = $('#source-strip'); strip.replaceChildren();
  const sources = state.current.sources;
  for (const [kind, label] of [['ticket', 'tickets'], ['email', 'emails'], ['chat', 'chat records']]) {
    const span = el('span'); span.append(el('strong', '', String(sources.filter(s => s.kind === kind).length)), document.createTextNode(' ' + label)); strip.append(span);
  }
  strip.append(el('span', '', state.current.tag || 'Custom investigation'));
  $('#evidence-count').textContent = sources.length;
  window.enhancements?.syncControls();
}
function modeNote() {
  const live = $('#mode').value === 'live';
  $('#mode-note').textContent = live ? (state.config.ai_available ? 'Sends selected project sources to the configured AI provider for a new analysis.' : 'Requires the selected provider API key on the server. Sample replay works now.') : 'Curated example report. No model call.';
}
function renderSources() {
  const list = $('#source-list'); list.replaceChildren();
  const query = $('#source-search').value.toLowerCase().trim();
  const rows = state.current.sources.filter(s => (state.filter === 'all' || s.kind === state.filter) && (!query || `${s.id} ${s.title} ${s.body} ${s.author}`.toLowerCase().includes(query)));
  for (const source of rows) {
    const button = el('button', 'source-row' + (state.selected === source.id ? ' selected' : ''));
    const top = el('span', 'row-top'); top.append(el('span', 'source-kind', source.kind), el('span', 'source-id', source.id));
    button.append(top, el('strong', '', source.title), el('small', '', dateTime(source.sent_at) + (state.excluded.has(source.id) ? ' · EXCLUDED' : '')));
    button.addEventListener('click', () => openSource(source.id)); list.append(button);
  }
  if (!rows.length) list.append(el('p', 'empty-sources', 'No matching sources.'));
  document.querySelectorAll('[data-filter]').forEach(button => {
    const active = button.dataset.filter === state.filter; button.classList.toggle('active', active); button.setAttribute('aria-pressed', String(active));
  });
}
function openSource(id, quote = '') {
  const source = state.current.sources.find(s => s.id === id);
  if (!source) return;
  state.selected = id; state.filter = 'all'; $('#source-search').value = ''; renderSources();
  const panel = $('#source-detail'); panel.replaceChildren(); panel.classList.remove('hidden');
  const close = el('button', 'close-source', '×'); close.setAttribute('aria-label', 'Close source');
  close.addEventListener('click', () => { panel.classList.add('hidden'); state.selected = null; renderSources(); });
  panel.append(close, el('span', 'source-kind', `${source.kind} / ${source.id}`), el('h3', '', source.title), el('p', 'detail-meta', `${source.author}\nSent ${dateTime(source.sent_at)}`));
  const body = el('p', 'source-body');
  const at = quote ? source.body.indexOf(quote) : -1;
  if (at >= 0) body.append(document.createTextNode(source.body.slice(0, at)), el('mark', '', quote), document.createTextNode(source.body.slice(at + quote.length)));
  else body.textContent = source.body;
  panel.append(body); window.enhancements?.decorateSource(panel, source); panel.scrollIntoView({ block: 'nearest', behavior: 'auto' }); panel.focus({ preventScroll: true });
}
function citations(evidence) {
  const row = el('div', 'citations');
  for (const item of evidence) {
    const button = el('button', 'citation', `↗ ${item.source_id}`); button.title = item.quote;
    button.setAttribute('aria-label', `Inspect ${item.source_id}: ${item.quote}`);
    button.addEventListener('click', () => openSource(item.source_id, item.quote)); row.append(button);
  }
  if (!evidence.length) row.append(el('span', 'muted', 'No supporting source available.'));
  return row;
}
function badge(kind) { return el('span', `badge ${kind}`, kind.replaceAll('_', ' ')); }
function finding(record, summary = false) {
  const card = el('section', summary ? 'summary-card' : 'finding');
  card.append(badge(record.kind), el(summary ? 'h2' : 'h3', '', record.title), el('p', '', record.statement), citations(record.evidence));
  return card;
}
function updateTabs() {
  document.querySelectorAll('[data-tab]').forEach(button => {
    const active = button.dataset.tab === state.tab; button.classList.toggle('active', active); button.setAttribute('aria-pressed', String(active));
  });
}
function renderReport() {
  if (!state.result) return;
  const { report, meta } = state.result; const target = $('#report-content'); target.replaceChildren();
  $('#welcome').classList.add('hidden'); $('#report-area').classList.remove('hidden');
  $('#report-label').textContent = meta.mode === 'sample' ? 'CURATED SAMPLE / NO AI CALL' : meta.mode === 'imported' ? 'IMPORTED / ORIGIN UNVERIFIED' : 'LIVE AI INVESTIGATION';
  $('#report-time').textContent = `${meta.verified_references} references checked · ${meta.cached ? 'cached' : (meta.elapsed_ms / 1000).toFixed(1) + 's'}`;
  $('#export-btn').disabled = false; updateTabs();
  if (state.tab === 'overview') {
    if (state.priorSummary) { const prior = el('div', 'actions'); prior.append(el('h3', '', 'Before the correction email'), el('p', '', state.priorSummary)); target.append(prior); }
    target.append(finding(report.summary, true));
    const heading = el('h2', 'section-title', 'What the evidence says'); heading.append(el('small', '', String(report.findings.length).padStart(2, '0'))); target.append(heading);
    report.findings.forEach(item => target.append(finding(item)));
    const actions = el('section', 'actions'); actions.append(el('h3', '', 'Recommended next steps'), el('small', '', 'Suggestions for the case owner; no external action is taken.'));
    const list = el('ol'); report.next_actions.forEach(action => list.append(el('li', '', action))); actions.append(list); target.append(actions);
  } else if (state.tab === 'timeline') {
    target.append(el('p', 'timeline-intro', 'Ordered by event time · all timestamps in UTC. Open a source to compare its send time.'));
    const timeline = el('div', 'timeline');
    report.timeline.forEach(item => {
      const node = el('article', 'timeline-item'); const time = el('time', '', dateTime(item.occurred_at)); time.dateTime = item.occurred_at;
      node.append(time, el('h3', '', item.title), el('span', 'actor', item.actor), el('p', '', item.statement), citations(item.evidence)); timeline.append(node);
    });
    if (!report.timeline.length) timeline.append(el('p', 'muted', 'No supported events were extracted.'));
    target.append(timeline);
  } else if (state.tab === 'commitments') {
    target.append(el('p', 'muted', 'Delivery status and prerequisite status are assessed separately. Overdue means observed noncompletion after a target, not an unconditional breach. Missing confirmation alone stays not verified.'));
    if (!report.commitments.length) target.append(el('p', 'muted', 'No explicit commitments were established from these sources.'));
    report.commitments.forEach(item => {
      const node = el('article', 'commitment'); const details = el('dl');
      details.append(el('dt', '', 'Owner'), el('dd', '', item.owner), el('dt', '', 'Due'), el('dd', '', item.due));
      node.append(badge(item.status), el('h3', '', item.promise), details, el('p', 'muted', `Prerequisite: ${item.condition || 'Not assessed'} · ${(item.condition_status || 'unknown').replaceAll('_', ' ')}`), el('p', '', item.status_reason || 'Legacy assessment; run Live AI to reassess.'), citations(item.evidence)); target.append(node);
    });
  } else if (['map', 'history', 'review'].includes(state.tab) && window.enhancements) {
    window.enhancements.render(state.tab, target);
  } else {
    const node = el('section', 'check-card'); node.append(el('h3', '', 'Provenance, checked.'), el('p', '', meta.limitation));
    const rows = [['Engine', meta.model], ['Input records', String(meta.source_count)], ['Verified references', String(meta.verified_references)], ...meta.checks.map(check => [check, 'Passed'])];
    for (const [key, value] of rows) { const row = el('div', 'check-row'); row.append(el('span', '', key), el('span', '', value)); node.append(row); }
    node.append(el('p', '', 'Fingerprint of this project and source set:'), el('div', 'digest', meta.fingerprint), el('p', '', `Report assembled: ${dateTime(meta.generated_at)}. Sample replay reports are authored fixtures, not generated AI outputs. No external actions or searches were performed.`)); target.append(node);
  }
  $('#ask-btn').disabled = !state.config.ai_available;
  $('#question').disabled = !state.config.ai_available;
  $('#ask-note').textContent = state.config.ai_available ? 'This sends the selected project sources and your question to the configured AI provider, even when viewing a sample report.' : 'Configure the selected provider API key on the server to enable open-ended questions. You can inspect all sources now.';
}
async function investigate() {
  if (state.busy || !state.current) return;
  clearMessage();
  if ($('#mode').value === 'live' && !state.config.ai_available) return tell('Live AI needs a server API key. Select Sample replay for built-in cases, or follow START_HERE_VI.md to configure AI.', true);
  setBusy(true); $('#run-btn').textContent = 'Investigating…';
  tell($('#mode').value === 'live' ? 'Analyzing the selected records. The report will appear only after structure and quotation checks pass.' : 'Loading the authored replay and validating its references. No AI is being called.');
  try {
    state.result = await api('/api/investigate', { project: state.current.project, sources: activeSources(), mode: $('#mode').value });
    state.current.lastResult = state.result;
    window.enhancements?.recordVersion();
    state.tab = 'overview'; $('#answer').replaceChildren(); renderReport();
    tell(state.result.meta.mode === 'sample' ? 'Sample replay ready. All quoted references were checked against the original records.' : 'Live AI report ready. Quote provenance was checked; review the evidence before relying on interpretations.');
    updateSupplement();
  } catch (error) { tell(error.message, true); }
  finally { setBusy(false); $('#run-btn').textContent = 'Investigate case ↗'; if (!state.config.ai_available) $('#ask-btn').disabled = true; }
}
function updateSupplement() {
  const current = state.current;
  const exists = current.supplement && current.sources.some(s => s.id === current.supplement.id);
  $('#supplement-box').classList.toggle('hidden', !current.supplement || exists);
}
function exportBrief() {
  if (!state.result) return;
  const { report, meta } = state.result;
  const lines = [`# ${state.current.project.title}`, '', `Customer: ${state.current.project.customer}`, `Engine: ${meta.model}`, `Built: ${meta.generated_at}`, `Source fingerprint: ${meta.fingerprint}`, '', '> ' + meta.limitation, ''];
  const addRefs = evidence => { for (const ref of evidence) lines.push(`- [${ref.source_id}] ${ref.quote}`); lines.push(''); };
  lines.push('## Summary', '', report.summary.statement, ''); addRefs(report.summary.evidence);
  lines.push('## Timeline', '');
  for (const item of report.timeline) { lines.push(`### ${item.occurred_at} — ${item.title}`, `${item.actor}: ${item.statement}`, ''); addRefs(item.evidence); }
  lines.push('## Commitments', '');
  for (const item of report.commitments) { lines.push(`- ${item.owner}: ${item.promise}`, `  Due: ${item.due}; delivery status: ${item.status}`, `  Prerequisite: ${item.condition || "Not assessed"}; assessment: ${item.condition_status || "unknown"}`, `  Rationale: ${item.status_reason || "Not assessed"}`, ''); addRefs(item.evidence); }
  lines.push('## Findings', '');
  for (const item of report.findings) { lines.push(`### ${item.title} (${item.kind})`, item.statement, ''); addRefs(item.evidence); }
  lines.push('## Recommended next steps', '', ...report.next_actions.map(s => '- ' + s), '', '## Source register', '');
  for (const source of activeSources()) lines.push(`- ${source.id} | ${source.kind} | ${source.author} | ${source.sent_at} | ${source.title}`);
  const annotations = state.current.versions?.at(-1)?.annotations;
  if (annotations && Object.keys(annotations).length) { lines.push('', '## Human reviewer notes (not AI findings)', ''); for (const [id, note] of Object.entries(annotations)) lines.push(`- ${id}: ${note.status}. ${note.note}`); }
  download(`${state.current.project.id}-investigation.md`, lines.join('\n'), 'text/markdown');
}
function download(name, content, type) {
  const url = URL.createObjectURL(new Blob([content], { type })); const anchor = el('a'); anchor.href = url; anchor.download = name;
  document.body.append(anchor); anchor.click(); anchor.remove(); setTimeout(() => URL.revokeObjectURL(url), 1000);
}
function validateImport(data) {
  if (!data || typeof data !== 'object' || Array.isArray(data)) throw new Error('Expected one JSON object.');
  if (!data.project || !Array.isArray(data.sources) || !data.sources.length || data.sources.length > 60) throw new Error('Include project metadata and 1–60 sources.');
  for (const key of ['id', 'title', 'customer']) if (typeof data.project[key] !== 'string' || !data.project[key].trim() || data.project[key].length > 200) throw new Error(`Missing or invalid project.${key}.`);
  if (!/^[A-Za-z0-9_-]{1,80}$/.test(data.project.id)) throw new Error('Use a simple alphanumeric project ID.');
  const ids = new Set(); let total = 0;
  for (const source of data.sources) {
    for (const key of ['id', 'project_id', 'kind', 'author', 'sent_at', 'title', 'body']) if (typeof source[key] !== 'string' || !source[key].trim()) throw new Error(`A source is missing ${key}.`);
    if (source.project_id !== data.project.id) throw new Error('Every source must belong to this project.');
    if (!/^[A-Za-z0-9_-]{1,80}$/.test(source.id) || ids.has(source.id)) throw new Error('Source IDs must be unique and alphanumeric.'); ids.add(source.id);
    if (!['email', 'ticket', 'chat'].includes(source.kind)) throw new Error('Source kind must be email, ticket or chat.');
    if (Number.isNaN(Date.parse(source.sent_at)) || !/(Z|[+-]\d\d:\d\d)$/.test(source.sent_at)) throw new Error('Source dates need ISO 8601 timestamps with a timezone.');
    if (source.author.length > 200 || source.title.length > 300 || source.body.length > 12000) throw new Error('A source field exceeds its size limit.');
    total += source.body.length;
  }
  if (total > 80000) throw new Error('Combined source text exceeds 80,000 characters.');
}
$('#run-btn').addEventListener('click', investigate); $('#welcome-run').addEventListener('click', investigate);
$('#mode').addEventListener('change', modeNote); $('#export-btn').addEventListener('click', exportBrief);
$('#source-search').addEventListener('input', renderSources);
document.querySelectorAll('[data-filter]').forEach(button => button.addEventListener('click', () => { state.filter = button.dataset.filter; renderSources(); }));
document.querySelectorAll('[data-tab]').forEach(button => button.addEventListener('click', () => { state.tab = button.dataset.tab; renderReport(); }));
$('#supplement-btn').addEventListener('click', () => {
  if (state.busy || !state.current.supplement || state.current.sources.some(s => s.id === state.current.supplement.id)) return;
  state.priorSummary = state.result?.report.summary.statement || 'Delivery could not be verified without a transfer receipt.';
  state.current.sources.push(copy(state.current.supplement)); state.current.priorSummary = state.priorSummary; state.result = null; state.current.lastResult = null;
  $('#report-area').classList.add('hidden'); $('#welcome').classList.remove('hidden'); $('#export-btn').disabled = true;
  updateSupplement(); renderCounts(); renderSources(); openSource(state.current.supplement.id);
  tell('Correction email added. Run the investigation again to compare the earlier conclusion with the new evidence.');
});
$('#ask-form').addEventListener('submit', async event => {
  event.preventDefault(); if (state.busy || !state.config.ai_available || !state.result) return;
  setBusy(true); $('#ask-btn').textContent = '…'; clearMessage();
  try {
    const data = await api('/api/ask', { project: state.current.project, sources: activeSources(), question: $('#question').value });
    $('#answer').replaceChildren(finding(data.answer), el('p', 'answer-note', `Live AI · ${data.model} · exact-quote provenance checked`));
  } catch (error) { tell(error.message, true); }
  finally { setBusy(false); $('#ask-btn').textContent = 'Ask ↗'; }
});
$('#import-btn').addEventListener('click', () => { $('#import-error').textContent = ''; $('#import-dialog').showModal(); });
$('#import-file').addEventListener('change', async event => {
  const file = event.target.files[0]; if (!file) return;
  if (file.size > 250000) { $('#import-error').textContent = 'The file exceeds 250,000 bytes.'; return; }
  try { $('#import-json').value = await file.text(); const ext = file.name.split('.').at(-1).toLowerCase(); if (['json','csv','eml'].includes(ext)) { $('#import-format').value = ext; window.enhancements?.importFormatChanged(); } } catch { $('#import-error').textContent = 'The file could not be read.'; }
});
$('#import-confirm').addEventListener('click', async () => {
  if (state.busy) return;
  $('#import-confirm').disabled = true; setBusy(true);
  try {
    const raw = $('#import-json').value; if (new TextEncoder().encode(raw).length > 250000) throw new Error('The JSON exceeds 250,000 bytes.');
    const request = { format: $('#import-format').value, content: raw };
    if (request.format !== 'json') request.project = { id: $('#import-project-id').value.trim(), title: $('#import-title').value.trim(), customer: $('#import-customer').value.trim() };
    const data = await api('/api/normalize', request); validateImport(data);
    if (state.cases.some(c => c.project.id === data.project.id)) throw new Error('Choose a project ID that is not already in the workspace.');
    const imported = { project: { id: data.project.id, title: data.project.title, customer: data.project.customer }, sources: data.sources, imported: true, tag: 'Imported project' };
    state.cases.push(imported); selectCase(state.cases.length - 1); $('#import-dialog').close();
    tell('Project imported into this tab. Select Live AI and Investigate to send its sources for analysis. Reloading clears imported projects.');
  } catch (error) { $('#import-error').textContent = error.message; }
  finally { $('#import-confirm').disabled = false; setBusy(false); }
});
async function init() {
  try {
    const [config, data] = await Promise.all([api('/api/config'), api('/api/cases')]);
    state.config = config; state.cases = data.cases;
    $('#connection').textContent = config.ai_available ? 'Live AI configured' : 'Sample mode ready';
    selectCase(0);
  } catch (error) { $('#connection').textContent = 'Connection issue'; $('#project-title').textContent = 'Workspace unavailable'; tell('Cannot load the server. Start it with python server.py, then refresh. ' + error.message, true); }
}
init();


// Personal credential controls; credentials never enter case state.
'use strict';
(() => {
  let serverConfig = null;
  const dialog = $('#personal-ai-dialog');
  $('#personal-ai-btn').addEventListener('click', () => {
    if (state.busy || !state.config) return;
    $('#personal-status').textContent = window.personalAI ? 'Your key is active for this tab. Enter a key to replace it.' : 'Using server settings. You can override them for this tab.';
    dialog.showModal();
  });
  $('#personal-provider').addEventListener('change', () => {
    $('#personal-model').value = $('#personal-provider').value === 'gemini' ? 'gemini-3.8-flash' : 'gpt-4.1-mini';
  });
  function refresh() {
    modeNote(); setBusy(false);
    if (state.result) renderReport();
    $('#connection').textContent = window.personalAI ? `Your ${window.personalAI.provider} key` : (state.config.ai_available ? 'Live AI configured' : 'Sample mode ready');
    $('#personal-ai-btn').textContent = window.personalAI ? 'Your key active · settings' : 'API settings';
  }
  $('#personal-ai-form').addEventListener('submit', event => {
    event.preventDefault();
    if (state.busy || !state.config) return;
    if (!['localhost','127.0.0.1','[::1]'].includes(location.hostname) && location.protocol !== 'https:') {
      $('#personal-status').textContent = 'Use HTTPS before entering credentials on a public deployment.'; return;
    }
    const key = $('#personal-key').value.trim();
    if (!/^[\x21-\x7E]{1,1024}$/.test(key)) { $('#personal-status').textContent = 'Check the key: no spaces or line breaks.'; return; }
    if (!serverConfig) serverConfig = {...state.config};
    window.personalAI = {key, provider:$('#personal-provider').value, model:$('#personal-model').value.trim()};
    state.config = {...serverConfig, ai_available:true, provider:window.personalAI.provider, model:window.personalAI.model, review_model:window.personalAI.model};
    $('#personal-key').value = ''; dialog.close(); refresh();
    tell('Your key will be used for new AI requests. Existing reports retain their original model labels.');
  });
  $('#personal-clear').addEventListener('click', () => {
    if (state.busy) return;
    window.personalAI = null; $('#personal-key').value = '';
    if (serverConfig) state.config = {...serverConfig};
    dialog.close(); refresh(); tell('Personal key cleared. Server settings restored.');
  });
})();
