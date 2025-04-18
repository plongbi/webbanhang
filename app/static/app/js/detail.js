document.addEventListener('DOMContentLoaded', function () {
  const quantityInput = document.querySelector('.quantity-control input');
  const minusBtn = document.querySelector('.quantity-btn.minus');
  const plusBtn = document.querySelector('.quantity-btn.plus');
  const addToCartBtn = document.querySelector('.btn.update-cart');

  // Tăng số lượng
  plusBtn.addEventListener('click', function () {
    let current = parseInt(quantityInput.value);
    if (current < parseInt(quantityInput.max)) {
      quantityInput.value = current + 1;
    }
  });

  // Giảm số lượng
  minusBtn.addEventListener('click', function () {
    let current = parseInt(quantityInput.value);
    if (current > parseInt(quantityInput.min)) {
      quantityInput.value = current - 1;
    }
  });

  // Thêm vào giỏ với đúng số lượng
  addToCartBtn.addEventListener('click', function () {
    const productId = this.getAttribute('data-product');
    const quantity = parseInt(quantityInput.value);

    // Gọi hàm updateUserOrder (nếu bạn có), truyền số lượng
    updateUserOrder(productId, 'add', quantity);
  });

  // Hàm gọi API hoặc Ajax thêm sản phẩm (tuỳ bạn xử lý backend thế nào)
  function updateUserOrder(productId, action, quantity) {
    fetch('/update_item/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
      },
      body: JSON.stringify({ 'productId': productId, 'action': action, 'quantity': quantity })
    })
    .then(response => response.json())
    .then(data => {
      console.log('Thêm thành công:', data);
      // Cập nhật giỏ hàng UI nếu muốn
    });
  }

  // Lấy CSRF token
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
});

