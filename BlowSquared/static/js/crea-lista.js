document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('searchProducts');
    const searchResults = document.getElementById('searchResults');
    const selectedProducts = document.getElementById('selectedProducts');
    const form = document.getElementById('createListForm');
    
    let selectedProductsData = [];
    let searchTimeout;
    
    // Ricerca prodotti
    searchInput.addEventListener('input', function() {
        const query = this.value.trim();
        
        clearTimeout(searchTimeout);
        
        if (query.length >= 2) {
            searchTimeout = setTimeout(() => {
                searchProducts(query);
            }, 300);
        } else {
            hideSearchResults();
        }
    });
    
    function searchProducts(query) {
        fetch(`/utenti/api/cerca-prodotti/?q=${encodeURIComponent(query)}`)
            .then(response => response.json())
            .then(data => {
                displaySearchResults(data.prodotti);
            })
            .catch(error => {
                console.error('Errore nella ricerca:', error);
            });
    }
    
    function displaySearchResults(prodotti) {
        if (prodotti.length === 0) {
            hideSearchResults();
            return;
        }
        
        const resultsHTML = prodotti.map(prodotto => `
            <div class="search-result-item" data-product-id="${prodotto.id}">
                <div class="result-info">
                    <h4>${prodotto.nome}</h4>
                    <p>${prodotto.marca} - €${prodotto.prezzo.toFixed(2)}</p>
                    <small>Stock: ${prodotto.stock}</small>
                </div>
            </div>
        `).join('');
        
        searchResults.innerHTML = resultsHTML;
        searchResults.style.display = 'block';
        
        // Aggiungi event listener ai risultati
        searchResults.querySelectorAll('.search-result-item').forEach(item => {
            item.addEventListener('click', function() {
                const productId = this.getAttribute('data-product-id');
                const prodotto = prodotti.find(p => p.id == productId);
                addProductToList(prodotto);
            });
        });
    }
    
    function hideSearchResults() {
        searchResults.style.display = 'none';
    }
    
    function addProductToList(prodotto) {
        // Verifica se il prodotto è già nella lista
        if (selectedProductsData.find(p => p.id === prodotto.id)) {
            alert('Prodotto già aggiunto alla lista!');
            return;
        }
        
        selectedProductsData.push(prodotto);
        updateSelectedProductsDisplay();
        searchInput.value = '';
        hideSearchResults();
    }
    
    function updateSelectedProductsDisplay() {
        if (selectedProductsData.length === 0) {
            selectedProducts.innerHTML = `
                <div class="no-products">
                    <span class="no-products-icon">🛒</span>
                    <p>Nessun prodotto selezionato. Usa la ricerca per aggiungere prodotti alla tua lista.</p>
                </div>
            `;
            return;
        }
        
        const productsHTML = selectedProductsData.map((prodotto, index) => `
            <div class="selected-product-item" data-index="${index}">
                <div class="product-info">
                    <h4>${prodotto.nome}</h4>
                    <p>${prodotto.marca} - €${prodotto.prezzo.toFixed(2)} ${prodotto.stock > 0 ? '✅ Disponibile' : '❌ Esaurito'}</p>
                </div>
                <div class="product-controls">
                    <div class="quantity-control">
                        <label for="quantity-${index}">
                            🔢 Quantità
                        </label>
                        <input type="number" 
                               id="quantity-${index}"
                               name="quantita" 
                               value="1" 
                               min="1" 
                               max="${prodotto.stock}" 
                               class="quantity-input">
                        <input type="hidden" name="prodotti" value="${prodotto.id}">
                    </div>
                    <div class="priority-control">
                        <label for="priority-${index}">
                            ⭐ Priorità
                        </label>
                        <select name="priorita" id="priority-${index}" class="priority-select">
                            <option value="0">🔹 Normale</option>
                            <option value="1">🟡 Alta</option>
                            <option value="2">🔴 Urgente</option>
                        </select>
                    </div>
                    <div class="notes-control">
                        <label for="notes-${index}">
                            📝 Note Aggiuntive
                        </label>
                        <input type="text" 
                               id="notes-${index}"
                               name="note" 
                               placeholder="es. marca specifica, se in offerta..." 
                               class="notes-input">
                    </div>
                    <button type="button" class="btn-remove-product" data-index="${index}">
                        🗑️ Rimuovi Prodotto
                    </button>
                </div>
            </div>
        `).join('');
        
        selectedProducts.innerHTML = productsHTML;
        
        // Aggiungi event listener per rimuovere prodotti con conferma
        selectedProducts.querySelectorAll('.btn-remove-product').forEach(btn => {
            btn.addEventListener('click', function() {
                const index = parseInt(this.getAttribute('data-index'));
                const prodotto = selectedProductsData[index];
                
                if (confirm(`Rimuovere "${prodotto.nome}" dalla lista?`)) {
                    removeProductFromList(index);
                }
            });
        });
        
        // Aggiungi validazione in tempo reale per le quantità
        selectedProducts.querySelectorAll('.quantity-input').forEach(input => {
            input.addEventListener('change', function() {
                const max = parseInt(this.getAttribute('max'));
                const value = parseInt(this.value);
                
                if (value > max) {
                    this.value = max;
                    alert(`Quantità massima disponibile: ${max}`);
                }
                
                if (value < 1) {
                    this.value = 1;
                }
                
                // Aggiorna il border del prodotto se quantità > stock
                const productItem = this.closest('.selected-product-item');
                if (value > max) {
                    productItem.style.border = '2px solid #e74c3c';
                } else {
                    productItem.style.border = '2px solid rgba(62, 116, 71, 0.1)';
                }
            });
        });
    }
    
    function removeProductFromList(index) {
        selectedProductsData.splice(index, 1);
        updateSelectedProductsDisplay();
    }
    
    // Nasconde risultati quando si clicca fuori
    document.addEventListener('click', function(e) {
        if (!searchInput.contains(e.target) && !searchResults.contains(e.target)) {
            hideSearchResults();
        }
    });
    
    // Validazione form
    form.addEventListener('submit', function(e) {
        const nomeLista = document.getElementById('nome_lista').value.trim();
        
        if (!nomeLista) {
            e.preventDefault();
            alert('Il nome della lista è obbligatorio!');
            return;
        }
        
        if (selectedProductsData.length === 0) {
            const confirm = window.confirm('Vuoi creare una lista vuota? Potrai aggiungere prodotti in seguito.');
            if (!confirm) {
                e.preventDefault();
            }
        }
    });
});
