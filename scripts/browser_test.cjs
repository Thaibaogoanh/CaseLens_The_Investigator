/* Optional isolated headless browser acceptance tests. No live AI requests. */
const assert=require('node:assert/strict');
const path=require('node:path');const fs=require('node:fs');const {spawn}=require('node:child_process');
const {chromium}=require('playwright');
const root=path.resolve(__dirname,'..');const artifacts=path.join(root,'artifacts','browser');fs.mkdirSync(artifacts,{recursive:true});
const server=spawn(process.env.PYTHON||'python',['-u','-c',`from server import create_server,Handler
class TestLimiter:
 def allow(self,address):return True
Handler.limiter=TestLimiter()
s=create_server('127.0.0.1',0)
print(s.server_port,flush=True)
s.serve_forever()`],{cwd:root,env:{...process.env,OPENAI_API_KEY:''},stdio:['ignore','pipe','pipe']});
let browser;const passes=[];const errors=[];
function pass(name){passes.push(name);console.log('PASS '+name);}
async function main(){
  const port=await new Promise((resolve,reject)=>{const timer=setTimeout(()=>reject(new Error('Server startup timeout')),8000);server.stdout.once('data',chunk=>{clearTimeout(timer);resolve(Number(chunk.toString().trim()));});server.once('error',reject);});
  browser=await chromium.launch({headless:true});const page=await browser.newPage({viewport:{width:1440,height:1050}});
  page.on('pageerror',error=>errors.push(error.message));
  await page.goto(`http://127.0.0.1:${port}`);await page.locator('.case-item').nth(2).waitFor();
  await page.screenshot({path:path.join(artifacts,'desktop-start.png'),fullPage:true});
  assert.equal(await page.locator('#connection').textContent(),'Sample mode ready');pass('desktop app loads');
  async function run(){await page.locator('#run-btn').click();await page.locator('#report-area').waitFor({state:'visible'});await page.locator('#run-btn:not([disabled])').waitFor();}
  await run();await page.locator('.citation').first().click();assert.ok((await page.locator('#source-detail mark').textContent()).length);pass('native evidence click highlights a source');
  await page.locator('[data-tab="map"]').click();assert.ok(await page.locator('.evidence-dot').count()>10);pass('evidence matrix renders');
  await page.locator('.case-item').nth(2).click();await run();await page.locator('#supplement-btn').click();await run();
  assert.match(await page.locator('#report-content').textContent(),/New evidence verifies on-time delivery/);pass('new email updates investigation');
  await page.locator('[data-tab="history"]').click();assert.equal(await page.locator('.version-card').count(),2);pass('version comparison visible');
  await page.screenshot({path:path.join(artifacts,'desktop-versions.png'),fullPage:true});
  await page.locator('[data-tab="review"]').click();assert.equal(await page.locator('.review-trigger').isDisabled(),true);
  await page.locator('.human-review select').first().selectOption('accepted');await page.locator('.human-review textarea').first().fill('Receipt verified by reviewer.');await page.locator('.review-save').first().click();pass('human review works without API');
  const briefEvent=page.waitForEvent('download');await page.locator('#print-brief-btn').click();const brief=await briefEvent;await brief.saveAs(path.join(artifacts,brief.suggestedFilename()));pass('printable HTML download works');
  const bundleEvent=page.waitForEvent('download');await page.locator('#bundle-btn').click();const bundle=await bundleEvent;const bundlePath=path.join(artifacts,bundle.suggestedFilename());await bundle.saveAs(bundlePath);pass('case file downloads');
  await page.locator('.case-item').first().click();await page.locator('#restore-file').setInputFiles(bundlePath);await page.locator('#report-label').filter({hasText:'ORIGIN UNVERIFIED'}).waitFor();
  assert.equal(await page.locator('#project-title').textContent(),'The missing receipt');pass('native file restore succeeds');
  await page.locator('#mode').selectOption('sample');await page.locator('[data-tab="map"]').click();await page.locator('.scope-row').filter({hasText:'CDR-E03'}).locator('input').uncheck();await run();assert.match(await page.locator('#report-content').textContent(),/cannot yet be verified/);pass('source exclusion produces expected uncertainty');
  await page.locator('#source-search').fill('no-such-record');assert.equal(await page.locator('.source-row').count(),0);await page.locator('#source-search').fill('');pass('source search empty state works');
  await page.setViewportSize({width:390,height:844});await page.locator('[data-tab="map"]').click();
  const width=await page.evaluate(()=>({scroll:document.documentElement.scrollWidth,client:document.documentElement.clientWidth}));assert.ok(width.scroll<=width.client+1,JSON.stringify(width));
  await page.screenshot({path:path.join(artifacts,'mobile-map.png'),fullPage:true});pass('390px mobile has no page-wide horizontal overflow');
  await page.locator('#import-btn').click();assert.equal(await page.locator('#import-dialog').isVisible(),true);await page.locator('#import-dialog .dialog-close').click();pass('native import dialog opens and closes');
  await page.locator('#tour-btn').click();await page.locator('#tour-start').click();assert.equal(await page.locator('#tour-dialog').isVisible(),false);pass('judge walkthrough opens the case');
  await page.setViewportSize({width:1440,height:1050});await page.locator('[data-tab="overview"]').click();await page.screenshot({path:path.join(artifacts,'desktop-report.png'),fullPage:true});
  assert.deepEqual(errors,[]);pass('no browser JavaScript errors');
  const result={passed:passes.length,checks:passes,browser:await browser.version(),live_ai:false};fs.writeFileSync(path.join(artifacts,'result.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result,null,2));
}
main().catch(error=>{console.error(error);process.exitCode=1;}).finally(async()=>{if(browser)await browser.close();server.kill();});
