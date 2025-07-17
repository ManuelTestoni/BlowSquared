// JavaScript per aggiungere prodotti al carrello

document.addEventListener('DOMContentLoaded', function() {
    
    // Gestione pulsanti "Aggiungi al carrello" nella lista prodotti
    const addToCartButtons = document.querySelectorAll('.btn-add-cart');
    
    
    addToCartButtons.forEach((button, index) => {
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
    
    // Validazione in tempo reale per l'input quantità
    const quantityInput = document.getElementById('quantity');
    if (quantityInput) {
        quantityInput.addEventListener('input', function() {
            const value = parseInt(this.value);
            const max = parseInt(this.getAttribute('max'));
            
            if (value > max) {
                this.style.borderColor = '#e74c3c';
                if (typeof showNotification === 'function') {
                    showNotification('Non ci sono abbastanza prodotti in magazzino', 'error');
                }
            } else {
                this.style.borderColor = '';
            }
        });
    }
    
    // Carica il contatore del carrello all'avvio
    if (typeof loadCartCounter === 'function') {
        loadCartCounter();
    }
});

function aggiungiAlCarrello(prodottoId, quantita, button) {
    
    // Verifica che le funzioni necessarie siano disponibili
    if (typeof getCookie !== 'function') {
        return;
    }
    if (typeof showNotification !== 'function') {
        return;
    }
    if (typeof updateCartCounter !== 'function') {
        return;
    }
    
    // Validazione della quantità prima di inviare la richiesta
    if (!validateQuantityStock(prodottoId, quantita)) {
        return;
    }
    
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
    .then(response => {
        return response.json();
    })
    .then(data => {
        console.log('Risposta dal server:', data); // Debug
        
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
            if (data.redirect_login) {
                // Per utenti non autenticati, mostra un messaggio specifico
                showNotification(data.message, 'info');
                
                // Opzionale: reindirizza al login dopo qualche secondo
                setTimeout(() => {
                    window.location.href = '/utenti/login/';
                }, 2000);
            } else {
                showNotification(data.message, 'error');
            }
            
            // Ripristina immediatamente il pulsante in caso di errore
            button.disabled = false;
            button.innerHTML = originalText;
            button.style.background = '';
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

// Funzione per validare la quantità richiesta contro lo stock disponibile
function validateQuantityStock(prodottoId, quantita) {
    // Cerca le informazioni del prodotto nella pagina corrente
    const productInfo = getProductStockInfo(prodottoId);
    
    if (!productInfo) {
        // Se non trova le informazioni del prodotto, lascia che sia il server a gestire l'errore
        return true;
    }
    
    const stockDisponibile = productInfo.stock;
    const quantitaGiaInCarrello = getQuantityInCart(prodottoId);
    const quantitaTotale = quantita + quantitaGiaInCarrello;
    
    if (quantitaTotale > stockDisponibile) {
        const messaggioErrore = `Non ci sono abbastanza prodotti in magazzino. Disponibili: ${stockDisponibile}, già nel carrello: ${quantitaGiaInCarrello}`;
        
        if (typeof showNotification === 'function') {
            showNotification(messaggioErrore, 'error');
        } else {
            alert(messaggioErrore);
        }
        
        return false;
    }
    
    return true;
}

// Funzione per ottenere le informazioni di stock del prodotto dalla pagina
function getProductStockInfo(prodottoId) {
    // Cerca nelle card prodotto (lista prodotti)
    const productCard = document.querySelector(`[data-product-id="${prodottoId}"]`);
    if (productCard) {
        // Cerca in diversi possibili selettori per lo stock
        const stockSelectors = [
            '.product-stock',
            '.stock-info', 
            '.stock-quantity',
            '.stock-value',
            '.disponibilità'
        ];
        
        for (const selector of stockSelectors) {
            const stockElement = productCard.querySelector(selector);
            if (stockElement) {
                const stockText = stockElement.textContent || stockElement.innerText;
                
                // Cerca pattern diversi per estrarre il numero
                const patterns = [
                    /Stock:\s*(\d+)/i,
                    /Disponibili:\s*(\d+)/i,
                    /(\d+)\s*pezzi/i,
                    /(\d+)\s*disponibili/i,
                    /(\d+)/  // Fallback: qualsiasi numero
                ];
                
                for (const pattern of patterns) {
                    const match = stockText.match(pattern);
                    if (match) {
                        const stockValue = parseInt(match[1]);
                        return { stock: stockValue };
                    }
                }
            }
        }
    }
    
    // Cerca nella pagina dettaglio prodotto
    const quantityInput = document.getElementById('quantity');
    if (quantityInput) {
        const maxStock = parseInt(quantityInput.getAttribute('max'));
        if (maxStock) {
            return { stock: maxStock };
        }
    }
    
    // Cerca in elementi con classe stock-quantity
    const stockElements = document.querySelectorAll('.stock-quantity, .stock-value');
    for (const element of stockElements) {
        const stockText = element.textContent || element.innerText;
        const stockValue = parseInt(stockText);
        if (!isNaN(stockValue)) {
            return { stock: stockValue };
        }
    }
    
    return null;
}

// Funzione per ottenere la quantità già presente nel carrello (se visualizzata)
function getQuantityInCart(prodottoId) {
    // Cerca se è visualizzata la quantità nel carrello per questo prodotto
    const cartQuantityElement = document.querySelector(`[data-cart-product-id="${prodottoId}"] .cart-quantity`);
    if (cartQuantityElement) {
        return parseInt(cartQuantityElement.textContent) || 0;
    }
    
    // Se non trova informazioni, assume 0
    return 0;
}

// Le funzioni getCookie, updateCartCounter, showNotification e loadCartCounter 
// sono definite in carrello.js per evitare duplicazioni

// Controlli quantità per la pagina di dettaglio
function changeQuantity(delta) {
    const quantityInput = document.getElementById('quantity');
    if (quantityInput) {
        let newValue = parseInt(quantityInput.value) + delta;
        const min = parseInt(quantityInput.min) || 1;
        const max = parseInt(quantityInput.max) || 99;
        
        if (newValue >= min && newValue <= max) {
            quantityInput.value = newValue;
        } else if (newValue > max) {
            // Mostra messaggio di errore se supera il massimo
            if (typeof showNotification === 'function') {
                showNotification('Non ci sono abbastanza prodotti in magazzino', 'error');
            } else {
                alert('Non ci sono abbastanza prodotti in magazzino');
            }
        }
    }
}
