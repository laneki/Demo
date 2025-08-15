export function includeHTML() {
  const elements = document.querySelectorAll('[data-include]');
  return Promise.all([...elements].map(el => {
    const file = el.getAttribute('data-include');
    if (!file) return Promise.resolve();
    return fetch(file).then(r => r.text()).then(html => { el.innerHTML = html; });
  }));
}

export function debounce(fn, ms=300){
  let t; return (...args)=>{ clearTimeout(t); t=setTimeout(()=>fn.apply(this,args),ms); };
}

export function toggle(el){
  el.hidden = !el.hidden;
}

export function trapFocus(container){
  const focusable = container.querySelectorAll('a,button,input,select,textarea');
  const first = focusable[0];
  const last = focusable[focusable.length -1];
  container.addEventListener('keydown', e => {
    if(e.key === 'Tab'){
      if(e.shiftKey && document.activeElement === first){e.preventDefault(); last.focus();}
      else if(!e.shiftKey && document.activeElement === last){e.preventDefault(); first.focus();}
    }
  });
}

export function accordion(){
  document.querySelectorAll('.accordion__toggle').forEach(btn=>{
    btn.addEventListener('click',()=>{
      const expanded=btn.getAttribute('aria-expanded')==='true';
      btn.setAttribute('aria-expanded',!expanded);
      btn.nextElementSibling.hidden = expanded;
    });
  });
}
