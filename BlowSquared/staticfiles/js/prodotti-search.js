document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.getElementById('search-input');
    const categoriaFilter = document.getElementById('categoria-filter');
    const prezzoMinFilter = document.getElementById('prezzo-min');
    const prezzoMaxFilter = document.getElementById('prezzo-max');
    const ordineFilter = document.getElementById('ordine-filter');
    const clearFiltersBtn = document.querySelector('.clear-filters-btn');
    const productsGrid = document.getElementById('products-grid');
    const loadingIndicator = document.getElementById('loading-indicator');
    const searchFiltersSection = document.querySelector('.search-filters-section');
    
    let searchTimeout;
    
    // Effetto scroll per rimpicciolire i filtri
    let lastScrollTop = 0;
    const scrollThreshold = 100; // Pixel di scroll prima che l'effetto si attivi
    
    window.addEventListener('scroll', function() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        if (scrollTop > scrollThreshold) {
            searchFiltersSection.classList.add('scrolled');
        } else {
            searchFiltersSection.classList.remove('scrolled');
        }
        
        lastScrollTop = scrollTop;
    }, { passive: true });
    
    // Funzione per effettuare la ricerca AJAX
    function performSearch() {
        clearTimeout(searchTimeout);
        searchTimeout = setTimeout(() => {
            const formData = new FormData();
            formData.append('search', searchInput.value);
            formData.append('categoria', categoriaFilter.value);
            formData.append('prezzo_min', prezzoMinFilter.value);
            formData.append('prezzo_max', prezzoMaxFilter.value);
            formData.append('ordine', ordineFilter.value);
            
            // Mostra loading
            loadingIndicator.style.display = 'block';
            productsGrid.style.opacity = '0.5';
            
            // Effettua la richiesta AJAX
            fetch(window.location.pathname + '?' + new URLSearchParams({
                search: searchInput.value,
                categoria: categoriaFilter.value,
                prezzo_min: prezzoMinFilter.value,
                prezzo_max: prezzoMaxFilter.value,
                ordine: ordineFilter.value
            }), {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                }
            })
            .then(response => response.json())
            .then(data => {
                updateProductsGrid(data.prodotti);
                updateProductsCount(data.count);
                
                // Nascondi loading
                loadingIndicator.style.display = 'none';
                productsGrid.style.opacity = '1';
            })
            .catch(error => {
                console.error('Errore nella ricerca:', error);
                loadingIndicator.style.display = 'none';
                productsGrid.style.opacity = '1';
            });
        }, 300); // Debounce di 300ms
    }
    
    function renderProductsGrid(prodotti) {
        const grid = document.getElementById('products-grid');
        
        if (prodotti.length === 0) {
            grid.innerHTML = `
                <div class="no-products">
                    <div class="no-products-icon">🛒</div>
                    <h3>Nessun prodotto trovato</h3>
                    <p>Prova a modificare i filtri di ricerca</p>
                </div>
            `;
            return;
        }
        
        grid.innerHTML = prodotti.map(prodotto => `
            <div class="product-card">
                <div class="product-image-container">
                    <a href="/prodotti/${prodotto.id}/" class="product-image-link">
                        ${prodotto.foto ? 
                            `<img src="${prodotto.foto}" alt="${prodotto.nome}" class="product-image">` :
                            `<div class="product-placeholder">
                                <div class="placeholder-icon">📦</div>
                                <span>${prodotto.nome.substring(0, 15)}</span>
                            </div>`
                        }
                    </a>
                    
                    ${prodotto.sconto > 0 ? 
                        `<div class="product-discount">-${Math.floor(prodotto.sconto)}%</div>` : ''
                    }
                    
                    <div class="product-category-badge">${prodotto.categoria}</div>
                    
                    ${prodotto.stock <= 5 && prodotto.stock > 0 ? 
                        `<div class="product-low-stock">Ultime ${prodotto.stock} disponibili</div>` : 
                        prodotto.stock === 0 ? 
                        `<div class="product-out-stock">Esaurito</div>` : ''
                    }
                </div>
                
                <div class="product-info">
                    <h3 class="product-name">${prodotto.nome.substring(0, 50)}${prodotto.nome.length > 50 ? '...' : ''}</h3>
                    <p class="product-brand">${prodotto.marca}</p>
                    
                    <div class="product-price">
                        ${prodotto.sconto > 0 ? 
                            `<span class="original-price">€${prodotto.prezzo}</span>
                             <span class="discounted-price">€${parseFloat(prodotto.prezzo_scontato).toFixed(2)}</span>` :
                            `<span class="current-price">€${prodotto.prezzo}</span>`
                        }
                    </div>
                    
                    <p class="product-description">
                        ${prodotto.descrizione.substring(0, 100)}${prodotto.descrizione.length > 100 ? '...' : ''}
                    </p>
                    
                    <div class="product-meta">
                        <span class="product-weight">${prodotto.peso}</span>
                        ${prodotto.numero_recensioni > 0 ? 
                            `<span class="product-reviews">${prodotto.numero_recensioni} recensioni</span>` : ''
                        }
                    </div>
                    
                    <div class="product-actions">
                        <button class="btn-add-cart" data-product-id="${prodotto.prodotto_id}" ${prodotto.stock === 0 ? 'disabled' : ''}>
                            ${prodotto.stock === 0 ? 
                                'Non disponibile' : 
                                '<span class="btn-icon">🛒</span> Aggiungi al carrello'
                            }
                        </button>
                        <a href="/prodotti/${prodotto.id}/" class="btn-info">
                            <span class="btn-icon">👁️</span>
                            Info
                        </a>
                    </div>
                </div>
            </div>
        `).join('');
        
        // Riattiva gli event listeners per i nuovi pulsanti del carrello
        attachCartEventListeners();
    }
    
    function attachCartEventListeners() {
        // Rimuovi i vecchi listener per evitare duplicati
        const oldButtons = document.querySelectorAll('.btn-add-cart[data-listener="true"]');
        oldButtons.forEach(btn => btn.removeAttribute('data-listener'));
        
        // Aggiungi nuovi listener
        const addToCartButtons = document.querySelectorAll('.btn-add-cart:not([data-listener="true"])');
        addToCartButtons.forEach(button => {
            button.setAttribute('data-listener', 'true');
            button.addEventListener('click', function() {
                const prodottoId = this.dataset.productId;
                if (prodottoId && !this.disabled) {
                    // Usa la funzione dal file prodotti-carrello.js
                    if (typeof aggiungiAlCarrello === 'function') {
                        aggiungiAlCarrello(prodottoId, 1, this);
                    }
                }
            });
        });
    }
    
    // Funzione per aggiornare la griglia dei prodotti
    function updateProductsGrid(prodotti) {
        if (prodotti.length === 0) {
            productsGrid.innerHTML = `
                <div class="no-products">
                    <div class="no-products-icon">🛒</div>
                    <h3>Nessun prodotto trovato</h3>
                    <p>Prova a modificare i filtri di ricerca</p>
                </div>
            `;
            return;
        }
        
        const productsHTML = prodotti.map(prodotto => {
            const hasDiscount = parseFloat(prodotto.sconto) > 0;
            const isOutOfStock = prodotto.stock === 0;
            const isLowStock = prodotto.stock <= 5 && prodotto.stock > 0;
            
            return `
                <div class="product-card">
                    <div class="product-image-container">
                        <a href="/prodotti/${prodotto.id}/" class="product-image-link">
                            ${prodotto.foto ? 
                                `<img src="${prodotto.foto}" alt="${prodotto.nome}" class="product-image">` :
                                `<div class="product-placeholder">
                                    <div class="placeholder-icon">📦</div>
                                    <span>${prodotto.nome.substring(0, 15)}...</span>
                                 </div>`
                            }
                        </a>
                        
                        ${hasDiscount ? `<div class="product-discount">-${Math.round(prodotto.sconto)}%</div>` : ''}
                        
                        <div class="product-category-badge">${prodotto.categoria}</div>
                        
                        ${isLowStock ? `<div class="product-low-stock">Ultime ${prodotto.stock} disponibili</div>` : ''}
                        ${isOutOfStock ? `<div class="product-out-stock">Esaurito</div>` : ''}
                    </div>
                    
                    <div class="product-info">
                        <h3 class="product-name">${prodotto.nome.length > 50 ? prodotto.nome.substring(0, 50) + '...' : prodotto.nome}</h3>
                        <p class="product-brand">${prodotto.marca}</p>
                        
                        <div class="product-price">
                            ${hasDiscount ? 
                                `<span class="original-price">€${prodotto.prezzo}</span>
                                 <span class="discounted-price">€${parseFloat(prodotto.prezzo_scontato).toFixed(2)}</span>` :
                                `<span class="current-price">€${prodotto.prezzo}</span>`
                            }
                        </div>
                        
                        <p class="product-description">
                            ${prodotto.descrizione.length > 100 ? prodotto.descrizione.substring(0, 100) + '...' : prodotto.descrizione}
                        </p>
                        
                        <div class="product-meta">
                            <span class="product-weight">${prodotto.peso}</span>
                            ${prodotto.numero_recensioni > 0 ? 
                                `<span class="product-reviews">${prodotto.numero_recensioni} recensioni</span>` : ''
                            }
                        </div>
                        
                        <div class="product-actions">
                            <button class="btn-add-cart" data-product-id="${prodotto.id}" ${isOutOfStock ? 'disabled' : ''}>
                                ${isOutOfStock ? 'Non disponibile' : 'Aggiungi al carrello'}
                            </button>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
        
        productsGrid.innerHTML = productsHTML;
    }
    
    // Funzione per aggiornare il conteggio prodotti
    function updateProductsCount(count) {
        const countElement = document.querySelector('.products-count');
        if (countElement) {
            countElement.textContent = `${count} prodotti trovati`;
        }
    }
    
    // Event listeners
    searchInput.addEventListener('input', performSearch);
    categoriaFilter.addEventListener('change', performSearch);
    prezzoMinFilter.addEventListener('input', performSearch);
    prezzoMaxFilter.addEventListener('input', performSearch);
    ordineFilter.addEventListener('change', performSearch);
    
    // Pulisci filtri
    clearFiltersBtn.addEventListener('click', function() {
        searchInput.value = '';
        categoriaFilter.value = '';
        prezzoMinFilter.value = '';
        prezzoMaxFilter.value = '';
        ordineFilter.value = 'nome';
        performSearch();
    });
    
    // Gestione pulsante ricerca
    document.querySelector('.search-btn').addEventListener('click', performSearch);
    
    // Ricerca con Enter
    searchInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            e.preventDefault();
            performSearch();
        }
    });
    
    // Attiva i listener iniziali
    attachCartEventListeners();
});
