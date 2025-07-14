// Cart JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 CARRELLO.JS CARICATO');
    
    // Quantity controls
    const quantityBtns = document.querySelectorAll('.quantity-btn');
    const quantityInputs = document.querySelectorAll('.quantity-input');
    console.log(`🔍 TROVATI ${quantityBtns.length} pulsanti quantità`);
    console.log(`🔍 TROVATI ${quantityInputs.length} input quantità`);
    
    quantityBtns.forEach((btn, index) => {
        console.log(`   Pulsante ${index}: action="${btn.dataset.action}", item-id="${btn.dataset.itemId}"`);
        btn.addEventListener('click', function() {
            console.log(`🖱️ CLICK su pulsante quantità ${this.dataset.action}`);
            const action = this.dataset.action;
            const itemId = this.dataset.itemId;
            
            if (action === 'increase') {
                incrementQuantity(itemId);
            } else if (action === 'decrease') {
                decrementQuantity(itemId);
            }
        });
    });
    
    quantityInputs.forEach((input, index) => {
        console.log(`   Input ${index}: item-id="${input.dataset.itemId}"`);
        input.addEventListener('change', function() {
            console.log(`🖱️ CHANGE su input quantità`);
            if (this.value < 1) this.value = 1;
            if (this.value > 99) this.value = 99;
            
            const itemId = this.dataset.itemId;
            const newQuantity = parseInt(this.value);
            updateQuantity(itemId, newQuantity);
        });
    });
    
    // Remove item buttons
    const removeButtons = document.querySelectorAll('.btn-remove-item');
    console.log(`🔍 TROVATI ${removeButtons.length} pulsanti rimuovi`);
    
    removeButtons.forEach((btn, index) => {
        console.log(`   Pulsante rimuovi ${index}: item-id="${btn.dataset.itemId}"`);
        btn.addEventListener('click', function() {
            console.log(`🖱️ CLICK su pulsante rimuovi`);
            const itemId = this.dataset.itemId;
            
            if (confirm('Sei sicuro di voler rimuovere questo prodotto dal carrello?')) {
                removeCartItem(itemId);
            }
        });
    });
    
    // Clear cart button
    const clearCartBtn = document.querySelector('.btn-clear-cart');
    console.log(`🔍 PULSANTE SVUOTA CARRELLO:`, clearCartBtn ? 'TROVATO' : 'NON TROVATO');
    
    if (clearCartBtn) {
        clearCartBtn.addEventListener('click', function() {
            console.log(`🖱️ CLICK su pulsante svuota carrello`);
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
    
    // Carica il contatore del carrello all'avvio
    loadCartCounter();
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

function removeCartItem(itemId) {
    console.log(`🗑️ RIMUOVI ELEMENTO: ID ${itemId}`);
    
    // Chiamata AJAX per rimuovere dal backend
    fetch(`/carrello/rimuovi/${itemId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json',
        }
    })
    .then(response => {
        console.log(`📡 RISPOSTA RIMOZIONE:`, response.status);
        return response.json();
    })
    .then(data => {
        console.log(`📦 DATI RIMOZIONE:`, data);
        
        if (data.success) {
            // Trova l'elemento nel DOM e rimuovilo con animazione
            const cartItem = document.querySelector(`[data-item-id="${itemId}"]`).closest('.cart-item');
            cartItem.style.animation = 'slideOut 0.3s ease';
            
            setTimeout(() => {
                cartItem.remove();
                updateOrderSummary();
                console.log(`🔢 AGGIORNO CONTATORE DOPO RIMOZIONE: ${data.carrello_count}`);
                updateCartCounter(data.carrello_count);
                
                // Controlla se il carrello è vuoto
                const remainingItems = document.querySelectorAll('.cart-item');
                if (remainingItems.length === 0) {
                    showEmptyCartMessage();
                }
            }, 300);
            
            // Mostra messaggio di successo
            showNotification(data.message, 'success');
        } else {
            console.log(`❌ ERRORE RIMOZIONE:`, data.message);
            alert('Errore nella rimozione: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Errore:', error);
        alert('Errore di rete durante la rimozione');
    });
}

function incrementQuantity(itemId) {
    // Chiamata AJAX per incrementare quantità nel backend
    fetch(`/carrello/incrementa/${itemId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Aggiorna il DOM con i nuovi valori
            const cartItem = document.querySelector(`[data-item-id="${itemId}"]`).closest('.cart-item');
            const quantityInput = cartItem.querySelector('.quantity-input');
            const totalPriceElement = cartItem.querySelector('.item-total-price');
            
            quantityInput.value = data.quantita;
            totalPriceElement.textContent = '€' + data.elemento_prezzo_totale.toFixed(2);
            
            updateOrderSummary();
            updateCartCounter(data.carrello_count);
            
            // Mostra messaggio di successo
            showNotification(data.message, 'success');
        } else {
            alert('Errore nell\'incremento: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Errore:', error);
        alert('Errore di rete durante l\'incremento');
    });
}

function decrementQuantity(itemId) {
    // Chiamata AJAX per decrementare quantità nel backend
    fetch(`/carrello/decrementa/${itemId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Aggiorna il DOM con i nuovi valori
            const cartItem = document.querySelector(`[data-item-id="${itemId}"]`).closest('.cart-item');
            const quantityInput = cartItem.querySelector('.quantity-input');
            const totalPriceElement = cartItem.querySelector('.item-total-price');
            
            quantityInput.value = data.quantita;
            totalPriceElement.textContent = '€' + data.elemento_prezzo_totale.toFixed(2);
            
            updateOrderSummary();
            updateCartCounter(data.carrello_count);
            
            // Mostra messaggio di successo
            showNotification(data.message, 'success');
        } else {
            alert('Errore nel decremento: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Errore:', error);
        alert('Errore di rete durante il decremento');
    });
}

function updateQuantity(itemId, newQuantity) {
    // Chiamata AJAX per aggiornare quantità nel backend
    const formData = new FormData();
    formData.append('quantita', newQuantity);
    
    fetch(`/carrello/aggiorna/${itemId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Aggiorna il DOM con i nuovi valori
            const cartItem = document.querySelector(`[data-item-id="${itemId}"]`).closest('.cart-item');
            const totalPriceElement = cartItem.querySelector('.item-total-price');
            
            totalPriceElement.textContent = '€' + data.elemento_prezzo_totale.toFixed(2);
            
            updateOrderSummary();
            updateCartCounter(data.carrello_count);
            
            // Mostra messaggio di successo
            showNotification(data.message, 'success');
        } else {
            alert('Errore nell\'aggiornamento: ' + data.message);
            // Ripristina il valore precedente se l'aggiornamento fallisce
            location.reload();
        }
    })
    .catch(error => {
        console.error('Errore:', error);
        alert('Errore di rete durante l\'aggiornamento');
        location.reload();
    });
}

function clearCart() {
    // Chiamata AJAX per svuotare il carrello nel backend
    fetch('/carrello/svuota/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Animazione di rimozione elementi
            const cartItems = document.querySelectorAll('.cart-item');
            cartItems.forEach((item, index) => {
                setTimeout(() => {
                    item.style.animation = 'slideOut 0.3s ease';
                    setTimeout(() => item.remove(), 300);
                }, index * 100);
            });
            
            setTimeout(() => {
                showEmptyCartMessage();
                // Aggiorna il contatore del carrello
                updateCartCounter(0);
            }, cartItems.length * 100 + 300);
        } else {
            alert('Errore nello svuotamento del carrello: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Errore:', error);
        alert('Errore di rete durante lo svuotamento del carrello');
    });
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

// Funzione per ottenere il CSRF token dai cookie
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

// Funzione per aggiornare il contatore del carrello nella navbar
function updateCartCounter(count) {
    const cartCounter = document.getElementById('cartCounter');
    if (cartCounter) {
        if (count > 0) {
            cartCounter.textContent = count;
            cartCounter.style.display = 'block';
        } else {
            cartCounter.style.display = 'none';
        }
    }
}

// Funzione per caricare il contatore del carrello all'avvio della pagina
function loadCartCounter() {
    fetch('/carrello/api/count/', {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateCartCounter(data.count);
        }
    })
    .catch(error => {
        console.error('Errore nel caricamento del contatore carrello:', error);
    });
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

// Funzione per mostrare notifiche
function showNotification(message, type = 'info') {
    // Crea un elemento notifica
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    // Stili per la notifica
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#4CAF50' : type === 'error' ? '#f44336' : '#2196F3'};
        color: white;
        padding: 12px 20px;
        border-radius: 4px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.2);
        z-index: 10000;
        font-size: 14px;
        max-width: 300px;
        animation: slideInFromRight 0.3s ease;
    `;
    
    // Aggiungi al documento
    document.body.appendChild(notification);
    
    // Rimuovi dopo 3 secondi
    setTimeout(() => {
        notification.style.animation = 'slideOutToRight 0.3s ease';
        setTimeout(() => {
            if (notification.parentNode) {
                notification.parentNode.removeChild(notification);
            }
        }, 300);
    }, 3000);
}

// Aggiungi animazioni per le notifiche
const notificationStyle = document.createElement('style');
notificationStyle.textContent = `
    @keyframes slideInFromRight {
        from { opacity: 0; transform: translateX(100%); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes slideOutToRight {
        from { opacity: 1; transform: translateX(0); }
        to { opacity: 0; transform: translateX(100%); }
    }
`;
document.head.appendChild(notificationStyle);

