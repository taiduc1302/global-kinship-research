// One-generation claim map. It never decides identity, parentage, or source truth.
const el = (id) => document.getElementById(id);
const newEl = (tag, className, label) => {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (label !== undefined) node.textContent = String(label);
  return node;
};
let graph = null;
let selected = '';
const ids = new Map();

function relativeCard(person, link) {
  const card = newEl('button', 'family-person-card');
  card.type = 'button';
  const title = newEl('strong', '', person.label);
  const meta = newEl('small', '', link
    ? `${link.relationship.replaceAll('_', ' ')} · ${link.status} · ${link.independent_source_groups.length} source groups`
    : (person.living === false ? 'Recorded as deceased' : 'Living status unknown / private'));
  card.append(title, meta);
  if (link) {
    const citation = newEl('small', 'family-claim', `Claim ${link.claim_id} · ${link.source_ids.length} citations`);
    card.append(citation);
  }
  card.addEventListener('click', () => {
    selected = person.id;
    el('tree-focus').value = selected;
    drawFocus();
  });
  return card;
}

function renderColumn(title, edges, relation) {
  const column = newEl('section', 'family-column');
  column.append(newEl('h3', '', title));
  if (!edges.length) {
    column.append(newEl('p', 'family-empty', 'No recorded links in this case'));
    return column;
  }
  const seen = new Set();
  for (const edge of edges) {
    const otherId = relation(edge);
    const person = ids.get(otherId);
    if (!person || seen.has(edge.claim_id)) continue;
    seen.add(edge.claim_id);
    column.append(relativeCard(person, edge));
  }
  return column;
}

function drawFocus() {
  const container = el('family-map');
  container.replaceChildren();
  if (!graph || !ids.has(selected)) {
    container.append(newEl('p', 'family-empty', 'Open a case to explore its recorded family connections.'));
    return;
  }
  const parentLinks = graph.edges.filter(x => x.relationship === 'parent_of' && x.to === selected);
  const childLinks = graph.edges.filter(x => x.relationship === 'parent_of' && x.from === selected);
  const partnerLinks = graph.edges.filter(x => x.relationship === 'spouse_of' && (x.from === selected || x.to === selected));
  const layout = newEl('div', 'family-map-grid');
  layout.append(renderColumn('Possible parents', parentLinks, x => x.from));
  const center = newEl('section', 'family-column family-center');
  center.append(newEl('h3', '', 'Selected person'));
  center.append(relativeCard(ids.get(selected), null));
  center.append(newEl('p', 'family-note', 'Links are claims, not confirmed ancestry.'));
  layout.append(center);
  layout.append(renderColumn('Possible children', childLinks, x => x.to));
  container.append(layout);
  const partners = newEl('div', 'family-partners');
  partners.append(renderColumn('Possible spouses / partners', partnerLinks, x => x.from === selected ? x.to : x.from));
  container.append(partners);
  container.append(newEl('p', 'family-note', graph.notice));
}

document.addEventListener('kinship-case-loaded', async (event) => {
  const container = el('family-map');
  container.replaceChildren(newEl('p', 'family-empty', 'Loading local relationships…'));
  try {
    const response = await fetch('/api/graph', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({case: event.detail.case})
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Unable to inspect relationships');
    graph = data;
    ids.clear();
    for (const person of graph.nodes) ids.set(person.id, person);
    const focus = el('tree-focus'); focus.replaceChildren();
    for (const person of graph.nodes) {
      const option = newEl('option', '', person.label);
      option.value = person.id;
      focus.append(option);
    }
    selected = graph.edges.length ? graph.edges[0].to : (graph.nodes[0]?.id || '');
    focus.value = selected;
    drawFocus();
  } catch (error) {
    graph = null;
    container.replaceChildren(newEl('p', 'family-empty', String(error.message)));
  }
});

el('tree-focus').addEventListener('change', (event) => {
  selected = event.target.value;
  drawFocus();
});
