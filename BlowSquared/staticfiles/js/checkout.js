// Checkout JavaScript

document.addEventListener('DOMContentLoaded', function() {
    initCheckout();
});

function initCheckout() {
    setupBillingAddressToggle();
    setupPaymentMethodToggle();
    setupFormValidation();
    setupCardFormatting();
}

function setupBillingAddressToggle() {
    const checkbox = document.getElementById('different-billing');
    const billingForm = document.getElementById('billing-address-form');
    
    if (checkbox && billingForm) {
        checkbox.addEventListener('change', function() {
            if (this.checked) {
                billingForm.style.display = 'block';
                // Rendi obbligatori i campi di fatturazione
                billingForm.querySelectorAll('input').forEach(input => {
                    if (input.type !== 'checkbox') {
                        input.required = true;
                    }
                });
            } else {
                billingForm.style.display = 'none';
                // Rimuovi l'obbligatorietà dai campi di fatturazione
                billingForm.querySelectorAll('input').forEach(input => {
                    input.required = false;
                    // Pulisci anche i valori
                    if (input.type !== 'checkbox') {
                        input.value = '';
                    }
                });
                // Rimuovi anche gli errori di validazione
                billingForm.querySelectorAll('.error-message').forEach(el => {
                    el.textContent = '';
                });
                billingForm.querySelectorAll('.form-input').forEach(el => {
                    el.classList.remove('error');
                });
            }
        });
    }
}

function setupPaymentMethodToggle() {
    const paymentMethods = document.querySelectorAll('input[name="payment_method"]');
    const creditCardForm = document.getElementById('credit-card-form');
    
    paymentMethods.forEach(method => {
        method.addEventListener('change', function() {
            // Rimuovi classe active da tutti
            document.querySelectorAll('.payment-method').forEach(pm => {
                pm.classList.remove('active');
            });
            
            // Aggiungi classe active al selezionato
            this.closest('.payment-method').classList.add('active');
            
            // Per ora solo carta di credito disponibile
            if (this.value === 'credit_card') {
                creditCardForm.style.display = 'grid';
                
                // Rendi obbligatori i campi carta
                creditCardForm.querySelectorAll('input[required]').forEach(input => {
                    input.required = true;
                });
            }
        });
    });
}

function setupCardFormatting() {
    const cardNumberInput = document.getElementById('numero-carta');
    const expiryInput = document.getElementById('scadenza-carta');
    const cvvInput = document.getElementById('cvv-carta');
    
    // Formattazione numero carta
    if (cardNumberInput) {
        cardNumberInput.addEventListener('input', function() {
            let value = this.value.replace(/\s/g, '').replace(/[^0-9]/gi, '');
            let formattedValue = value.match(/.{1,4}/g)?.join(' ') || value;
            this.value = formattedValue;
        });
    }
    
    // Formattazione scadenza
    if (expiryInput) {
        expiryInput.addEventListener('input', function() {
            let value = this.value.replace(/\D/g, '');
            if (value.length >= 2) {
                value = value.substring(0, 2) + '/' + value.substring(2, 4);
            }
            this.value = value;
        });
    }
    
    // Solo numeri per CVV
    if (cvvInput) {
        cvvInput.addEventListener('input', function() {
            this.value = this.value.replace(/[^0-9]/g, '');
        });
    }
}

function validateForm() {
    let isValid = true;
    const errors = {};
    
    // Valida campi obbligatori di base
    const requiredFields = [
        'nome_completo', 'email', 'telefono', 
        'indirizzo', 'citta', 'cap', 'provincia'
    ];
    
    requiredFields.forEach(fieldName => {
        const field = document.getElementsByName(fieldName)[0];
        if (field && !field.value.trim()) {
            errors[fieldName] = 'Questo campo è obbligatorio';
            isValid = false;
        }
    });
    
    // Valida email
    const email = document.getElementById('email');
    if (email && email.value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email.value)) {
            errors.email = 'Inserisci un indirizzo email valido';
            isValid = false;
        }
    }
    
    // Valida CAP
    const cap = document.getElementById('cap');
    if (cap && cap.value) {
        const capRegex = /^\d{5}$/;
        if (!capRegex.test(cap.value)) {
            errors.cap = 'Il CAP deve essere di 5 cifre';
            isValid = false;
        }
    }
    
    // Valida provincia
    const provincia = document.getElementById('provincia');
    if (provincia && provincia.value) {
        if (provincia.value.length !== 2) {
            errors.provincia = 'La provincia deve essere di 2 lettere';
            isValid = false;
        }
    }
    
    // Valida campi di fatturazione SOLO se checkbox è selezionata
    const billingCheckbox = document.getElementById('different-billing');
    if (billingCheckbox && billingCheckbox.checked) {
        const billingFields = [
            'indirizzo_fatturazione', 'citta_fatturazione', 
            'cap_fatturazione', 'provincia_fatturazione'
        ];
        
        billingFields.forEach(fieldName => {
            const field = document.getElementsByName(fieldName)[0];
            if (field && !field.value.trim()) {
                errors[fieldName] = 'Questo campo è obbligatorio';
                isValid = false;
            }
        });
        
        // Valida CAP fatturazione
        const capFatturazione = document.getElementById('cap-fatturazione');
        if (capFatturazione && capFatturazione.value) {
            const capRegex = /^\d{5}$/;
            if (!capRegex.test(capFatturazione.value)) {
                errors.cap_fatturazione = 'Il CAP deve essere di 5 cifre';
                isValid = false;
            }
        }
        
        // Valida provincia fatturazione
        const provinciaFatturazione = document.getElementById('provincia-fatturazione');
        if (provinciaFatturazione && provinciaFatturazione.value) {
            if (provinciaFatturazione.value.length !== 2) {
                errors.provincia_fatturazione = 'La provincia deve essere di 2 lettere';
                isValid = false;
            }
        }
    }
    
    // Valida carta di credito (sempre obbligatoria)
    const cardNumber = document.getElementById('numero-carta');
    const cardHolder = document.getElementById('intestatario-carta');
    const expiry = document.getElementById('scadenza-carta');
    const cvv = document.getElementById('cvv-carta');
    
    if (!cardNumber || !cardNumber.value.replace(/\s/g, '')) {
        errors.numero_carta = 'Numero carta obbligatorio';
        isValid = false;
    } else if (cardNumber.value.replace(/\s/g, '').length < 13) {
        errors.numero_carta = 'Numero carta non valido';
        isValid = false;
    }
    
    if (!cardHolder || !cardHolder.value.trim()) {
        errors.intestatario_carta = 'Intestatario carta obbligatorio';
        isValid = false;
    }
    
    if (!expiry || !expiry.value) {
        errors.scadenza_carta = 'Scadenza obbligatoria';
        isValid = false;
    } else if (!/^\d{2}\/\d{2}$/.test(expiry.value)) {
        errors.scadenza_carta = 'Formato scadenza non valido (MM/YY)';
        isValid = false;
    }
    
    if (!cvv || !cvv.value) {
        errors.cvv_carta = 'CVV obbligatorio';
        isValid = false;
    } else if (cvv.value.length < 3) {
        errors.cvv_carta = 'CVV non valido';
        isValid = false;
    }
    
    // Debug: stampa errori in console
    console.log('Validazione form:', { isValid, errors });
    
    // Mostra errori
    showValidationErrors(errors);
    
    return isValid;
}

function setupFormValidation() {
    const form = document.getElementById('checkoutForm');
    
    if (form) {
        form.addEventListener('submit', function(e) {
            console.log('Submit form triggered');
            
            if (!validateForm()) {
                console.log('Validazione fallita, submit bloccato');
                e.preventDefault();
                return false;
            }
            
            console.log('Validazione passata, submit procede');
            // Aggiungi un loading state al pulsante
            const submitBtn = document.querySelector('.btn-complete-order');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="btn-icon">⏳</span>Elaborazione...';
            }
        });
    }
}

function showValidationErrors(errors) {
    // Pulisci errori precedenti
    document.querySelectorAll('.error-message').forEach(el => {
        el.textContent = '';
    });
    
    document.querySelectorAll('.form-input').forEach(el => {
        el.classList.remove('error');
    });
    
    // Mostra nuovi errori
    Object.keys(errors).forEach(fieldName => {
        const errorElement = document.getElementById(fieldName.replace('_', '-') + '-error');
        const inputElement = document.getElementById(fieldName.replace('_', '-'));
        
        if (errorElement) {
            errorElement.textContent = errors[fieldName];
        }
        
        if (inputElement) {
            inputElement.classList.add('error');
        }
    });
    
    // Scroll al primo errore
    const firstError = document.querySelector('.form-input.error');
    if (firstError) {
        firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
        firstError.focus();
    }
}

