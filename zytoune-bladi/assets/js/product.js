import { addToCart } from './cart.js';

function initGallery(){
  const main=document.getElementById('main-image');
  document.querySelectorAll('.thumb').forEach(btn=>{
    btn.addEventListener('click',()=>{
      main.src=btn.dataset.src;
    });
  });
}

function initTabs(){
  const tabs=document.querySelectorAll('.tab');
  tabs.forEach(btn=>{
    btn.addEventListener('click',()=>{
      tabs.forEach(t=>t.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c=>c.classList.remove('active'));
      btn.classList.add('active');
      document.getElementById('tab-'+btn.dataset.tab).classList.add('active');
    });
  });
}

document.addEventListener('DOMContentLoaded',()=>{
  initGallery();
  initTabs();
  document.getElementById('add-to-cart')?.addEventListener('click',()=>addToCart(1,parseInt(document.getElementById('quantity').value)));
});
