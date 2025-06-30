// Main JavaScript file for BlowSquared - Safari Compatible

document.addEventListener('DOMContentLoaded', function() {
  // Debug per Safari
  const isSafari = /^((?!chrome|android).)*safari/i.test(navigator.userAgent);
  if (isSafari) {
    console.log('Safari rilevato - usando ottimizzazioni specifiche');
  }
  
  // Controlla se siamo nella home page
  const isHomePage = window.location.pathname === '/' || window.location.pathname === '';
  
  // LOGICA COMPATIBILE CON SAFARI
  if (isHomePage) {
    const loadingAudio = document.getElementById('loading-audio');
    const pageLoader = document.getElementById('page-loader');
    
    // Gestione loader con timeout di sicurezza per Safari
    if (pageLoader) {
      let progress = 0;
      const progressFill = document.querySelector('.progress-fill');
      const progressText = document.querySelector('.progress-text');
      
      // Timeout di sicurezza - forza la chiusura dopo 5 secondi max
      const safetyTimeout = setTimeout(() => {
        console.log('Safety timeout attivato per Safari');
        pageLoader.style.opacity = '0';
        setTimeout(() => {
          pageLoader.style.display = 'none';
        }, 500);
      }, 5000);
      
      const interval = setInterval(() => {
        progress += Math.random() * 15 + 5; // Progresso più veloce per Safari
        if (progress >= 100) {
          progress = 100;
          clearInterval(interval);
          clearTimeout(safetyTimeout);
          
          // Nascondi il loader
          setTimeout(() => {
            pageLoader.style.opacity = '0';
            setTimeout(() => {
              pageLoader.style.display = 'none';
            }, 500);
          }, 300);
        }
        
        if (progressFill) progressFill.style.width = progress + '%';
        if (progressText) progressText.textContent = Math.round(progress) + '%';
      }, 100); // Intervallo più rapido per Safari
    }
    
    // Audio con gestione Safari-friendly
    if (loadingAudio) {
      // Safari: richiede interazione utente per audio
      const playAudio = () => {
        loadingAudio.play().catch(e => {
          console.log('Audio non riproducibile automaticamente in Safari');
        });
      };
      
      // Prova a riprodurre dopo il caricamento della pagina
      setTimeout(playAudio, 800);
      
      // Fallback: riproduci audio al primo click/touch dell'utente
      const enableAudioOnInteraction = () => {
        playAudio();
        document.removeEventListener('click', enableAudioOnInteraction);
        document.removeEventListener('touchstart', enableAudioOnInteraction);
      };
      
      document.addEventListener('click', enableAudioOnInteraction, { once: true });
      document.addEventListener('touchstart', enableAudioOnInteraction, { once: true });
    }
  }
  
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

