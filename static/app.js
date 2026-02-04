(function () {
  document.addEventListener('click', function (e) {
    var btn = e.target.closest('[data-add-to-cart]');
    if (!btn) return;
    e.preventDefault();
    var productId = btn.getAttribute('data-product-id');
    
    fetch('/cart/add', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ product_id: productId, quantity: 1 })
    })
      .then(function (r) { return r.json(); })
      .then(function (data) {
        if (data.ok) {
          var el = document.getElementById('cart-count');
          if (el) el.textContent = data.cart_count;
          var old = btn.textContent;
          btn.textContent = 'Added!';
          setTimeout(function () { btn.textContent = old; }, 800);
        } else {
          console.error('Error adding to cart:', data.error);
          alert('Failed to add to cart: ' + (data.error || 'unknown'));
        }
      })
      .catch(function (err) { 
        console.error('Network error:', err);
        alert('Network error'); 
      });
  });
})();