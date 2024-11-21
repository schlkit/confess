// Initialize AOS (Animate On Scroll)
document.addEventListener('DOMContentLoaded', function() {
    AOS.init({
        duration: 1000,
        once: true
    });
});

// Navbar scroll effect
window.addEventListener('scroll', function() {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 50) {
        navbar.style.backgroundColor = 'rgba(255, 255, 255, 0.95)';
    } else {
        navbar.style.backgroundColor = 'rgba(255, 255, 255, 0.8)';
    }
});

// Add smooth scrolling to all links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        document.querySelector(this.getAttribute('href')).scrollIntoView({
            behavior: 'smooth'
        });
    });
});

// Add this to your existing script.js
document.addEventListener('DOMContentLoaded', function() {
    const fonts = [
        'Cabinet Grotesk',     // Modern geometric sans
        'Playfair Display',
        'Space Grotesk',       // Technical sans
        'Bodoni Moda',         // Classic italic serif
        'General Sans',        // Clean contemporary
        'Syne',                // Unique modern
        'Outfit',              // Rounded sans
        'Clash Display',       // Sharp modern
        'SF Pro Display'       // Apple's system font
    ];
    
    // Create hidden elements with each font to trigger loading
    const preloadDiv = document.createElement('div');
    preloadDiv.style.opacity = '0';
    preloadDiv.style.position = 'absolute';
    document.body.appendChild(preloadDiv);
    
    // Preload all fonts
    Promise.all(fonts.map(font => {
        return new Promise((resolve) => {
            preloadDiv.style.fontFamily = `${font}, sans-serif`;
            // Use Font Loading API
            document.fonts.ready.then(() => {
                resolve();
            });
        });
    })).then(() => {
        // Start animation only after fonts are loaded
        const title = document.querySelector('.main-title');
        let currentFont = 0;
        const interval = 120;
        
        const fontAnimation = setInterval(() => {
            title.style.fontFamily = `${fonts[currentFont]}, sans-serif`;
            currentFont++;
            
            if (currentFont >= fonts.length) {
                clearInterval(fontAnimation);
                document.body.removeChild(preloadDiv); // Clean up
            }
        }, interval);
    });

    // Handle tap to reveal
    document.querySelectorAll('.confession-author').forEach(author => {
        author.addEventListener('click', function() {
            this.innerHTML = 'posted by <span style="color: #1d1d1f;">anonymous</span>';
        });
    });
});
