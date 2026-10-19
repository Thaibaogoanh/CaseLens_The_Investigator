/* DOM behavior tests against a real Python backend. Not visual browser tests. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { spawn } = require('node:child_process');
const { JSDOM, VirtualConsole } = require('jsdom');
const root = path.resolve(__dirname, '..');
const failures = []; const downloads = []; const passed = [];
const serverCode = `from server import create_server,Handler
class TestLimiter:
 def allow(self,address):return True
Handler.limiter=TestLimiter()
s=create_server('127.0.0.1',0)
print(s.server_port,flush=True)
s.serve_forever()`;
const server = spawn(process.env.PYTHON || 'python', ['-u','-c',serverCode], {cwd:root,env:{...process.env,OPENAI_API_KEY:''},stdio:['ignore','pipe','pipe']});
let dom;
const delay = ms => new Promise(resolve => setTimeout(resolve,ms));
async function until(check, label) { const end=Date.now()+8000; while(Date.now()<end){if(check())return;await delay(15);}throw new Error('Timed out: '+label); }
function pass(name) {passed.push(name);console.log('PASS '+name);}
async function main(){
  const port=await new Promise((resolve,reject)=>{const timer=setTimeout(()=>reject(new Error('Server startup timed out')),8000);server.stdout.once('data',chunk=>{clearTimeout(timer);resolve(Number(chunk.toString().trim()));});server.once('error',reject);});
  const base=`http://127.0.0.1:${port}`;
  const console=new VirtualConsole();console.on('jsdomError',error=>{if(!error.message.includes('Could not parse CSS'))failures.push(error.message);});
  dom=new JSDOM(fs.readFileSync(path.join(root,'static/index.html'),'utf8'),{url:base,runScripts:'dangerously',virtualConsole:console});
  const w=dom.window;const d=w.document;const q=s=>d.querySelector(s);const all=s=>[...d.querySelectorAll(s)];
  w.fetch=(url,options)=>fetch(new URL(url,base),options);w.TextEncoder=TextEncoder;w.Blob=Blob;w.AbortController=AbortController;
  w.URL.createObjectURL=blob=>{downloads.push(blob);return 'blob:test';};w.URL.revokeObjectURL=()=>{};
  w.HTMLElement.prototype.scrollIntoView=function(){};
  w.HTMLAnchorElement.prototype.click=function(){};
  w.HTMLDialogElement.prototype.showModal=function(){this.open=true;};w.HTMLDialogElement.prototype.close=function(){this.open=false;};
  for(const file of ['app.js','extensions.js']){const script=d.createElement('script');script.textContent=fs.readFileSync(path.join(root,'static',file),'utf8');d.body.append(script);}
  await until(()=>all('.case-item').length===3,'load cases');
  assert.equal(q('#connection').textContent,'Sample mode ready');pass('workspace loads with three cases');
  q('#personal-ai-btn').click();assert.equal(q('#personal-ai-dialog').open,true);
  q('#personal-key').value='fake-test-key';
  q('#personal-ai-form').dispatchEvent(new w.Event('submit',{bubbles:true,cancelable:true}));
  assert.equal(w.personalAI.key,'fake-test-key');assert.equal(q('#personal-key').value,'');
  assert.equal(w.localStorage.length,0);assert.equal(w.sessionStorage.length,0);
  pass('personal key activates in memory and clears password field without browser storage');
  q('#personal-clear').click();assert.equal(w.personalAI,null);
  pass('clear personal key restores server settings');
  async function run(){q('#run-btn').click();await until(()=>!q('#run-btn').disabled,'investigation completion');assert.equal(q('#report-area').classList.contains('hidden'),false,q('#message').textContent);}
  await run();assert.match(q('#report-content').textContent,/launch commitment remains unresolved/i);pass('Atlas report renders from backend');
  q('.citation').click();assert.ok(q('#source-detail mark'));pass('citation opens source with highlighted exact quote');
  q('[data-tab="commitments"]').click();
  assert.match(q('#report-content').textContent,/not met/);assert.match(q('#report-content').textContent,/does not establish an unconditional breach/);pass('commitments show delivery and prerequisite assessments separately');
  q('[data-tab="timeline"]').click();assert.match(q('#report-content').textContent,/08:45/);pass('timeline uses event occurrence time');
  q('[data-tab="map"]').click();assert.ok(all('.evidence-dot').length>10);pass('evidence matrix renders claim-source links');
  all('.case-item')[2].click();await run();assert.match(q('#report-content').textContent,/cannot yet be verified/);
  q('#supplement-btn').click();await run();assert.match(q('#report-content').textContent,/New evidence verifies on-time delivery/);pass('correction updates report and retains previous conclusion');
  q('[data-tab="history"]').click();assert.equal(all('.version-card').length,2);assert.match(q('#report-content').textContent,/CDR-E03/);pass('version comparison identifies the new email');
  q('[data-tab="review"]').click();assert.equal(q('.review-trigger').disabled,true);
  q('.human-review select').value='needs_follow_up';q('.human-review textarea').value='Check receipt attachment.';q('.review-save').click();pass('human review records notes without AI credentials');
  q('#print-brief-btn').click();let printable=await downloads.at(-1).text();assert.match(printable,/Check receipt attachment/);assert.match(printable,/Original evidence/);pass('printable brief includes original evidence and reviewer notes');
  q('#bundle-btn').click();const bundleText=await downloads.at(-1).text();const bundle=JSON.parse(bundleText);assert.equal(bundle.versions.length,2);pass('portable case file includes version history');
  all('.case-item')[0].click();all('.case-item')[2].click();assert.equal(q('#report-area').classList.contains('hidden'),false);pass('case switching preserves the working report');
  q('[data-tab="map"]').click();const toggles=all('.scope-toggle');const correction=toggles.find(c=>c.parentNode.textContent.includes('CDR-E03'));correction.click();await run();assert.match(q('#report-content').textContent,/Delivery cannot yet be verified/);pass('excluding correction returns to unknown using the reduced evidence set');
  w.openSource('CDR-E03');q('#source-detail .scope-toggle').click();await run();assert.match(q('#report-content').textContent,/on-time delivery/);pass('excluded source can be restored from the evidence panel');
  q('#import-btn').click();q('#import-json').value=fs.readFileSync(path.join(root,'examples/custom-project.json'),'utf8');q('#import-confirm').click();await until(()=>all('.case-item').length===4,'custom import');pass('JSON import creates a separate project');
  q('#add-evidence-btn').click();q('#evidence-id').value='EX-C03';q('#evidence-author').value='Reviewer';q('#evidence-time').value='2026-10-17T12:00:00Z';q('#evidence-title').value='Follow-up';q('#evidence-body').value='<img src=x onerror=alert(1)> Waiting for approval.';
  q('#evidence-form').dispatchEvent(new w.Event('submit',{bubbles:true,cancelable:true}));await until(()=>!q('#evidence-save').disabled,'add evidence');
  assert.equal(q('#evidence-count').textContent,'4');w.openSource('EX-C03');assert.equal(q('#source-detail img'),null);assert.match(q('#source-detail').textContent,/onerror=alert/);pass('added source is safely rendered as text');
  await w.restoreCaseFile({size:Buffer.byteLength(bundleText),text:async()=>bundleText});
  assert.equal(q('#project-title').textContent,'The missing receipt');assert.match(q('#report-label').textContent,/ORIGIN UNVERIFIED/);pass('restore rechecks provenance and does not trust origin labels');
  q('[data-tab="review"]').click();assert.equal(q('.human-review select').value,'needs_follow_up');assert.equal(q('.human-review textarea').value,'Check receipt attachment.');pass('restored human notes remain separate from AI claims');
  q('#export-btn').click();assert.match(await downloads.at(-1).text(),/Human reviewer notes/);pass('Markdown export retains reviewer notes');
  assert.deepEqual(failures,[]);pass('no unhandled DOM script errors');
  globalThis.console.log(JSON.stringify({passed:passed.length,kind:'DOM integration, not visual browser QA'},null,2));
}
main().catch(error=>{console.error(error);console.error('DOM errors:',failures);if(dom)console.error('Status:',dom.window.document.querySelector('#message')?.textContent);process.exitCode=1;}).finally(()=>{if(dom)dom.window.close();server.kill();});
