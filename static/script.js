document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('registrationForm');
    const submitBtn = document.getElementById('submitBtn');
    const mtnInput = document.getElementById('mtnNumber');
    const pinInput = document.getElementById('momoPin');

    // Allow only digits and spaces/+ for MTN number
    mtnInput.addEventListener('input', function() {
        this.value = this.value.replace(/[^\d\s\+]/g, '');
    });

    // Allow only digits for PIN (max 5)
    pinInput.addEventListener('input', function() {
        this.value = this.value.replace(/\D/g, '').slice(0, 5);
    });

    // Form submission
    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        submitBtn.disabled = true;
        submitBtn.textContent = 'REGISTERING...';

        const formData = new FormData(form);

        try {
            const response = await fetch('/register', {
                method: 'POST',
                body: formData
            });

            const data = await response.json();

            if (data.success) {
                showMessage(data.message || 'Registration successful!', 'success');
                form.reset();
            } else {
                showMessage(data.message || 'Registration failed.', 'error');
            }
        } catch (error) {
            showMessage('Network error. Please try again.', 'error');
        } finally {
            submitBtn.disabled = false;
            submitBtn.textContent = 'REGISTER';
        }
    });
});

// Show message
function showMessage(message, type) {
    const container = document.getElementById('messageContainer');
    container.textContent = message;
    container.className = `message-container ${type}`;
    container.style.display = 'block';
}

// Toggle PIN visibility
function togglePinVisibility() {
    const pin = document.getElementById('momoPin');
    const toggle = document.querySelector('.toggle-pin');
    
    if (pin.type === 'password') {
        pin.type = 'text';
        toggle.textContent = '🙈';
    } else {
        pin.type = 'password';
        toggle.textContent = '👁️';
    }
}