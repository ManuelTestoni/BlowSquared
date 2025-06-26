class Carousel {
  constructor(selector) {
    this.carousel = document.querySelector(selector);
    if (!this.carousel) return;
    
    this.items = this.carousel.querySelectorAll('.carousel-item');
    this.dots = document.querySelectorAll('.carousel-dot');
    this.prevBtn = document.querySelector('.carousel-prev');
    this.nextBtn = document.querySelector('.carousel-next');
    this.currentIndex = 0;
    this.intervalId = null;
    
    this.init();
  }
  
  init() {
    this.showItem(0);
    this.setupEventListeners();
    this.startAutoplay();
  }
  
  setupEventListeners() {
    // Navigation buttons
    if (this.prevBtn) {
      this.prevBtn.addEventListener('click', () => this.prevItem());
    }
    
    if (this.nextBtn) {
      this.nextBtn.addEventListener('click', () => this.nextItem());
    }
    
    // Dots navigation
    this.dots.forEach((dot, index) => {
      dot.addEventListener('click', () => this.showItem(index));
    });
    
    // Keyboard navigation
    document.addEventListener('keydown', (e) => {
      if (e.key === 'ArrowLeft') this.prevItem();
      if (e.key === 'ArrowRight') this.nextItem();
    });
    
    // Touch/swipe support
    let startX = null;
    this.carousel.addEventListener('touchstart', (e) => {
      startX = e.touches[0].clientX;
    });
    
    this.carousel.addEventListener('touchend', (e) => {
      if (!startX) return;
      
      const endX = e.changedTouches[0].clientX;
      const diff = startX - endX;
      
      if (Math.abs(diff) > 50) {
        if (diff > 0) {
          this.nextItem();
        } else {
          this.prevItem();
        }
      }
      
      startX = null;
    });
  }
  
  showItem(index) {
    // Update carousel items
    this.items.forEach((item, i) => {
      item.classList.toggle('active', i === index);
    });
    
    // Update dots
    this.dots.forEach((dot, i) => {
      dot.classList.toggle('active', i === index);
    });
    
    this.currentIndex = index;
  }
  
  nextItem() {
    const nextIndex = (this.currentIndex + 1) % this.items.length;
    this.showItem(nextIndex);
  }
  
  prevItem() {
    const prevIndex = (this.currentIndex - 1 + this.items.length) % this.items.length;
    this.showItem(prevIndex);
  }
  
  startAutoplay() {
    this.intervalId = setInterval(() => {
      this.nextItem();
    }, 5000); // Aumentato a 5 secondi per dare più tempo di lettura
  }
  
  stopAutoplay() {
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
  }
  
  restartAutoplay() {
    this.stopAutoplay();
    this.startAutoplay();
  }
}

// Initialize carousel when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
  const carousel = new Carousel('.carousel');
  
  // Pause autoplay on hover/interaction and restart when leaving
  const heroSection = document.querySelector('.hero-section');
  if (heroSection && carousel) {
    heroSection.addEventListener('mouseenter', () => carousel.stopAutoplay());
    heroSection.addEventListener('mouseleave', () => carousel.startAutoplay());
    
    // Restart autoplay after manual interaction
    const navButtons = document.querySelectorAll('.carousel-nav, .carousel-dot');
    navButtons.forEach(button => {
      button.addEventListener('click', () => {
        carousel.restartAutoplay();
      });
    });
  }
});
