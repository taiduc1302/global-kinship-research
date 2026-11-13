// Browser-only state. No localStorage, analytics, auto-uploads or archive scraping.
const state = { case: null, regions: [], region: 'vietnam', kind: 'all', query: '',
  results: [], selected: null, mode: 'guided-offline', remote: false };
const $ = (id) => document.getElementById(id);
const make = (tag, className = '', text) => {
  const n = document.createElement(tag);
  if (className) n.className = className;
  if (text !== undefined) n.textContent = String(text);
  return n;
};
const clear = (el) => el.replaceChildren();
function appendText(parent, text, tag = 'p', className = '') {
  const p = make(tag, className, text);
  parent.append(p); return p;
}
function safeLink(url, label = 'Open source portal ↗') {
  try {
    const parsed = new URL(url);
    if (parsed.protocol !== 'https:') return null;
    const a = make('a', 'source-link', label);
    a.href = parsed.href; a.target = '_blank'; a.rel = 'noopener noreferrer';
    return a;
  } catch { return null; }
}
let toastHandle;
function notify(message) {
  const el = $('toast'); el.textContent = String(message); el.classList.add('visible');
  clearTimeout(toastHandle);
  toastHandle = setTimeout(() => el.classList.remove('visible'), 3700);
}
async function api(path, body = null) {
  const options = body === null ? {} : {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(body)};
  const res = await fetch(path, options);
  let data;
  try { data = await res.json(); } catch { throw new Error('Server did not return JSON'); }
  if (!res.ok) throw new Error(data.error || `Request failed (${res.status})`);
  return data;
}
function showView(name) {
  const views = {explore: 'Explore case', sources: 'Archive directory', research: 'Research assistant', evidence: 'Evidence review'};
  if (!(name in views)) return;
  for (const [key] of Object.entries(views)) $(`view-${key}`).hidden = key !== name;
  for (const b of document.querySelectorAll('.nav-button')) {
    const active = b.dataset.view === name;
    b.classList.toggle('active', active);
    if (active) b.setAttribute('aria-current', 'page'); else b.removeAttribute('aria-current');
  }
  $('breadcrumb').textContent = views[name];
  if (name === 'sources') refreshSources().catch(e => notify(e.message));
  if (name === 'evidence') renderEvidence();
  window.scrollTo({top: 0, behavior: 'smooth'});
}
function caseRows() {
  if (!state.case) return [];
  const records = [];
  for (const person of state.case.people || []) records.push({kind: 'people', id: person.id, title: person.names?.[0]?.original || person.id,
    description: 'Individual record · identity not confirmed'});
  for (const artifact of state.case.artifacts || []) records.push({kind: 'artifacts', id: artifact.id, title: artifact.citation,
    description: `Source group ${artifact.independence_group} · ${artifact.access || 'unknown access'}`});
  for (const claim of state.case.claims || []) records.push({kind: 'claims', id: claim.id, title: claim.literal_value || claim.type,
    description: `${claim.status} · ${claim.type}`});
  return records;
}
async function resetDemo() {
  const demo = await api('/api/demo');
  await useCase(demo.case, 'Synthetic sample');
  $('search-query').value = '';
  notify('Synthetic case restored. No real records included.');
}
async function useCase(value, label) {
  const audit = await api('/api/audit', {case: value});
  if (!audit.ok) throw new Error('Case rejected by evidence audit: ' + audit.findings.filter(x => x.level === 'error').map(x => x.code).slice(0, 4).join(', '));
  const summary = await api('/api/case-summary', {case: value});
  state.case = value; state.query = ''; state.selected = null;
  $('case-tag').textContent = `${label} · ${summary.case_id}`;
  $('stat-people').textContent = summary.people;
  $('stat-artifacts').textContent = summary.artifacts;
  $('stat-claims').textContent = summary.claims;
  $('stat-groups').textContent = summary.source_groups;
  $('search-query').value = '';
  $('case-tag').title = summary.visibility === 'synthetic' ? 'Synthetic data — safe for demo' : 'Sensitive case — local browser memory only';
  const firstRegion = (value.regions || []).find(r => state.regions.some(p => p.code === r));
  if (firstRegion) state.region = firstRegion;
  $('agent-region').value = state.region;
  $('region-select').value = state.region;
  state.results = caseRows();
  renderResults();
  clear($('detail-body'));
  $('detail-body').append(make('div', 'empty', 'Choose a record on the left to inspect its citations and source group.'));
  renderEvidence();
  document.dispatchEvent(new CustomEvent('kinship-case-loaded', {detail: {case: value}}));
}
function kindSymbol(kind) { return kind === 'people' ? '◉' : kind === 'artifacts' ? '▤' : '◇'; }
function renderResults() {
  const parent = $('results-list'); clear(parent);
  const rows = state.results.filter(r => state.kind === 'all' || r.kind === state.kind);
  $('results-count').textContent = `${rows.length}${state.query ? ' matching' : ' available'} records`;
  if (!rows.length) { appendText(parent, 'No matching records in this case. Try another spelling or open an official archive link.', 'p', 'result-empty'); return; }
  rows.forEach(record => {
    const button = make('button', 'result-item' + (state.selected === `${record.kind}:${record.id}` ? ' selected' : ''));
    button.type = 'button'; button.setAttribute('aria-label', `Open ${record.kind} ${record.title}`);
    button.append(make('div', `record-avatar ${record.kind}`, kindSymbol(record.kind)));
    const content = make('div', 'record-info');
    content.append(make('div', 'record-title', record.title), make('div', 'record-desc', record.description));
    button.append(content, make('span', 'record-arrow', '›'));
    button.addEventListener('click', () => openRecord(record.kind, record.id).catch(e => notify(e.message)));
    parent.append(button);
  });
}
function section(parent, title) { const s = make('section', 'detail-section'); s.append(make('h4', '', title)); parent.append(s); return s; }
function chip(parent, text, extra = '') { parent.append(make('span', `chip ${extra}`, text)); }
function renderPerson(detail) {
  const root = $('detail-body'); clear(root);
  const p = detail.person;
  appendText(root, 'PERSON RECORD · ' + p.id, 'div', 'detail-type');
  appendText(root, p.names?.[0]?.original || p.id, 'h3', 'detail-name');
  const tags = make('div', 'detail-meta');
  chip(tags, p.living === true ? 'Living · private' : p.living === false ? 'Recorded as deceased' : 'Living status unknown', p.living !== false ? 'negative' : '');
  root.append(tags);
  let s = section(root, 'Original name forms');
  (p.names || []).forEach(n => appendText(s, `${n.original}${n.language ? ' · ' + n.language : ''}${n.script ? ' / ' + n.script : ''}`, 'p', 'detail-ref'));
  s = section(root, 'Research claims linked to this person');
  if (!detail.claims.length) appendText(s, 'No claims cited in this case.', 'p', 'small-note');
  detail.claims.forEach(c => appendText(s, `${c.id} · ${c.type} · ${c.status} · ${c.artifact_ids?.join(', ') || 'no sources'}`, 'p', 'detail-ref'));
  s = section(root, 'Cited source records');
  if (!detail.artifacts.length) appendText(s, 'No records cited.', 'p', 'small-note');
  detail.artifacts.forEach(a => appendText(s, `${a.id}: ${a.citation} [group ${a.independence_group}]`, 'p', 'detail-ref'));
  appendText(root, detail.notice, 'p', 'small-note');
}
function renderArtifact(detail) {
  const root = $('detail-body'); clear(root);
  const a = detail.artifact;
  appendText(root, 'SOURCE RECORD · ' + a.id, 'div', 'detail-type');
  appendText(root, a.citation, 'h3', 'detail-name');
  const tags = make('div', 'detail-meta'); chip(tags, `Group ${a.independence_group}`); chip(tags, a.access || 'Access not stated'); root.append(tags);
  if (a.url) { const s = section(root, 'Original source URL'); const link = safeLink(a.url, 'Open original record ↗');
    if (link) s.append(link); else appendText(s, 'URL not safely openable (HTTPS required)', 'p', 'small-note'); }
  let s = section(root, 'Dependent copies from the same source');
  appendText(s, detail.independent.join(', '), 'div', 'detail-value');
  s = section(root, 'Claims referencing this record');
  if (!detail.claims.length) appendText(s, 'Not cited by any claim.', 'p', 'small-note');
  detail.claims.forEach(c => appendText(s, `${c.id} · ${c.type} · ${c.status}`, 'div', 'detail-ref'));
  appendText(root, detail.notice, 'p', 'small-note');
}
function renderClaim(claim) {
  const root = $('detail-body'); clear(root);
  appendText(root, 'EVIDENCE CLAIM · ' + claim.id, 'div', 'detail-type');
  appendText(root, claim.literal_value || claim.type, 'h3', 'detail-name');
  const tags = make('div', 'detail-meta'); chip(tags, claim.status); chip(tags, claim.type); root.append(tags);
  let s = section(root, 'Relationship / factual assertion');
  appendText(s, `${claim.subject_id} ${claim.type} ${claim.object_id || claim.literal_value || ''}`, 'p', 'detail-value');
  s = section(root, 'Cited artifacts');
  const byId = new Map((state.case.artifacts || []).map(a => [a.id, a]));
  (claim.artifact_ids || []).forEach(id => { const a = byId.get(id); if (a) appendText(s, `${id} · ${a.citation} · group ${a.independence_group}`, 'p', 'detail-ref'); });
  if (!claim.artifact_ids?.length) appendText(s, 'No source IDs — this is not corroborated.', 'p', 'small-note');
  if (claim.notes) { s = section(root, 'Researcher notes'); appendText(s, claim.notes, 'p', 'detail-value'); }
  appendText(root, 'Status is a structural evidence threshold, not proof of ancestry.', 'p', 'small-note');
}
async function openRecord(kind, id) {
  if (!state.case) return;
  state.selected = `${kind}:${id}`; renderResults();
  if (kind === 'people') renderPerson(await api('/api/person', {case: state.case, person_id: id}));
  else if (kind === 'artifacts') renderArtifact(await api('/api/artifact', {case: state.case, artifact_id: id}));
  else { const claim = (state.case.claims || []).find(c => c.id === id); if (claim) renderClaim(claim); }
  if (window.innerWidth < 720) $('detail-body').scrollIntoView({behavior: 'smooth', block: 'center'});
}
async function doSearch() {
  if (!state.case) return;
  const query = $('search-query').value.trim(); state.query = query;
  const searched = query ? await api('/api/search', {case: state.case, query, kind: 'all'}) : null;
  state.results = searched ? searched.results : caseRows();
  state.selected = null; renderResults();
  if (searched?.truncated) notify('Showing the first 25 local matches. Refine your search.');
}
async function refreshSources() {
  const region = $('region-select').value || state.region;
  state.region = region; $('agent-region').value = region;
  const {sources} = await api(`/api/sources?region=${encodeURIComponent(region)}`);
  const root = $('source-list'); clear(root); $('source-count').textContent = `${sources.length} reviewed leads`;
  if (!sources.length) { appendText(root, 'No verified archive leads available.', 'p', 'small-note'); return; }
  for (const a of sources) {
    const card = make('article', 'source-card'); const left = make('div');
    appendText(left, a.institution, 'h3'); appendText(left, a.purpose);
    const tags = make('div', 'source-tags');
    tags.append(make('span', '', a.source_id), make('span', '', a.access), make('span', '', 'Manual portal'));
    left.append(tags); card.append(left);
    const right = make('div', 'source-action'); const link = safeLink(a.url, 'Open portal ↗');
    if (link) right.append(link); card.append(right); root.append(card);
  }
}
function renderAgent(data) {
  const root = $('agent-result'); clear(root);
  $('agent-run-state').textContent = data.mode === 'model-assisted' ? 'AI draft · review needed' : 'Offline research route';
  appendText(root, data.answer, 'p', 'detail-value');
  appendText(root, 'Execution mode: ' + data.mode, 'p', 'small-note');
  if (data.plan) {
    appendText(root, 'Queries to try (not executed)', 'h3');
    const ul = make('ul'); for (const q of data.plan.queries_to_try.slice(0, 8)) appendText(ul, q, 'li'); root.append(ul);
  }
  if (data.archive_leads?.length) {
    appendText(root, 'Suggested archive destinations', 'h3');
    for (const s of data.archive_leads) {
      const p = make('p', 'detail-ref'); const link = safeLink(s.url, s.institution || s.name);
      if (link) p.append(link); else p.textContent = s.institution || s.name;
      root.append(p);
    }
  }
  if (data.tool_trace?.length) {
    appendText(root, 'Tool execution trace', 'h3');
    const ul = make('ul'); for (const t of data.tool_trace) appendText(ul, `${t.name}: ${t.status}`, 'li'); root.append(ul);
  }
  appendText(root, data.limitations || 'Verify all claims against original sources.', 'p', 'small-note');
}
async function renderEvidence() {
  if (!state.case) return;
  const root = $('audit-result'); clear(root);
  const audit = await api('/api/audit', {case: state.case});
  appendText(root, audit.ok ? '✓ Structural audit passed' : 'Attention: evidence audit errors', 'div', audit.ok ? 'audit-ok' : 'audit-errors');
  if (!audit.findings.length) appendText(root, 'No structural findings. Historical truth and source authenticity have not been established.', 'p', 'small-note');
  else audit.findings.forEach(f => appendText(root, `${f.level.toUpperCase()} · ${f.code}: ${f.detail}`, 'div', 'audit-item'));
  const claims = $('claims-list'); clear(claims);
  for (const c of state.case.claims || []) {
    const button = make('button', 'claim-item'); button.type = 'button';
    const info = make('div'); appendText(info, c.id + ' · ' + c.type, 'strong'); appendText(info, c.status, 'span');
    button.append(info, make('span', '', `${c.artifact_ids?.length || 0} citations ›`));
    button.addEventListener('click', () => { showView('explore'); openRecord('claims', c.id).catch(e => notify(e.message)); });
    claims.append(button);
  }
}
async function init() {
  for (const nav of document.querySelectorAll('.nav-button')) nav.addEventListener('click', () => showView(nav.dataset.view));
  $('search-form').addEventListener('submit', e => { e.preventDefault(); doSearch().catch(err => notify(err.message)); });
  for (const b of document.querySelectorAll('.filter')) b.addEventListener('click', () => {
    state.kind = b.dataset.kind;
    document.querySelectorAll('.filter').forEach(x => { const on = x === b; x.classList.toggle('active', on); x.setAttribute('aria-pressed', String(on)); });
    renderResults();
  });
  $('case-file').addEventListener('change', async e => {
    const file = e.target.files?.[0]; if (!file) return;
    try {
      if (file.size > 512000) throw new Error('Local case limit is 512 KB');
      const json = JSON.parse(await file.text());
      await useCase(json, 'Local case'); notify('Loaded into browser memory only. Nothing saved to disk.');
    } catch (err) { notify(err.message); } finally { e.target.value = ''; }
  });
  $('gedcom-file').addEventListener('change', async event => {
    const file = event.target.files?.[0]; if (!file) return;
    try {
      if (file.size > 512000) throw new Error('GEDCOM import limit is 512 KB');
      const text = await file.text();
      const parsed = await api('/api/import-gedcom', {gedcom: text, region: state.region,
        case_id: 'local-gedcom', question: 'Review the evidence for relationships in this GEDCOM family file'});
      await useCase(parsed.case, 'Private GEDCOM import');
      notify('Imported family links as hypotheses; verify each original source.');
    } catch (error) { notify(error.message); }
    finally { event.target.value = ''; }
  });
  $('load-demo').addEventListener('click', () => resetDemo().catch(e => notify(e.message)));
  $('region-select').addEventListener('change', () => refreshSources().catch(e => notify(e.message)));
  $('agent-region').addEventListener('change', e => { state.region = e.target.value; $('region-select').value = state.region; });
  $('run-audit').addEventListener('click', () => renderEvidence().catch(e => notify(e.message)));
  $('agent-form').addEventListener('submit', async e => {
    e.preventDefault(); if (!state.case) return;
    const button = $('agent-submit'); button.disabled = true; $('agent-run-state').textContent = 'Running tools…';
    try {
      const data = await api('/api/agent', {case: state.case, region: $('agent-region').value,
        question: $('agent-question').value, remote_consent: $('remote-consent').checked});
      renderAgent(data);
    } catch(err) { $('agent-run-state').textContent = 'Request rejected'; notify(err.message); }
    finally { button.disabled = false; }
  });
  const [health, regions] = await Promise.all([api('/api/health'), api('/api/regions')]);
  state.mode = health.agent_mode; state.remote = health.remote_model; state.regions = regions.regions;
  $('model-status').textContent = state.mode === 'model-assisted' ? 'AI tools enabled' : 'Guided offline tools';
  $('remote-consent-wrap').hidden = !state.remote;
  for (const select of [$('region-select'), $('agent-region')]) {
    for (const region of regions.regions) {
      const option = make('option', '', region.name); option.value = region.code; select.append(option);
    }
    select.value = state.region;
  }
  await useCase((await api('/api/demo')).case, 'Synthetic sample');
}
init().catch(e => notify('Unable to initialize local workbench: ' + e.message));
