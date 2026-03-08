import React, { useState, useEffect } from 'react';
import { X, Users, Building2, Check, Star, ShoppingBag, Briefcase, Search, Award, Shield } from 'lucide-react';

const WelcomePopup = () => {
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    // Vérifier si c'est la première visite
    const hasVisited = localStorage.getItem('titelli_visited');
    
    if (!hasVisited) {
      // Attendre un peu avant d'afficher la popup
      const timer = setTimeout(() => {
        setIsVisible(true);
      }, 2000);
      
      return () => clearTimeout(timer);
    }
  }, []);

  const handleClose = () => {
    setIsVisible(false);
    // Marquer comme visité
    localStorage.setItem('titelli_visited', 'true');
    localStorage.setItem('titelli_first_visit_date', new Date().toISOString());
  };

  const handleExplore = () => {
    handleClose();
    window.location.href = '/auth';
  };

  if (!isVisible) return null;

  // Avantages pour les clients
  const clientAdvantages = [
    { icon: Search, text: "Trouvez facilement les meilleurs prestataires" },
    { icon: Star, text: "Accédez aux avis vérifiés" },
    { icon: ShoppingBag, text: "Réservez et commandez en ligne" },
    { icon: Shield, text: "Paiement sécurisé garanti" },
  ];

  // Avantages pour les entreprises
  const enterpriseAdvantages = [
    { icon: Users, text: "Développez votre clientèle locale" },
    { icon: Award, text: "Obtenez la certification Titelli" },
    { icon: Briefcase, text: "Publiez vos offres d'emploi" },
    { icon: Star, text: "Boostez votre visibilité premium" },
  ];

  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center p-3 sm:p-4">
      {/* Overlay sombre */}
      <div 
        className="absolute inset-0 bg-black/80 backdrop-blur-sm"
        onClick={handleClose}
      />
      
      {/* Popup - Landscape sur desktop, Portrait sur mobile */}
      <div className="relative w-full max-w-[340px] sm:max-w-3xl lg:max-w-4xl bg-white rounded-2xl shadow-2xl overflow-hidden animate-in fade-in zoom-in duration-300">
        
        {/* Bouton fermer */}
        <button 
          onClick={handleClose}
          className="absolute top-3 right-3 z-10 w-8 h-8 bg-gray-100 hover:bg-gray-200 rounded-full flex items-center justify-center text-gray-500 hover:text-gray-700 transition-all"
          data-testid="welcome-popup-close"
        >
          <X className="w-4 h-4" />
        </button>

        {/* Layout: Colonne sur mobile, Ligne sur desktop */}
        <div className="flex flex-col sm:flex-row">
          
          {/* Section gauche - Titre et branding */}
          <div className="bg-gradient-to-br from-[#0047AB] to-[#002266] p-5 sm:p-8 sm:w-2/5 flex flex-col justify-center items-center text-center">
            <h1 className="text-2xl sm:text-4xl font-bold text-white mb-2" style={{ fontFamily: 'Playfair Display, serif' }}>
              Bienvenue
            </h1>
            <p className="text-white/80 text-xs sm:text-sm">
              La plateforme suisse qui connecte<br className="hidden sm:block" /> clients et prestataires
            </p>
            <div className="mt-3 sm:mt-6 flex items-center gap-2">
              <div className="w-2 h-2 bg-[#D4AF37] rounded-full" />
              <span className="text-[#D4AF37] text-xs sm:text-sm font-medium">Lausanne & région</span>
            </div>
          </div>

          {/* Section droite - Avantages */}
          <div className="p-4 sm:p-8 sm:w-3/5 bg-white">
            
            {/* Layout en colonnes sur desktop, empilé sur mobile */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
              
              {/* Colonne Clients */}
              <div>
                <div className="flex items-center gap-2 mb-3 sm:mb-4">
                  <div className="p-1.5 sm:p-2 rounded-lg bg-[#0047AB]/10">
                    <Users className="w-4 h-4 sm:w-5 sm:h-5 text-[#0047AB]" />
                  </div>
                  <h3 className="font-semibold text-gray-900 text-sm sm:text-base">Pour les clients</h3>
                </div>
                <ul className="space-y-2 sm:space-y-3">
                  {clientAdvantages.map((item, index) => (
                    <li key={index} className="flex items-start gap-2 sm:gap-3">
                      <div className="mt-0.5 flex-shrink-0">
                        <Check className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-green-500" />
                      </div>
                      <span className="text-gray-700 text-xs sm:text-sm leading-snug">{item.text}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Colonne Entreprises */}
              <div>
                <div className="flex items-center gap-2 mb-3 sm:mb-4">
                  <div className="p-1.5 sm:p-2 rounded-lg bg-[#D4AF37]/10">
                    <Building2 className="w-4 h-4 sm:w-5 sm:h-5 text-[#D4AF37]" />
                  </div>
                  <h3 className="font-semibold text-gray-900 text-sm sm:text-base">Pour les entreprises</h3>
                </div>
                <ul className="space-y-2 sm:space-y-3">
                  {enterpriseAdvantages.map((item, index) => (
                    <li key={index} className="flex items-start gap-2 sm:gap-3">
                      <div className="mt-0.5 flex-shrink-0">
                        <Check className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-green-500" />
                      </div>
                      <span className="text-gray-700 text-xs sm:text-sm leading-snug">{item.text}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Boutons */}
            <div className="flex flex-col sm:flex-row gap-2 sm:gap-3 mt-5 sm:mt-8">
              <button
                onClick={handleClose}
                className="flex-1 px-4 py-2.5 sm:py-3 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-xl transition-all text-xs sm:text-sm font-medium"
                data-testid="welcome-popup-later"
              >
                Plus tard
              </button>
              <button
                onClick={handleExplore}
                className="flex-1 px-4 py-2.5 sm:py-3 bg-[#0047AB] hover:bg-[#003080] text-white rounded-xl transition-all text-xs sm:text-sm font-medium"
                data-testid="welcome-popup-signup"
              >
                S'inscrire gratuitement
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default WelcomePopup;
