document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('confessionForm');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData();
        formData.append('confessionText', document.getElementById('confessionText').value);
        
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
});