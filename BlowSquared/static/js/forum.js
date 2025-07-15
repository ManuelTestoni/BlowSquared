// Forum Chat JavaScript

class ForumChat {
    constructor(username) {
        this.username = username;
        this.socket = null;
        this.isConnected = false;
        this.messagesContainer = document.getElementById('chatMessages');
        this.messageInput = document.getElementById('messageInput');
        this.currentContentType = 'chat';
        this.selectedIngredients = [];
        
        this.init();
    }
    
    init() {
        this.hideLoadingMessages();
        this.setupEventListeners();
        this.connectWebSocket();
        this.loadInitialMessages();
    }
    
    hideLoadingMessages() {
        // Nascondi il loading spinner
        const loadingMessages = document.querySelector('.loading-messages');
        if (loadingMessages) {
            loadingMessages.style.display = 'none';
        }
    }
    
    loadInitialMessages() {
        // Carica i messaggi recenti tramite API REST (backup se WebSocket non funziona)
        fetch('/forum/api/messaggi-recenti/', {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success && data.messaggi) {
                data.messaggi.forEach(messaggio => {
                    this.addMessage(messaggio);
                });
                this.scrollToBottom();
            } else {
                this.showWelcomeMessage();
            }
        })
        .catch(error => {
            console.error('Errore caricamento messaggi:', error);
            this.showWelcomeMessage();
        });
    }
    
    showWelcomeMessage() {
        // Mostra messaggio di benvenuto se non ci sono messaggi
        const welcomeHtml = `
            <div class="welcome-message">
                <div class="welcome-content">
                    <h4>🎉 Benvenuto nel Forum!</h4>
                    <p>Inizia una conversazione, condividi una recensione o una ricetta.</p>
                    <button onclick="document.getElementById('addContentBtn').click()" class="welcome-btn">
                        ➕ Scrivi il primo messaggio
                    </button>
                </div>
            </div>
        `;
        this.messagesContainer.innerHTML = welcomeHtml;
    }
    
    connectWebSocket() {
        // Per ora usiamo solo la modalità REST API
        // Il WebSocket sarà implementato successivamente quando installiamo Redis
        this.isConnected = true;
        this.updateConnectionStatus(true);
    }
    
    setupEventListeners() {
        // Invio messaggio con Enter
        this.messageInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        
        // Pulsante invio
        document.getElementById('sendBtn').addEventListener('click', () => {
            this.sendMessage();
        });
        
        // Pulsante aggiungi contenuto
        document.getElementById('addContentBtn').addEventListener('click', () => {
            this.openAddContentModal();
        });
        
        // Selettori tipo contenuto
        document.querySelectorAll('.content-type-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                this.selectContentType(btn.dataset.type);
            });
        });
        
        // Rating stelle
        document.querySelectorAll('.star').forEach(star => {
            star.addEventListener('click', () => {
                this.selectRating(parseInt(star.dataset.rating));
            });
        });
        
        // Submit contenuto
        document.getElementById('submitContentBtn').addEventListener('click', () => {
            this.submitContent();
        });
        
        // Ricerca prodotti per ricette
        document.getElementById('prodottoSearch').addEventListener('input', (e) => {
            this.searchProdotti(e.target.value);
        });
        
        // Carica negozi
        this.loadNegozi();
    }
    
    sendMessage() {
        const message = this.messageInput.value.trim();
        if (!message) return;
        
        this.sendToServer({
            tipo: 'chat',
            contenuto: message
        });
        
        this.messageInput.value = '';
    }
    
    sendToServer(data) {
        // Invia tramite API REST
        fetch('/forum/api/invia-messaggio/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.getCsrfToken(),
                'X-Requested-With': 'XMLHttpRequest',
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(result => {
            if (result.success) {
                this.addMessage(result.messaggio);
                this.scrollToBottom();
            } else {
                console.error('Errore server:', result.error);
                alert('Errore nell\'invio del messaggio: ' + (result.error || 'Errore sconosciuto'));
            }
        })
        .catch(error => {
            console.error('Errore fetch:', error);
            alert('Errore di connessione. Riprova.');
        });
    }
    
    addMessage(messageData) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${messageData.autore === this.username ? 'own' : 'other'}`;
        
        let messageContent = '';
        
        if (messageData.tipo === 'recensione') {
            messageContent = `
                <div class="message-header">
                    <span class="message-author">${messageData.autore}</span>
                    <span class="message-time">${messageData.data_creazione}</span>
                </div>
                <div class="message-type recensione">⭐ RECENSIONE</div>
                <div class="recensione-info">
                    <div class="recensione-negozio">🏪 ${messageData.negozio?.nome || 'Negozio'} - ${messageData.negozio?.citta || ''}</div>
                    <div class="recensione-stelle">${messageData.stelle_emoji}</div>
                </div>
                <div class="message-content">${messageData.contenuto}</div>
            `;
        } else if (messageData.tipo === 'ricetta') {
            let ingredientiHtml = '';
            if (messageData.ingredienti && messageData.ingredienti.length > 0) {
                ingredientiHtml = messageData.ingredienti.map(ing => 
                    `<div class="ingrediente-item">
                        <span>${ing.nome} (${ing.marca})</span>
                        <span>x${ing.quantita}</span>
                    </div>`
                ).join('');
            }
            
            messageContent = `
                <div class="message-header">
                    <span class="message-author">${messageData.autore}</span>
                    <span class="message-time">${messageData.data_creazione}</span>
                </div>
                <div class="message-type ricetta">🍝 RICETTA</div>
                <div class="ricetta-info">
                    <div class="ricetta-nome">👨‍🍳 ${messageData.nome_ricetta || 'Ricetta'}</div>
                    ${ingredientiHtml ? `<div class="ricetta-ingredienti">${ingredientiHtml}</div>` : ''}
                    ${messageData.note_ricetta ? `<div class="ricetta-note">📝 ${messageData.note_ricetta}</div>` : ''}
                </div>
                <div class="message-content">${messageData.contenuto}</div>
            `;
        } else {
            messageContent = `
                <div class="message-header">
                    <span class="message-author">${messageData.autore}</span>
                    <span class="message-time">${messageData.data_creazione}</span>
                </div>
                <div class="message-content">${messageData.contenuto}</div>
            `;
        }
        
        messageDiv.innerHTML = messageContent;
        this.messagesContainer.appendChild(messageDiv);
    }
    
    scrollToBottom() {
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }
    
    openAddContentModal() {
        document.getElementById('addContentModal').style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }
    
    selectContentType(type) {
        this.currentContentType = type;
        
        // Aggiorna pulsanti
        document.querySelectorAll('.content-type-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        document.querySelector(`[data-type="${type}"]`).classList.add('active');
        
        // Mostra form corretto
        document.querySelectorAll('.content-form').forEach(form => {
            form.classList.remove('active');
        });
        document.getElementById(`${type}Form`).classList.add('active');
    }
    
    selectRating(rating) {
        document.getElementById('stelleInput').value = rating;
        
        document.querySelectorAll('.star').forEach((star, index) => {
            if (index < rating) {
                star.classList.add('active');
            } else {
                star.classList.remove('active');
            }
        });
    }
    
    submitContent() {
        let data = { tipo: this.currentContentType };
        
        if (this.currentContentType === 'chat') {
            data.contenuto = document.getElementById('chatMessage').value;
        } else if (this.currentContentType === 'recensione') {
            const negozioId = document.getElementById('negozioSelect').value;
            const stelle = parseInt(document.getElementById('stelleInput').value);
            const recensioneText = document.getElementById('recensioneMessage').value.trim();
            
            if (!negozioId) {
                alert('Seleziona un negozio per la recensione');
                return;
            }
            
            if (!recensioneText) {
                alert('Scrivi una recensione');
                return;
            }
            
            // Non serve campo contenuto extra per le recensioni
            data.contenuto = recensioneText;
            data.negozio_id = negozioId;
            data.stelle = stelle;
            
        } else if (this.currentContentType === 'ricetta') {
            const nomeRicetta = document.getElementById('nomeRicetta').value.trim();
            const noteRicetta = document.getElementById('noteRicetta').value.trim();
            
            if (!nomeRicetta) {
                alert('Inserisci il nome della ricetta');
                return;
            }
            
            if (this.selectedIngredients.length === 0) {
                alert('Aggiungi almeno un ingrediente');
                return;
            }
            
            // Il contenuto sarà auto-generato dal server
            data.nome_ricetta = nomeRicetta;
            data.ingredienti = this.selectedIngredients;
            data.note_ricetta = noteRicetta;
        }
        
        if (this.currentContentType === 'chat' && (!data.contenuto || data.contenuto.trim() === '')) {
            alert('Inserisci un messaggio');
            return;
        }
        
        this.sendToServer(data);
        this.closeAddContentModal();
    }
    
    loadNegozi() {
        fetch('/forum/api/negozi/')
        .then(response => response.json())
        .then(data => {
            const select = document.getElementById('negozioSelect');
            data.negozi.forEach(negozio => {
                const option = document.createElement('option');
                option.value = negozio.id;
                option.textContent = `${negozio.nome} - ${negozio.citta}`;
                select.appendChild(option);
            });
        })
        .catch(error => console.error('Errore caricamento negozi:', error));
    }
    
    searchProdotti(query) {
        if (query.length < 2) {
            document.getElementById('prodottoResults').style.display = 'none';
            return;
        }
        
        fetch(`/forum/api/prodotti/?q=${encodeURIComponent(query)}`)
        .then(response => response.json())
        .then(data => {
            this.showProdottoResults(data.prodotti);
        })
        .catch(error => console.error('Errore ricerca prodotti:', error));
    }
    
    showProdottoResults(prodotti) {
        const resultsDiv = document.getElementById('prodottoResults');
        
        if (prodotti.length === 0) {
            resultsDiv.style.display = 'none';
            return;
        }
        
        resultsDiv.innerHTML = prodotti.map(prodotto => 
            `<div class="search-result" onclick="forumChat.addIngredient(${prodotto.id}, '${prodotto.nome}', '${prodotto.marca}')">
                <strong>${prodotto.nome}</strong><br>
                <small>${prodotto.marca} - ${prodotto.categoria}</small>
            </div>`
        ).join('');
        
        resultsDiv.style.display = 'block';
    }
    
    addIngredient(id, nome, marca) {
        if (this.selectedIngredients.find(ing => ing.prodotto_id === id)) {
            return; // Già aggiunto
        }
        
        this.selectedIngredients.push({
            prodotto_id: id,
            nome: nome,
            marca: marca,
            quantita: '1',
            note: ''
        });
        
        this.updateIngredientiSelected();
        document.getElementById('prodottoSearch').value = '';
        document.getElementById('prodottoResults').style.display = 'none';
    }
    
    updateIngredientiSelected() {
        const container = document.getElementById('ingredientiSelezionati');
        container.innerHTML = this.selectedIngredients.map((ing, index) =>
            `<div class="ingrediente-selected">
                <span>${ing.nome} (${ing.marca})</span>
                <button class="ingrediente-remove" onclick="forumChat.removeIngredient(${index})">×</button>
            </div>`
        ).join('');
    }
    
    removeIngredient(index) {
        this.selectedIngredients.splice(index, 1);
        this.updateIngredientiSelected();
    }
    
    updateConnectionStatus(connected) {
        const statusDiv = document.getElementById('connectionStatus');
        if (connected) {
            statusDiv.style.display = 'none';
        } else {
            statusDiv.style.display = 'flex';
        }
    }
    
    getCsrfToken() {
        // Cerca il token CSRF nel DOM
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        if (csrfToken) {
            return csrfToken.value;
        }
        
        // Fallback: cerca nel cookie
        const cookieValue = document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='));
        
        if (cookieValue) {
            return cookieValue.split('=')[1];
        }
        
        // Fallback finale: usa il meta tag se presente
        const metaToken = document.querySelector('meta[name="csrf-token"]');
        if (metaToken) {
            return metaToken.getAttribute('content');
        }
        
        console.error('CSRF token non trovato');
        return '';
    }
}

// Funzioni globali per il modal
function closeAddContentModal() {
    document.getElementById('addContentModal').style.display = 'none';
    document.body.style.overflow = 'auto';
    
    // Reset form
    document.querySelectorAll('.content-form input, .content-form textarea').forEach(input => {
        input.value = '';
    });
    
    if (window.forumChat) {
        window.forumChat.selectedIngredients = [];
        window.forumChat.updateIngredientiSelected();
        window.forumChat.selectContentType('chat');
        window.forumChat.selectRating(5);
    }
}

// Chiudi modal cliccando fuori
document.addEventListener('click', function(e) {
    const modal = document.getElementById('addContentModal');
    if (e.target === modal) {
        closeAddContentModal();
    }
});

// Chiudi modal con ESC
document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
        closeAddContentModal();
    }
});
