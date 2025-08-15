import { includeHTML, debounce, toggle, accordion } from './ui.js';

document.addEventListener('DOMContentLoaded', async () => {
  await includeHTML();
  accordion();
  
  document.querySelectorAll('[data-breadcrumb]').forEach(bc=>{
    const data=JSON.parse(bc.getAttribute('data-breadcrumb')||'[]');
    const nav=bc.querySelector('.breadcrumb');
    if(nav){
      const ol=document.createElement('ol');
      data.forEach((item,i)=>{
        const li=document.createElement('li');
        if(item.url && i<data.length-1){
          const a=document.createElement('a');a.href=item.url;a.textContent=item.name;li.appendChild(a);
        }else{li.textContent=item.name;}
        ol.appendChild(li);
      });
      nav.appendChild(ol);
    }
  });
  const yearEl = document.getElementById('year');
  if(yearEl) yearEl.textContent = new Date().getFullYear();

  // Back to top
  const backTop = document.createElement('button');
  backTop.id = 'back-top';
  backTop.className = 'btn';
  backTop.textContent = '↑';
  backTop.hidden = true;
  document.body.appendChild(backTop);
  backTop.addEventListener('click',()=>window.scrollTo({top:0,behavior:'smooth'}));
  window.addEventListener('scroll',()=>{backTop.hidden = window.scrollY < 300;});

  // WhatsApp button
  const wa = document.createElement('a');
  wa.href='https://wa.me/212600000000';
  wa.className='whatsapp-fab';
  wa.textContent='💬';
  wa.target='_blank';
  document.body.appendChild(wa);

  // Search
  const search = document.getElementById('search-input');
  if(search){
    const doSearch = debounce(q=>console.log('search', q),300);
    search.addEventListener('input',e=>doSearch(e.target.value));
  }

  // Mobile nav
  const menuBtn = document.getElementById('mobile-menu-open');
  const mobileNav = document.getElementById('mobile-nav');
  if(menuBtn && mobileNav){
    menuBtn.addEventListener('click',()=>toggle(mobileNav));
  }

  // Cart drawer
  const cartBtn = document.getElementById('cart-open');
  const cartDrawer = document.getElementById('cart-drawer');
  if(cartBtn && cartDrawer){
    cartBtn.addEventListener('click',()=>toggle(cartDrawer));
  }

  // Newsletter
  const news = document.getElementById('newsletter-form');
  if(news){
    news.addEventListener('submit',e=>{
      e.preventDefault();
      const email = news.querySelector('input').value;
      if(/^[^@]+@[^@]+\.[^@]+$/.test(email)){
        alert('Subscribed');
        news.reset();
      } else {
        alert('Invalid email');
      }
    });
  }
});
