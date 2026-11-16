"""Optional Chromium UI smoke against a real local Workbench API.

Browser loopback navigation may be blocked by hosted Chromium policy. Load
unmodified shipped HTML/CSS/JS and bridge only fetch() calls to the real
Python loopback server. This verifies UI+API behavior, not Chromium transport.
Requires Playwright and Chromium; only synthetic fixtures are used.
"""
import sys,threading,json,shutil
from pathlib import Path
from playwright.sync_api import sync_playwright
from urllib.request import Request,urlopen
from urllib.error import HTTPError
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from kinship.web import Workbench

def exercise(page,label):
    errors=[]
    page.on('pageerror', lambda err: errors.append(str(err)))
    # The Chromium sandbox blocks loopback navigation. Bridge each browser API
    # request to the *actual* local server from Python, while executing the
    # shipped HTML, CSS and JavaScript unmodified in the browser.
    def backend(source, args):
        endpoint = args['path']
        assert endpoint.startswith('/api/'), endpoint
        data = args.get('body')
        headers = {'Content-Type':'application/json'} if data is not None else {}
        req = Request(URL+endpoint, data=data.encode('utf-8') if data is not None else None,
                      headers=headers, method='POST' if data is not None else 'GET')
        try:res=urlopen(req,timeout=5)
        except HTTPError as exc:res=exc
        try:return {'status':res.status,'json':json.loads(res.read())}
        finally:res.close()
    page.expose_binding('fetchBridge',backend)
    html=(ROOT/'src/kinship/static/index.html').read_text('utf-8')
    import re
    html=re.sub(r'<link rel="stylesheet" href="/[^" ]+">','',html)
    html=re.sub(r'<script type="module" src="/[^" ]+"></script>','',html)
    page.set_content(html,wait_until='load')
    page.evaluate("""() => {window.fetch = async (url, options={}) => {
      const data = await window.fetchBridge({path:String(url),body:options.body||null});
      return {ok:data.status >=200 && data.status<300,status:data.status,json:async()=>data.json};
    }; }""")
    page.add_style_tag(content=(ROOT/'src/kinship/static/styles.css').read_text('utf-8'))
    page.add_style_tag(content=(ROOT/'src/kinship/static/family.css').read_text('utf-8'))
    page.add_script_tag(content=(ROOT/'src/kinship/static/family.js').read_text('utf-8'))
    page.add_script_tag(content=(ROOT/'src/kinship/static/app.js').read_text('utf-8'))
    page.locator('#case-tag').get_attribute('title',timeout=6000)
    page.get_by_text('Synthetic sample',exact=False).first.wait_for()
    assert page.locator('#stat-people').inner_text()=='3'
    page.locator('#family-map .family-person-card').first.wait_for(timeout=6000)
    assert 'Links are claims' in page.locator('#family-map').inner_text()
    page.locator('#search-query').fill('Nguyen Van An')
    page.locator('#search-form button[type=submit]').click()
    page.wait_for_function("document.querySelector('#results-count').textContent.includes('matching')",timeout=4000)
    assert page.locator('.result-item').count() >= 1
    page.locator('.result-item').first.click()
    page.locator('#detail-body').get_by_text('Nguyễn Văn An').first.wait_for()
    page.locator('.nav-button[data-view=sources]').click()
    page.locator('#region-select').select_option('china')
    page.get_by_text('Shanghai Library',exact=False).first.wait_for(timeout=6000)
    page.locator('.nav-button[data-view=research]').click()
    page.locator('#agent-submit').click()
    page.locator('#agent-result').get_by_text('guided-offline',exact=False).first.wait_for(timeout=5000)
    page.locator('.nav-button[data-view=evidence]').click()
    page.locator('#audit-result').get_by_text('Structural audit passed',exact=False).first.wait_for(timeout=5000)
    page.locator('.nav-button[data-view=explore]').click()
    page.locator('#gedcom-file').set_input_files(str(ROOT/'examples/synthetic-gedcom-551.ged'))
    page.locator('#case-tag').get_by_text('Private GEDCOM import',exact=False).wait_for(timeout=8000)
    page.locator('#family-map').get_by_text('Possible parents',exact=False).first.wait_for(timeout=5000)
    assert page.locator('#stat-people').inner_text()=='3'
    assert 'source groups' in page.locator('#family-map').inner_text()
    page.locator('#load-demo').click()
    page.locator('#case-tag').get_by_text('Synthetic sample',exact=False).wait_for(timeout=6000)
    if errors: raise AssertionError((label,errors))
    doc_width=page.evaluate('document.documentElement.scrollWidth')
    client_width=page.evaluate('document.documentElement.clientWidth')
    assert doc_width<=client_width+2,(label,'overflow',doc_width,client_width)
    return {'view':label,'js_errors':errors,'width':client_width,'overflow':doc_width-client_width}

server=Workbench(('127.0.0.1',0));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();URL=f'http://127.0.0.1:{server.server_port}'
try:
 with sync_playwright() as p:
  exe=shutil.which('chromium') or shutil.which('google-chrome')
  browser=p.chromium.launch(headless=True,**({'executable_path':exe,'args':['--no-sandbox']} if exe else {}))
  try:
   results=[]
   for width,height,label in [(1440,900,'desktop'),(390,844,'mobile')]:
    page=browser.new_page(viewport={'width':width,'height':height})
    try:results.append(exercise(page,label))
    finally:page.close()
   print(json.dumps({'status':'passed','results':results},ensure_ascii=False,indent=2))
  finally:browser.close()
finally:
 server.shutdown();server.server_close();thread.join(timeout=3)