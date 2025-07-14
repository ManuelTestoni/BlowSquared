// JavaScript per aggiungere prodotti al carrello

document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 PRODOTTI-CARRELLO.JS CARICATO');
    
    // Gestione pulsanti "Aggiungi al carrello" nella lista prodotti
    const addToCartButtons = document.querySelectorAll('.btn-add-cart');
    console.log(`🔍 TROVATI ${addToCartButtons.length} pulsanti .btn-add-cart`);
    
    addToCartButtons.forEach((button, index) => {
        console.log(`   Pulsante ${index}: data-product-id="${button.dataset.productId}"`);
        button.addEventListener('click', function() {
            console.log(`🖱️ CLICK su pulsante lista prodotti`);
            const prodottoId = this.dataset.productId;
            if (prodottoId && !this.disabled) {
                aggiungiAlCarrello(prodottoId, 1, this);
            } else {
                console.log(`❌ Pulsante disabilitato o senza product-id`);
            }
        });
    });
    
    // Gestione pulsante "Aggiungi al carrello" nel dettaglio prodotto
    const addToCartDetailButton = document.querySelector('.btn-add-cart-detail');
    console.log(`🔍 PULSANTE DETTAGLIO:`, addToCartDetailButton ? 'TROVATO' : 'NON TROVATO');
    
    if (addToCartDetailButton) {
        addToCartDetailButton.addEventListener('click', function() {
            console.log(`🖱️ CLICK su pulsante dettaglio prodotto`);
            const prodottoId = this.dataset.productId;
            const quantityInput = document.getElementById('quantity');
            const quantita = quantityInput ? parseInt(quantityInput.value) : 1;
            
            if (prodottoId && !this.disabled && quantita > 0) {
                aggiungiAlCarrello(prodottoId, quantita, this);
            } else {
                console.log(`❌ Pulsante dettaglio disabilitato o dati mancanti`);
            }
        });
    }
    
    // Carica il contatore del carrello all'avvio
    if (typeof loadCartCounter === 'function') {
        console.log('📊 CARICO CONTATORE CARRELLO');
        loadCartCounter();
    } else {
        console.log('❌ FUNZIONE loadCartCounter NON DISPONIBILE');
    }
});

function aggiungiAlCarrello(prodottoId, quantita, button) {
    console.log(`🛒 AGGIUNGI AL CARRELLO: Prodotto ${prodottoId}, Quantità ${quantita}`);
    
    // Verifica che le funzioni necessarie siano disponibili
    if (typeof getCookie !== 'function') {
        console.error('❌ FUNZIONE getCookie NON DISPONIBILE');
        return;
    }
    if (typeof showNotification !== 'function') {
        console.error('❌ FUNZIONE showNotification NON DISPONIBILE');
        return;
    }
    if (typeof updateCartCounter !== 'function') {
        console.error('❌ FUNZIONE updateCartCounter NON DISPONIBILE');
        return;
    }
    
    console.log('✅ Tutte le funzioni sono disponibili');
    
    // Disabilita il pulsante durante la richiesta
    const originalText = button.innerHTML;
    button.disabled = true;
    button.innerHTML = '<span class="btn-icon">⏳</span> Aggiunta...';
    
    // Ottieni il token CSRF
    const csrfToken = getCookie('csrftoken');
    console.log(`🔑 CSRF Token:`, csrfToken ? 'PRESENTE' : 'MANCANTE');
    
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
        console.log(`📡 RISPOSTA SERVER:`, response.status);
        return response.json();
    })
    .then(data => {
        console.log(`📦 DATI RISPOSTA:`, data);
        
        if (data.success) {
            // Mostra messaggio di successo
            showNotification(data.message, 'success');
            
            // Aggiorna il pulsante temporaneamente
            button.innerHTML = '<span class="btn-icon">✅</span> Aggiunto!';
            button.style.background = '#27ae60';
            
            // Aggiorna contatore carrello
            console.log(`🔢 AGGIORNO CONTATORE: ${data.carrello_count}`);
            updateCartCounter(data.carrello_count);
            
            // Ripristina il pulsante dopo 2 secondi
            setTimeout(() => {
                button.disabled = false;
                button.innerHTML = originalText;
                button.style.background = '';
            }, 2000);
            
        } else {
            console.log(`❌ ERRORE:`, data.message);
            // Mostra messaggio di errore
            if (data.redirect_login) {
                // Per utenti non autenticati, mostra un messaggio specifico
                showNotification(data.message, 'info');
            } else {
                showNotification(data.message, 'error');
            }
            
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
        }
    }
}
