document.addEventListener('DOMContentLoaded', function() {
  console.log('🎭 LOADER TEATRALE ULTRA-AGGRESSIVO AVVIATO');
  
  const loader = document.getElementById('page-loader');
  const audio = document.getElementById('loading-audio');
  const progressFill = document.querySelector('.progress-fill');
  const progressText = document.querySelector('.progress-text');
  
  let audioStarted = false;
  let progress = 0;
  let audioContext = null;
  let audioBuffer = null;
  let audioSource = null;
  
  // === CONFIGURAZIONE AUDIO ULTRA-AGGRESSIVA ===
  function initUltraAggressiveAudio() {
    console.log('🔊 Inizializzazione audio ultra-aggressiva...');
    
    if (audio) {
      // Configurazione base
      audio.muted = false;
      audio.volume = 0.8;
      audio.autoplay = true;
      audio.loop = false;
      audio.preload = 'auto';
      
      // Event listeners
      audio.addEventListener('play', () => {
        console.log('✅ AUDIO PARTITO FINALMENTE!');
        audioStarted = true;
      });
      
      audio.addEventListener('error', (e) => {
        console.log('❌ Errore audio HTML5:', e);
        tryWebAudioAPI();
      });
      
      audio.addEventListener('canplaythrough', () => {
        console.log('📡 Audio pronto, forzo riproduzione...');
        forcePlayAllMethods();
      });
    }
    
    // Inizializza Web Audio Context
    initWebAudioContext();
    
    // Avvia tutti i metodi aggressivi
    setTimeout(() => forcePlayAllMethods(), 100);
    setTimeout(() => forcePlayAllMethods(), 500);
    setTimeout(() => forcePlayAllMethods(), 1000);
    
    // Avvia hack Safari specifici
    setTimeout(() => safariAudioHack(), 200);
    setTimeout(() => triggerInvisibleInteraction(), 800);
  }
  
  // === WEB AUDIO CONTEXT ===
  function initWebAudioContext() {
    try {
      window.AudioContext = window.AudioContext || window.webkitAudioContext;
      audioContext = new AudioContext();
      
      console.log('🎵 AudioContext creato:', audioContext.state);
      
      // Forza l'unlock dell'AudioContext
      if (audioContext.state === 'suspended') {
        audioContext.resume().then(() => {
          console.log('🔓 AudioContext sbloccato');
          loadAudioBuffer();
        });
      } else {
        loadAudioBuffer();
      }
    } catch (e) {
      console.warn('❌ AudioContext fallito:', e);
    }
  }
  
  function loadAudioBuffer() {
    if (!audioContext) return;
    
    fetch('/static/audio/loading.mp3')
      .then(response => response.arrayBuffer())
      .then(data => audioContext.decodeAudioData(data))
      .then(buffer => {
        audioBuffer = buffer;
        console.log('📦 Audio buffer caricato');
        playWebAudio();
      })
      .catch(e => console.log('❌ Caricamento buffer fallito:', e));
  }
  
  function playWebAudio() {
    if (!audioContext || !audioBuffer || audioStarted) return;
    
    try {
      audioSource = audioContext.createBufferSource();
      audioSource.buffer = audioBuffer;
      
      const gainNode = audioContext.createGain();
      gainNode.gain.value = 0.8;
      
      audioSource.connect(gainNode);
      gainNode.connect(audioContext.destination);
      
      audioSource.start(0);
      audioStarted = true;
      console.log('✅ AUDIO PARTITO VIA WEB AUDIO API!');
      
      // Simula eventi per sincronizzazione
      setTimeout(() => {
        console.log('🎵 Audio Web terminato');
        if (audioSource) {
          audioSource.stop();
        }
        startTheaterSequence();
      }, audioBuffer.duration * 1000);
      
    } catch (e) {
      console.log('❌ Web Audio playback fallito:', e);
    }
  }
  
  // === METODI AGGRESSIVI DI RIPRODUZIONE ===
  function forcePlayAllMethods() {
    if (audioStarted) return;
    
    console.log('🚀 Tentativo tutti i metodi aggressivi...');
    
    // Metodo 1: Play diretto
    method1DirectPlay();
    
    // Metodo 2: Ricrea elemento audio
    setTimeout(() => method2RecreateAudio(), 100);
    
    // Metodo 3: Nuovo oggetto Audio
    setTimeout(() => method3NewAudioObject(), 200);
    
    // Metodo 4: Simula interazione utente
    setTimeout(() => method4SimulateInteraction(), 300);
    
    // Metodo 5: Forza via JavaScript
    setTimeout(() => method5ForceJavaScript(), 400);
    
    // Metodo 6: Iframe trick
    setTimeout(() => method6IframeTrick(), 500);
    
    // Metodo 7: Blob URL
    setTimeout(() => method7BlobURL(), 600);
  }
  
  function method1DirectPlay() {
    if (!audio || audioStarted) return;
    console.log('🎯 Metodo 1: Play diretto');
    
    audio.currentTime = 0;
    audio.play().then(() => {
      console.log('✅ Metodo 1 SUCCESSO!');
      audioStarted = true;
    }).catch(e => console.log('❌ Metodo 1 fallito:', e.message));
  }
  
  function method2RecreateAudio() {
    if (audioStarted) return;
    console.log('🔄 Metodo 2: Ricrea elemento audio');
    
    const newAudio = document.createElement('audio');
    newAudio.src = '/static/audio/loading.mp3';
    newAudio.volume = 0.8;
    newAudio.autoplay = true;
    newAudio.muted = false;
    
    newAudio.play().then(() => {
      console.log('✅ Metodo 2 SUCCESSO!');
      audioStarted = true;
      // Sostituisci l'audio originale
      audio.parentNode.replaceChild(newAudio, audio);
    }).catch(e => console.log('❌ Metodo 2 fallito:', e.message));
  }
  
  function method3NewAudioObject() {
    if (audioStarted) return;
    console.log('🆕 Metodo 3: Nuovo oggetto Audio');
    
    try {
      const newAudio = new Audio('/static/audio/loading.mp3');
      newAudio.volume = 0.8;
      newAudio.play().then(() => {
        console.log('✅ Metodo 3 SUCCESSO!');
        audioStarted = true;
      }).catch(e => console.log('❌ Metodo 3 fallito:', e.message));
    } catch (e) {
      console.log('❌ Metodo 3 eccezione:', e);
    }
  }
  
  function method4SimulateInteraction() {
    if (audioStarted) return;
    console.log('👆 Metodo 4: Simula interazione');
    
    // Simula click, touch, keypress
    const events = ['click', 'touchstart', 'keydown', 'mousedown'];
    events.forEach(eventType => {
      const event = new Event(eventType, { bubbles: true });
      document.dispatchEvent(event);
    });
    
    setTimeout(() => {
      if (audio && !audioStarted) {
        audio.play().then(() => {
          console.log('✅ Metodo 4 SUCCESSO!');
          audioStarted = true;
        }).catch(e => console.log('❌ Metodo 4 fallito:', e.message));
      }
    }, 50);
  }
  
  function method5ForceJavaScript() {
    if (audioStarted) return;
    console.log('⚡ Metodo 5: Forza JavaScript');
    
    // Override delle proprietà audio
    if (audio) {
      Object.defineProperty(audio, 'paused', { value: false });
      Object.defineProperty(audio, 'muted', { value: false });
      
      // Forza l'evento play
      const playEvent = new Event('play');
      audio.dispatchEvent(playEvent);
      
      // Prova play forzato
      try {
        audio.play();
        audioStarted = true;
        console.log('✅ Metodo 5 SUCCESSO!');
      } catch (e) {
        console.log('❌ Metodo 5 fallito:', e);
      }
    }
  }
  
  function method6IframeTrick() {
    if (audioStarted) return;
    console.log('🖼️ Metodo 6: Iframe trick');
    
    const iframe = document.createElement('iframe');
    iframe.style.display = 'none';
    iframe.src = 'data:text/html,<audio autoplay><source src="/static/audio/loading.mp3"></audio>';
    document.body.appendChild(iframe);
    
    setTimeout(() => {
      const iframeAudio = iframe.contentDocument?.querySelector('audio');
      if (iframeAudio) {
        iframeAudio.play().then(() => {
          console.log('✅ Metodo 6 SUCCESSO!');
          audioStarted = true;
        }).catch(e => console.log('❌ Metodo 6 fallito:', e.message));
      }
    }, 100);
  }
  
  function method7BlobURL() {
    if (audioStarted) return;
    console.log('🗃️ Metodo 7: Blob URL');
    
    fetch('/static/audio/loading.mp3')
      .then(response => response.blob())
      .then(blob => {
        const blobURL = URL.createObjectURL(blob);
        const blobAudio = new Audio(blobURL);
        blobAudio.volume = 0.8;
        
        return blobAudio.play();
      })
      .then(() => {
        console.log('✅ Metodo 7 SUCCESSO!');
        audioStarted = true;
      })
      .catch(e => console.log('❌ Metodo 7 fallito:', e.message));
  }
  
  function tryWebAudioAPI() {
    if (audioStarted || !audioContext) return;
    console.log('🌐 Tentativo Web Audio API...');
    playWebAudio();
  }
  
  // === RILEVAZIONE INTERAZIONE UTENTE ===
  function setupUserInteractionDetection() {
    const interactionEvents = ['click', 'touchstart', 'keydown', 'mousedown', 'mousemove'];
    
    const onInteraction = () => {
      if (!audioStarted) {
        console.log('👤 Interazione utente rilevata, forzo audio...');
        forcePlayAllMethods();
      }
      
      // Rimuovi listener dopo prima interazione
      interactionEvents.forEach(event => {
        document.removeEventListener(event, onInteraction);
      });
    };
    
    interactionEvents.forEach(event => {
      document.addEventListener(event, onInteraction, { once: true });
    });
  }
  
  // === PROGRESS BAR ===
  function updateProgress() {
    progress += Math.random() * 15 + 5;
    progress = Math.min(progress, 100);
    
    if (progressFill) progressFill.style.width = progress + '%';
    if (progressText) progressText.textContent = Math.round(progress) + '%';
    
    if (progress < 100) {
      setTimeout(updateProgress, 150);
    }
  }
  
  // === SEQUENZA TEATRALE ===
  function startTheaterSequence() {
    console.log('🎭 Inizio sequenza teatrale...');
    
    progress = 100;
    if (progressFill) progressFill.style.width = '100%';
    if (progressText) progressText.textContent = '100%';
    
    // Spotlight
    const spotlight = document.createElement('div');
    spotlight.className = 'spotlight';
    const stage = document.querySelector('.stage');
    if (stage) stage.appendChild(spotlight);
    
    setTimeout(() => {
      console.log('🎭 Apertura tende...');
      if (loader) {
        loader.classList.add('opening');
        
        setTimeout(() => {
          loader.classList.add('hidden');
          setTimeout(() => {
            if (loader && loader.parentNode) {
              loader.parentNode.removeChild(loader);
              console.log('🎭 Loader rimosso!');
            }
          }, 1000);
        }, 2500);
      }
    }, 500);
  }
  
  // === AVVIO ===
  initUltraAggressiveAudio();
  setupUserInteractionDetection();
  updateProgress();
  
  // Timer di sicurezza - 4 secondi max
  setTimeout(() => {
    if (!audioStarted) {
      console.log('⏰ Timer sicurezza - avvio senza audio');
    }
    startTheaterSequence();
  }, 4000);
  
  // Se audio parte, aspetta che finisca (max 10s)
  const checkAudioEnd = () => {
    if (audioStarted && audio && !audio.ended) {
      setTimeout(checkAudioEnd, 200);
    } else if (audioStarted) {
      console.log('🎵 Audio finito, avvio sequenza');
      setTimeout(startTheaterSequence, 300);
    }
  };
  
  setTimeout(checkAudioEnd, 1000);
});

// AGGIUNTA: Metodo estremo per Safari
document.addEventListener('DOMContentLoaded', function() {
  console.log('🎭 LOADER con hack Safari...');
  
  // NUOVO: Hack specifico per Safari
  function safariAudioHack() {
    console.log('🍎 Tentativo hack Safari...');
    
    // Crea un oscillatore silenzioso per sbloccare AudioContext
    if (audioContext) {
      try {
        const oscillator = audioContext.createOscillator();
        const gainNode = audioContext.createGain();
        
        oscillator.connect(gainNode);
        gainNode.connect(audioContext.destination);
        
        gainNode.gain.value = 0; // Volume zero
        oscillator.frequency.value = 20; // Frequenza bassissima
        oscillator.start();
        oscillator.stop(audioContext.currentTime + 0.01);
        
        console.log('✅ Safari AudioContext sbloccato');
        
        // Prova l'audio dopo
        setTimeout(() => forcePlayAllMethods(), 100);
      } catch (e) {
        console.log('❌ Safari hack fallito:', e);
      }
    }
  }
  
  // NUOVO: Auto-click invisibile per Safari
  function triggerInvisibleInteraction() {
    console.log('👻 Trigger interazione invisibile...');
    
    // Crea un elemento invisibile cliccabile
    const hiddenButton = document.createElement('button');
    hiddenButton.style.position = 'fixed';
    hiddenButton.style.top = '-1000px';
    hiddenButton.style.left = '-1000px';
    hiddenButton.style.width = '1px';
    hiddenButton.style.height = '1px';
    hiddenButton.style.opacity = '0';
    hiddenButton.style.pointerEvents = 'none';
    
    document.body.appendChild(hiddenButton);
    
    // Auto-click dopo 500ms
    setTimeout(() => {
      hiddenButton.click();
      hiddenButton.focus();
      
      // Prova audio dopo il click
      setTimeout(() => {
        forcePlayAllMethods();
        safariAudioHack();
      }, 100);
      
      // Rimuovi l'elemento
      setTimeout(() => {
        document.body.removeChild(hiddenButton);
      }, 1000);
    }, 500);
  }
});

