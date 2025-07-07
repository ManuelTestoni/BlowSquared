// JavaScript per aggiungere prodotti al carrello

document.addEventListener('DOMContentLoaded', function() {
    // Gestione pulsanti "Aggiungi al carrello" nella lista prodotti
    const addToCartButtons = document.querySelectorAll('.btn-add-cart');
    addToCartButtons.forEach(button => {
        button.addEventListener('click', function() {
            const prodottoId = this.dataset.productId;
            if (prodottoId && !this.disabled) {
                aggiungiAlCarrello(prodottoId, 1, this);
            }
        });
    });
    
    // Gestione pulsante "Aggiungi al carrello" nel dettaglio prodotto
    const addToCartDetailButton = document.querySelector('.btn-add-cart-detail');
    if (addToCartDetailButton) {
        addToCartDetailButton.addEventListener('click', function() {
            const prodottoId = this.dataset.productId;
            const quantityInput = document.getElementById('quantity');
            const quantita = quantityInput ? parseInt(quantityInput.value) : 1;
            
            if (prodottoId && !this.disabled && quantita > 0) {
                aggiungiAlCarrello(prodottoId, quantita, this);
            }
        });
    }
    
    // Carica il contatore del carrello all'avvio
    loadCartCounter();
});

function aggiungiAlCarrello(prodottoId, quantita, button) {
    // Disabilita il pulsante durante la richiesta
    const originalText = button.innerHTML;
    button.disabled = true;
    button.innerHTML = '<span class="btn-icon">⏳</span> Aggiunta...';
    
    // Ottieni il token CSRF
    const csrfToken = getCookie('csrftoken');
    
    fetch(`/carrello/aggiungi/${prodottoId}/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrfToken,
            'X-Requested-With': 'XMLHttpRequest',
        },
        body: `quantita=${quantita}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Mostra messaggio di successo
            showNotification(data.message, 'success');
            
            // Aggiorna il pulsante temporaneamente
            button.innerHTML = '<span class="btn-icon">✅</span> Aggiunto!';
            button.style.background = '#27ae60';
            
            // Aggiorna contatore carrello
            updateCartCounter(data.carrello_count);
            
            // Ripristina il pulsante dopo 2 secondi
            setTimeout(() => {
                button.disabled = false;
                button.innerHTML = originalText;
                button.style.background = '';
            }, 2000);
            
        } else {
            // Mostra messaggio di errore
            showNotification(data.message, 'error');
            
            // Ripristina il pulsante
            button.disabled = false;
            button.innerHTML = originalText;
        }
    })
    .catch(error => {
        console.error('Errore:', error);
        showNotification('Errore di rete. Riprova.', 'error');
        
        // Ripristina il pulsante
        button.disabled = false;
        button.innerHTML = originalText;
    });
}

function updateCartCounter(count) {
    const cartCounter = document.getElementById('cartCounter');
    if (cartCounter) {
        cartCounter.textContent = count;
        if (count > 0) {
            cartCounter.style.display = 'flex';
            // Anima il contatore quando viene aggiornato
            cartCounter.style.animation = 'none';
            setTimeout(() => {
                cartCounter.style.animation = 'pulse 0.5s ease';
            }, 10);
        } else {
            cartCounter.style.display = 'none';
        }
    }
}

function loadCartCounter() {
    // Carica il numero di elementi nel carrello all'avvio della pagina
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

// Controlli quantità per la pagina di dettaglio
function changeQuantity(delta) {
    const quantityInput = document.getElementById('quantity');
    if (quantityInput) {
        let newValue = parseInt(quantityInput.value) + delta;
        const min = parseInt(quantityInput.min) || 1;
        const max = parseInt(quantityInput.max) || 99;
        
        if (newValue >= min && newValue <= max) {
            quantityInput.value = newValue;
        }
    }
}

function showNotification(message, type = 'info') {
    // Crea notifica temporanea
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span class="notification-icon">
                ${type === 'success' ? '✅' : type === 'error' ? '❌' : 'ℹ️'}
            </span>
            <span class="notification-message">${message}</span>
        </div>
    `;
    
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#27ae60' : type === 'error' ? '#e74c3c' : '#3498db'};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 10px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        z-index: 10000;
        font-weight: 600;
        animation: slideInRight 0.3s ease;
        max-width: 300px;
    `;
    
    document.body.appendChild(notification);
    
    // Rimuovi dopo 4 secondi
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 4000);
}

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

// CSS per le animazioni
if (!document.querySelector('#cart-animations')) {
    const style = document.createElement('style');
    style.id = 'cart-animations';
    style.textContent = `
        @keyframes slideInRight {
            from { opacity: 0; transform: translateX(100%); }
            to { opacity: 1; transform: translateX(0); }
        }
        
        @keyframes slideOutRight {
            from { opacity: 1; transform: translateX(0); }
            to { opacity: 0; transform: translateX(100%); }
        }
        
        .notification-content {
            display: flex;
            align-items: center;
            gap: 0.8rem;
        }
        
        .notification-icon {
            font-size: 1.2rem;
        }
    `;
    document.head.appendChild(style);
}
