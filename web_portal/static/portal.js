async function fetchJSON(url, opts={}) {
  const res = await fetch(url, {
    headers: { 'Content-Type': 'application/json' },
    credentials: 'same-origin',
    ...opts
  });
  return res.json();
}

function el(tag, attrs={}, children=[]) {
  const e = document.createElement(tag);
  Object.entries(attrs).forEach(([k,v]) => {
    if (k === 'class') e.className = v; else e.setAttribute(k, v);
  });
  (Array.isArray(children) ? children : [children]).forEach(c => {
    if (typeof c === 'string') e.appendChild(document.createTextNode(c));
    else if (c) e.appendChild(c);
  });
  return e;
}

async function loadProfessions() {
  const data = await fetchJSON('/api/professions');
  const list = document.getElementById('professions');
  const sel = document.getElementById('professionSelect');
  list.innerHTML = '';
  sel.innerHTML = '';
  (data.professions || []).forEach(p => {
    list.appendChild(el('li', {}, p));
    sel.appendChild(el('option', { value: p }, p));
  });
}

async function loadTenders() {
  const data = await fetchJSON('/api/tenders');
  const wrap = document.getElementById('tenders');
  wrap.innerHTML = '';
  const tenders = data.tenders || [];
  const bids = data.bids || [];
  tenders.forEach(t => {
    const tbids = bids.filter(b => b.tender_id === t.id);
    const card = el('div', { class: 'card' }, [
      el('h3', {}, t.title + ' [' + t.profession + ']'),
      el('div', { class: 'muted' }, `Budget: ${t.budget} | Deadline: ${t.deadline}`),
      el('p', {}, t.description || ''),
      el('div', {}, `Bids: ${tbids.length}`),
    ]);
    const form = el('form', { class: 'inlineForm' }, [
      el('input', { name: 'bidder_name', placeholder: 'Your name', required: 'true' }),
      el('input', { name: 'bid_amount', type: 'number', min: '0', step: '1', required: 'true', placeholder: 'Amount' }),
      el('input', { name: 'message', placeholder: 'Short message', required: 'true' }),
      el('button', { type: 'submit' }, 'Place Bid')
    ]);
    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const fd = new FormData(form);
      const payload = {
        tender_id: t.id,
        bidder_name: fd.get('bidder_name'),
        bid_amount: Number(fd.get('bid_amount')),
        message: fd.get('message')
      };
      const res = await fetchJSON('/api/bids', { method: 'POST', body: JSON.stringify(payload) });
      if (res.ok) {
        await loadTenders();
      } else {
        alert('Bid failed: ' + (res.error || 'unknown'));
      }
    });

    const auto = el('button', { class: 'secondary' }, 'Auto-bid (Agent)');
    auto.addEventListener('click', async () => {
      const res = await fetchJSON('/api/auto_bid', { method: 'POST', body: JSON.stringify({ tender_id: t.id, profession: t.profession }) });
      if (res.ok) await loadTenders(); else alert('Auto-bid failed');
    });

    card.appendChild(form);
    card.appendChild(auto);
    wrap.appendChild(card);
  });
}

async function initCreateTender() {
  const form = document.getElementById('tenderForm');
  const out = document.getElementById('tenderCreateResult');
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const fd = new FormData(form);
    const payload = Object.fromEntries(fd.entries());
    payload.budget = Number(payload.budget);
    payload.consent = !!fd.get('consent');
    const res = await fetchJSON('/api/tenders', { method: 'POST', body: JSON.stringify(payload) });
    out.textContent = res.ok ? 'Tender created!' : ('Error: ' + (res.error || 'unknown'));
    if (res.ok) {
      form.reset();
      await loadTenders();
    }
  });
}

function initConsent() {
  const bar = document.getElementById('consent');
  const btn = document.getElementById('acceptConsent');
  const key = 'portalConsentV1';
  if (!localStorage.getItem(key)) bar.classList.remove('hidden');
  btn.addEventListener('click', () => { localStorage.setItem(key, '1'); bar.classList.add('hidden'); });
}

(async function main() {
  initConsent();
  await loadProfessions();
  await initCreateTender();
  await loadTenders();
})();