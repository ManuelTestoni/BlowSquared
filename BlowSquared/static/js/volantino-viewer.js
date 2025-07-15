// Volantino Viewer JavaScript

class VolantinoViewer {
    constructor() {
        this.currentPage = 0;
        this.totalPages = parseInt(document.getElementById('totalPages').textContent);
        this.isZoomed = false;
        this.flipbookPages = document.getElementById('flipbookPages');
        this.viewport = document.querySelector('.flipbook-viewport');
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.updatePageDisplay();
        this.setupKeyboardNavigation();
        this.setupTouchGestures();
    }
    
    setupEventListeners() {
        // Navigation buttons
        document.getElementById('prevPage').addEventListener('click', () => this.previousPage());
        document.getElementById('nextPage').addEventListener('click', () => this.nextPage());
        
        // Zoom controls
        document.getElementById('zoomIn').addEventListener('click', () => this.zoomIn());
        document.getElementById('zoomOut').addEventListener('click', () => this.zoomOut());
        
        // Fullscreen
        document.getElementById('fullscreen').addEventListener('click', () => this.toggleFullscreen());
        
        // Thumbnails
        document.querySelectorAll('.thumbnail').forEach(thumb => {
            thumb.addEventListener('click', () => {
                const pageNum = parseInt(thumb.dataset.page);
                this.goToPage(pageNum);
            });
        });
        
        // Page image click for zoom
        document.querySelectorAll('.page-image').forEach(img => {
            img.addEventListener('click', () => this.toggleZoom());
        });
    }
    
    setupKeyboardNavigation() {
        document.addEventListener('keydown', (e) => {
            switch(e.key) {
                case 'ArrowLeft':
                    e.preventDefault();
                    this.previousPage();
                    break;
                case 'ArrowRight':
                    e.preventDefault();
                    this.nextPage();
                    break;
                case 'Escape':
                    if (this.isZoomed) {
                        this.zoomOut();
                    }
                    break;
                case 'f':
                case 'F':
                    if (e.ctrlKey || e.metaKey) {
                        e.preventDefault();
                        this.toggleFullscreen();
                    }
                    break;
            }
        });
    }
    
    setupTouchGestures() {
        let startX = 0;
        let startY = 0;
        
        this.viewport.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
        });
        
        this.viewport.addEventListener('touchend', (e) => {
            const endX = e.changedTouches[0].clientX;
            const endY = e.changedTouches[0].clientY;
            const diffX = startX - endX;
            const diffY = startY - endY;
            
            // Solo se il movimento orizzontale è maggiore di quello verticale
            if (Math.abs(diffX) > Math.abs(diffY) && Math.abs(diffX) > 50) {
                if (diffX > 0) {
                    this.nextPage();
                } else {
                    this.previousPage();
                }
            }
        });
    }
    
    goToPage(pageNumber) {
        if (pageNumber < 1 || pageNumber > this.totalPages) return;
        
        console.log(`Navigando alla pagina ${pageNumber}`);
        
        this.currentPage = pageNumber;
        this.updatePageDisplay();
        this.updateThumbnails();
        this.updateNavButtons();
        
        // Smooth scroll animation
        const translateX = -((pageNumber - 1) * 100);
        this.flipbookPages.style.transform = `translateX(${translateX}%)`;
        
        console.log(`Transform applicato: translateX(${translateX}%)`);
        
        // Add page flip animation class
        this.flipbookPages.classList.add('flipping');
        setTimeout(() => {
            this.flipbookPages.classList.remove('flipping');
        }, 500);
    }
    
    nextPage() {
        if (this.currentPage < this.totalPages) {
            this.goToPage(this.currentPage + 1);
        }
    }
    
    previousPage() {
        if (this.currentPage > 1) {
            this.goToPage(this.currentPage - 1);
        }
    }
    
    updatePageDisplay() {
        document.getElementById('currentPage').textContent = this.currentPage;
    }
    
    updateThumbnails() {
        document.querySelectorAll('.thumbnail').forEach(thumb => {
            thumb.classList.remove('active');
        });
        
        const activeThumbnail = document.querySelector(`[data-page="${this.currentPage}"]`);
        if (activeThumbnail) {
            activeThumbnail.classList.add('active');
            
            // Scroll thumbnails into view
            activeThumbnail.scrollIntoView({
                behavior: 'smooth',
                block: 'nearest',
                inline: 'center'
            });
        }
    }
    
    updateNavButtons() {
        const prevBtn = document.getElementById('prevPage');
        const nextBtn = document.getElementById('nextPage');
        
        prevBtn.disabled = this.currentPage === 1;
        nextBtn.disabled = this.currentPage === this.totalPages;
    }
    
    zoomIn() {
        this.isZoomed = true;
        this.viewport.classList.add('zoomed');
        document.getElementById('zoomIn').style.display = 'none';
        document.getElementById('zoomOut').style.display = 'inline-flex';
        
        // Enable pan functionality
        this.enablePanning();
    }
    
    zoomOut() {
        this.isZoomed = false;
        this.viewport.classList.remove('zoomed');
        document.getElementById('zoomIn').style.display = 'inline-flex';
        document.getElementById('zoomOut').style.display = 'none';
        
        // Reset image position
        const currentImage = document.querySelector('.flipbook-page.active .page-image');
        if (currentImage) {
            currentImage.style.transform = 'scale(1) translate(0, 0)';
        }
    }
    
    toggleZoom() {
        if (this.isZoomed) {
            this.zoomOut();
        } else {
            this.zoomIn();
        }
    }
    
    enablePanning() {
        const images = document.querySelectorAll('.page-image');
        
        images.forEach(img => {
            let isDragging = false;
            let startX = 0;
            let startY = 0;
            let translateX = 0;
            let translateY = 0;
            
            img.addEventListener('mousedown', (e) => {
                if (this.isZoomed) {
                    isDragging = true;
                    startX = e.clientX - translateX;
                    startY = e.clientY - translateY;
                    img.style.cursor = 'grabbing';
                }
            });
            
            img.addEventListener('mousemove', (e) => {
                if (isDragging && this.isZoomed) {
                    translateX = e.clientX - startX;
                    translateY = e.clientY - startY;
                    img.style.transform = `scale(1.5) translate(${translateX}px, ${translateY}px)`;
                }
            });
            
            img.addEventListener('mouseup', () => {
                isDragging = false;
                img.style.cursor = 'grab';
            });
            
            img.addEventListener('mouseleave', () => {
                isDragging = false;
                img.style.cursor = 'grab';
            });
        });
    }
    
    toggleFullscreen() {
        const container = document.querySelector('.flipbook-container');
        
        if (!document.fullscreenElement) {
            container.requestFullscreen().catch(err => {
                console.log(`Error attempting to enable fullscreen: ${err.message}`);
            });
        } else {
            document.exitFullscreen();
        }
    }
}

// Initialize viewer when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    const viewer = new VolantinoViewer();
    
    // Hide zoom out button initially
    document.getElementById('zoomOut').style.display = 'none';
    
    // Auto-advance demo (optional)
    if (window.location.search.includes('demo=true')) {
        setInterval(() => {
            if (viewer.currentPage < viewer.totalPages) {
                viewer.nextPage();
            } else {
                viewer.goToPage(1);
            }
        }, 3000);
    }
});

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    .flipbook-pages.flipping {
        transition: transform 0.6s cubic-bezier(0.25, 0.46, 0.45, 0.94);
    }
    
    @keyframes pageFlip {
        0% { transform: rotateY(0deg); }
        50% { transform: rotateY(-90deg); }
        100% { transform: rotateY(0deg); }
    }
    
    .page-flipping {
        animation: pageFlip 0.6s ease-in-out;
    }
    
    .flipbook-viewport:fullscreen {
        background: #000;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .flipbook-viewport:fullscreen .flipbook-pages {
        height: 100vh;
    }
`;
document.head.appendChild(style);
