// custom.js - Hospital Management System Frontend Functionality

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    initCarousels();
    initAnimations();
    initCounters();
    initFormValidations();
    initImageLoading();
    setupEventListeners();
    handleMobileMenu();
    setupSmoothScrolling();
});

/**
 * Initialize Owl Carousels
 */
function initCarousels() {
    // Doctor Carousel
    $(".doctor-carousel").owlCarousel({
        loop: true,
        margin: 20,
        nav: true,
        dots: false,
        navText: [
            '<i class="bi bi-chevron-left"></i>',
            '<i class="bi bi-chevron-right"></i>'
        ],
        responsive: {
            0: { items: 1 },
            768: { items: 2 },
            992: { items: 3 }
        }
    });

    // Testimonial Carousel (if you add one)
    $(".testimonial-carousel").owlCarousel({
        items: 1,
        loop: true,
        autoplay: true,
        autoplayTimeout: 5000,
        autoplayHoverPause: true
    });
}

/**
 * Setup scroll animations using Waypoints
 */
function initAnimations() {
    // Animate elements when they come into view
    const animateElements = document.querySelectorAll('.animate-on-scroll');

    animateElements.forEach(element => {
        new Waypoint({
            element: element,
            handler: function(direction) {
                if (direction === 'down') {
                    element.classList.add('animated');
                    this.destroy(); // Only animate once
                }
            },
            offset: '75%'
        });
    });

    // Add animation delays to department cards
    document.querySelectorAll('.department-card').forEach((card, index) => {
        card.style.transitionDelay = `${index * 0.1}s`;
    });
}

/**
 * Animate counter numbers
 */
function initCounters() {
    $('.stats-bar .display-5').each(function() {
        const $this = $(this);
        const target = parseInt($this.text().replace('+', ''));
        const suffix = $this.text().includes('+') ? '+' : '';

        $({ count: 0 }).animate({ count: target }, {
            duration: 2000,
            easing: 'swing',
            step: function() {
                $this.text(Math.ceil(this.count) + suffix);
            }
        });
    });
}

/**
 * Form validation and submission handling
 */
function initFormValidations() {
    // Contact form validation
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();

            // Simple validation
            const name = document.getElementById('name').value;
            const email = document.getElementById('email').value;
            const message = document.getElementById('message').value;

            if (!name || !email || !message) {
                showAlert('Please fill all required fields', 'danger');
                return;
            }

            // Simulate form submission
            const submitBtn = contactForm.querySelector('button[type="submit"]');
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Sending...';

            // In a real app, you would use fetch() to submit the form
            setTimeout(() => {
                showAlert('Your message has been sent successfully!', 'success');
                contactForm.reset();
                submitBtn.disabled = false;
                submitBtn.textContent = 'Send Message';
            }, 1500);
        });
    }

    // Appointment form handling
    const appointmentBtns = document.querySelectorAll('.book-appointment-btn');
    appointmentBtns.forEach(btn => {
        btn.addEventListener('click', function(e) {
            if (!this.dataset.doctorId) return;

            // In a real app, this would redirect to appointment page with doctor ID
            console.log('Booking appointment with doctor ID:', this.dataset.doctorId);
        });
    });
}

/**
 * Handle image loading states
 */
function initImageLoading() {
    const images = document.querySelectorAll('img, .image-loading');

    images.forEach(img => {
        if (img.complete) {
            img.classList.remove('image-loading');
        } else {
            img.addEventListener('load', function() {
                this.classList.remove('image-loading');
            });
            img.addEventListener('error', function() {
                // Fallback for broken images
                if (this.tagName === 'IMG') {
                    this.src = 'https://via.placeholder.com/400x300?text=Image+Not+Available';
                }
                this.classList.remove('image-loading');
            });
        }
    });
}

/**
 * Setup global event listeners
 */
function setupEventListeners() {
    // Tooltips
    $('[data-bs-toggle="tooltip"]').tooltip();

    // Popovers
    $('[data-bs-toggle="popover"]').popover();

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                window.scrollTo({
                    top: target.offsetTop - 80,
                    behavior: 'smooth'
                });
            }
        });
    });

    // Back to top button
    const backToTopBtn = document.createElement('button');
    backToTopBtn.innerHTML = '<i class="bi bi-arrow-up"></i>';
    backToTopBtn.className = 'btn btn-primary btn-back-to-top';
    backToTopBtn.title = 'Back to top';
    document.body.appendChild(backToTopBtn);

    window.addEventListener('scroll', function() {
        if (window.pageYOffset > 300) {
            backToTopBtn.classList.add('show');
        } else {
            backToTopBtn.classList.remove('show');
        }
    });

    backToTopBtn.addEventListener('click', function() {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
}

/**
 * Mobile menu toggle functionality
 */
function handleMobileMenu() {
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const mobileMenu = document.getElementById('mobileMenu');

    if (mobileMenuBtn && mobileMenu) {
        mobileMenuBtn.addEventListener('click', function() {
            mobileMenu.classList.toggle('show');
            this.classList.toggle('active');
            document.body.classList.toggle('mobile-menu-open');
        });
    }
}

/**
 * Smooth scrolling for anchor links
 */
function setupSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                window.scrollTo({
                    top: target.offsetTop - 80,
                    behavior: 'smooth'
                });

                // Close mobile menu if open
                const mobileMenu = document.getElementById('mobileMenu');
                if (mobileMenu && mobileMenu.classList.contains('show')) {
                    mobileMenu.classList.remove('show');
                    document.getElementById('mobileMenuBtn').classList.remove('active');
                    document.body.classList.remove('mobile-menu-open');
                }
            }
        });
    });
}

/**
 * Show alert messages
 * @param {string} message - The message to display
 * @param {string} type - Alert type (success, danger, warning, info)
 */
function showAlert(message, type = 'success') {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;

    const alertsContainer = document.getElementById('alertsContainer') || document.body;
    alertsContainer.prepend(alertDiv);

    // Auto-remove after 5 seconds
    setTimeout(() => {
        const alert = bootstrap.Alert.getOrCreateInstance(alertDiv);
        alert.close();
    }, 5000);
}

/**
 * Handle AJAX form submissions
 * @param {HTMLElement} form - The form element
 * @param {string} successMessage - Message to show on success
 */
function handleAjaxForm(form, successMessage) {
    form.addEventListener('submit', function(e) {
        e.preventDefault();

        const formData = new FormData(form);
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.innerHTML;

        // Show loading state
        submitBtn.disabled = true;
        submitBtn.innerHTML = `
            <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
            Processing...
        `;

        // Simulate AJAX request
        setTimeout(() => {
            // In a real app, you would use fetch() here
            console.log('Form data:', Object.fromEntries(formData));

            // Show success message
            showAlert(successMessage, 'success');
            form.reset();

            // Reset button
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
        }, 1500);
    });
}

// Initialize any AJAX forms on the page
document.querySelectorAll('.ajax-form').forEach(form => {
    handleAjaxForm(form, 'Form submitted successfully!');
});

/**
 * Lazy load images
 */
if ('IntersectionObserver' in window) {
    const lazyImageObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (entry.isIntersecting) {
                const lazyImage = entry.target;
                lazyImage.src = lazyImage.dataset.src;
                lazyImage.classList.remove('lazy');
                lazyImageObserver.unobserve(lazyImage);
            }
        });
    });

    document.querySelectorAll('img.lazy').forEach((img) => {
        lazyImageObserver.observe(img);
    });
}