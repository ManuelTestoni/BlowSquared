// Checkout JavaScript functionality

document.addEventListener('DOMContentLoaded', function() {
    // Address toggle functionality
    const sameAddressCheckbox = document.getElementById('same-address');
    const billingSection = document.getElementById('billing-section');
    
    sameAddressCheckbox.addEventListener('change', function() {
        if (this.checked) {
            billingSection.style.display = 'none';
            clearBillingFields();
            removeBillingRequired();
        } else {
            billingSection.style.display = 'block';
            addBillingRequired();
        }
    });
    
    // Card number formatting
    const numeroCartaInput = document.getElementById('numero-carta');
    numeroCartaInput.addEventListener('input', function() {
        let value = this.value.replace(/\s/g, '').replace(/[^0-9]/gi, '');
        let formattedValue = value.match(/.{1,4}/g)?.join(' ') || value;
        this.value = formattedValue;
    });
    
    // Expiry date formatting
    const scadenzaInput = document.getElementById('scadenza-carta');
    scadenzaInput.addEventListener('input', function() {
        let value = this.value.replace(/\D/g, '');
        if (value.length >= 2) {
            value = value.substring(0, 2) + '/' + value.substring(2, 4);
        }
        this.value = value;
    });
    
    // CVV validation
    const cvvInput = document.getElementById('cvv-carta');
    cvvInput.addEventListener('input', function() {
        this.value = this.value.replace(/[^0-9]/g, '');
    });
    
    // Phone number formatting
    const telefonoInput = document.getElementById('telefono');
    telefonoInput.addEventListener('input', function() {
        let value = this.value.replace(/[^0-9+\s]/g, '');
        this.value = value;
    });
    
    // CAP validation
    const capInputs = document.querySelectorAll('input[name$="_spedizione"], input[name$="_fatturazione"]');
    capInputs.forEach(input => {
        if (input.name.includes('cap')) {
            input.addEventListener('input', function() {
                this.value = this.value.replace(/[^0-9]/g, '').substring(0, 5);
            });
        }
    });
    
    // Form validation
    const form = document.getElementById('checkoutForm');
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (validateForm()) {
            // Show loading state
            const submitBtn = document.querySelector('.btn-complete-order');
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<span class="btn-icon">⏳</span> Elaborazione...';
            submitBtn.disabled = true;
            
            // Simulate processing
            setTimeout(() => {
                alert('Ordine completato con successo!');
                // In a real app, you would submit the form here
                // form.submit();
            }, 2000);
        }
    });
    
    // Real-time validation
    const inputs = form.querySelectorAll('input[required]');
    inputs.forEach(input => {
        input.addEventListener('blur', function() {
            validateField(this);
        });
        
        input.addEventListener('input', function() {
            if (this.classList.contains('error')) {
                validateField(this);
            }
        });
    });
});

function clearBillingFields() {
    const billingInputs = document.querySelectorAll('#billing-section input');
    billingInputs.forEach(input => {
        input.value = '';
    });
}

function addBillingRequired() {
    const billingInputs = document.querySelectorAll('#billing-section input');
    billingInputs.forEach(input => {
        input.setAttribute('required', 'required');
    });
}

function removeBillingRequired() {
    const billingInputs = document.querySelectorAll('#billing-section input');
    billingInputs.forEach(input => {
        input.removeAttribute('required');
    });
}

function validateField(field) {
    const errorElement = document.getElementById(field.name + '-error');
    let isValid = true;
    let errorMessage = '';
    
    // Required field validation
    if (field.hasAttribute('required') && !field.value.trim()) {
        isValid = false;
        errorMessage = 'Questo campo è obbligatorio';
    }
    
    // Email validation
    else if (field.type === 'email') {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (field.value && !emailRegex.test(field.value)) {
            isValid = false;
            errorMessage = 'Inserisci un indirizzo email valido';
        }
    }
    
    // Phone validation
    else if (field.name === 'telefono') {
        const phoneRegex = /^[\+]?[0-9\s]{8,15}$/;
        if (field.value && !phoneRegex.test(field.value)) {
            isValid = false;
            errorMessage = 'Inserisci un numero di telefono valido';
        }
    }
    
    // CAP validation
    else if (field.name.includes('cap')) {
        const capRegex = /^[0-9]{5}$/;
        if (field.value && !capRegex.test(field.value)) {
            isValid = false;
            errorMessage = 'Il CAP deve essere di 5 cifre';
        }
    }
    
    // Credit card validation
    else if (field.name === 'numero_carta') {
        const cardNumber = field.value.replace(/\s/g, '');
        if (field.value && (cardNumber.length < 13 || cardNumber.length > 19)) {
            isValid = false;
            errorMessage = 'Numero carta non valido';
        }
    }
    
    // Expiry date validation
    else if (field.name === 'scadenza_carta') {
        const expiryRegex = /^(0[1-9]|1[0-2])\/([0-9]{2})$/;
        if (field.value && !expiryRegex.test(field.value)) {
            isValid = false;
            errorMessage = 'Formato scadenza non valido (MM/YY)';
        } else if (field.value) {
            const [month, year] = field.value.split('/');
            const expiry = new Date(2000 + parseInt(year), parseInt(month) - 1);
            const now = new Date();
            if (expiry < now) {
                isValid = false;
                errorMessage = 'La carta è scaduta';
            }
        }
    }
    
    // CVV validation
    else if (field.name === 'cvv_carta') {
        const cvvRegex = /^[0-9]{3,4}$/;
        if (field.value && !cvvRegex.test(field.value)) {
            isValid = false;
            errorMessage = 'CVV non valido (3-4 cifre)';
        }
    }
    
    // Province validation
    else if (field.name.includes('provincia')) {
        const provinciaRegex = /^[A-Z]{2}$/;
        if (field.value && !provinciaRegex.test(field.value)) {
            isValid = false;
            errorMessage = 'Inserisci la sigla della provincia (es. BO)';
        }
    }
    
    // Update UI
    if (isValid) {
        field.classList.remove('error');
        if (errorElement) {
            errorElement.textContent = '';
            errorElement.classList.remove('show');
        }
    } else {
        field.classList.add('error');
        if (errorElement) {
            errorElement.textContent = errorMessage;
            errorElement.classList.add('show');
        }
    }
    
    return isValid;
}

function validateForm() {
    const form = document.getElementById('checkoutForm');
    const requiredFields = form.querySelectorAll('input[required]');
    let isFormValid = true;
    
    requiredFields.forEach(field => {
        if (!validateField(field)) {
            isFormValid = false;
        }
    });
    
    if (!isFormValid) {
        // Scroll to first error
        const firstError = form.querySelector('.error');
        if (firstError) {
            firstError.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
    }
    
    return isFormValid;
}

// Add error styles
const style = document.createElement('style');
style.textContent = `
    .form-input.error,
    .form-textarea.error {
        border-color: #e74c3c;
        background-color: #fdf2f2;
    }
    
    .form-input.error:focus,
    .form-textarea.error:focus {
        box-shadow: 0 0 0 3px rgba(231, 76, 60, 0.1);
    }
`;
document.head.appendChild(style);
