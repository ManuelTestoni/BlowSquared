// Team Section Interactive Features - FINAL CLEAN VERSION

document.addEventListener('DOMContentLoaded', function() {
  
  const teamCards = document.querySelectorAll('.team-card');
  const statItems = document.querySelectorAll('.stat-item');

  // Counter animation for stats
  function animateCounter(element, target, duration = 2000) {
    const start = 0;
    const increment = target / (duration / 16);
    let current = start;

    const timer = setInterval(() => {
      current += increment;
      if (current >= target) {
        current = target;
        clearInterval(timer);
      }
      
      let displayValue = Math.round(current);
      const originalText = element.dataset.originalText || element.textContent;
      
      if (originalText.includes('+')) {
        displayValue += '+';
      } else if (originalText.includes('%')) {
        displayValue += '%';
      }
      
      element.textContent = displayValue;
    }, 16);
  }

  // Trigger counter animations when stats come into view
  const statsObserver = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const numberEl = entry.target.querySelector('.stat-number');
        if (!numberEl) return;
        
        const originalText = numberEl.textContent;
        numberEl.dataset.originalText = originalText;
        
        if (originalText.includes('/')) {
          numberEl.style.transform = 'scale(1.2)';
          numberEl.style.color = 'var(--primary-color)';
          setTimeout(() => {
            numberEl.style.transform = 'scale(1)';
            numberEl.style.color = '';
          }, 300);
        } else {
          const number = parseInt(originalText.replace(/\D/g, ''));
          
          if (!isNaN(number) && !numberEl.dataset.animated) {
            numberEl.dataset.animated = 'true';
            numberEl.textContent = '0';
            animateCounter(numberEl, number);
          }
        }
      }
    });
  }, { threshold: 0.3 });

  statItems.forEach(stat => {
    statsObserver.observe(stat);
  });

  teamCards.forEach(card => {
    card.addEventListener('mouseenter', function() {
      this.style.position = 'relative';
      this.style.zIndex = '10';
    });

    card.addEventListener('mouseleave', function() {
      this.style.position = '';
      this.style.zIndex = '';
    });
  });
});
  

  // Team filter functionality
  function filterTeam(role) {
    teamCards.forEach(card => {
      if (role === 'all' || card.dataset.role === role) {
        card.style.display = 'block';
      } else {
        card.style.display = 'none';
      }
    });
  }

  // Make filter function available globally
  window.filterTeam = filterTeam;

  // Easter egg: Konami code
  let konamiCode = [];
  const konamiSequence = ['ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight', 'KeyB', 'KeyA'];
  
  document.addEventListener('keydown', function(e) {
    konamiCode.push(e.code);
    if (konamiCode.length > konamiSequence.length) {
      konamiCode.shift();
    }
    
    if (konamiCode.join(',') === konamiSequence.join(',')) {
      // Special team animation
      teamCards.forEach((card, index) => {
        setTimeout(() => {
          card.style.animation = 'none';
          card.style.transform = 'rotateY(360deg) scale(1.1)';
          card.style.transition = 'transform 1s ease';
          
          setTimeout(() => {
            card.style.transform = '';
          }, 1000);
        }, index * 200);
      });
      
      konamiCode = [];
    }
  });







