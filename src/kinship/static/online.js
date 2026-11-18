// Browser-only, explicitly initiated external catalog search; no localStorage or auto-queries.
const archiveEl = id => document.getElementById(id);
const resultsRoot = archiveEl('online-results');
const statusRoot = archiveEl('online-search-status');
const form = archiveEl('online-form');
const submit = archiveEl('online-submit');
const pager = archiveEl('online-pagination');
const prev = archiveEl('online-prev');
const next = archiveEl('online-next');
let lastPage = 1;
let lastHasNext = false;
let busy = false;
let searchVersion = 0;

function textElement(tag, className, value) {
  const el = document.createElement(tag);
  if (className) el.className = className;
  el.textContent = value == null ? '' : String(value);
  return el;
}
function statusMessage(message, error = false) {
  statusRoot.textContent = message;
  statusRoot.classList.toggle('is-error', error);
}
function archiveLink(url) {
  try {
    const parsed = new URL(url);
    if (parsed.protocol !== 'https:' || parsed.hostname !== 'www.loc.gov') return null;
    const link = textElement('a', 'source-link', 'Inspect original catalog item');
    link.href = parsed.href;
    link.target = '_blank';
    link.rel = 'noopener noreferrer';
    return link;
  } catch { return null; }
}
function displayRecord(record) {
  const article = textElement('article', 'online-result', '');
  article.append(textElement('h3', '', record.title_as_cataloged || 'Untitled catalog item'));
  const fields = [
    ['Record date', record.date_as_cataloged],
    ['Catalog location', record.location_as_cataloged],
    ['Contributors', record.contributors_as_cataloged],
    ['Source ID', record.source_id],
    ['Access', record.access_restricted === true ? 'Restricted; check collection access' : 'Review original access rules'],
  ];
  for (const [label, value] of fields) {
    if (value != null && value !== '') article.append(textElement('p', 'online-meta', `${label}: ${value}`));
  }
  if (record.description) article.append(textElement('p', '', record.description));
  if (record.rights_note) article.append(textElement('p', '', `Reuse terms: ${record.rights_note}`));
  article.append(textElement('p', 'small-note', 'Catalog lead only. Identity, relationship and original document are NOT verified.'));
  const link = archiveLink(record.record_url);
  if (link) article.append(link);
  const candidate = textElement('button', 'button button-soft online-add', 'Add as unverified lead to my case');
  candidate.type = 'button';
  candidate.addEventListener('click', () => document.dispatchEvent(
    new CustomEvent('kinship-add-archive-lead', {detail: {record}})));
  article.append(candidate);
  return article;
}
function showSearch(data) {
  if (!Array.isArray(data.results) || !data.pagination) throw new Error('Provider response was not complete');
  resultsRoot.replaceChildren();
  for (const record of data.results) resultsRoot.append(displayRecord(record));
  const count = data.results.length;
  archiveEl('online-result-count').textContent = `${count} catalog items shown · Page ${data.pagination.page}`;
  const known = data.pagination.total == null ? '' : `; provider reports ${data.pagination.total} indexed items`;
  if (data.status === 'no_results') {
    statusMessage('No catalog items were returned for this exact query. This is NOT proof that a person or record does not exist. Try another spelling, collection or archive.');
  } else if (data.status === 'incomplete') {
    statusMessage('The archive response could not be reliably interpreted. No record is asserted. Try a different query or review the archive directly.', true);
  } else {
    statusMessage(`${count} catalog leads returned from Library of Congress${known}. ${data.omitted_unusable_or_duplicate_rows || 0} incomplete/duplicate records omitted. No individuals were identified or linked.`);
  }
  lastPage = data.pagination.page;
  lastHasNext = data.pagination.has_next === true;
  prev.disabled = lastPage <= 1;
  next.disabled = !lastHasNext;
  archiveEl('online-page-label').textContent = `Page ${lastPage}`;
  pager.hidden = lastPage === 1 && !lastHasNext;
}
async function searchArchives(page) {
  if (busy) return;
  if (!archiveEl('online-consent').checked) {
    statusMessage('External transfer requires you to check the consent box.', true);
    return;
  }
  busy = true;
  submit.disabled = true;
  prev.disabled = true;
  next.disabled = true;
  const version = ++searchVersion;
  resultsRoot.replaceChildren();
  pager.hidden = true;
  archiveEl('online-result-count').textContent = 'Archive request pending';
  statusMessage('Contacting the official Library of Congress catalog. No records have been found or confirmed yet.');
  const yearFrom = archiveEl('online-year-start').value.trim();
  const yearTo = archiveEl('online-year-end').value.trim();
  const payload = {
    provider_id: 'loc', name: archiveEl('online-name').value.trim(),
    place: archiveEl('online-place').value.trim(),
    collection: archiveEl('online-collection').value,
    start_year: yearFrom === '' ? null : Number(yearFrom),
    end_year: yearTo === '' ? null : Number(yearTo),
    page, consent: true,
  };
  try {
    const response = await fetch('/api/search-archives', {
      method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(payload),
    });
    const data = await response.json();
    if (version !== searchVersion) return;
    if (!response.ok) {
      const wait = data.retry_after_seconds ? ` Retry after ${data.retry_after_seconds} seconds.` : '';
      throw new Error((data.error || `Archive request returned HTTP ${response.status}`) + wait);
    }
    if (!data.record_search_executed) throw new Error('Archive search was not executed');
    showSearch(data);
  } catch (error) {
    archiveEl('online-result-count').textContent = 'Search failed, not zero matches';
    statusMessage(`${error.message || 'Archive request failed'}. No conclusion about a person's existence was made.`, true);
  } finally {
    busy = false;
    submit.disabled = false;
    if (!pager.hidden) {
      prev.disabled = lastPage <= 1;
      next.disabled = !lastHasNext;
    }
  }
}

form.addEventListener('submit', event => {
  event.preventDefault();
  searchArchives(1);
});
prev.addEventListener('click', () => searchArchives(Math.max(1, lastPage - 1)));
next.addEventListener('click', () => searchArchives(lastPage + 1));
