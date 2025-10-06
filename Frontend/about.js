// About page JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Add smooth scrolling for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]');
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href').substring(1);
            const targetElement = document.getElementById(targetId);
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Add animation on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    // Observe all cards for animation
    const cards = document.querySelectorAll('.about-card, .tech-card, .features-card, .tips-card, .contact-card');
    cards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'all 0.6s ease';
        observer.observe(card);
    });
    
    // Add interactive hover effects to tech items
    const techItems = document.querySelectorAll('.tech-item');
    techItems.forEach(item => {
        item.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 10px 25px rgba(0, 0, 0, 0.1)';
        });
        
        item.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.1)';
        });
    });
    
    // Add interactive hover effects to feature items
    const featureItems = document.querySelectorAll('.feature-item');
    featureItems.forEach(item => {
        item.addEventListener('mouseenter', function() {
            const icon = this.querySelector('i');
            if (icon) {
                icon.style.transform = 'scale(1.2)';
                icon.style.color = '#667eea';
            }
        });
        
        item.addEventListener('mouseleave', function() {
            const icon = this.querySelector('i');
            if (icon) {
                icon.style.transform = 'scale(1)';
                icon.style.color = '#4ecdc4';
            }
        });
    });
    
    // Add typing animation to the main title
    const mainTitle = document.querySelector('.page-header h2');
    if (mainTitle) {
        const text = mainTitle.textContent;
        mainTitle.textContent = '';
        mainTitle.style.borderRight = '2px solid #667eea';
        
        let i = 0;
        const typeWriter = () => {
            if (i < text.length) {
                mainTitle.textContent += text.charAt(i);
                i++;
                setTimeout(typeWriter, 100);
            } else {
                mainTitle.style.borderRight = 'none';
            }
        };
        
        setTimeout(typeWriter, 500);
    }
    
    // Add parallax effect to background shapes
    window.addEventListener('scroll', () => {
        const scrolled = window.pageYOffset;
        const shapes = document.querySelectorAll('.shape');
        
        shapes.forEach((shape, index) => {
            const speed = 0.5 + (index * 0.1);
            shape.style.transform = `translateY(${scrolled * speed}px) rotate(${scrolled * 0.1}deg)`;
        });
    });
    
    // Add click-to-copy functionality for contact info
    const contactItems = document.querySelectorAll('.contact-item span');
    contactItems.forEach(item => {
        item.style.cursor = 'pointer';
        item.title = 'Click to copy';
        
        item.addEventListener('click', function() {
            const text = this.textContent;
            navigator.clipboard.writeText(text).then(() => {
                showCopyNotification('Copied to clipboard!');
            }).catch(() => {
                // Fallback for older browsers
                const textArea = document.createElement('textarea');
                textArea.value = text;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
                showCopyNotification('Copied to clipboard!');
            });
        });
    });
    
    function showCopyNotification(message) {
        const notification = document.createElement('div');
        notification.className = 'copy-notification';
        notification.innerHTML = `
            <i class="fas fa-check"></i>
            <span>${message}</span>
        `;
        
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: #f0fdf4;
            color: #166534;
            padding: 12px 16px;
            border-radius: 8px;
            border: 1px solid #bbf7d0;
            display: flex;
            align-items: center;
            gap: 8px;
            z-index: 1000;
            animation: slideInRight 0.3s ease-out;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            font-size: 0.9rem;
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.animation = 'slideOutRight 0.3s ease-out';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 2000);
    }
    
    // Add smooth transitions to all interactive elements
    const interactiveElements = document.querySelectorAll('button, .tech-item, .feature-item, .contact-item');
    interactiveElements.forEach(element => {
        element.style.transition = 'all 0.3s ease';
    });
    
    // Add loading animation for the page
    const pageContent = document.querySelector('.main-content');
    if (pageContent) {
        pageContent.style.opacity = '0';
        pageContent.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            pageContent.style.transition = 'all 0.8s ease';
            pageContent.style.opacity = '1';
            pageContent.style.transform = 'translateY(0)';
        }, 100);
    }
});
