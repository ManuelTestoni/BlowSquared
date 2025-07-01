// Gestione popup liste della spesa

function visualizzaLista(listaId) {
    fetch(`/utenti/liste-spesa/${listaId}/visualizza/`, {
        method: 'GET',
        headers: {
            'X-Requested-With': 'XMLHttpRequest',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            mostraPopupLista(data.lista, data.elementi);
        } else {
            alert('Errore nel caricamento della lista');
        }
    })
    .catch(error => {
        console.error('Errore:', error);
        alert('Errore di rete');
    });
}

function mostraPopupLista(lista, elementi) {
    // Aggiorna titolo
    document.getElementById('popupListaNome').textContent = lista.nome;
    
    // Aggiorna informazioni lista
    const infoHtml = `
        <div class="info-grid">
            <div class="info-stat">
                <span class="stat-value">${lista.numero_prodotti}</span>
                <span class="stat-label">Prodotti</span>
            </div>
            <div class="info-stat">
                <span class="stat-value">${lista.quantita_totale}</span>
                <span class="stat-label">Quantità</span>
            </div>
            <div class="info-stat">
                <span class="stat-value">€${lista.prezzo_stimato.toFixed(2)}</span>
                <span class="stat-label">Totale</span>
            </div>
            <div class="info-stat">
                <span class="stat-value">${lista.data_creazione}</span>
                <span class="stat-label">Creata</span>
            </div>
        </div>
        ${lista.descrizione ? `<p style="margin-top: 1rem; font-style: italic; color: #666;">${lista.descrizione}</p>` : ''}
    `;
    document.getElementById('popupListaInfo').innerHTML = infoHtml;
    
    // Aggiorna elementi
    if (elementi.length === 0) {
        document.getElementById('popupListaElementi').innerHTML = `
            <div style="text-align: center; padding: 2rem; color: #666;">
                <div style="font-size: 3rem; margin-bottom: 1rem;">📭</div>
                <h4>Lista Vuota</h4>
                <p>Non ci sono prodotti in questa lista.</p>
            </div>
        `;
    } else {
        const elementiHtml = elementi.map(elemento => `
            <div class="elemento-item">
                <div class="elemento-info">
                    <h5>${elemento.nome}</h5>
                    <div class="elemento-details">
                        ${elemento.marca} • ${elemento.categoria}
                        ${elemento.note ? `<br><em>"${elemento.note}"</em>` : ''}
                        ${!elemento.disponibile ? '<br><span style="color: #e74c3c;">⚠️ Non disponibile</span>' : ''}
                    </div>
                </div>
                <div class="elemento-meta">
                    <div class="elemento-quantita">x${elemento.quantita}</div>
                    <div class="elemento-prezzo">€${elemento.prezzo_totale.toFixed(2)}</div>
                    <span class="elemento-priorita" title="${elemento.priorita}">${elemento.priorita_emoji}</span>
                </div>
            </div>
        `).join('');
        
        document.getElementById('popupListaElementi').innerHTML = `
            <h4 style="margin-bottom: 1rem; color: var(--primary-color);">Prodotti nella Lista:</h4>
            ${elementiHtml}
        `;
    }
    
    // Mostra popup
    document.getElementById('listaPopup').style.display = 'flex';
    document.body.style.overflow = 'hidden';
}

function chiudiPopup() {
    document.getElementById('listaPopup').style.display = 'none';
    document.body.style.overflow = 'auto';
}

function eliminaLista(listaId, nomeLista) {
    if (confirm(`Sei sicuro di voler eliminare la lista "${nomeLista}"?\nQuesta azione non può essere annullata.`)) {
        fetch(`/utenti/liste-spesa/${listaId}/elimina/`, {
            method: 'POST',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Rimuovi elemento dalla UI
                const listItem = document.querySelector(`[data-lista-id="${listaId}"]`);
                if (listItem) {
                    listItem.style.animation = 'slideOut 0.3s ease';
                    setTimeout(() => {
                        listItem.remove();
                        
                        // Controlla se non ci sono più liste
                        const container = document.querySelector('.lists-container');
                        if (container && container.children.length === 0) {
                            location.reload(); // Ricarica per mostrare placeholder
                        }
                    }, 300);
                }
                
                // Mostra messaggio
                showNotification(data.message, 'success');
            } else {
                alert('Errore nell\'eliminazione della lista');
            }
        })
        .catch(error => {
            console.error('Errore:', error);
            alert('Errore di rete');
        });
    }
}

// Utility function per CSRF token
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

// Notification system
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        background: ${type === 'success' ? '#27ae60' : '#3498db'};
        color: white;
        padding: 1rem 2rem;
        border-radius: 10px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        z-index: 10000;
        font-weight: 600;
        animation: slideInRight 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.style.animation = 'slideOutRight 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    }, 3000);
}

// Chiudi popup cliccando fuori
document.addEventListener('click', function(e) {
    const popup = document.getElementById('listaPopup');
    if (e.target === popup) {
        chiudiPopup();
    }
});

// Chiudi popup con ESC
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        chiudiPopup();
    }
});

// CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOut {
        from { opacity: 1; transform: translateX(0); }
        to { opacity: 0; transform: translateX(-100%); }
    }
    
    @keyframes slideInRight {
        from { opacity: 0; transform: translateX(100%); }
        to { opacity: 1; transform: translateX(0); }
    }
    
    @keyframes slideOutRight {
        from { opacity: 1; transform: translateX(0); }
        to { opacity: 0; transform: translateX(100%); }
    }
`;
document.head.appendChild(style);
