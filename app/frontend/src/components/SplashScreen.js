import React, { useState, useEffect, useRef } from 'react';

const SplashScreen = ({ onComplete }) => {
  const [progress, setProgress] = useState(0);
  const [currentPhrase, setCurrentPhrase] = useState(0);
  const [fadeOut, setFadeOut] = useState(false);
  const [videoLoaded, setVideoLoaded] = useState(false);
  const videoRef = useRef(null);

  // Reduced phrases for faster loading (3 seconds total)
  const phrases = [
    "Découvrez les meilleurs prestataires...",
    "Beauté • Bien-être • Artisanat",
    "Titelli - Votre marketplace locale"
  ];

  // Optimized: 3 second splash screen
  const SPLASH_DURATION = 3000;
  const PROGRESS_INTERVAL = SPLASH_DURATION / 100;

  useEffect(() => {
    // Progress bar animation (3 seconds)
    const progressInterval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(progressInterval);
          return 100;
        }
        return prev + 1;
      });
    }, PROGRESS_INTERVAL);

    // Phrase rotation (1 second each)
    const phraseInterval = setInterval(() => {
      setCurrentPhrase(prev => (prev + 1) % phrases.length);
    }, 1000);

    // Complete after 3 seconds
    const completeTimeout = setTimeout(() => {
      setFadeOut(true);
      setTimeout(() => {
        onComplete();
      }, 500); // Reduced fade time
    }, SPLASH_DURATION);

    return () => {
      clearInterval(progressInterval);
      clearInterval(phraseInterval);
      clearTimeout(completeTimeout);
    };
  }, [onComplete, phrases.length]);

  return (
    <div 
      className={`splash-screen ${fadeOut ? 'fade-out' : ''}`}
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        backgroundColor: '#000',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        zIndex: 9999,
        transition: 'opacity 0.8s ease-out, transform 0.8s ease-out',
        opacity: fadeOut ? 0 : 1,
        transform: fadeOut ? 'translateX(100%)' : 'translateX(0)',
        willChange: 'opacity, transform',
      }}
    >
      {/* Background particles - reduced from 20 to 8 for performance */}
      <div className="particles">
        {[...Array(8)].map((_, i) => (
          <div 
            key={i} 
            className="particle"
            style={{
              position: 'absolute',
              width: '4px',
              height: '4px',
              background: 'rgba(212, 175, 55, 0.3)',
              borderRadius: '50%',
              left: `${12.5 * i}%`,
              top: `${10 + (i % 3) * 30}%`,
              animation: `float 3s ease-in-out infinite`,
              animationDelay: `${i * 0.2}s`,
            }}
          />
        ))}
      </div>

      {/* Logo container with glow effect */}
      <div 
        className="logo-container"
        style={{
          position: 'relative',
          marginBottom: '60px',
          animation: fadeOut ? 'none' : 'pulse-glow 2s ease-in-out infinite',
          transition: 'transform 0.6s ease-out, opacity 0.6s ease-out',
          transform: fadeOut ? 'translateX(150px)' : 'translateX(0)',
          opacity: fadeOut ? 0 : 1,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        {/* Glow effect behind logo */}
        <div 
          style={{
            position: 'absolute',
            top: '75px',
            left: '50%',
            transform: 'translateX(-50%)',
            width: '200px',
            height: '200px',
            background: 'radial-gradient(circle, rgba(0,71,171,0.4) 0%, transparent 70%)',
            borderRadius: '50%',
            filter: 'blur(30px)',
            animation: 'breathe 3s ease-in-out infinite',
          }}
        />
        
        {/* Video logo - optimized with lazy loading and fallback */}
        <div 
          style={{
            width: '150px',
            height: '150px',
            borderRadius: '50%',
            overflow: 'hidden',
            border: '3px solid rgba(212, 175, 55, 0.5)',
            boxShadow: '0 0 40px rgba(0, 71, 171, 0.5), 0 0 80px rgba(212, 175, 55, 0.2)',
            position: 'relative',
            zIndex: 1,
            background: 'linear-gradient(135deg, #0047AB 0%, #D4AF37 100%)',
            flexShrink: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          {/* Fallback logo while video loads */}
          {!videoLoaded && (
            <span style={{
              fontSize: '48px',
              fontWeight: 'bold',
              color: '#fff',
              fontFamily: 'Playfair Display, serif',
            }}>T</span>
          )}
          <video 
            ref={videoRef}
            autoPlay 
            loop 
            muted 
            playsInline
            preload="metadata"
            onLoadedData={() => setVideoLoaded(true)}
            style={{
              width: '100%',
              height: '100%',
              objectFit: 'cover',
              transform: 'scale(1.5)',
              position: 'absolute',
              top: 0,
              left: 0,
              opacity: videoLoaded ? 1 : 0,
              transition: 'opacity 0.3s ease',
            }}
            src={`${process.env.REACT_APP_BACKEND_URL}/api/uploads/video_logo_titelli_final.mp4`}
          />
        </div>

        {/* Brand name - perfectly centered */}
        <h1 
          style={{
            fontFamily: 'Playfair Display, serif',
            fontSize: '42px',
            color: '#fff',
            marginTop: '24px',
            marginBottom: 0,
            textAlign: 'center',
            letterSpacing: '8px',
            textTransform: 'uppercase',
            animation: 'shimmer 2s ease-in-out infinite',
            width: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          Titelli
        </h1>
      </div>

      {/* Phrase animation */}
      <div 
        style={{
          height: '30px',
          marginBottom: '40px',
          overflow: 'hidden',
        }}
      >
        <p 
          key={currentPhrase}
          style={{
            fontFamily: 'Inter, sans-serif',
            fontSize: '16px',
            color: 'rgba(255, 255, 255, 0.7)',
            textAlign: 'center',
            animation: 'slideUp 1.25s ease-out',
            letterSpacing: '1px',
          }}
        >
          {phrases[currentPhrase]}
        </p>
      </div>

      {/* Loading bar container */}
      <div 
        style={{
          width: '300px',
          maxWidth: '80%',
        }}
      >
        {/* Progress bar background */}
        <div 
          style={{
            height: '4px',
            backgroundColor: 'rgba(255, 255, 255, 0.1)',
            borderRadius: '4px',
            overflow: 'hidden',
            position: 'relative',
          }}
        >
          {/* Progress fill */}
          <div 
            style={{
              height: '100%',
              width: `${progress}%`,
              background: 'linear-gradient(90deg, #0047AB 0%, #D4AF37 50%, #0047AB 100%)',
              backgroundSize: '200% 100%',
              animation: 'gradient-shift 2s linear infinite',
              borderRadius: '4px',
              transition: 'width 0.1s linear',
              boxShadow: '0 0 10px rgba(212, 175, 55, 0.5)',
            }}
          />
        </div>

        {/* Percentage */}
        <p 
          style={{
            fontFamily: 'Inter, sans-serif',
            fontSize: '12px',
            color: 'rgba(255, 255, 255, 0.5)',
            textAlign: 'center',
            marginTop: '12px',
            letterSpacing: '2px',
          }}
        >
          {progress}%
        </p>
      </div>

      {/* CSS Animations */}
      <style>{`
        @keyframes float {
          0%, 100% { transform: translateY(0) rotate(0deg); opacity: 0.3; }
          50% { transform: translateY(-20px) rotate(180deg); opacity: 0.6; }
        }

        @keyframes pulse-glow {
          0%, 100% { transform: scale(1); }
          50% { transform: scale(1.02); }
        }

        @keyframes breathe {
          0%, 100% { opacity: 0.5; transform: translate(-50%, -50%) scale(1); }
          50% { opacity: 0.8; transform: translate(-50%, -50%) scale(1.1); }
        }

        @keyframes shimmer {
          0%, 100% { 
            text-shadow: 0 0 20px rgba(212, 175, 55, 0.3);
          }
          50% { 
            text-shadow: 0 0 40px rgba(212, 175, 55, 0.6), 0 0 60px rgba(0, 71, 171, 0.4);
          }
        }

        @keyframes slideUp {
          0% { 
            opacity: 0; 
            transform: translateY(20px); 
          }
          20% { 
            opacity: 1; 
            transform: translateY(0); 
          }
          80% { 
            opacity: 1; 
            transform: translateY(0); 
          }
          100% { 
            opacity: 0; 
            transform: translateY(-20px); 
          }
        }

        @keyframes gradient-shift {
          0% { background-position: 0% 50%; }
          100% { background-position: 200% 50%; }
        }

        .splash-screen.fade-out {
          pointer-events: none;
        }
      `}</style>
    </div>
  );
};

export default SplashScreen;
