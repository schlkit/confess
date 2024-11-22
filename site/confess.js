document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('confessionForm');
    const colorOptions = document.querySelectorAll('.color-option');
    const selectedColorInput = document.getElementById('selectedColor');
    const rulesModal = document.getElementById('rulesModal');
    const agreeButton = document.getElementById('agreeButton');
    const cancelButton = document.getElementById('cancelButton');

    // Handle color selection
    colorOptions.forEach(option => {
        option.addEventListener('click', function() {
            colorOptions.forEach(opt => opt.classList.remove('active'));
            this.classList.add('active');
            selectedColorInput.value = this.dataset.color;
        });
    });

    // Form submission
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        rulesModal.style.display = 'block';
    });

    // Handle agree button click
    agreeButton.addEventListener('click', async function() {
        rulesModal.style.display = 'none';
        
        // Create FormData here, when actually submitting
        const formData = new FormData();
        formData.append('confessionText', document.getElementById('confessionText').value);
        formData.append('color', selectedColorInput.value);
        
        try {
            const response = await fetch('/submit_confession', {
                method: 'POST',
                body: formData
            });
            
            if (response.ok) {
                form.reset();
                alert('Your confession has been submitted for review!');
                window.location.href = '/confess';
            } else {
                throw new Error('Failed to submit confession');
            }
        } catch (error) {
            console.error('Error:', error);
            alert('Failed to submit confession. Please try again.');
        }
    });

    // Handle cancel button click
    cancelButton.addEventListener('click', function() {
        rulesModal.style.display = 'none';
    });

    // Close modal if clicking outside
    window.addEventListener('click', function(e) {
        if (e.target === rulesModal) {
            rulesModal.style.display = 'none';
        }
    });
});