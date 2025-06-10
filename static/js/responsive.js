/**
 * Responsive.js - A lightweight responsive helper library
 *
 * Features:
 * - Viewport size tracking
 * - Breakpoint detection
 * - Responsive event listeners
 * - Mobile/desktop detection
 * - Orientation change handling
 * - Responsive image handling
 */

class Responsive {
  constructor() {
    this.breakpoints = {
      xs: 0,
      sm: 576,
      md: 768,
      lg: 992,
      xl: 1200,
      xxl: 1400
    };

    this.currentBreakpoint = null;
    this.isMobile = null;
    this.isTablet = null;
    this.isDesktop = null;
    this.orientation = null;

    // Initialize
    this.init();
  }

  init() {
    // Set initial values
    this._detectViewport();
    this._detectDeviceType();
    this._detectOrientation();

    // Add event listeners
    window.addEventListener('resize', this._handleResize.bind(this));
    window.addEventListener('orientationchange', this._handleOrientationChange.bind(this));

    // Run responsive images handler
    this._handleResponsiveImages();
  }

  // Private methods
  _detectViewport() {
    const width = window.innerWidth;
    let breakpoint = 'xs';

    for (const [key, value] of Object.entries(this.breakpoints)) {
      if (width >= value) {
        breakpoint = key;
      }
    }

    if (this.currentBreakpoint !== breakpoint) {
      this.currentBreakpoint = breakpoint;
      this._dispatchEvent('breakpointChange', { breakpoint: this.currentBreakpoint });
    }
  }

  _detectDeviceType() {
    const width = window.innerWidth;
    const newIsMobile = width < this.breakpoints.md;
    const newIsTablet = width >= this.breakpoints.md && width < this.breakpoints.lg;
    const newIsDesktop = width >= this.breakpoints.lg;

    if (this.isMobile !== newIsMobile || this.isTablet !== newIsTablet || this.isDesktop !== newIsDesktop) {
      this.isMobile = newIsMobile;
      this.isTablet = newIsTablet;
      this.isDesktop = newIsDesktop;
      this._dispatchEvent('deviceTypeChange', {
        isMobile: this.isMobile,
        isTablet: this.isTablet,
        isDesktop: this.isDesktop
      });
    }
  }

  _detectOrientation() {
    const newOrientation = window.innerWidth > window.innerHeight ? 'landscape' : 'portrait';

    if (this.orientation !== newOrientation) {
      this.orientation = newOrientation;
      this._dispatchEvent('orientationChange', { orientation: this.orientation });
    }
  }

  _handleResize() {
    this._detectViewport();
    this._detectDeviceType();
    this._detectOrientation();
  }

  _handleOrientationChange() {
    // Add slight delay to ensure accurate orientation detection
    setTimeout(() => {
      this._detectOrientation();
    }, 100);
  }

  _handleResponsiveImages() {
    // Handle picture elements and srcset
    const images = document.querySelectorAll('img[data-srcset]');

    images.forEach(img => {
      if (img.dataset.srcset) {
        const sources = img.dataset.srcset.split(',');
        let selectedSrc = img.src;

        sources.forEach(source => {
          const [url, condition] = source.trim().split(' ');
          if (condition) {
            const minWidth = parseInt(condition.replace('min-width:', '').replace('px', ''));
            if (window.innerWidth >= minWidth) {
              selectedSrc = url;
            }
          }
        });

        if (img.src !== selectedSrc) {
          img.src = selectedSrc;
        }
      }
    });
  }

  _dispatchEvent(eventName, detail) {
    const event = new CustomEvent(eventName, { detail });
    window.dispatchEvent(event);
  }

  // Public methods
  getCurrentBreakpoint() {
    return this.currentBreakpoint;
  }

  isBreakpointUp(breakpoint) {
    return window.innerWidth >= this.breakpoints[breakpoint];
  }

  isBreakpointDown(breakpoint) {
    return window.innerWidth < this.breakpoints[breakpoint];
  }

  on(eventName, callback) {
    window.addEventListener(eventName, (e) => callback(e.detail));
  }
}

// Initialize Responsive helper
const responsive = new Responsive();

// Common responsive utilities
const ResponsiveUtils = {
  // Debounce function for resize events
  debounce: function(func, wait = 100) {
    let timeout;
    return function() {
      const context = this, args = arguments;
      clearTimeout(timeout);
      timeout = setTimeout(() => {
        func.apply(context, args);
      }, wait);
    };
  },

  // Throttle function for scroll/resize events
  throttle: function(func, limit = 100) {
    let inThrottle;
    return function() {
      const args = arguments;
      const context = this;
      if (!inThrottle) {
        func.apply(context, args);
        inThrottle = true;
        setTimeout(() => inThrottle = false, limit);
      }
    };
  },

  // Load different content based on viewport
  loadResponsiveContent: function(selector, mobileContent, desktopContent) {
    const element = document.querySelector(selector);
    if (element) {
      element.innerHTML = responsive.isMobile ? mobileContent : desktopContent;

      // Update content when viewport changes
      responsive.on('deviceTypeChange', () => {
        element.innerHTML = responsive.isMobile ? mobileContent : desktopContent;
      });
    }
  },

  // Toggle classes based on breakpoints
  toggleClass: function(element, className, breakpoint, direction = 'down') {
    const toggle = () => {
      if (
        (direction === 'down' && responsive.isBreakpointDown(breakpoint)) ||
        (direction === 'up' && responsive.isBreakpointUp(breakpoint))
      ) {
        element.classList.add(className);
      } else {
        element.classList.remove(className);
      }
    };

    // Initial toggle
    toggle();

    // Toggle on resize
    window.addEventListener('resize', ResponsiveUtils.debounce(toggle));
  }
};

// Make available globally
window.Responsive = responsive;
window.ResponsiveUtils = ResponsiveUtils;

// Optional: Self-initializing components
document.addEventListener('DOMContentLoaded', function() {
  // Example: Responsive menu toggle
  const menuToggle = document.querySelector('[data-responsive-toggle]');
  const menuTarget = document.querySelector(menuToggle?.dataset.responsiveToggle);

  if (menuToggle && menuTarget) {
    ResponsiveUtils.toggleClass(menuTarget, 'hidden', 'lg', 'down');

    menuToggle.addEventListener('click', () => {
      menuTarget.classList.toggle('hidden');
    });
  }

  // Add your own responsive components initialization here
});

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
  module.exports = { responsive, ResponsiveUtils };
}