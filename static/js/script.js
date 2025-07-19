// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Mobile Navigation Toggle
    const hamburger = document.querySelector('.hamburger');
    const navMenu = document.querySelector('.nav-menu');
    
    if (hamburger && navMenu) {
        hamburger.addEventListener('click', function() {
            hamburger.classList.toggle('active');
            navMenu.classList.toggle('active');
        });
        
        // Close mobile menu when clicking on a link
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', () => {
                hamburger.classList.remove('active');
                navMenu.classList.remove('active');
            });
        });
    }
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // Scroll animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animate');
                
                // Animate skill bars
                if (entry.target.classList.contains('skill-item')) {
                    const skillProgress = entry.target.querySelector('.skill-progress');
                    if (skillProgress) {
                        const width = skillProgress.getAttribute('data-width');
                        setTimeout(() => {
                            skillProgress.style.width = width + '%';
                        }, 200);
                    }
                }
            }
        });
    }, observerOptions);
    
    // Observe all scroll-animate elements
    document.querySelectorAll('.scroll-animate').forEach(el => {
        observer.observe(el);
    });
    
    // Observe skill items for progress bar animation
    document.querySelectorAll('.skill-item').forEach(el => {
        observer.observe(el);
    });
    
    // Navbar background on scroll
    window.addEventListener('scroll', function() {
        const navbar = document.querySelector('.navbar');
        if (navbar) {
            if (window.scrollY > 100) {
                navbar.style.background = 'rgba(255, 255, 255, 0.98)';
                navbar.style.boxShadow = '0 2px 20px rgba(0, 0, 0, 0.1)';
            } else {
                navbar.style.background = 'rgba(255, 255, 255, 0.95)';
                navbar.style.boxShadow = 'none';
            }
        }
    });
    
    // Flash message close functionality
    document.querySelectorAll('.flash-close').forEach(closeBtn => {
        closeBtn.addEventListener('click', function() {
            const flashMessage = this.parentElement;
            flashMessage.style.animation = 'slideOutRight 0.3s ease forwards';
            setTimeout(() => {
                flashMessage.remove();
            }, 300);
        });
    });
    
    // Auto-hide flash messages after 5 seconds
    document.querySelectorAll('.flash').forEach(flash => {
        setTimeout(() => {
            if (flash.parentElement) {
                flash.style.animation = 'slideOutRight 0.3s ease forwards';
                setTimeout(() => {
                    if (flash.parentElement) {
                        flash.remove();
                    }
                }, 300);
            }
        }, 5000);
    });
    
    // Contact form validation
    const contactForm = document.querySelector('.contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            const name = this.querySelector('#name').value.trim();
            const email = this.querySelector('#email').value.trim();
            const phone = this.querySelector('#phone').value.trim();
            const purpose = this.querySelector('#purpose').value;
            
            if (!name || !email || !phone || !purpose) {
                e.preventDefault();
                showNotification('Please fill in all required fields.', 'error');
                return false;
            }
            
            // Email validation
            const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailPattern.test(email)) {
                e.preventDefault();
                showNotification('Please enter a valid email address.', 'error');
                return false;
            }
            
            // Phone validation (basic)
            const phonePattern = /^[\+]?[1-9][\d]{0,15}$/;
            if (!phonePattern.test(phone.replace(/[\s\-\(\)]/g, ''))) {
                e.preventDefault();
                showNotification('Please enter a valid phone number.', 'error');
                return false;
            }
        });
    }
    
    // Utility function to show notifications
    function showNotification(message, type = 'info') {
        const flashContainer = document.querySelector('.flash-container') || createFlashContainer();
        
        const flash = document.createElement('div');
        flash.className = `flash flash-${type}`;
        flash.innerHTML = `
            ${message}
            <button class="flash-close">&times;</button>
        `;
        
        flashContainer.appendChild(flash);
        
        // Add close event listener
        flash.querySelector('.flash-close').addEventListener('click', function() {
            flash.style.animation = 'slideOutRight 0.3s ease forwards';
            setTimeout(() => flash.remove(), 300);
        });
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            if (flash.parentElement) {
                flash.style.animation = 'slideOutRight 0.3s ease forwards';
                setTimeout(() => flash.remove(), 300);
            }
        }, 5000);
    }
    
    function createFlashContainer() {
        const container = document.createElement('div');
        container.className = 'flash-container';
        document.body.appendChild(container);
        return container;
    }
    
    // Typewriter effect enhancement
    const typewriterElement = document.querySelector('.typewriter');
    if (typewriterElement) {
        // Add blinking cursor animation after typewriter completes
        setTimeout(() => {
            typewriterElement.style.borderRight = '3px solid transparent';
            setInterval(() => {
                typewriterElement.style.borderRight = 
                    typewriterElement.style.borderRight === '3px solid transparent' 
                        ? '3px solid var(--primary-color)' 
                        : '3px solid transparent';
            }, 750);
        }, 4000);
    }
    
    // Parallax effect for hero section
    window.addEventListener('scroll', function() {
        const scrolled = window.pageYOffset;
        const parallaxElements = document.querySelectorAll('.hero::before');
        
        parallaxElements.forEach(element => {
            const speed = 0.5;
            element.style.transform = `translateY(${scrolled * speed}px)`;
        });
    });
    
    // Loading animation for external links
    document.querySelectorAll('a[target="_blank"]').forEach(link => {
        link.addEventListener('click', function() {
            this.style.opacity = '0.7';
            this.style.transform = 'scale(0.95)';
            
            setTimeout(() => {
                this.style.opacity = '1';
                this.style.transform = 'scale(1)';
            }, 200);
        });
    });
    
    // Image lazy loading (for future implementation)
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.classList.remove('lazy');
                        observer.unobserve(img);
                    }
                }
            });
        });
        
        document.querySelectorAll('img[data-src]').forEach(img => {
            imageObserver.observe(img);
        });
    }
    
    // Add keyboard navigation support
    document.addEventListener('keydown', function(e) {
        // Close mobile menu with Escape key
        if (e.key === 'Escape') {
            const hamburger = document.querySelector('.hamburger');
            const navMenu = document.querySelector('.nav-menu');
            
            if (hamburger && navMenu && navMenu.classList.contains('active')) {
                hamburger.classList.remove('active');
                navMenu.classList.remove('active');
            }
            
            // Close flash messages with Escape key
            document.querySelectorAll('.flash').forEach(flash => {
                flash.style.animation = 'slideOutRight 0.3s ease forwards';
                setTimeout(() => flash.remove(), 300);
            });
        }
    });
    
    // Preload critical images
    const criticalImages = [
        '/static/images/profile.svg',
        '/static/images/logo.svg'
    ];
    
    criticalImages.forEach(src => {
        const img = new Image();
        img.src = src;
    });
    
    // Performance monitoring (optional)
    if ('performance' in window) {
        window.addEventListener('load', function() {
            const loadTime = performance.timing.loadEventEnd - performance.timing.navigationStart;
            console.log(`Page load time: ${loadTime}ms`);
        });
    }
});

// Additional CSS animations for slideOutRight
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOutRight {
        from {
            opacity: 1;
            transform: translateX(0);
        }
        to {
            opacity: 0;
            transform: translateX(100px);
        }
    }
`;
document.head.appendChild(style);
