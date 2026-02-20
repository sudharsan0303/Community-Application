/**
 * Form Validation Utility for Community Helper Hub
 * Provides client-side validation for forms with detailed error messages
 * and visual feedback.
 */

class FormValidator {
    constructor(formElement, options = {}) {
        this.form = formElement;
        this.options = {
            validateOnInput: true,
            validateOnBlur: true,
            ...options
        };
        this.validators = {};
        this.init();
    }

    init() {
        if (!this.form) return;
        
        // Prevent default form submission and validate instead
        this.form.addEventListener('submit', (e) => {
            if (!this.validateAll()) {
                e.preventDefault();
            }
        });

        // Set up input validation events if enabled
        if (this.options.validateOnInput || this.options.validateOnBlur) {
            const inputs = this.form.querySelectorAll('input, select, textarea');
            
            inputs.forEach(input => {
                if (this.options.validateOnInput) {
                    input.addEventListener('input', () => {
                        this.validateField(input.name);
                    });
                }
                
                if (this.options.validateOnBlur) {
                    input.addEventListener('blur', () => {
                        this.validateField(input.name);
                    });
                }
            });
        }
    }

    // Add a validator for a specific field
    addValidator(fieldName, validatorFn, errorMessage) {
        if (!this.validators[fieldName]) {
            this.validators[fieldName] = [];
        }
        
        this.validators[fieldName].push({
            validate: validatorFn,
            message: errorMessage
        });
    }

    // Validate a specific field
    validateField(fieldName) {
        const field = this.form.querySelector(`[name="${fieldName}"]`);
        if (!field || !this.validators[fieldName]) return true;
        
        // Remove existing error messages
        this.clearError(field);
        
        // Run all validators for this field
        for (const validator of this.validators[fieldName]) {
            if (!validator.validate(field.value, field)) {
                this.showError(field, validator.message);
                return false;
            }
        }
        
        // Field is valid
        this.showSuccess(field);
        return true;
    }

    // Validate all fields in the form
    validateAll() {
        let isValid = true;
        
        // Validate each field that has validators
        for (const fieldName in this.validators) {
            if (!this.validateField(fieldName)) {
                isValid = false;
            }
        }
        
        return isValid;
    }

    // Display error message for a field
    showError(field, message) {
        field.classList.add('is-invalid');
        field.classList.remove('is-valid');
        
        // Create or update error message
        let errorElement = field.parentElement.querySelector('.invalid-feedback');
        
        if (!errorElement) {
            errorElement = document.createElement('div');
            errorElement.className = 'invalid-feedback';
            field.parentElement.appendChild(errorElement);
        }
        
        errorElement.textContent = message;
    }

    // Display success state for a field
    showSuccess(field) {
        field.classList.remove('is-invalid');
        field.classList.add('is-valid');
        
        // Remove any existing error message
        const errorElement = field.parentElement.querySelector('.invalid-feedback');
        if (errorElement) {
            errorElement.remove();
        }
    }

    // Clear validation state for a field
    clearError(field) {
        field.classList.remove('is-invalid');
        field.classList.remove('is-valid');
        
        const errorElement = field.parentElement.querySelector('.invalid-feedback');
        if (errorElement) {
            errorElement.remove();
        }
    }
}

// Common validators
const Validators = {
    required: (value) => value.trim() !== '',
    email: (value) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value),
    minLength: (min) => (value) => value.length >= min,
    maxLength: (max) => (value) => value.length <= max,
    pattern: (regex) => (value) => regex.test(value),
    match: (otherFieldName) => (value, field) => {
        const otherField = field.form.querySelector(`[name="${otherFieldName}"]`);
        return otherField && value === otherField.value;
    },
    // Prevent common XSS attacks
    noScript: (value) => !/<script[\s\S]*?>/i.test(value),
    // Sanitize input to prevent SQL injection
    noSqlInjection: (value) => !/['"\\;]/.test(value)
};

// Initialize form validation on page load
document.addEventListener('DOMContentLoaded', () => {
    // Example usage for login form
    const loginForm = document.getElementById('login-form');
    if (loginForm) {
        const validator = new FormValidator(loginForm);
        
        validator.addValidator('email', Validators.required, 'Email is required');
        validator.addValidator('email', Validators.email, 'Please enter a valid email address');
        validator.addValidator('email', Validators.noSqlInjection, 'Invalid characters detected');
        
        validator.addValidator('password', Validators.required, 'Password is required');
        validator.addValidator('password', Validators.minLength(8), 'Password must be at least 8 characters');
    }
    
    // Example usage for registration form
    const registrationForm = document.getElementById('registration-form');
    if (registrationForm) {
        const validator = new FormValidator(registrationForm);
        
        validator.addValidator('name', Validators.required, 'Name is required');
        validator.addValidator('name', Validators.noScript, 'Invalid characters detected');
        
        validator.addValidator('email', Validators.required, 'Email is required');
        validator.addValidator('email', Validators.email, 'Please enter a valid email address');
        validator.addValidator('email', Validators.noSqlInjection, 'Invalid characters detected');
        
        validator.addValidator('password', Validators.required, 'Password is required');
        validator.addValidator('password', Validators.minLength(8), 'Password must be at least 8 characters');
        
        validator.addValidator('confirm_password', Validators.required, 'Please confirm your password');
        validator.addValidator('confirm_password', Validators.match('password'), 'Passwords do not match');
    }
    
    // Example usage for service request form
    const serviceRequestForm = document.getElementById('service-request-form');
    if (serviceRequestForm) {
        const validator = new FormValidator(serviceRequestForm);
        
        validator.addValidator('title', Validators.required, 'Title is required');
        validator.addValidator('title', Validators.maxLength(100), 'Title must be less than 100 characters');
        validator.addValidator('title', Validators.noScript, 'Invalid characters detected');
        
        validator.addValidator('description', Validators.required, 'Description is required');
        validator.addValidator('description', Validators.minLength(20), 'Description must be at least 20 characters');
        validator.addValidator('description', Validators.noScript, 'Invalid characters detected');
        
        validator.addValidator('location', Validators.required, 'Location is required');
        validator.addValidator('date', Validators.required, 'Date is required');
    }
});