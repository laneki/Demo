const API_BASE = window.location.hostname === 'localhost'
  ? 'http://localhost:8000'
  : `${window.location.protocol}//${window.location.hostname}:8000`;

const countersEl = document.getElementById('counters');
const eventsEl = document.getElementById('events');

const counterOrder = [
  'total_received',
  'authorized',
  'blocked',
  'ida_attack',
  'ida_normal',
  'vma_high_risk'
];

function renderCounters(metrics) {
  countersEl.innerHTML = '';
  counterOrder.forEach((key) => {
    const card = document.createElement('div');
    card.className = 'card';
    card.innerHTML = `<div class="label">${key}</div><div class="value">${metrics[key] ?? 0}</div>`;
    countersEl.appendChild(card);
  });
}

function renderEvents(items) {
  eventsEl.innerHTML = '';
  items.forEach((ev) => {
    const div = document.createElement('div');
    div.className = 'event';
    div.innerHTML = `
      <div class="meta">${ev.timestamp} · ${ev.event_type}</div>
      <pre>${JSON.stringify(ev.payload, null, 2)}</pre>
    `;
    eventsEl.appendChild(div);
  });
}

async function refresh() {
  try {
    const [mRes, eRes] = await Promise.all([
      fetch(`${API_BASE}/api/metrics`),
      fetch(`${API_BASE}/api/events`)
    ]);
    const metrics = await mRes.json();
    const events = await eRes.json();
    renderCounters(metrics);
    renderEvents(events.items || []);
  } catch (err) {
    console.error('Refresh failed', err);
  }
}

refresh();
setInterval(refresh, 1000);
