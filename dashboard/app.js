const cardsRoot = document.getElementById('cards');
const eventsRoot = document.getElementById('events');

const cardKeys = [
  'total_received',
  'authorized',
  'blocked',
  'ida_pred_attack',
  'ida_pred_normal',
  'vma_high_risk'
];

function renderCards(metrics) {
  cardsRoot.innerHTML = '';
  cardKeys.forEach((key) => {
    const card = document.createElement('div');
    card.className = 'card';
    card.innerHTML = `<div class="label">${key}</div><div class="value">${metrics[key] ?? 0}</div>`;
    cardsRoot.appendChild(card);
  });
}

function eventText(event) {
  const p = event.payload || {};
  if (event.type === 'authorized') return `${p.payload?.device_id || '-'} authorized`;
  if (event.type === 'blocked') return `${p.payload?.device_id || '-'} blocked`;
  if (event.type === 'ida') return `${p.device_id || '-'} prediction=${p.prediction} score=${(p.score ?? 0).toFixed ? (p.score ?? 0).toFixed(2) : p.score}`;
  if (event.type === 'vma') return `${p.device_id || '-'} risk=${p.risk_score} factors=${(p.factors || []).join(',')}`;
  return JSON.stringify(event);
}

function renderEvents(events) {
  eventsRoot.innerHTML = '';
  events.forEach((ev) => {
    const li = document.createElement('li');
    li.innerHTML = `<span class="badge ${ev.type}">${ev.type}</span>${eventText(ev)}`;
    eventsRoot.appendChild(li);
  });
}

async function poll() {
  try {
    const [mRes, eRes] = await Promise.all([
      fetch('/api/metrics'),
      fetch('/api/events')
    ]);
    const metrics = await mRes.json();
    const events = await eRes.json();
    renderCards(metrics);
    renderEvents(events.events || []);
  } catch (err) {
    console.error(err);
  }
}

setInterval(poll, 1000);
poll();
