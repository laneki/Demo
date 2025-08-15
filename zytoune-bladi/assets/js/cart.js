const CART_KEY = 'zb-cart';
let cart = JSON.parse(localStorage.getItem(CART_KEY) || '[]');

function save(){ localStorage.setItem(CART_KEY, JSON.stringify(cart)); renderMini(); }

export function addToCart(id, qty=1){
  const item = cart.find(i=>i.id===id);
  if(item) item.qty += qty; else cart.push({id, qty});
  save();
}

export function removeFromCart(id){ cart = cart.filter(i=>i.id!==id); save(); }

export function clearCart(){ cart = []; save(); }

function subtotal(){ return cart.reduce((s,i)=>s+i.qty*10,0); } // mock price

function renderMini(){
  const countEl = document.getElementById('cart-count');
  if(countEl) countEl.textContent = cart.reduce((s,i)=>s+i.qty,0);
  const list = document.getElementById('mini-cart-items');
  if(list){
    list.innerHTML='';
    cart.forEach(i=>{
      const div=document.createElement('div');
      div.textContent=`Item ${i.id} x${i.qty}`;
      list.appendChild(div);
    });
    const sub=document.getElementById('mini-cart-subtotal');
    if(sub) sub.textContent=`$${subtotal().toFixed(2)}`;
  }
}

document.addEventListener('DOMContentLoaded',()=>{
  renderMini();
  document.body.addEventListener('click',e=>{
    if(e.target.classList.contains('add-to-cart')){
      const id=e.target.dataset.productId; addToCart(id); alert('Added to cart');
    }
  });
});

// Render cart page
function renderCartPage(){
  const container=document.getElementById('cart-items');
  if(!container) return;
  container.innerHTML='';
  cart.forEach(i=>{
    const div=document.createElement('div');
    div.textContent=`Product ${i.id} qty ${i.qty}`;
    container.appendChild(div);
  });
  document.getElementById('subtotal').textContent=`$${subtotal().toFixed(2)}`;
  const vat=subtotal()*0.2; document.getElementById('vat').textContent=`$${vat.toFixed(2)}`;
  document.getElementById('total').textContent=`$${(subtotal()+vat).toFixed(2)}`;
}

document.addEventListener('DOMContentLoaded',renderCartPage);
