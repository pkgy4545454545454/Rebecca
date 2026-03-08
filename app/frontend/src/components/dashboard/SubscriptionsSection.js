import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Crown, Check, Zap, ChevronDown, Star, Building2, TrendingUp, Shield, Users, Target, Briefcase, Package, Gift, Clock, CreditCard, FileText, Phone, MessageSquare, Calendar, Newspaper, Sparkles, Image, Video, ArrowRight } from 'lucide-react';
import { subscriptionsAPI, paymentAPI } from '../../services/api';
import { toast } from 'sonner';

const SubscriptionsSection = () => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState('base');
  const [plans, setPlans] = useState([]);
  const [currentPlan, setCurrentPlan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [expandedFeatures, setExpandedFeatures] = useState(false);

  useEffect(() => {
    fetchPlans();
  }, []);

  const fetchPlans = async () => {
    try {
      const response = await subscriptionsAPI.getPlans();
      setPlans(response.data.plans || []);
      setCurrentPlan(response.data.current_plan);
    } catch (error) {
      console.error('Error fetching plans:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSubscribe = async (planId, price) => {
    try {
      toast.loading('Redirection vers le paiement...');
      const response = await subscriptionsAPI.createCheckout(planId);
      toast.dismiss();
      if (response.data.url) {
        window.open(response.data.url, '_blank');
      } else {
        toast.error('Erreur: URL de paiement non reçue');
      }
    } catch (error) {
      toast.dismiss();
      console.error('Subscription error:', error);
      toast.error(error.response?.data?.detail || 'Erreur lors de la souscription');
    }
  };

  const handleAddonSubscribe = async (addonId) => {
    try {
      toast.loading('Redirection vers le paiement...');
      const response = await subscriptionsAPI.createAddonCheckout(addonId);
      toast.dismiss();
      if (response.data.url) {
        window.open(response.data.url, '_blank');
      } else {
        toast.error('Erreur: URL de paiement non reçue');
      }
    } catch (error) {
      toast.dismiss();
      console.error('Addon subscription error:', error);
      toast.error(error.response?.data?.detail || 'Erreur lors de la souscription');
    }
  };

  const baseFeatures = [
    { icon: FileText, text: 'Fiches exigences clients' },
    { icon: Calendar, text: 'Calendrier client' },
    { icon: Calendar, text: 'Agenda interne' },
    { icon: Package, text: 'Espace de formation, documents, finance' },
    { icon: Target, text: 'Accès aux publicités spontanées' },
    { icon: MessageSquare, text: 'Messagerie' },
    { icon: Newspaper, text: "Fil d'actualités clients" },
    { icon: Building2, text: 'Feed des entreprises régionales' },
    { icon: Users, text: 'Gestion des contacts' },
  ];

  const tabs = [
    { id: 'base', label: 'Forfaits de base' },
    { id: 'premium', label: 'Premium' },
    { id: 'optimisation', label: "Optimisation d'entreprise" },
    { id: 'alacarte', label: 'Options à la carte' },
  ];

  const basePlans = [
    {
      id: 'standard',
      name: 'Standard',
      price: 200,
      period: '/mois',
      features: [
        'Exposition standard',
        '1 publicité/mois',
        'Cash-Back (10%)',
        'Gestion des stocks',
      ],
      color: '#0047AB',
    },
    {
      id: 'guest',
      name: 'Guest',
      price: 250,
      period: '/mois',
      popular: true,
      features: [
        'Profil professionnel complet',
        'Référencement préférentiel',
        'Publicités illimitées',
        'Statistiques avancées',
      ],
      color: '#D4AF37',
    },
  ];

  const premiumPlans = [
    {
      id: 'premium',
      name: 'Premium',
      price: 500,
      period: '/mois',
      features: [
        '4 publicités/mois',
        'Accès investisseurs',
        'Livraison 24/24',
        'Gestion du personnel',
        'Indicateurs performance',
      ],
      color: '#0047AB',
    },
    {
      id: 'premium_mvp',
      name: 'Premium MVP',
      price: 1000,
      period: '/mois',
      popular: true,
      features: [
        '5 publicités + 1 vidéo/mois',
        'Accès fournisseurs',
        'Local commercial 24/24',
        'Conseiller dédié',
        'Formation incluse',
      ],
      color: '#D4AF37',
    },
  ];

  const optimisationPlans = [
    { id: 'opti_starter_2k', name: 'Starter 2K', price: 2000, features: ['8 publicités/mois', 'Formations business', 'Immobilier commercial', 'Expert conseil'] },
    { id: 'opti_starter_3k', name: 'Starter+ 3K', price: 3000, features: ['15 publicités/mois', '5h prestations OU 2 déjeuners', 'Support prioritaire'] },
    { id: 'opti_5k', name: 'Opti 5K', price: 5000, features: ['10h prestations', "3'000 CHF liquidés", 'Accès premium complet'] },
    { id: 'opti_10k', name: 'Opti 10K', price: 10000, features: ['20h prestations', "7'000 CHF liquidés", 'Fiscaliste dédié'] },
    { id: 'opti_20k', name: 'Opti 20K', price: 20000, features: ['25 publicités/mois', '40h prestations', "15'000 CHF liquidés"] },
    { id: 'opti_50k', name: 'Opti 50K', price: 50000, features: ['80h prestations', "40'000 CHF liquidés", 'Service conciergerie'] },
  ];

  const alacarteOptions = [
    { id: 'media_pub', name: '🎨 Pub Média IA', price: 'Dès 19.90', period: '/création', description: 'Créez vos publicités avec notre IA', isSpecial: true, specialType: 'media_pub' },
    { id: 'video_pub', name: '🎬 Vidéo Pub IA', price: 'Dès 49.90', period: '/création', description: 'Vidéos publicitaires générées par IA', isSpecial: true, specialType: 'video_pub' },
    { id: 'pub_extra', name: 'Publicités extra', price: 200, period: '/mois', description: '+2 publicités + 1 vidéo par mois' },
    { id: 'investors_access', name: 'Accès Investisseurs', price: 300, period: '/mois', description: 'Visibilité auprès des investisseurs' },
    { id: 'delivery_24', name: 'Livraison 24/24', price: 300, period: '/mois', description: 'Service de livraison permanent' },
    { id: 'local_access', name: 'Local commercial', price: 300, period: '/mois', description: 'Accès au local 24h/24' },
    { id: 'suppliers_access', name: 'Accès Fournisseurs', price: 500, period: '/mois', description: 'Réseau de fournisseurs exclusifs' },
    { id: 'premium_trainings', name: 'Formations', price: 200, period: '/mois', description: 'Formations business mensuelles' },
    { id: 'instant_recruitment', name: 'Recrutement', price: 200, period: '/mois', description: 'Aide au recrutement' },
    { id: 'real_estate_access', name: 'Immobilier', price: 200, period: '/mois', description: 'Annonces immobilières' },
    { id: 'expert_conseil', name: 'Expert conseil', price: 1000, period: '/mois', description: 'Conseiller dédié' },
    { id: 'fiscaliste', name: 'Fiscaliste', price: 4000, period: '/mois', description: 'Accompagnement fiscal' },
    { id: 'prestation_liquidee', name: 'Prestations liquidées', price: 1000, period: '/mois', description: '800 CHF de prestations' },
    { id: 'expert_label', name: 'Expert labellisation', price: 400, period: 'ponctuel', description: 'Accompagnement certification' },
    { id: 'prestation_20h', name: '20h Prestations', price: 1000, period: 'ponctuel', description: '20 heures de prestations' },
    { id: 'dejeuner_equipe', name: '20 déjeuners équipe', price: 2000, period: 'ponctuel', description: "Déjeuners d'équipe" },
  ];

  const handleSpecialOption = (option) => {
    if (option.specialType === 'media_pub') {
      navigate('/media-pub');
    } else if (option.specialType === 'video_pub') {
      toast.info('Vidéo Pub IA - Bientôt disponible !');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <div className="w-10 h-10 border-4 border-[#D4AF37] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="subscriptions-section">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
            Abonnements
          </h1>
          <p className="text-gray-400 mt-1">Choisissez le forfait adapté à vos besoins</p>
        </div>
        {currentPlan && (
          <div className="flex items-center gap-2 px-4 py-2 bg-[#D4AF37]/20 rounded-lg">
            <Crown className="w-5 h-5 text-[#D4AF37]" />
            <span className="text-[#D4AF37] font-medium">Plan actuel: {currentPlan}</span>
          </div>
        )}
      </div>

      {/* Base Features */}
      <div className="card-service rounded-xl p-6">
        <button 
          onClick={() => setExpandedFeatures(!expandedFeatures)}
          className="w-full flex items-center justify-between text-left"
        >
          <div className="flex items-center gap-3">
            <Shield className="w-6 h-6 text-[#0047AB]" />
            <div>
              <h2 className="text-lg font-semibold text-white">Features incluses dans tous les forfaits</h2>
              <p className="text-sm text-gray-400">{baseFeatures.length} fonctionnalités de base</p>
            </div>
          </div>
          <ChevronDown className={`w-5 h-5 text-gray-400 transition-transform ${expandedFeatures ? 'rotate-180' : ''}`} />
        </button>
        {expandedFeatures && (
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mt-4 pt-4 border-t border-white/10">
            {baseFeatures.map((feature, i) => (
              <div key={i} className="flex items-center gap-2 text-sm text-gray-300">
                <feature.icon className="w-4 h-4 text-[#0047AB]" />
                {feature.text}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Tabs */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 rounded-lg text-sm whitespace-nowrap transition-colors ${
              activeTab === tab.id
                ? 'bg-[#0047AB] text-white'
                : 'bg-white/5 text-gray-400 hover:bg-white/10'
            }`}
          >
            {tab.label}
          </button>
        ))}
      </div>

      {/* Base Plans */}
      {activeTab === 'base' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {basePlans.map((plan) => (
            <div 
              key={plan.id} 
              className={`card-service rounded-xl p-6 relative ${plan.popular ? 'border-[#D4AF37]' : ''}`}
            >
              {plan.popular && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 bg-[#D4AF37] text-black text-xs font-bold rounded-full">
                  POPULAIRE
                </div>
              )}
              <h3 className="text-xl font-bold text-white mb-2">{plan.name}</h3>
              <div className="flex items-baseline gap-1 mb-6">
                <span className="text-4xl font-bold" style={{ color: plan.color }}>{plan.price}</span>
                <span className="text-gray-400">CHF{plan.period}</span>
              </div>
              <ul className="space-y-3 mb-6">
                {plan.features.map((feature, i) => (
                  <li key={i} className="flex items-center gap-2 text-gray-300">
                    <Check className="w-4 h-4" style={{ color: plan.color }} />
                    {feature}
                  </li>
                ))}
              </ul>
              <button 
                onClick={() => handleSubscribe(plan.id, plan.price)}
                className={`w-full py-3 rounded-lg font-medium transition-colors ${
                  plan.popular 
                    ? 'bg-[#D4AF37] text-black hover:bg-[#D4AF37]/90' 
                    : 'bg-[#0047AB] text-white hover:bg-[#0047AB]/90'
                }`}
              >
                Choisir ce forfait
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Premium Plans */}
      {activeTab === 'premium' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {premiumPlans.map((plan) => (
            <div 
              key={plan.id} 
              className={`card-service rounded-xl p-6 relative ${plan.popular ? 'border-[#D4AF37]' : ''}`}
            >
              {plan.popular && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 bg-[#D4AF37] text-black text-xs font-bold rounded-full flex items-center gap-1">
                  <Star className="w-3 h-3" /> MVP
                </div>
              )}
              <h3 className="text-xl font-bold text-white mb-2">{plan.name}</h3>
              <div className="flex items-baseline gap-1 mb-6">
                <span className="text-4xl font-bold" style={{ color: plan.color }}>{plan.price.toLocaleString()}</span>
                <span className="text-gray-400">CHF{plan.period}</span>
              </div>
              <ul className="space-y-3 mb-6">
                {plan.features.map((feature, i) => (
                  <li key={i} className="flex items-center gap-2 text-gray-300">
                    <Check className="w-4 h-4" style={{ color: plan.color }} />
                    {feature}
                  </li>
                ))}
              </ul>
              <button 
                onClick={() => handleSubscribe(plan.id, plan.price)}
                className={`w-full py-3 rounded-lg font-medium transition-colors ${
                  plan.popular 
                    ? 'bg-[#D4AF37] text-black hover:bg-[#D4AF37]/90' 
                    : 'bg-[#0047AB] text-white hover:bg-[#0047AB]/90'
                }`}
              >
                Choisir ce forfait
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Optimisation Plans */}
      {activeTab === 'optimisation' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {optimisationPlans.map((plan) => (
            <div key={plan.id} className="card-service rounded-xl p-5">
              <h3 className="text-lg font-bold text-white mb-2">{plan.name}</h3>
              <div className="flex items-baseline gap-1 mb-4">
                <span className="text-2xl font-bold text-[#D4AF37]">{plan.price.toLocaleString()}</span>
                <span className="text-gray-400 text-sm">CHF/mois</span>
              </div>
              <ul className="space-y-2 mb-4">
                {plan.features.map((feature, i) => (
                  <li key={i} className="flex items-center gap-2 text-sm text-gray-300">
                    <Zap className="w-3 h-3 text-[#D4AF37]" />
                    {feature}
                  </li>
                ))}
              </ul>
              <button 
                onClick={() => handleSubscribe(plan.id, plan.price)}
                className="w-full py-2 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-colors text-sm"
              >
                Souscrire
              </button>
            </div>
          ))}
        </div>
      )}

      {/* A la carte */}
      {activeTab === 'alacarte' && (
        <div className="space-y-4">
          {/* Options spéciales IA en haut */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {alacarteOptions.filter(o => o.isSpecial).map((option) => (
              <div 
                key={option.id} 
                className="card-service rounded-xl p-6 relative overflow-hidden cursor-pointer hover:border-purple-500/50 transition-all group"
                onClick={() => handleSpecialOption(option)}
              >
                <div className="absolute inset-0 bg-gradient-to-br from-purple-600/10 to-blue-600/10"></div>
                <div className="relative">
                  <div className="flex items-center gap-2 mb-2">
                    {option.specialType === 'media_pub' ? (
                      <Image className="w-6 h-6 text-purple-400" />
                    ) : (
                      <Video className="w-6 h-6 text-blue-400" />
                    )}
                    <span className="px-2 py-0.5 bg-purple-500/20 text-purple-300 text-xs rounded-full">IA</span>
                  </div>
                  <h4 className="text-xl font-bold text-white mb-1">{option.name}</h4>
                  <p className="text-sm text-gray-400 mb-3">{option.description}</p>
                  <div className="flex items-center justify-between">
                    <div className="flex items-baseline gap-1">
                      <span className="text-2xl font-bold text-[#D4AF37]">{option.price}</span>
                      <span className="text-gray-500 text-sm">CHF {option.period}</span>
                    </div>
                    <button 
                      className="flex items-center gap-2 px-4 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg text-sm transition-colors group-hover:translate-x-1"
                    >
                      Créer <ArrowRight className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
          
          {/* Options standards */}
          <h3 className="text-lg font-semibold text-white mt-6 mb-4">Autres options</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {alacarteOptions.filter(o => !o.isSpecial).map((option) => (
              <div key={option.id} className="card-service rounded-xl p-4 flex items-start justify-between">
                <div className="flex-1">
                  <h4 className="text-white font-medium">{option.name}</h4>
                  <p className="text-sm text-gray-400 mb-2">{option.description}</p>
                  <div className="flex items-baseline gap-1">
                    <span className="text-lg font-bold text-[#D4AF37]">{option.price}</span>
                    <span className="text-gray-500 text-xs">CHF {option.period}</span>
                  </div>
                </div>
                <button 
                  onClick={() => handleAddonSubscribe(option.id)}
                  className="px-3 py-1.5 bg-[#0047AB]/20 text-[#0047AB] rounded-lg text-sm hover:bg-[#0047AB]/30 transition-colors"
                >
                  Ajouter
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default SubscriptionsSection;
