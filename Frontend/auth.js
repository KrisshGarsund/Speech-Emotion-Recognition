// Authentication JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Password toggle functionality
    const passwordToggles = document.querySelectorAll('.password-toggle');
    passwordToggles.forEach(toggle => {
        toggle.addEventListener('click', function() {
            const input = this.parentElement.querySelector('input');
            const icon = this.querySelector('i');
            
            if (input.type === 'password') {
                input.type = 'text';
                icon.classList.remove('fa-eye');
                icon.classList.add('fa-eye-slash');
            } else {
                input.type = 'password';
                icon.classList.remove('fa-eye-slash');
                icon.classList.add('fa-eye');
            }
        });
    });

    // Form validation
    const forms = document.querySelectorAll('.auth-form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!validateForm(this)) {
                e.preventDefault();
            }
        });
    });

    // Real-time validation
    const inputs = document.querySelectorAll('input[required]');
    inputs.forEach(input => {
        input.addEventListener('blur', function() {
            validateField(this);
        });
        
        input.addEventListener('input', function() {
            clearFieldError(this);
        });
    });

    // Signup form specific validation
    const signupForm = document.getElementById('signupForm');
    if (signupForm) {
        const password = document.getElementById('password');
        const confirmPassword = document.getElementById('confirm_password');
        
        if (password && confirmPassword) {
            confirmPassword.addEventListener('input', function() {
                validatePasswordMatch(password, confirmPassword);
            });
        }
    }

    // Auto-hide flash messages
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach(message => {
        setTimeout(() => {
            message.style.opacity = '0';
            message.style.transform = 'translateY(-10px)';
            setTimeout(() => {
                if (message.parentNode) {
                    message.parentNode.removeChild(message);
                }
            }, 300);
        }, 5000);
    });

    // Add smooth transitions to flash messages
    flashMessages.forEach(message => {
        message.style.transition = 'all 0.3s ease';
    });
});

function validateForm(form) {
    let isValid = true;
    const inputs = form.querySelectorAll('input[required]');
    
    inputs.forEach(input => {
        if (!validateField(input)) {
            isValid = false;
        }
    });
    
    // Special validation for signup form
    if (form.id === 'signupForm') {
        const password = document.getElementById('password');
        const confirmPassword = document.getElementById('confirm_password');
        
        if (password && confirmPassword) {
            if (!validatePasswordMatch(password, confirmPassword)) {
                isValid = false;
            }
        }
        
        const terms = document.querySelector('input[name="terms"]');
        if (terms && !terms.checked) {
            showFieldError(terms, 'You must agree to the terms and conditions');
            isValid = false;
        }
    }
    
    return isValid;
}

function validateField(field) {
    const value = field.value.trim();
    const fieldName = field.name;
    
    // Clear previous errors
    clearFieldError(field);
    
    // Required field validation
    if (!value) {
        showFieldError(field, `${getFieldLabel(fieldName)} is required`);
        return false;
    }
    
    // Email validation
    if (fieldName === 'email' && !isValidEmail(value)) {
        showFieldError(field, 'Please enter a valid email address');
        return false;
    }
    
    // Password validation
    if (fieldName === 'password' && value.length < 6) {
        showFieldError(field, 'Password must be at least 6 characters long');
        return false;
    }
    
    // Username validation
    if (fieldName === 'username' && value.length < 3) {
        showFieldError(field, 'Username must be at least 3 characters long');
        return false;
    }
    
    return true;
}

function validatePasswordMatch(password, confirmPassword) {
    clearFieldError(confirmPassword);
    
    if (password.value !== confirmPassword.value) {
        showFieldError(confirmPassword, 'Passwords do not match');
        return false;
    }
    
    return true;
}

function showFieldError(field, message) {
    clearFieldError(field);
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error';
    errorDiv.textContent = message;
    errorDiv.style.cssText = `
        color: #dc2626;
        font-size: 0.8rem;
        margin-top: 4px;
        display: flex;
        align-items: center;
        gap: 4px;
    `;
    
    field.parentElement.appendChild(errorDiv);
    field.style.borderColor = '#dc2626';
    field.style.backgroundColor = '#fef2f2';
}

function clearFieldError(field) {
    const existingError = field.parentElement.querySelector('.field-error');
    if (existingError) {
        existingError.remove();
    }
    
    field.style.borderColor = '#e2e8f0';
    field.style.backgroundColor = '#f8fafc';
}

function getFieldLabel(fieldName) {
    const labels = {
        'username': 'Username',
        'email': 'Email',
        'password': 'Password',
        'confirm_password': 'Confirm Password'
    };
    return labels[fieldName] || fieldName;
}

function isValidEmail(email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
}

// Add loading state to forms
function addLoadingState(form) {
    const submitBtn = form.querySelector('.auth-btn');
    const originalText = submitBtn.querySelector('span').textContent;
    
    submitBtn.disabled = true;
    submitBtn.querySelector('span').textContent = 'Processing...';
    submitBtn.style.background = 'linear-gradient(45deg, #cbd5e0, #a0aec0)';
    
    // Add spinner
    const spinner = document.createElement('i');
    spinner.className = 'fas fa-spinner fa-spin';
    spinner.style.marginLeft = '8px';
    submitBtn.appendChild(spinner);
    
    return function removeLoadingState() {
        submitBtn.disabled = false;
        submitBtn.querySelector('span').textContent = originalText;
        submitBtn.style.background = 'linear-gradient(45deg, #667eea, #764ba2)';
        const spinner = submitBtn.querySelector('.fa-spinner');
        if (spinner) {
            spinner.remove();
        }
    };
}

// Enhanced form submission
document.addEventListener('DOMContentLoaded', function() {
    const forms = document.querySelectorAll('.auth-form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (validateForm(this)) {
                const removeLoading = addLoadingState(this);
                
                // Simulate processing time for better UX
                setTimeout(() => {
                    // The form will submit naturally after validation
                }, 1000);
            }
        });
    });
});

// Add input focus effects
document.addEventListener('DOMContentLoaded', function() {
    const inputs = document.querySelectorAll('input');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.classList.add('focused');
        });
        
        input.addEventListener('blur', function() {
            this.parentElement.classList.remove('focused');
        });
    });
});

// Add smooth animations
document.addEventListener('DOMContentLoaded', function() {
    // Animate auth card on load
    const authCard = document.querySelector('.auth-card');
    if (authCard) {
        authCard.style.opacity = '0';
        authCard.style.transform = 'translateY(30px)';
        
        setTimeout(() => {
            authCard.style.transition = 'all 0.6s ease';
            authCard.style.opacity = '1';
            authCard.style.transform = 'translateY(0)';
        }, 100);
    }
    
    // Animate dashboard elements
    const dashboardElements = document.querySelectorAll('.dashboard-welcome, .upload-section, .activity-section');
    dashboardElements.forEach((element, index) => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            element.style.transition = 'all 0.6s ease';
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }, 200 + (index * 100));
    });
});
