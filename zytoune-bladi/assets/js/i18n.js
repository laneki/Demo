const defaultLang = 'en';
const lang = localStorage.getItem('lang') || defaultLang;
const html = document.documentElement;
fetch(`/data/i18n.${lang}.json`).then(r=>r.json()).then(dict=>{
  document.querySelectorAll('[data-i18n]').forEach(el=>{
    const key = el.getAttribute('data-i18n');
    if(dict[key]) el.textContent = dict[key];
  });
  if(lang === 'ar'){
    html.setAttribute('dir','rtl');
    html.setAttribute('lang','ar');
    const link = document.createElement('link');
    link.rel='stylesheet'; link.href='/assets/css/rtl.css';
    document.head.appendChild(link);
    document.body.style.fontFamily='Cairo, sans-serif';
  } else {
    html.setAttribute('dir','ltr');
    document.body.style.fontFamily='Inter, sans-serif';
  }
});

document.addEventListener('click',e=>{
  if(e.target.matches('[data-lang]')){
    const l = e.target.getAttribute('data-lang');
    localStorage.setItem('lang', l);
    location.reload();
  }
});
