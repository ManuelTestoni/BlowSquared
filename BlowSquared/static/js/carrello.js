// Cart JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    // Quantity controls
    const quantityBtns = document.querySelectorAll('.quantity-btn');
    const quantityInputs = document.querySelectorAll('.quantity-input');
    
    quantityBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const action = this.dataset.action;
            const input = this.parentElement.querySelector('.quantity-input');
            let currentValue = parseInt(input.value);
            
            if (action === 'increase') {
                currentValue++;
            } else if (action === 'decrease' && currentValue > 1) {
                currentValue--;
            }
            
            input.value = currentValue;
            updateItemTotal(this.closest('.cart-item'));
        });
    });
    
    quantityInputs.forEach(input => {
        input.addEventListener('change', function() {
            if (this.value < 1) this.value = 1;
            if (this.value > 99) this.value = 99;
            updateItemTotal(this.closest('.cart-item'));
        });
    });
    
    // Remove item buttons
    const removeButtons = document.querySelectorAll('.btn-remove-item');
    removeButtons.forEach(btn => {
        btn.addEventListener('click', function() {
            const itemId = this.dataset.itemId;
            const cartItem = this.closest('.cart-item');
            
            if (confirm('Sei sicuro di voler rimuovere questo prodotto dal carrello?')) {
                removeCartItem(cartItem, itemId);
            }
        });
    });
    
    // Clear cart button
    const clearCartBtn = document.querySelector('.btn-clear-cart');
    if (clearCartBtn) {
        clearCartBtn.addEventListener('click', function() {
            if (confirm('Sei sicuro di voler svuotare completamente il carrello?')) {
                clearCart();
            }
        });
    }
    
    // Checkout button - Rimuovo la gestione onclick perché ora è un link
    const checkoutBtn = document.querySelector('.btn-checkout');
    if (checkoutBtn && checkoutBtn.tagName === 'BUTTON') {
        checkoutBtn.addEventListener('click', function() {
            // Se per qualche motivo è ancora un button, redirigi al checkout
            window.location.href = '/carrello/checkout/';
        });
    }
});

function updateItemTotal(cartItem) {
    const quantityInput = cartItem.querySelector('.quantity-input');
    const unitPriceText = cartItem.querySelector('.item-unit-price').textContent;
    const totalPriceElement = cartItem.querySelector('.item-total-price');
    
    // Estrai il prezzo unitario (rimuovi € e "cad.")
    const unitPrice = parseFloat(unitPriceText.replace('€', '').replace('cad.', '').trim());
    const quantity = parseInt(quantityInput.value);
    const total = unitPrice * quantity;
    
    totalPriceElement.textContent = '€' + total.toFixed(2);
    
    // Aggiorna il riepilogo ordine
    updateOrderSummary();
}

function removeCartItem(cartItem, itemId) {
    // Animazione di rimozione
    cartItem.style.animation = 'slideOut 0.3s ease';
    
    setTimeout(() => {
        cartItem.remove();
        updateOrderSummary();
        
        // Controlla se il carrello è vuoto
        const remainingItems = document.querySelectorAll('.cart-item');
        if (remainingItems.length === 0) {
            showEmptyCartMessage();
        }
    }, 300);
}

function clearCart() {
    const cartItems = document.querySelectorAll('.cart-item');
    cartItems.forEach((item, index) => {
        setTimeout(() => {
            item.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => item.remove(), 300);
        }, index * 100);
    });
    
    setTimeout(() => {
        showEmptyCartMessage();
    }, cartItems.length * 100 + 300);
}

function updateOrderSummary() {
    const cartItems = document.querySelectorAll('.cart-item');
    let subtotal = 0;
    let totalQuantity = 0;
    
    cartItems.forEach(item => {
        const quantity = parseInt(item.querySelector('.quantity-input').value);
        const totalPrice = parseFloat(item.querySelector('.item-total-price').textContent.replace('€', ''));
        
        subtotal += totalPrice;
        totalQuantity += quantity;
    });
    
    // Aggiorna subtotale
    const subtotalElement = document.querySelector('.summary-row .summary-value');
    if (subtotalElement) {
        subtotalElement.textContent = '€' + subtotal.toFixed(2);
    }
    
    // Calcola spedizione
    const soglia = 30.00;
    const costoSpedizione = subtotal >= soglia ? 0 : 4.90;
    const totale = subtotal + costoSpedizione;
    
    // Aggiorna spedizione
    const shippingElement = document.querySelector('.shipping-row .summary-value');
    if (shippingElement) {
        if (costoSpedizione === 0) {
            shippingElement.innerHTML = '<span class="free-shipping">GRATIS</span>';
        } else {
            shippingElement.textContent = '€' + costoSpedizione.toFixed(2);
        }
    }
    
    // Aggiorna totale
    const totalElement = document.querySelector('.total-value');
    if (totalElement) {
        totalElement.textContent = '€' + totale.toFixed(2);
    }
}

function showEmptyCartMessage() {
    const cartLayout = document.querySelector('.cart-layout');
    if (cartLayout) {
        cartLayout.innerHTML = `
            <div class="empty-cart-centered">
                <div class="empty-cart">
                    <div class="empty-cart-icon">🛒</div>
                    <h2 class="empty-cart-title">Il Tuo Carrello è Vuoto</h2>
                    <p class="empty-cart-message">
                        Aggiungi prodotti al carrello per iniziare i tuoi acquisti
                    </p>
                    <a href="/prodotti/" class="btn-start-shopping">
                        <span class="btn-icon">🛍️</span>
                        Inizia a Fare Acquisti
                    </a>
                </div>
            </div>
        `;
    }
}

// CSS Animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        from { opacity: 1; transform: translateX(0); }
        to { opacity: 0; transform: translateX(-100%); }
    }
`;
document.head.appendChild(style);

