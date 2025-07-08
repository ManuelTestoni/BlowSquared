let negozioDaSelezionare = null;

function mostraDettaglio(negozioId) {
    fetch(`/negozi/${negozioId}/`, {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            popolaDettaglioNegozio(data.negozio);
            negozioDaSelezionare = negozioId;
        } else {
            alert('Errore nel caricamento dei dettagli del negozio');
        }
    })
    .catch(error => {
        console.error('Errore:', error);
        alert('Errore di rete');
    });
}

function popolaDettaglioNegozio(negozio) {
    document.getElementById('popupStoreName').textContent = negozio.nome;
    
    const detailsHtml = `
        <div class="store-detail-layout">
            <!-- Sezione Immagine (sinistra) -->
            <div class="store-image-section">
                <div class="store-main-image">
                    <img src="/media/negozi/${negozio.codice.toLowerCase()}_store.jpg" 
                         alt="${negozio.nome}" 
                         class="store-photo"
                         onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';">
                    <div class="store-photo-placeholder" style="display: none;">
                        <div class="placeholder-logo">🏪</div>
                        <div class="placeholder-brand">Blow²</div>
                        <div class="placeholder-location">${negozio.nome}</div>
                    </div>
                </div>
                <div class="store-badge-container">
                    <div class="store-code-badge">${negozio.codice}</div>
                    <div class="store-status-badge">🟢 Aperto</div>
                </div>
            </div>
            
            <!-- Sezione Informazioni (destra) -->
            <div class="store-info-section">
                <div class="store-header-info">
                    <h3 class="store-detail-name">${negozio.nome}</h3>
                    <p class="store-products-count">${negozio.prodotti_disponibili} prodotti disponibili</p>
                </div>
                
                <!-- Informazioni di Base -->
                <div class="info-block">
                    <h4 class="info-block-title">
                        <span class="info-icon">📍</span>
                        Posizione e Contatti
                    </h4>
                    <div class="info-list">
                        <div class="info-row">
                            <span class="info-label">Indirizzo:</span>
                            <span class="info-value">${negozio.indirizzo_completo}</span>
                        </div>
                        ${negozio.telefono ? `
                        <div class="info-row">
                            <span class="info-label">Telefono:</span>
                            <span class="info-value">${negozio.telefono}</span>
                        </div>
                        ` : ''}
                        ${negozio.email ? `
                        <div class="info-row">
                            <span class="info-label">Email:</span>
                            <span class="info-value">${negozio.email}</span>
                        </div>
                        ` : ''}
                    </div>
                </div>
                
                <!-- Caratteristiche Struttura -->
                <div class="info-block">
                    <h4 class="info-block-title">
                        <span class="info-icon">🏢</span>
                        Caratteristiche Struttura
                    </h4>
                    <div class="info-grid">
                        <div class="info-stat">
                            <span class="stat-number">${negozio.superficie_mq}</span>
                            <span class="stat-unit">m²</span>
                            <span class="stat-label">Superficie</span>
                        </div>
                        <div class="info-stat">
                            <span class="stat-number">${negozio.numero_casse}</span>
                            <span class="stat-unit"></span>
                            <span class="stat-label">Casse</span>
                        </div>
                        <div class="info-stat">
                            <span class="stat-number">${negozio.posti_parcheggio}</span>
                            <span class="stat-unit"></span>
                            <span class="stat-label">Posti Auto</span>
                        </div>
                    </div>
                </div>
                
                <!-- Orari -->
                <div class="info-block">
                    <h4 class="info-block-title">
                        <span class="info-icon">🕒</span>
                        Orari di Apertura
                    </h4>
                    <div class="schedule-grid">
                        ${Object.entries(negozio.orari).map(([giorno, orario]) => `
                            <div class="schedule-row">
                                <span class="schedule-day">${giorno.charAt(0).toUpperCase() + giorno.slice(1)}</span>
                                <span class="schedule-time">${orario}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
                
                <!-- Servizi -->
                ${negozio.servizi.length > 0 ? `
                <div class="info-block">
                    <h4 class="info-block-title">
                        <span class="info-icon">🛎️</span>
                        Servizi Disponibili
                    </h4>
                    <div class="services-tags">
                        ${negozio.servizi.map(servizio => `
                            <div class="service-tag">
                                <span class="service-emoji">${servizio.icona}</span>
                                <span class="service-name">${servizio.nome}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
                ` : ''}
                
                <!-- Management -->
                <div class="info-block">
                    <h4 class="info-block-title">
                        <span class="info-icon">👨‍💼</span>
                        Informazioni Gestione
                    </h4>
                    <div class="info-list">
                        ${negozio.direttore ? `
                        <div class="info-row">
                            <span class="info-label">Direttore:</span>
                            <span class="info-value">${negozio.direttore}</span>
                        </div>
                        ` : ''}
                        <div class="info-row">
                            <span class="info-label">Apertura:</span>
                            <span class="info-value">${negozio.data_apertura}</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    document.getElementById('storeDetails').innerHTML = detailsHtml;
    
    // Aggiorna il pulsante di selezione
    const selectBtn = document.getElementById('selectStoreBtn');
    selectBtn.onclick = () => selezionaNegozio(negozio.id);
    
    // Mostra popup
    document.getElementById('storePopup').style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function selezionaNegozio(negozioId) {
    window.location.href = `/negozi/${negozioId}/seleziona/`;
}

function chiudiDettaglio() {
    document.getElementById('storePopup').style.display = 'none';
    document.body.style.overflow = 'auto';
    negozioDaSelezionare = null;
}

// Chiudi popup cliccando fuori o con ESC
document.addEventListener('click', function(e) {
    const popup = document.getElementById('storePopup');
    if (e.target === popup) {
        chiudiDettaglio();
    }
});

document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        chiudiDettaglio();
    }
});