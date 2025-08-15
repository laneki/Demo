import { includeHTML } from './ui.js';
import { addToCart } from './cart.js';

let products = [];
let page = 1; const perPage = 8;

function render(list){
  const grid = document.getElementById('product-grid') || document.getElementById('category-grid');
  if(!grid) return;
  const template = document.getElementById('product-card-template');
  grid.innerHTML='';
  list.forEach(p=>{
    const node = template.content.cloneNode(true);
    node.querySelector('.product-card__title').textContent=p.title;
    node.querySelector('.product-card__img').src=p.images[0];
    node.querySelector('.product-card__link').href=`/shop/product.html?slug=${p.slug}`;
    node.querySelector('.product-card__price').textContent=`$${p.price}`;
    node.querySelector('.add-to-cart').dataset.productId=p.id;
    grid.appendChild(node);
  });
}

function apply(){
  let list=[...products];
  const catSel=document.getElementById('category-filter');
  if(catSel && catSel.value) list=list.filter(p=>p.categoryId==catSel.value);
  const inStock=document.getElementById('in-stock');
  if(inStock && inStock.checked) list=list.filter(p=>p.stock>0);
  const start=(page-1)*perPage; const end=start+perPage;
  render(list.slice(start,end));
  const info=document.getElementById('page-info');
  if(info) info.textContent=`${page}/${Math.ceil(list.length/perPage)}`;
  document.getElementById('prev-page').disabled=page===1;
  document.getElementById('next-page').disabled=end>=list.length;
}

fetch('/data/products.json').then(r=>r.json()).then(data=>{products=data; apply();});

document.addEventListener('change',e=>{ if(['category-filter','in-stock'].includes(e.target.id)){page=1;apply();} });

document.addEventListener('click',e=>{
  if(e.target.id==='prev-page'){page--;apply();}
  if(e.target.id==='next-page'){page++;apply();}
});
