import React, { useState, useEffect } from 'react';
import { ChevronRight, ChevronLeft, Check, User, Building, Sparkles, Target, Gift } from 'lucide-react';

const OnboardingGuide = ({ onComplete, userType = 'client' }) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    // Vérifier si l'onboarding a déjà été fait
    const onboardingDone = localStorage.getItem(`titelli_onboarding_${userType}`);
    if (!onboardingDone) {
      setIsVisible(true);
    }
  }, [userType]);

  const clientSteps = [
    {
      title: "Bienvenue sur Titelli !",
      description: "Découvrez la plateforme suisse qui connecte les meilleurs prestataires avec leurs clients.",
      icon: Sparkles,
      color: "from-blue-500 to-purple-500",
      tips: [
        "Trouvez des services de qualité près de chez vous",
        "Bénéficiez de cashback sur chaque achat",
        "Profitez d'offres exclusives"
      ]
    },
    {
      title: "Complétez votre profil",
      description: "Un profil complet vous permet de recevoir des recommandations personnalisées.",
      icon: User,
      color: "from-green-500 to-teal-500",
      tips: [
        "Ajoutez une photo de profil",
        "Renseignez vos préférences",
        "Indiquez votre localisation"
      ],
      action: {
        label: "Compléter mon profil",
        link: "/dashboard/client?tab=profile"
      }
    },
    {
      title: "Découvrez le Cashback",
      description: "Gagnez de l'argent sur chaque achat effectué sur Titelli !",
      icon: Gift,
      color: "from-yellow-500 to-orange-500",
      tips: [
        "1% de cashback avec le compte gratuit",
        "Jusqu'à 15% avec l'abonnement VIP",
        "Retirez votre cashback à partir de 50 CHF"
      ],
      action: {
        label: "Voir mon cashback",
        link: "/dashboard/client?tab=cashback"
      }
    },
    {
      title: "Explorez les services",
      description: "Parcourez notre catalogue de prestataires de qualité.",
      icon: Target,
      color: "from-pink-500 to-red-500",
      tips: [
        "Utilisez la recherche pour trouver ce que vous cherchez",
        "Filtrez par catégorie, prix ou note",
        "Lisez les avis des autres clients"
      ],
      action: {
        label: "Explorer les services",
        link: "/services"
      }
    }
  ];

  const enterpriseSteps = [
    {
      title: "Bienvenue sur Titelli Pro !",
      description: "Développez votre activité avec notre plateforme de mise en relation premium.",
      icon: Building,
      color: "from-blue-500 to-purple-500",
      tips: [
        "Atteignez de nouveaux clients",
        "Outils de gestion complets",
        "Marketing IA intégré"
      ]
    },
    {
      title: "Créez votre vitrine",
      description: "Présentez votre entreprise de manière professionnelle.",
      icon: User,
      color: "from-green-500 to-teal-500",
      tips: [
        "Ajoutez votre logo et photos",
        "Décrivez votre activité",
        "Définissez vos horaires"
      ],
      action: {
        label: "Compléter mon profil",
        link: "/dashboard/entreprise?tab=profile"
      }
    },
    {
      title: "Ajoutez vos services",
      description: "Créez votre catalogue de services et produits.",
      icon: Target,
      color: "from-yellow-500 to-orange-500",
      tips: [
        "Photos de qualité = plus de clients",
        "Descriptions détaillées",
        "Prix compétitifs"
      ],
      action: {
        label: "Ajouter un service",
        link: "/dashboard/entreprise?tab=services"
      }
    },
    {
      title: "Boostez votre visibilité",
      description: "Utilisez nos outils marketing pour attirer plus de clients.",
      icon: Sparkles,
      color: "from-pink-500 to-red-500",
      tips: [
        "Créez des publicités avec l'IA",
        "Utilisez le code BIENVENUE100 (100 CHF offerts)",
        "Lancez des promotions"
      ],
      action: {
        label: "Créer une pub",
        link: "/media-pub"
      }
    }
  ];

  const steps = userType === 'entreprise' ? enterpriseSteps : clientSteps;

  const handleNext = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      handleComplete();
    }
  };

  const handlePrev = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleComplete = () => {
    localStorage.setItem(`titelli_onboarding_${userType}`, 'true');
    setIsVisible(false);
    if (onComplete) onComplete();
  };

  const handleSkip = () => {
    localStorage.setItem(`titelli_onboarding_${userType}`, 'true');
    setIsVisible(false);
    if (onComplete) onComplete();
  };

  if (!isVisible) return null;

  const currentStepData = steps[currentStep];
  const IconComponent = currentStepData.icon;

  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center p-4">
      {/* Overlay */}
      <div className="absolute inset-0 bg-black/80 backdrop-blur-sm" />
      
      {/* Modal */}
      <div className="relative w-full max-w-lg bg-[#0a0a0f] rounded-2xl border border-white/10 shadow-2xl overflow-hidden">
        {/* Progress Bar */}
        <div className="h-1 bg-white/10">
          <div 
            className="h-full bg-gradient-to-r from-blue-500 to-purple-500 transition-all duration-300"
            style={{ width: `${((currentStep + 1) / steps.length) * 100}%` }}
          />
        </div>

        {/* Header avec gradient */}
        <div className={`h-40 bg-gradient-to-r ${currentStepData.color} relative overflow-hidden`}>
          {/* Cercles décoratifs */}
          <div className="absolute -top-10 -right-10 w-40 h-40 bg-white/10 rounded-full" />
          <div className="absolute -bottom-10 -left-10 w-32 h-32 bg-white/10 rounded-full" />
          
          {/* Icône centrale */}
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-20 h-20 bg-white/20 backdrop-blur-sm rounded-full flex items-center justify-center">
              <IconComponent className="w-10 h-10 text-white" />
            </div>
          </div>

          {/* Step indicator */}
          <div className="absolute top-4 right-4 bg-black/30 px-3 py-1 rounded-full text-white text-sm">
            {currentStep + 1} / {steps.length}
          </div>

          {/* Skip button */}
          <button
            onClick={handleSkip}
            className="absolute top-4 left-4 text-white/70 hover:text-white text-sm"
          >
            Passer
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          <h2 className="text-2xl font-bold text-white mb-2 text-center">
            {currentStepData.title}
          </h2>
          <p className="text-gray-400 text-center mb-6">
            {currentStepData.description}
          </p>

          {/* Tips */}
          <div className="bg-white/5 rounded-xl p-4 mb-6 border border-white/10">
            <ul className="space-y-3">
              {currentStepData.tips.map((tip, index) => (
                <li key={index} className="flex items-start gap-3">
                  <Check className="w-5 h-5 text-green-400 mt-0.5 flex-shrink-0" />
                  <span className="text-gray-300 text-sm">{tip}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Action Button (if present) */}
          {currentStepData.action && (
            <a
              href={currentStepData.action.link}
              onClick={handleComplete}
              className="block w-full text-center py-3 bg-white/10 hover:bg-white/20 rounded-xl text-white font-medium transition-colors mb-4"
            >
              {currentStepData.action.label}
            </a>
          )}

          {/* Navigation */}
          <div className="flex items-center justify-between">
            <button
              onClick={handlePrev}
              disabled={currentStep === 0}
              className="flex items-center gap-2 px-4 py-2 text-gray-400 hover:text-white disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
            >
              <ChevronLeft className="w-5 h-5" />
              Précédent
            </button>

            {/* Step dots */}
            <div className="flex gap-2">
              {steps.map((_, index) => (
                <button
                  key={index}
                  onClick={() => setCurrentStep(index)}
                  className={`w-2 h-2 rounded-full transition-all ${
                    index === currentStep 
                      ? 'w-6 bg-blue-500' 
                      : index < currentStep 
                        ? 'bg-blue-500/50' 
                        : 'bg-white/20'
                  }`}
                />
              ))}
            </div>

            <button
              onClick={handleNext}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-500 rounded-lg text-white font-medium transition-colors"
            >
              {currentStep === steps.length - 1 ? 'Terminer' : 'Suivant'}
              <ChevronRight className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OnboardingGuide;
