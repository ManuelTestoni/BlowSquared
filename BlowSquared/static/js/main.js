// Main JavaScript file for BlowSquared - Safari Compatible

document.addEventListener('DOMContentLoaded', function() {
  // Debug per Safari
  const isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);
  
  // Controlla se siamo nella home page
  const isHomePage = window.location.pathname === '/' || window.location.pathname === '';
  
  // Smooth scrolling for anchor links
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

  // Navbar scroll effect
  const navbar = document.querySelector('.navbar');
  
  if (navbar) {
    window.addEventListener('scroll', () => {
      if (window.scrollY > 100) {
        navbar.classList.add('navbar-scrolled');
      } else {
        navbar.classList.remove('navbar-scrolled');
      }
    }, { passive: true });
  }
  
  // Effetti hover globali per i bottoni
  const buttons = document.querySelectorAll('button:not(.carousel-nav):not(.search-btn), .btn:not(.btn-hero), .nav-link');
  buttons.forEach(button => {
    button.addEventListener('mouseenter', function() {
      if (!this.style.transform || this.style.transform === 'translateY(0px)') {
        this.style.transform = 'translateY(-2px)';
      }
    });
    
    button.addEventListener('mouseleave', function() {
      if (this.style.transform === 'translateY(-2px)') {
        this.style.transform = 'translateY(0)';
      }
    });
  });
});

