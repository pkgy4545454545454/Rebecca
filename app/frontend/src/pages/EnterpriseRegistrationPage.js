import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Building2, MapPin, Phone, Globe, ChevronRight, Upload, User, FileText, Users, CheckCircle, ArrowLeft, X, Star, TrendingUp, Shield, Zap, Gift, Crown, Award, Sparkles, Target, BarChart, Truck, Megaphone, Package, GraduationCap, Banknote, Briefcase, Heart, Eye, Palette, ChevronDown, ChevronUp } from 'lucide-react';
import { toast } from 'sonner';
import axios from 'axios';

const API_URL = `${process.env.REACT_APP_BACKEND_URL}/api`;

// Enterprise Benefits Popup Component - CDC Complet
const EnterpriseBenefitsPopup = ({ onClose }) => {
  const [activeTab, setActiveTab] = useState('services');
  const [expandedPack, setExpandedPack] = useState(null);

  const servicesBase = [
    {
      title: "Inscription annuelle",
      price: "250.-",
      period: "obligatoire",
      description: "Activation de votre compte entreprise sur Titelli",
      icon: Building2,
      color: "text-white",
      required: true
    },
    {
      title: "Premium livraison instantanée",
      price: "50.-/mois ou 500.-/an",
      description: "Nos clients consomment et apprécient d'avantage que l'on réponde à leurs demandes instantanément.",
      icon: Truck,
      color: "text-blue-400"
    },
    {
      title: "Pub Référencement mensuel",
      price: "100.-/mois ou 1'000.-/an",
      description: "Se faire référencer dans son domaine d'activité ou dans sa rubrique préférée tout au long de l'année.",
      icon: Megaphone,
      color: "text-purple-400"
    },
    {
      title: "Premium dépôt 24/24",
      price: "100.-/mois ou 1'000.-/an",
      description: "Un dépôt accessible à nos chauffeurs après 19h vous permettant de liquider votre stock en vous reposant.",
      icon: Package,
      color: "text-green-400"
    },
    {
      title: "Formations avancées",
      price: "200.- ou 2'000.-/an",
      description: "Les meilleures techniques, méthodes et outils sur le marché. Des formations faites par des spécialistes Suisses triés sur un registre stricte et ultra sélectif.",
      icon: GraduationCap,
      color: "text-orange-400"
    },
    {
      title: "Liquidation de ton stock",
      price: "1'000.-/mois ou 10'000.-/an",
      description: "Nos experts liquident vos produits à hauteur du montant engagé mensuellement. Et si Titelli liquide votre stock, que vous reste-t-il à faire ? Quoi que ce soit, Titelli le fait aussi.",
      icon: TrendingUp,
      color: "text-red-400"
    }
  ];

  const investissements = [
    {
      title: "Investissement",
      price: "200.- ou 2'000.-/an",
      description: "Trouver un partenaire, proposez un prix, proposez des parts.",
      icon: Banknote,
      color: "text-green-400"
    },
    {
      title: "Investissement élite",
      price: "500.- ou 5'000.-/an",
      description: "Demandez un investissement contre bénéfice pour la durée de votre choix. Accès à d'innombrables opportunités d'investissements.",
      icon: Crown,
      color: "text-[#D4AF37]"
    }
  ];

  const fournisseurs = [
    {
      title: "Fournisseurs",
      price: "200.- ou 2'000.-/an",
      description: "Accès à des fournisseurs qui permettent l'optimisation de votre entreprise en répondant à une qualité plus prestigieuse pour un meilleur prix.",
      level: "Standard"
    },
    {
      title: "Fournisseurs guest",
      price: "300.- ou 3'000.-/an",
      description: "Accès à tous les fournisseurs concernant votre domaine d'activité, ce qui vous donne du choix, immédiatement et continuellement.",
      level: "Guest"
    },
    {
      title: "Fournisseurs premium",
      price: "500.- ou 5'000.-/an",
      description: "Accès à tous les fournisseurs du marché, voire même des producteurs, ce qui vaut de l'or.",
      level: "Premium"
    },
    {
      title: "Fournisseurs élite",
      price: "1'000.- ou 10'000.-/an",
      description: "Accès à des fournisseurs et producteurs hors marchés, précieux et rares. Le privilège d'une qualité de haut standing qui ne se voit pas dans son prix.",
      level: "Élite"
    }
  ];

  const gestion = [
    {
      title: "Soins entreprise",
      price: "500.- ou 5'000.-/an",
      description: "Des soins pour votre personnel ou votre entreprise, un entretien ou un renouvellement continu pour une meilleure ambiance, productivité et image.",
      icon: Heart
    },
    {
      title: "Gestion d'entreprise starter",
      price: "1'000.- ou 10'000.-/an",
      description: "Un expert qui s'occupe de votre image et de votre campagne marketing tous les mois.",
      icon: Briefcase
    },
    {
      title: "Gestion d'entreprise premium",
      price: "3'000.- ou 30'000.-/an",
      description: "Un expert marketing et un fiscaliste pour une meilleure gestion de votre entreprise tout au long de l'année.",
      icon: Award
    },
    {
      title: "Gestion d'entreprise élite",
      price: "5'000.-/mois ou 50'000.-/an",
      description: "Un expert en gestion d'image, un expert juridique et plusieurs spécialistes de votre domaine d'activité font prendre à votre entreprise une nouvelle direction.",
      icon: Crown
    }
  ];

  const marketing = [
    {
      title: "Marketing visuel",
      price: "100.- ou 1'000.-/an",
      description: "Accès aux meilleurs outils informatisés sur le marché toute l'année afin de vous permettre une nouvelle revalorisation de votre métier, entreprise et prestations.",
      icon: Eye
    },
    {
      title: "Expert marketing visuel",
      price: "200.- ou 2'000.-/an",
      description: "Un expert révise votre publicité par les meilleurs outils informatisés tous les mois.",
      icon: Palette
    },
    {
      title: "Expert marketing premium",
      price: "500.- ou 5'000.-/an",
      description: "Un expert vous suggère de véritables publicités sur-mesure tous les mois.",
      icon: Sparkles
    },
    {
      title: "Expert marketing élite",
      price: "1'000.- ou 10'000.-/an",
      description: "Un expert construit votre image et mène une véritable campagne marketing tout au long de l'année.",
      icon: Target
    }
  ];

  const packs = [
    {
      name: "Entreprenariat",
      price: "200.-/mois",
      color: "from-gray-600 to-gray-800",
      items: ["Premium livraison instant 50.-", "Pub Référence mensuelle 100.-", "Marketing visuel 100.-"]
    },
    {
      name: "Patronat",
      price: "500.-/mois",
      color: "from-blue-600 to-blue-800",
      items: ["Premium livraison instant 50.-", "Pub Référence mensuelle 100.-", "Marketing visuel 100.-", "Premium dépôt 24/24 100.-", "Fournisseurs 200.-", "Investissement 200.-"]
    },
    {
      name: "Indépendant",
      price: "1'000.-/mois",
      color: "from-purple-600 to-purple-800",
      items: ["Premium livraison instant 50.-", "Pub référence mensuelle 200.-", "Expert marketing visuel 200.-", "Premium dépôt 24/24 100.-", "Fournisseurs 200.-", "Investissement 500.-", "Formations avancées 200.-"]
    },
    {
      name: "Directeur",
      price: "2'000.-/mois",
      color: "from-[#D4AF37] to-yellow-700",
      items: ["Premium livraison instantanée", "Pub référence mensuelle 400.-", "Expert marketing visuel 500.-", "Premium dépôt 24/24 100.-", "Fournisseurs 300.-", "Investissement 500.-", "Formations avancées 200.-", "Soins entreprise 500.-"]
    },
    {
      name: "Dirigeant",
      price: "3'000.-/mois",
      color: "from-orange-500 to-red-600",
      items: ["Premium livraison instant 50.-", "Pub Référence mensuelle 400.-", "Expert marketing visuel 500.-", "Premium dépôt 24/24 100.-", "Fournisseurs 300.-", "Investissement 500.-", "Formations avancées 500.-", "Soins entreprise 500.-", "Liquidation de votre stock 1'000.-"]
    },
    {
      name: "CEO",
      price: "5'000.-/mois",
      color: "from-red-600 to-pink-600",
      items: ["Premium livraison instant 50.-", "Pub Référence mensuelle 400.-", "Expert marketing visuel 500.-", "Premium dépôt 24/24 100.-", "Fournisseurs 500.-", "Investissement 500.-", "Formations avancées 500.-", "Soins entreprise 500.-", "Liquidation de ton stock 2'000.-", "Gestion d'entreprise starter"]
    }
  ];

  const tabs = [
    { id: 'services', label: 'Services' },
    { id: 'fournisseurs', label: 'Fournisseurs' },
    { id: 'gestion', label: 'Gestion' },
    { id: 'marketing', label: 'Marketing' },
    { id: 'packs', label: 'Packs' }
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-2 sm:p-4 bg-black/90 backdrop-blur-sm">
      <div className="bg-gradient-to-br from-[#0a0a0a] to-[#1a1a2e] border border-white/10 rounded-2xl max-w-4xl w-full max-h-[95vh] overflow-hidden shadow-2xl flex flex-col">
        {/* Header */}
        <div className="relative p-4 sm:p-6 text-center border-b border-white/10 bg-gradient-to-r from-[#0047AB]/20 to-[#D4AF37]/20 flex-shrink-0">
          <div className="relative z-10">
            <div className="w-12 h-12 sm:w-16 sm:h-16 mx-auto mb-3 bg-gradient-to-br from-[#0047AB] to-[#D4AF37] rounded-full flex items-center justify-center">
              <Sparkles className="w-6 h-6 sm:w-8 sm:h-8 text-white" />
            </div>
            <h2 className="text-xl sm:text-2xl font-bold text-white mb-1" style={{ fontFamily: 'Playfair Display, serif' }}>
              Bienvenue sur Titelli !
            </h2>
            <p className="text-gray-300 text-sm">
              Découvrez vos opportunités partenariales
            </p>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex border-b border-white/10 overflow-x-auto flex-shrink-0 scrollbar-hide">
          {tabs.map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-3 text-sm font-medium whitespace-nowrap transition-all ${
                activeTab === tab.id 
                  ? 'text-[#D4AF37] border-b-2 border-[#D4AF37]' 
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Content - Scrollable */}
        <div className="flex-1 overflow-y-auto p-4 sm:p-6">
          {/* Services Tab */}
          {activeTab === 'services' && (
            <div className="space-y-3">
              <div className="bg-[#D4AF37]/20 border border-[#D4AF37]/30 rounded-xl p-4 mb-4">
                <div className="flex items-center gap-3">
                  <Building2 className="w-6 h-6 text-[#D4AF37]" />
                  <div>
                    <h3 className="text-white font-bold">Inscription annuelle - 250.- (obligatoire)</h3>
                    <p className="text-gray-300 text-sm">L'activation effective de votre compte est soumise à un contrôle stricte et peut prendre 30 à 60 jours ouvrables.</p>
                  </div>
                </div>
              </div>
              
              {servicesBase.slice(1).map((service, index) => (
                <div key={index} className="bg-white/5 border border-white/5 rounded-xl p-4 hover:border-white/10 transition-all">
                  <div className="flex items-start gap-3">
                    <div className={`w-10 h-10 rounded-lg bg-white/10 flex items-center justify-center flex-shrink-0 ${service.color}`}>
                      <service.icon className="w-5 h-5" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between flex-wrap gap-2">
                        <h3 className="text-white font-semibold">{service.title}</h3>
                        <span className="text-[#D4AF37] text-sm font-medium">{service.price}</span>
                      </div>
                      <p className="text-gray-400 text-sm mt-1">{service.description}</p>
                    </div>
                  </div>
                </div>
              ))}

              {investissements.map((inv, index) => (
                <div key={index} className="bg-white/5 border border-white/5 rounded-xl p-4 hover:border-white/10 transition-all">
                  <div className="flex items-start gap-3">
                    <div className={`w-10 h-10 rounded-lg bg-white/10 flex items-center justify-center flex-shrink-0 ${inv.color}`}>
                      <inv.icon className="w-5 h-5" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between flex-wrap gap-2">
                        <h3 className="text-white font-semibold">{inv.title}</h3>
                        <span className="text-[#D4AF37] text-sm font-medium">{inv.price}</span>
                      </div>
                      <p className="text-gray-400 text-sm mt-1">{inv.description}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Fournisseurs Tab */}
          {activeTab === 'fournisseurs' && (
            <div className="space-y-3">
              <p className="text-gray-400 text-sm mb-4">Accédez aux meilleurs fournisseurs selon votre niveau de partenariat.</p>
              {fournisseurs.map((f, index) => (
                <div key={index} className="bg-white/5 border border-white/5 rounded-xl p-4 hover:border-white/10 transition-all">
                  <div className="flex items-center justify-between flex-wrap gap-2 mb-2">
                    <div className="flex items-center gap-2">
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        f.level === 'Élite' ? 'bg-[#D4AF37]/20 text-[#D4AF37]' :
                        f.level === 'Premium' ? 'bg-purple-500/20 text-purple-400' :
                        f.level === 'Guest' ? 'bg-blue-500/20 text-blue-400' :
                        'bg-gray-500/20 text-gray-400'
                      }`}>{f.level}</span>
                      <h3 className="text-white font-semibold">{f.title}</h3>
                    </div>
                    <span className="text-[#D4AF37] text-sm font-medium">{f.price}</span>
                  </div>
                  <p className="text-gray-400 text-sm">{f.description}</p>
                </div>
              ))}
            </div>
          )}

          {/* Gestion Tab */}
          {activeTab === 'gestion' && (
            <div className="space-y-3">
              <p className="text-gray-400 text-sm mb-4">Des experts dédiés pour gérer et développer votre entreprise.</p>
              {gestion.map((g, index) => (
                <div key={index} className="bg-white/5 border border-white/5 rounded-xl p-4 hover:border-white/10 transition-all">
                  <div className="flex items-start gap-3">
                    <div className="w-10 h-10 rounded-lg bg-white/10 flex items-center justify-center flex-shrink-0 text-[#D4AF37]">
                      <g.icon className="w-5 h-5" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between flex-wrap gap-2">
                        <h3 className="text-white font-semibold">{g.title}</h3>
                        <span className="text-[#D4AF37] text-sm font-medium">{g.price}</span>
                      </div>
                      <p className="text-gray-400 text-sm mt-1">{g.description}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Marketing Tab */}
          {activeTab === 'marketing' && (
            <div className="space-y-3">
              <p className="text-gray-400 text-sm mb-4">Optimisez votre image et votre visibilité avec nos experts marketing.</p>
              {marketing.map((m, index) => (
                <div key={index} className="bg-white/5 border border-white/5 rounded-xl p-4 hover:border-white/10 transition-all">
                  <div className="flex items-start gap-3">
                    <div className="w-10 h-10 rounded-lg bg-white/10 flex items-center justify-center flex-shrink-0 text-purple-400">
                      <m.icon className="w-5 h-5" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between flex-wrap gap-2">
                        <h3 className="text-white font-semibold">{m.title}</h3>
                        <span className="text-[#D4AF37] text-sm font-medium">{m.price}</span>
                      </div>
                      <p className="text-gray-400 text-sm mt-1">{m.description}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* Packs Tab */}
          {activeTab === 'packs' && (
            <div className="space-y-4">
              <p className="text-gray-400 text-sm mb-4">Choisissez le pack qui correspond à vos ambitions.</p>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {packs.map((pack, index) => (
                  <div 
                    key={index} 
                    className={`bg-gradient-to-br ${pack.color} rounded-xl overflow-hidden cursor-pointer transition-all hover:scale-[1.02]`}
                    onClick={() => setExpandedPack(expandedPack === index ? null : index)}
                  >
                    <div className="p-4">
                      <div className="flex items-center justify-between mb-2">
                        <h3 className="text-white font-bold">{pack.name}</h3>
                        {expandedPack === index ? <ChevronUp className="w-4 h-4 text-white/70" /> : <ChevronDown className="w-4 h-4 text-white/70" />}
                      </div>
                      <p className="text-white/90 text-lg font-semibold">{pack.price}</p>
                    </div>
                    {expandedPack === index && (
                      <div className="bg-black/30 p-4 space-y-1">
                        {pack.items.map((item, i) => (
                          <div key={i} className="flex items-center gap-2 text-white/80 text-sm">
                            <CheckCircle className="w-3 h-3 text-white/60" />
                            <span>{item}</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>

              {/* Premium Service Info */}
              <div className="mt-6 p-4 bg-gradient-to-r from-[#0047AB]/20 to-[#D4AF37]/20 rounded-xl border border-white/10">
                <h4 className="text-white font-semibold mb-2 flex items-center gap-2">
                  <Zap className="w-5 h-5 text-[#D4AF37]" />
                  Le service Premium
                </h4>
                <p className="text-gray-300 text-sm">
                  Permet de renforcer votre accessibilité sur le marché ainsi que de répondre à une clientèle plus exigeante. 
                  Mettez-vous à disposition du client en tout temps et en tout lieu.
                </p>
                <p className="text-[#D4AF37] text-sm mt-2 italic">
                  « Ce que vous voulez, où vous le voulez, quand vous le voulez »
                </p>
              </div>
            </div>
          )}
        </div>

        {/* CTA Button - Fixed at bottom */}
        <div className="p-4 sm:p-6 border-t border-white/10 flex-shrink-0 bg-[#0a0a0a]">
          <button
            onClick={onClose}
            className="w-full py-4 bg-gradient-to-r from-[#0047AB] to-[#D4AF37] text-white font-semibold rounded-xl hover:opacity-90 transition-all flex items-center justify-center gap-2 group"
            data-testid="benefits-popup-close"
          >
            <span>C'est compris, commençons !</span>
            <ChevronRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </button>
        </div>
      </div>
    </div>
  );
};

const EnterpriseRegistrationPage = () => {
  const navigate = useNavigate();
  const [step, setStep] = useState(1); // 1: Select enterprise, 2: Fill form, 3: Success
  const [showBenefitsPopup, setShowBenefitsPopup] = useState(false);
  const [enterprises, setEnterprises] = useState([]);
  const [managers, setManagers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedEnterprise, setSelectedEnterprise] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  
  // Check for demo mode to preview popup
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('demo') === 'benefits') {
      setShowBenefitsPopup(true);
    }
  }, []);
  
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    confirmPassword: '',
    first_name: '',
    last_name: '',
    phone: '',
    commerce_register_id: '',
    manager_id: '',
    identity_document: null
  });

  useEffect(() => {
    fetchEnterprises();
    fetchManagers();
  }, []);

  const fetchEnterprises = async (search = '') => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/enterprises/available`, { params: { search, limit: 200 } });
      setEnterprises(response.data.enterprises || []);
    } catch (error) {
      console.error('Error fetching enterprises:', error);
      toast.error('Erreur lors du chargement des entreprises');
    } finally {
      setLoading(false);
    }
  };

  const fetchManagers = async () => {
    try {
      const response = await axios.get(`${API_URL}/managers`);
      setManagers(response.data.managers || []);
    } catch (error) {
      console.error('Error fetching managers:', error);
    }
  };

  const handleSearch = (e) => {
    const value = e.target.value;
    setSearchQuery(value);
    fetchEnterprises(value);
  };

  const handleSelectEnterprise = (enterprise) => {
    setSelectedEnterprise(enterprise);
    // Show benefits popup first when clicking on enterprise
    setShowBenefitsPopup(true);
  };

  // Handle closing benefits popup - goes to form after
  const handleCloseBenefitsPopup = () => {
    setShowBenefitsPopup(false);
    if (selectedEnterprise) {
      setStep(2); // Go to form after closing popup
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      if (file.size > 5 * 1024 * 1024) {
        toast.error('Le fichier ne doit pas dépasser 5 Mo');
        return;
      }
      const reader = new FileReader();
      reader.onloadend = () => {
        setFormData({ ...formData, identity_document: reader.result });
      };
      reader.readAsDataURL(file);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (formData.password !== formData.confirmPassword) {
      toast.error('Les mots de passe ne correspondent pas');
      return;
    }

    if (formData.password.length < 6) {
      toast.error('Le mot de passe doit contenir au moins 6 caractères');
      return;
    }

    if (!formData.commerce_register_id) {
      toast.error('L\'ID du registre du commerce est requis');
      return;
    }

    if (!formData.manager_id) {
      toast.error('Veuillez sélectionner un manager');
      return;
    }

    try {
      setSubmitting(true);
      await axios.post(`${API_URL}/auth/register-enterprise`, {
        enterprise_id: selectedEnterprise.id,
        email: formData.email,
        password: formData.password,
        first_name: formData.first_name,
        last_name: formData.last_name,
        phone: formData.phone,
        commerce_register_id: formData.commerce_register_id,
        manager_id: formData.manager_id,
        identity_document: formData.identity_document
      });
      
      // Show benefits popup first, then proceed to success
      setShowBenefitsPopup(true);
    } catch (error) {
      console.error('Error registering:', error);
      toast.error(error.response?.data?.detail || 'Erreur lors de l\'inscription');
    } finally {
      setSubmitting(false);
    }
  };

  // Step 1: Select Enterprise
  if (step === 1) {
    return (
      <>
        {showBenefitsPopup && <EnterpriseBenefitsPopup onClose={handleCloseBenefitsPopup} />}
        <div className="min-h-screen bg-[#050505] pt-24 px-4">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold text-white mb-4" style={{ fontFamily: 'Playfair Display, serif' }}>
              Activez votre entreprise
            </h1>
            <p className="text-gray-400 text-lg">
              Recherchez et sélectionnez votre entreprise pour commencer l'inscription
            </p>
          </div>

          {/* Search */}
          <div className="relative mb-8">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Rechercher votre entreprise par nom, catégorie ou adresse..."
              value={searchQuery}
              onChange={handleSearch}
              className="w-full pl-12 pr-4 py-4 bg-white/5 border border-white/10 rounded-xl text-white placeholder:text-gray-500 focus:outline-none focus:border-[#0047AB]/50 text-lg"
            />
          </div>

          {/* Enterprise List */}
          <div className="space-y-4">
            {loading ? (
              <div className="flex justify-center py-12">
                <div className="w-12 h-12 border-4 border-[#0047AB] border-t-transparent rounded-full animate-spin" />
              </div>
            ) : enterprises.length === 0 ? (
              <div className="text-center py-12 text-gray-400">
                <Building2 className="w-16 h-16 mx-auto mb-4 opacity-50" />
                <p>Aucune entreprise trouvée</p>
              </div>
            ) : (
              enterprises.map((enterprise) => (
                <div
                  key={enterprise.id}
                  onClick={() => handleSelectEnterprise(enterprise)}
                  className="bg-white/5 border border-white/10 rounded-xl p-4 cursor-pointer hover:border-[#0047AB]/50 hover:bg-white/10 transition-all group"
                >
                  <div className="flex items-center gap-4">
                    <img
                      src={enterprise.image || `https://ui-avatars.com/api/?name=${enterprise.name}&background=0047AB&color=fff`}
                      alt={enterprise.name}
                      className="w-16 h-16 rounded-lg object-cover"
                    />
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <h3 className="text-white font-semibold text-lg">{enterprise.name}</h3>
                        <span className={`px-2 py-0.5 rounded-full text-xs ${
                          enterprise.status === 'disponible' 
                            ? 'bg-green-500/20 text-green-400' 
                            : 'bg-yellow-500/20 text-yellow-400'
                        }`}>
                          {enterprise.status === 'disponible' ? 'Disponible' : 'Bientôt disponible'}
                        </span>
                      </div>
                      <p className="text-[#D4AF37] text-sm mb-1">{enterprise.category}</p>
                      <div className="flex items-center gap-4 text-gray-400 text-sm">
                        <span className="flex items-center gap-1">
                          <MapPin className="w-4 h-4" />
                          {enterprise.address}
                        </span>
                        {enterprise.phone && (
                          <span className="flex items-center gap-1">
                            <Phone className="w-4 h-4" />
                            {enterprise.phone}
                          </span>
                        )}
                      </div>
                    </div>
                    <ChevronRight className="w-6 h-6 text-gray-400 group-hover:text-[#0047AB] transition-colors" />
                  </div>
                </div>
              ))
            )}
          </div>

          <p className="text-center text-gray-500 mt-8">
            {enterprises.length} entreprises disponibles
          </p>
        </div>
      </div>
      </>
    );
  }

  // Step 2: Registration Form
  if (step === 2) {
    return (
      <>
        {showBenefitsPopup && <EnterpriseBenefitsPopup onClose={handleCloseBenefitsPopup} />}
        <div className="min-h-screen bg-[#050505] pt-24 px-4 pb-12">
        <div className="max-w-2xl mx-auto">
          <button
            onClick={() => setStep(1)}
            className="flex items-center gap-2 text-gray-400 hover:text-white mb-8 transition-colors"
          >
            <ArrowLeft className="w-5 h-5" />
            Retour à la sélection
          </button>

          {/* Selected Enterprise */}
          <div className="bg-[#0047AB]/10 border border-[#0047AB]/30 rounded-xl p-4 mb-8">
            <div className="flex items-center gap-4">
              <img
                src={selectedEnterprise.image || `https://ui-avatars.com/api/?name=${selectedEnterprise.name}&background=0047AB&color=fff`}
                alt={selectedEnterprise.name}
                className="w-16 h-16 rounded-lg object-cover"
              />
              <div>
                <h3 className="text-white font-semibold text-lg">{selectedEnterprise.name}</h3>
                <p className="text-[#D4AF37] text-sm">{selectedEnterprise.category}</p>
                <p className="text-gray-400 text-sm">{selectedEnterprise.address}</p>
              </div>
            </div>
          </div>

          <h2 className="text-2xl font-bold text-white mb-6" style={{ fontFamily: 'Playfair Display, serif' }}>
            Formulaire d'inscription
          </h2>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Personal Info */}
            <div className="bg-white/5 border border-white/10 rounded-xl p-6">
              <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
                <User className="w-5 h-5 text-[#0047AB]" />
                Informations personnelles
              </h3>
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-gray-400 text-sm mb-2">Prénom *</label>
                  <input
                    type="text"
                    required
                    value={formData.first_name}
                    onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none focus:border-[#0047AB]/50"
                  />
                </div>
                <div>
                  <label className="block text-gray-400 text-sm mb-2">Nom *</label>
                  <input
                    type="text"
                    required
                    value={formData.last_name}
                    onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none focus:border-[#0047AB]/50"
                  />
                </div>
              </div>
              <div className="mt-4">
                <label className="block text-gray-400 text-sm mb-2">Téléphone *</label>
                <input
                  type="tel"
                  required
                  value={formData.phone}
                  onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                  className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none focus:border-[#0047AB]/50"
                  placeholder="+41 XX XXX XX XX"
                />
              </div>
            </div>

            {/* Account Info */}
            <div className="bg-white/5 border border-white/10 rounded-xl p-6">
              <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
                <Building2 className="w-5 h-5 text-[#0047AB]" />
                Informations de connexion
              </h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-gray-400 text-sm mb-2">Email professionnel *</label>
                  <input
                    type="email"
                    required
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none focus:border-[#0047AB]/50"
                  />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-gray-400 text-sm mb-2">Mot de passe *</label>
                    <input
                      type="password"
                      required
                      value={formData.password}
                      onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                      className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none focus:border-[#0047AB]/50"
                    />
                  </div>
                  <div>
                    <label className="block text-gray-400 text-sm mb-2">Confirmer *</label>
                    <input
                      type="password"
                      required
                      value={formData.confirmPassword}
                      onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                      className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none focus:border-[#0047AB]/50"
                    />
                  </div>
                </div>
              </div>
            </div>

            {/* Business Documents */}
            <div className="bg-white/5 border border-white/10 rounded-xl p-6">
              <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
                <FileText className="w-5 h-5 text-[#0047AB]" />
                Documents requis
              </h3>
              <div className="space-y-4">
                <div>
                  <label className="block text-gray-400 text-sm mb-2">ID du registre du commerce *</label>
                  <input
                    type="text"
                    required
                    value={formData.commerce_register_id}
                    onChange={(e) => setFormData({ ...formData, commerce_register_id: e.target.value })}
                    className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none focus:border-[#0047AB]/50"
                    placeholder="CHE-XXX.XXX.XXX"
                  />
                </div>
                <div>
                  <label className="block text-gray-400 text-sm mb-2">Pièce d'identité (PDF ou image) *</label>
                  <div className="relative">
                    <input
                      type="file"
                      accept=".pdf,.jpg,.jpeg,.png"
                      onChange={handleFileChange}
                      className="hidden"
                      id="identity-doc"
                    />
                    <label
                      htmlFor="identity-doc"
                      className="flex items-center justify-center gap-2 w-full px-4 py-4 bg-white/5 border border-dashed border-white/20 rounded-lg text-gray-400 hover:border-[#0047AB]/50 hover:text-white cursor-pointer transition-colors"
                    >
                      <Upload className="w-5 h-5" />
                      {formData.identity_document ? 'Document téléchargé ✓' : 'Cliquez pour télécharger'}
                    </label>
                  </div>
                </div>
              </div>
            </div>

            {/* Manager Selection */}
            <div className="bg-white/5 border border-white/10 rounded-xl p-6">
              <h3 className="text-white font-semibold mb-4 flex items-center gap-2">
                <Users className="w-5 h-5 text-[#0047AB]" />
                Manager référent
              </h3>
              <p className="text-gray-400 text-sm mb-4">
                Sélectionnez le manager Titelli qui vous a recommandé
              </p>
              <select
                required
                value={formData.manager_id}
                onChange={(e) => setFormData({ ...formData, manager_id: e.target.value })}
                className="w-full px-4 py-3 bg-white/5 border border-white/10 rounded-lg text-white focus:outline-none focus:border-[#0047AB]/50"
              >
                <option value="" className="bg-[#0F0F0F]">Sélectionnez un manager</option>
                {managers.map((manager, index) => (
                  <option key={index} value={manager.name} className="bg-[#0F0F0F]">
                    {manager.name} - {manager.role}
                  </option>
                ))}
              </select>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={submitting}
              className="w-full py-4 bg-[#0047AB] text-white font-semibold rounded-xl hover:bg-[#0047AB]/80 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {submitting ? (
                <>
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Envoi en cours...
                </>
              ) : (
                <>
                  Soumettre ma demande
                  <ChevronRight className="w-5 h-5" />
                </>
              )}
            </button>
          </form>
        </div>
      </div>
      </>
    );
  }

  // Step 3: Success
  return (
    <div className="min-h-screen bg-[#050505] pt-24 px-4 flex items-center justify-center">
      <div className="max-w-lg mx-auto text-center">
        <div className="w-24 h-24 bg-green-500/20 rounded-full flex items-center justify-center mx-auto mb-8">
          <CheckCircle className="w-12 h-12 text-green-500" />
        </div>
        <h1 className="text-3xl font-bold text-white mb-4" style={{ fontFamily: 'Playfair Display, serif' }}>
          Demande envoyée !
        </h1>
        <p className="text-gray-400 text-lg mb-8">
          Votre inscription est en attente de validation. Vous recevrez un email lorsque votre compte sera activé.
        </p>
        <div className="bg-white/5 border border-white/10 rounded-xl p-6 text-left mb-8">
          <h3 className="text-white font-semibold mb-3">Prochaines étapes :</h3>
          <ul className="text-gray-400 space-y-2">
            <li className="flex items-start gap-2">
              <span className="text-[#D4AF37]">1.</span>
              Notre équipe vérifie vos documents
            </li>
            <li className="flex items-start gap-2">
              <span className="text-[#D4AF37]">2.</span>
              Validation de votre identité et registre du commerce
            </li>
            <li className="flex items-start gap-2">
              <span className="text-[#D4AF37]">3.</span>
              Activation de votre compte entreprise
            </li>
            <li className="flex items-start gap-2">
              <span className="text-[#D4AF37]">4.</span>
              Notification par email de confirmation
            </li>
          </ul>
        </div>
        <button
          onClick={() => navigate('/')}
          className="px-8 py-3 bg-white/10 text-white rounded-xl hover:bg-white/20 transition-colors"
        >
          Retour à l'accueil
        </button>
      </div>
    </div>
  );
};

export default EnterpriseRegistrationPage;
