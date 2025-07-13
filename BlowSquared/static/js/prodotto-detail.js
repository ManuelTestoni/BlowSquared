// JavaScript per gestire i controlli della quantità nel dettaglio prodotto

function changeQuantity(delta) {
    const quantityInput = document.getElementById('quantity');
    const currentValue = parseInt(quantityInput.value) || 1;
    const min = parseInt(quantityInput.min) || 1;
    const max = parseInt(quantityInput.max) || 999;
    
    const newValue = currentValue + delta;
    
    if (newValue >= min && newValue <= max) {
        quantityInput.value = newValue;
        
        // Aggiungi animazione al cambio
        quantityInput.style.transform = 'scale(1.1)';
        setTimeout(() => {
            quantityInput.style.transform = 'scale(1)';
        }, 150);
        
        // Aggiorna la quantità nel pulsante del carrello se necessario
        updateCartButton();
    }
}

function updateCartButton() {
    const quantity = document.getElementById('quantity').value;
    const cartButton = document.querySelector('.btn-add-cart-detail');
    
    if (cartButton && !cartButton.disabled) {
        // Aggiungi un piccolo effetto visivo quando cambia la quantità
        cartButton.style.transform = 'scale(0.95)';
        setTimeout(() => {
            cartButton.style.transform = '';
        }, 100);
    }
}

// Gestione dell'input diretto della quantità
document.addEventListener('DOMContentLoaded', function() {
    const quantityInput = document.getElementById('quantity');
    
    if (quantityInput) {
        quantityInput.addEventListener('input', function() {
            const value = parseInt(this.value);
            const min = parseInt(this.min) || 1;
            const max = parseInt(this.max) || 999;
            
            if (value < min) {
                this.value = min;
            } else if (value > max) {
                this.value = max;
            }
            
            updateCartButton();
        });
        
        // Gestione delle frecce della tastiera
        quantityInput.addEventListener('keydown', function(e) {
            if (e.key === 'ArrowUp') {
                e.preventDefault();
                changeQuantity(1);
            } else if (e.key === 'ArrowDown') {
                e.preventDefault();
                changeQuantity(-1);
            }
        });
    }
    
    // Gestione del pulsante aggiungi al carrello
    const cartButton = document.querySelector('.btn-add-cart-detail');
    if (cartButton) {
        cartButton.addEventListener('click', function() {
            const quantity = document.getElementById('quantity').value;
            const productId = this.getAttribute('data-product-id');
            
            // Aggiungi animazione di successo
            const originalText = this.innerHTML;
            this.innerHTML = '<span class="btn-icon">✅</span> Aggiunto!';
            this.style.background = 'linear-gradient(135deg, #27ae60 0%, #2ecc71 100%)';
            
            setTimeout(() => {
                this.innerHTML = originalText;
                this.style.background = '';
            }, 2000);
            
            // Qui andrà la logica per aggiungere al carrello
            console.log(`Aggiungendo ${quantity} unità del prodotto ${productId} al carrello`);
        });
    }
});

// Animazioni aggiuntive per i pulsanti quantità
document.addEventListener('DOMContentLoaded', function() {
    const quantityButtons = document.querySelectorAll('.quantity-btn');
    
    quantityButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Animazione di click
            this.style.transform = 'scale(0.9)';
            setTimeout(() => {
                this.style.transform = '';
            }, 150);
        });
    });
});
