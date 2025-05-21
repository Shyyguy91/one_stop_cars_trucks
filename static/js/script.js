// Smooth scrolling for anchor links
document.querySelectorAll('nav a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();

        const targetId = this.getAttribute('href');
        const targetElement = document.querySelector(targetId);

        if (targetElement) {
            targetElement.scrollIntoView({
                behavior: 'smooth'
            });
        }
    });
});

// Basic client-side form validation (example for contact form)
// This is separate from Flask's server-side validation.
document.addEventListener('DOMContentLoaded', () => {
    const contactForm = document.querySelector('.contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            const nameInput = this.querySelector('input[type="text"]');
            const emailInput = this.querySelector('input[type="email"]');
            const messageInput = this.querySelector('textarea');

            let isValid = true;
            if (nameInput.value.trim() === '') {
                alert('Please enter your name.');
                isValid = false;
                nameInput.focus();
            } else if (emailInput.value.trim() === '' || !emailInput.value.includes('@')) {
                alert('Please enter a valid email address.');
                isValid = false;
                emailInput.focus();
            } else if (messageInput.value.trim() === '') {
                alert('Please enter your message.');
                isValid = false;
                messageInput.focus();
            }

            if (!isValid) {
                e.preventDefault(); // Stop form submission if validation fails
            } else {
                // In a real app, you'd send this data via fetch or XMLHttpRequest
                // For now, we'll just show a success message and prevent default
                // to illustrate client-side validation without a backend endpoint.
                e.preventDefault();
                alert('Your message has been sent (demo)!');
                contactForm.reset();
            }
        });
    }
});

// Add more JavaScript here as needed:
// - Image carousel for car detail pages
// - Filtering/sorting inventory on the public side
// - AJAX requests for dynamic updates on the admin dashboard