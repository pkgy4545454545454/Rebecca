import React, { useState, useEffect, useRef } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  LayoutDashboard, Building2, Package, ShoppingCart, Users, MessageSquare, 
  CreditCard, Settings, Bell, Plus, Edit, Trash2, Eye, Calendar, FileText, 
  Megaphone, ChevronRight, TrendingUp, DollarSign, Star, Gift, Briefcase,
  Home, PieChart, GraduationCap, Clock, CheckCircle, XCircle, Archive,
  FolderOpen, BookOpen, Wallet, Target, BarChart3, PlayCircle, Pause,
  UserPlus, ClipboardList, AlertTriangle, Box, ArrowUpDown, Upload, Image, X,
  Search, Rss, Newspaper, Truck, Activity, Phone, Heart, HelpCircle, Info,
  Handshake, UserCircle, Receipt, Send, Crown, Zap, Check, ChevronDown, Camera,
  Menu, Shield, Sparkles, Tag
} from 'lucide-react';
import { 
  enterpriseAPI, servicesProductsAPI, orderAPI, paymentAPI, offersAPI,
  trainingsAPI, jobsAPI, realEstateAPI, investmentsAPI, stockAPI,
  agendaAPI, teamAPI, permanentOrdersAPI, documentsAPI, financesAPI, advertisingAPI,
  uploadAPI, enterpriseApplicationsAPI, enterpriseContactsAPI, messagesAPI
} from '../services/api';
import api from '../services/api';
import { toast } from 'sonner';
// Composants extraits pour réduire la taille du fichier
import { IAClientsSection, InfluencersSection, InvitationsSection, SubscriptionsSection } from '../components/dashboard';
import CommandesTitelliSection from '../components/dashboard/CommandesTitelliSection';


const EnterpriseDashboard = () => {
  const { user, isEnterprise } = useAuth();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [activeTab, setActiveTab] = useState(() => {
    const tabParam = searchParams.get('tab');
    return tabParam || 'overview';
  });
  const [enterprise, setEnterprise] = useState(null);
  const [loading, setLoading] = useState(true);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  
  // Data states
  const [services, setServices] = useState([]);
  const [orders, setOrders] = useState([]);
  const [offers, setOffers] = useState([]);
  const [trainings, setTrainings] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [realEstate, setRealEstate] = useState([]);
  const [investments, setInvestments] = useState([]);
  const [stock, setStock] = useState({ items: [], alerts: [] });
  const [agenda, setAgenda] = useState([]);
  const [team, setTeam] = useState([]);
  const [teamOrders, setTeamOrders] = useState([]);
  const [permanentOrders, setPermanentOrders] = useState([]);
  const [documents, setDocuments] = useState([]);
  const [finances, setFinances] = useState({ transactions: [], summary: {} });
  const [advertising, setAdvertising] = useState({ campaigns: [], stats: {} });
  const [applications, setApplications] = useState({ applications: [], jobs: [], stats: {} });
  const [contacts, setContacts] = useState({ contacts: [], total: 0, type_counts: {} });

  // Modal states
  const [showModal, setShowModal] = useState(false);
  const [modalType, setModalType] = useState('');
  const [editItem, setEditItem] = useState(null);

  useEffect(() => {
    if (!isEnterprise) {
      navigate('/');
      return;
    }
    fetchAllData();
  }, [isEnterprise, navigate, user]);

  const fetchAllData = async () => {
    try {
      // Get enterprise by listing all and finding by user_id
      const enterpriseRes = await enterpriseAPI.list({});
      if (enterpriseRes.data.enterprises.length > 0) {
        const ent = enterpriseRes.data.enterprises.find(e => e.user_id === user?.id);
        if (ent) {
          setEnterprise(ent);
          const servicesRes = await servicesProductsAPI.list({ enterprise_id: ent.id });
          setServices(servicesRes.data.items);
        }
      }
      
      // Fetch all data in parallel
      const [ordersRes, offersRes, trainingsRes, jobsRes, realEstateRes, 
             investmentsRes, stockRes, agendaRes, teamRes, teamOrdersRes,
             permanentOrdersRes, documentsRes, financesRes, advertisingRes, applicationsRes, contactsRes] = await Promise.all([
        orderAPI.list().catch(() => ({ data: [] })),
        offersAPI.list().catch(() => ({ data: [] })),
        trainingsAPI.list().catch(() => ({ data: [] })),
        jobsAPI.list().catch(() => ({ data: [] })),
        realEstateAPI.list().catch(() => ({ data: [] })),
        investmentsAPI.list().catch(() => ({ data: [] })),
        stockAPI.list().catch(() => ({ data: { items: [], alerts: [] } })),
        agendaAPI.list().catch(() => ({ data: [] })),
        teamAPI.list().catch(() => ({ data: [] })),
        teamAPI.listOrders().catch(() => ({ data: [] })),
        permanentOrdersAPI.list().catch(() => ({ data: [] })),
        documentsAPI.list().catch(() => ({ data: [] })),
        financesAPI.get().catch(() => ({ data: { transactions: [], summary: {} } })),
        advertisingAPI.list().catch(() => ({ data: { campaigns: [], stats: {} } })),
        enterpriseApplicationsAPI.list().catch(() => ({ data: { applications: [], jobs: [], stats: {} } })),
        enterpriseContactsAPI.list().catch(() => ({ data: { contacts: [], total: 0, type_counts: {} } })),
      ]);

      setOrders(ordersRes.data || []);
      setOffers(offersRes.data || []);
      setTrainings(trainingsRes.data || []);
      setJobs(jobsRes.data || []);
      setRealEstate(realEstateRes.data || []);
      setInvestments(investmentsRes.data || []);
      setStock(stockRes.data || { items: [], alerts: [] });
      setAgenda(agendaRes.data || []);
      setTeam(teamRes.data || []);
      setTeamOrders(teamOrdersRes.data || []);
      setPermanentOrders(permanentOrdersRes.data || []);
      setDocuments(documentsRes.data || []);
      setFinances(financesRes.data || { transactions: [], summary: {} });
      setAdvertising(advertisingRes.data || { campaigns: [], stats: {} });
      setApplications(applicationsRes.data || { applications: [], jobs: [], stats: {} });
      setContacts(contactsRes.data || { contacts: [], total: 0, type_counts: {} });
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  // Menu restructuré selon les besoins
  const menuSections = [
    {
      title: 'Principal',
      gradient: 'from-blue-500/20 to-blue-600/10',
      borderColor: 'border-blue-500/30',
      items: [
        { id: 'overview', label: 'Accueil', icon: LayoutDashboard },
        { id: 'profile', label: 'Profil entreprise', icon: Building2 },
        { id: 'media', label: 'Galerie média', icon: Image },
        { id: 'feed', label: 'Mon fil d\'actualité', icon: Rss },
        { id: 'business_feed', label: 'Mon feed entreprises', icon: Newspaper },
      ]
    },
    {
      title: 'Commercial',
      gradient: 'from-green-500/20 to-green-600/10',
      borderColor: 'border-green-500/30',
      items: [
        { id: 'services', label: 'Services & Produits', icon: Package },
        { id: 'orders', label: 'Mes commandes', icon: ShoppingCart, notifKey: 'orders' },
        { id: 'deliveries', label: 'Mes livraisons', icon: Truck },
        { id: 'activities', label: 'Mes activités', icon: Activity },
        { id: 'stock', label: 'Gestion des stocks', icon: Box },
        { id: 'permanent', label: 'Commandes permanentes', icon: ClipboardList },
      ]
    },
    {
      title: 'Marketing',
      gradient: 'from-purple-500/20 to-purple-600/10',
      borderColor: 'border-purple-500/30',
      items: [
        { id: 'offers', label: 'Offres & Promotions', icon: Gift },
        { id: 'advertising', label: 'Mes publicités', icon: Megaphone },
        { id: 'commercial_gesture', label: 'Geste commercial', icon: Heart },
        { id: 'tendances', label: 'Tendances actuelles', icon: TrendingUp },
        { id: 'guests', label: 'Guests du moment', icon: Star },
      ]
    },
    {
      title: 'IA & Marketing',
      gradient: 'from-cyan-500/20 to-cyan-600/10',
      borderColor: 'border-cyan-500/30',
      items: [
        { id: 'ia_clients', label: 'IA Ciblage clients', icon: Target },
        { id: 'influencers', label: 'Influenceurs', icon: Users },
        { id: 'invitations', label: 'Invitations clients', icon: Send },
        { id: 'media_pub', label: 'Créer une Pub', icon: Sparkles, isExternal: true, externalUrl: '/media-pub', color: 'text-purple-400' },
        { id: 'commandes-titelli', label: 'Commandes Titelli', icon: Package, notifKey: 'pub_orders' },
      ]
    },
    {
      title: 'Ressources Humaines',
      gradient: 'from-orange-500/20 to-orange-600/10',
      borderColor: 'border-orange-500/30',
      items: [
        { id: 'team', label: 'Mon personnel', icon: Users },
        { id: 'jobs', label: 'Emplois & Stages', icon: Briefcase },
        { id: 'applications', label: 'Postulations', icon: ClipboardList, notifKey: 'applications' },
        { id: 'trainings', label: 'Formations', icon: GraduationCap },
      ]
    },
    {
      title: 'Finances & Investissements',
      gradient: 'from-yellow-500/20 to-yellow-600/10',
      borderColor: 'border-yellow-500/30',
      items: [
        { id: 'finances', label: 'Mes finances', icon: Wallet },
        { id: 'cards', label: 'Mes cartes', icon: CreditCard },
        { id: 'investments', label: 'Mes investissements', icon: PieChart },
        { id: 'donations', label: 'Donations', icon: Heart },
      ]
    },
    {
      title: 'Actualités & Formation',
      gradient: 'from-indigo-500/20 to-indigo-600/10',
      borderColor: 'border-indigo-500/30',
      items: [
        { id: 'business_news', label: 'Business News', icon: Newspaper },
        { id: 'development', label: 'Formations métier', icon: BookOpen },
      ]
    },
    {
      title: 'Communication',
      gradient: 'from-pink-500/20 to-pink-600/10',
      borderColor: 'border-pink-500/30',
      items: [
        { id: 'messages', label: 'Messagerie', icon: MessageSquare, notifKey: 'messages' },
        { id: 'contacts', label: 'Contacts', icon: Phone },
        { id: 'salonpro_planning', label: 'Voir Planning', icon: Calendar, isExternal: true, color: 'text-green-400' },
      ]
    },
    {
      title: 'Documents & Paramètres',
      gradient: 'from-teal-500/20 to-teal-600/10',
      borderColor: 'border-teal-500/30',
      items: [
        { id: 'subscriptions', label: 'Abonnements', icon: Crown },
        { id: 'documents', label: 'Documents', icon: FolderOpen },
        { id: 'realestate', label: 'Immobilier', icon: Home },
        { id: 'settings', label: 'Paramètres', icon: Settings },
      ]
    },
    {
      title: 'Aide & Informations',
      gradient: 'from-slate-500/20 to-slate-600/10',
      borderColor: 'border-slate-500/30',
      items: [
        { id: 'support', label: 'Service client', icon: HelpCircle },
        { id: 'partners', label: 'Partenaires', icon: Handshake },
        { id: 'about', label: 'À propos', icon: Info },
      ]
    },
  ];

  // Admin emails that have access to admin panel
  const ADMIN_EMAILS = ['admin@titelli.com', 'spa.luxury@titelli.com'];
  const isAdmin = ADMIN_EMAILS.includes(user?.email);

  // Notification counts for menu items
  const getNotificationCount = (key) => {
    switch(key) {
      case 'orders':
        return orders.filter(o => o.status === 'pending').length;
      case 'applications':
        return (applications?.applications || []).filter(a => a.status === 'pending').length;
      case 'messages':
        return 0; // Can be connected to unread messages
      default:
        return 0;
    }
  };

  // Flatten menu items for easy lookup
  const menuItems = menuSections.flatMap(section => section.items);

  // Stats cards with colors matching their section categories
  const stats = [
    { 
      label: 'Vues ce mois', 
      value: '1,234', 
      icon: Eye, 
      trend: '+12%', 
      gradient: 'from-blue-500/20 to-blue-600/10',
      borderColor: 'border-blue-500/30',
      iconBg: 'bg-blue-500/20',
      iconColor: 'text-blue-400',
      trendColor: 'text-blue-400'
    },
    { 
      label: 'Commandes', 
      value: orders.length.toString(), 
      icon: ShoppingCart, 
      trend: orders.filter(o => o.status === 'pending').length > 0 ? `${orders.filter(o => o.status === 'pending').length} en attente` : '+5%',
      notifCount: orders.filter(o => o.status === 'pending').length,
      gradient: 'from-green-500/20 to-green-600/10',
      borderColor: 'border-green-500/30',
      iconBg: 'bg-green-500/20',
      iconColor: 'text-green-400',
      trendColor: 'text-green-400'
    },
    { 
      label: 'Revenus', 
      value: `${finances.summary.total_income?.toFixed(0) || 0} CHF`, 
      icon: DollarSign, 
      trend: '+18%',
      gradient: 'from-yellow-500/20 to-yellow-600/10',
      borderColor: 'border-yellow-500/30',
      iconBg: 'bg-yellow-500/20',
      iconColor: 'text-yellow-400',
      trendColor: 'text-yellow-400'
    },
    { 
      label: 'Note moyenne', 
      value: enterprise?.rating?.toFixed(1) || '0.0', 
      icon: Star, 
      trend: '+0.2',
      gradient: 'from-purple-500/20 to-purple-600/10',
      borderColor: 'border-purple-500/30',
      iconBg: 'bg-purple-500/20',
      iconColor: 'text-purple-400',
      trendColor: 'text-purple-400'
    },
  ];

  const openModal = (type, item = null) => {
    setModalType(type);
    setEditItem(item);
    setShowModal(true);
  };

  const handleSubscribe = async (plan) => {
    try {
      const response = await paymentAPI.createCheckout(plan);
      window.location.href = response.data.url;
    } catch (error) {
      toast.error('Erreur lors de la création du paiement');
    }
  };

  // Generic delete handler
  const handleDelete = async (type, id) => {
    if (!window.confirm('Êtes-vous sûr de vouloir supprimer cet élément ?')) return;
    
    try {
      switch(type) {
        case 'offer': await offersAPI.delete(id); setOffers(offers.filter(o => o.id !== id)); break;
        case 'training': await trainingsAPI.delete(id); setTrainings(trainings.filter(t => t.id !== id)); break;
        case 'job': await jobsAPI.delete(id); setJobs(jobs.filter(j => j.id !== id)); break;
        case 'realestate': await realEstateAPI.delete(id); setRealEstate(realEstate.filter(r => r.id !== id)); break;
        case 'investment': await investmentsAPI.delete(id); setInvestments(investments.filter(i => i.id !== id)); break;
        case 'team': await teamAPI.delete(id); setTeam(team.filter(t => t.id !== id)); break;
        case 'permanent': await permanentOrdersAPI.delete(id); setPermanentOrders(permanentOrders.filter(p => p.id !== id)); break;
        case 'document': await documentsAPI.delete(id); setDocuments(documents.filter(d => d.id !== id)); break;
        case 'advertising': await advertisingAPI.delete(id); fetchAllData(); break;
        case 'service': await servicesProductsAPI.delete(id); setServices(services.filter(s => s.id !== id)); break;
        default: break;
      }
      toast.success('Supprimé avec succès');
    } catch (error) {
      toast.error('Erreur lors de la suppression');
    }
  };

  // Handle SalonPro Planning redirect with auto-login
  const handleSalonProRedirect = async () => {
    try {
      toast.loading('Connexion à SalonPro en cours...', { id: 'salonpro' });
      const token = localStorage.getItem('titelli_token');
      const response = await api.get('/auth/salonpro-token', {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.data?.redirect_url) {
        toast.success('Redirection vers SalonPro...', { id: 'salonpro' });
        // Open in new tab for better UX
        window.open(response.data.redirect_url, '_blank');
      } else {
        throw new Error('URL de redirection non disponible');
      }
    } catch (error) {
      console.error('SalonPro redirect error:', error);
      toast.error('Erreur de connexion à SalonPro', { id: 'salonpro' });
    }
  };

  // Handle menu item click - supports both internal tabs and external redirects
  const handleMenuItemClick = (item) => {
    if (item.isExternal && item.id === 'salonpro_planning') {
      handleSalonProRedirect();
    } else if (item.isExternal && item.externalUrl) {
      // Navigate to external URL (like media-pub)
      navigate(item.externalUrl);
    } else {
      setActiveTab(item.id);
    }
    // Close mobile menu after click
    setMobileMenuOpen(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#050505] pt-24 flex items-center justify-center">
        <div className="w-16 h-16 border-4 border-[#0047AB] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#050505] pt-20" data-testid="enterprise-dashboard">
      {/* Mobile Menu Button */}
      <button 
        onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
        className="lg:hidden fixed top-24 left-4 z-[60] w-12 h-12 bg-[#D4AF37] rounded-xl flex items-center justify-center shadow-lg border border-white/10"
        data-testid="mobile-menu-toggle"
      >
        {mobileMenuOpen ? <X className="w-5 h-5 text-black" /> : <Menu className="w-5 h-5 text-black" />}
      </button>

      {/* Mobile Menu Overlay */}
      {mobileMenuOpen && (
        <div 
          className="lg:hidden fixed inset-0 bg-black/90 z-[45]"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}

      <div className="flex">
        {/* Sidebar - Mobile: Slide-in panel, Desktop: Fixed sidebar */}
      <aside 
        className={`
          fixed top-0 bottom-0 z-[50]
          bg-[#111111] border-r border-white/10 
          overflow-y-auto overflow-x-hidden 
          transition-all duration-300 ease-in-out
          dashboard-sidebar pt-4
          w-[280px] sm:w-[300px] lg:w-72 lg:top-20
          ${mobileMenuOpen ? 'left-0' : '-left-[300px] lg:left-0'}
        `}
        style={{ backgroundColor: '#111111' }}
      >
        <div className="p-4 hide-scrollbar overflow-x-hidden pb-24">
            {/* Enterprise Header */}
            <div className="flex items-center gap-3 mb-4 pb-4 border-b border-white/10">
              <div className="w-10 h-10 rounded-xl bg-[#0047AB]/20 flex items-center justify-center overflow-hidden flex-shrink-0">
                {enterprise?.logo ? (
                  <img src={enterprise.logo} alt="" className="w-full h-full object-cover" />
                ) : (
                  <Building2 className="w-5 h-5 text-[#0047AB]" />
                )}
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-semibold text-white text-sm truncate">
                  {enterprise?.business_name || 'Mon Entreprise'}
                </p>
                <p className="text-xs text-gray-500">Espace entreprise</p>
              </div>
            </div>

            {/* Search Bar */}
            <div className="relative mb-4">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
              <input 
                type="text" 
                placeholder="Rechercher..." 
                className="w-full pl-9 pr-3 py-2 bg-white/5 border border-white/10 rounded-lg text-sm text-white placeholder:text-gray-500 focus:outline-none focus:border-[#0047AB]/50"
              />
            </div>

            {/* Admin Panel Button - Only for admins */}
            {isAdmin && (
              <Link
                to="/admin"
                className="flex items-center gap-3 px-4 py-3 mb-4 rounded-xl bg-gradient-to-r from-red-600/20 to-orange-600/20 border border-red-500/30 text-white hover:from-red-600/30 hover:to-orange-600/30 transition-all"
              >
                <Shield className="w-5 h-5 text-red-400" />
                <div className="flex-1">
                  <span className="font-semibold">Panel Admin</span>
                  <p className="text-xs text-gray-400">Comptabilité & Gestion</p>
                </div>
                <ChevronRight className="w-4 h-4 text-gray-400" />
              </Link>
            )}

            {/* Menu Sections */}
            <nav className="space-y-3 overflow-hidden">
              {menuSections.map((section) => (
                <div key={section.title} className={`rounded-xl p-3 bg-gradient-to-br ${section.gradient} border ${section.borderColor} menu-section`}>
                  <p className="text-xs text-gray-300 uppercase tracking-wider px-2 mb-2 truncate">{section.title}</p>
                  <div className="space-y-0.5">
                    {section.items.map((item) => {
                      const notifCount = item.notifKey ? getNotificationCount(item.notifKey) : 0;
                      const hasNotif = notifCount > 0;
                      const stockAlerts = item.id === 'stock' ? stock.alerts.length : 0;
                      
                      return (
                        <button
                          key={item.id}
                          onClick={() => handleMenuItemClick(item)}
                          data-testid={`menu-item-${item.id}`}
                          className={`w-full flex items-center justify-between gap-2 px-3 py-2 rounded-lg text-sm transition-all overflow-hidden ${
                            activeTab === item.id && !item.isExternal
                              ? 'bg-white/20 text-white shadow-lg'
                              : item.color || 'text-gray-300 hover:bg-white/10 hover:text-white'
                          }`}
                          style={hasNotif || stockAlerts > 0 ? {
                            boxShadow: '0 0 0 2px rgba(34, 197, 94, 0.5)',
                            animation: 'pulse-green 2s infinite'
                          } : {}}
                        >
                          <div className="flex items-center gap-2 min-w-0 flex-1">
                            <item.icon className={`w-4 h-4 flex-shrink-0 ${item.color || ''}`} />
                            <span className={`truncate text-left ${item.color || ''}`}>{item.label}</span>
                            {item.isExternal && (
                              <ChevronRight className={`w-3 h-3 flex-shrink-0 ${item.color || 'text-gray-400'}`} />
                            )}
                          </div>
                          {(hasNotif || stockAlerts > 0) && (
                            <span className="flex items-center justify-center min-w-[20px] h-5 px-1.5 bg-green-500 text-white text-xs font-bold rounded-full animate-bounce flex-shrink-0">
                              {notifCount || stockAlerts}
                            </span>
                          )}
                        </button>
                      );
                    })}
                  </div>
                </div>
              ))}
            </nav>
            
            {/* Close button at bottom of mobile menu */}
            <div className="lg:hidden mt-6 pt-4 border-t border-white/10">
              <button
                onClick={() => setMobileMenuOpen(false)}
                className="w-full py-3 bg-white/5 rounded-xl text-gray-400 hover:bg-white/10 hover:text-white transition-colors flex items-center justify-center gap-2"
              >
                <X className="w-4 h-4" />
                Fermer le menu
              </button>
            </div>
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 lg:ml-72 p-4 md:p-8 pt-6 lg:pt-4">
          {/* Mobile Quick Access - Optional tabs for quick navigation */}
          <div className="lg:hidden mb-6 overflow-x-auto">
            <div className="flex gap-2 pb-2">
              {menuItems.slice(0, 6).map((item) => (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm whitespace-nowrap ${
                    activeTab === item.id
                      ? 'bg-[#D4AF37] text-black'
                      : 'bg-white/5 text-gray-400'
                  }`}
                >
                  <item.icon className="w-4 h-4" />
                  {item.label}
                </button>
              ))}
            </div>
          </div>

          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <div className="space-y-6">
              <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
                Tableau de bord
              </h1>

              {!enterprise && (
                <div className="card-service rounded-xl p-6 border-[#D4AF37] text-center">
                  <Building2 className="w-12 h-12 text-[#D4AF37] mx-auto mb-4" />
                  <h2 className="text-xl font-semibold text-white mb-2">Créez votre profil entreprise</h2>
                  <p className="text-gray-400 mb-4">Pour accéder à toutes les fonctionnalités</p>
                  <button onClick={() => setActiveTab('profile')} className="btn-primary">
                    Créer mon profil
                  </button>
                </div>
              )}

              {/* Stats Grid */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {stats.map((stat, index) => (
                  <div 
                    key={index} 
                    className={`rounded-xl p-4 bg-gradient-to-br ${stat.gradient} border ${stat.borderColor} relative overflow-hidden`}
                    style={stat.notifCount > 0 ? {
                      animation: 'pulse-green 2s infinite'
                    } : {}}
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className={`w-10 h-10 rounded-lg ${stat.iconBg} flex items-center justify-center`}>
                        <stat.icon className={`w-5 h-5 ${stat.iconColor}`} />
                      </div>
                      <span className={`text-xs font-medium ${stat.trendColor}`}>{stat.trend}</span>
                    </div>
                    <p className="text-2xl font-bold text-white">{stat.value}</p>
                    <p className="text-xs text-gray-400">{stat.label}</p>
                    {stat.notifCount > 0 && (
                      <span className="absolute top-2 right-2 w-6 h-6 bg-green-500 text-white text-xs font-bold rounded-full flex items-center justify-center animate-bounce">
                        {stat.notifCount}
                      </span>
                    )}
                  </div>
                ))}
              </div>

              {/* Alerts */}
              {stock.alerts.length > 0 && (
                <div className="card-service rounded-xl p-4 border-red-500/50">
                  <div className="flex items-center gap-2 text-red-400 mb-2">
                    <AlertTriangle className="w-5 h-5" />
                    <span className="font-semibold">Alertes Stock</span>
                  </div>
                  <p className="text-gray-400 text-sm">{stock.alerts.length} produit(s) en stock faible</p>
                </div>
              )}

              {/* Quick Actions */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <button onClick={() => { setActiveTab('services'); openModal('service'); }} className="card-service rounded-xl p-4 hover:border-[#0047AB]/50 transition-colors text-left">
                  <Package className="w-8 h-8 text-[#0047AB] mb-2" />
                  <p className="text-white font-medium">Ajouter service</p>
                </button>
                <button onClick={() => { setActiveTab('offers'); openModal('offer'); }} className="card-service rounded-xl p-4 hover:border-[#D4AF37]/50 transition-colors text-left">
                  <Gift className="w-8 h-8 text-[#D4AF37] mb-2" />
                  <p className="text-white font-medium">Créer offre</p>
                </button>
                <button onClick={() => { setActiveTab('jobs'); openModal('job'); }} className="card-service rounded-xl p-4 hover:border-green-500/50 transition-colors text-left">
                  <Briefcase className="w-8 h-8 text-green-500 mb-2" />
                  <p className="text-white font-medium">Publier emploi</p>
                </button>
                <button onClick={() => setActiveTab('agenda')} className="card-service rounded-xl p-4 hover:border-purple-500/50 transition-colors text-left">
                  <Calendar className="w-8 h-8 text-purple-500 mb-2" />
                  <p className="text-white font-medium">Voir agenda</p>
                </button>
              </div>

              {/* Recent Orders */}
              <div className="card-service rounded-xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold text-white">Dernières commandes</h2>
                  <button onClick={() => setActiveTab('orders')} className="text-[#0047AB] text-sm hover:underline">
                    Voir tout
                  </button>
                </div>
                {orders.length > 0 ? (
                  <div className="space-y-3">
                    {orders.slice(0, 5).map((order) => (
                      <div key={order.id} className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                        <div>
                          <p className="text-white font-medium">#{order.id.slice(0, 8)}</p>
                          <p className="text-xs text-gray-400">{order.items?.length || 0} article(s)</p>
                        </div>
                        <div className="text-right">
                          <p className="text-[#D4AF37] font-semibold">{order.total?.toFixed(2)} CHF</p>
                          <span className={`text-xs px-2 py-0.5 rounded-full ${
                            order.status === 'completed' ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'
                          }`}>
                            {order.status === 'completed' ? 'Terminée' : 'En cours'}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-400 text-center py-8">Aucune commande</p>
                )}
              </div>
            </div>
          )}

          {/* Profile Tab */}
          {activeTab === 'profile' && (
            <ProfileSection enterprise={enterprise} onUpdate={() => fetchAllData()} />
          )}

          {/* Media Gallery Tab */}
          {activeTab === 'media' && (
            <MediaGallerySection enterprise={enterprise} onUpdate={() => fetchAllData()} />
          )}

          {/* Services Tab */}
          {activeTab === 'services' && (
            <ServicesSection services={services} onAdd={() => openModal('service')} onDelete={(id) => handleDelete('service', id)} onRefresh={fetchAllData} />
          )}

          {/* Orders Tab */}
          {activeTab === 'orders' && (
            <OrdersSection orders={orders} onRefresh={fetchAllData} />
          )}

          {/* Offers Tab */}
          {activeTab === 'offers' && (
            <GenericSection
              title="Offres & Promotions"
              icon={Gift}
              items={offers}
              onAdd={() => openModal('offer')}
              onDelete={(id) => handleDelete('offer', id)}
              emptyText="Aucune offre créée"
              renderItem={(item) => (
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-white font-medium">{item.title}</p>
                    <p className="text-sm text-gray-400">{item.discount_value}% de réduction</p>
                  </div>
                  <span className={`px-2 py-1 rounded-full text-xs ${item.is_active ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'}`}>
                    {item.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
              )}
            />
          )}

          {/* Trainings Tab */}
          {activeTab === 'trainings' && (
            <GenericSection
              title="Formations"
              icon={GraduationCap}
              items={trainings}
              onAdd={() => openModal('training')}
              onDelete={(id) => handleDelete('training', id)}
              emptyText="Aucune formation proposée"
              renderItem={(item) => (
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-white font-medium">{item.title}</p>
                    <p className="text-sm text-gray-400">{item.duration} • {item.is_online ? 'En ligne' : 'Présentiel'}</p>
                  </div>
                  <p className="text-[#D4AF37] font-semibold">{item.price} CHF</p>
                </div>
              )}
            />
          )}

          {/* Jobs Tab */}
          {activeTab === 'jobs' && (
            <GenericSection
              title="Offres d'emploi"
              icon={Briefcase}
              items={jobs}
              onAdd={() => openModal('job')}
              onDelete={(id) => handleDelete('job', id)}
              emptyText="Aucune offre d'emploi"
              renderItem={(item) => (
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-white font-medium">{item.title}</p>
                    <p className="text-sm text-gray-400">{item.location} • {item.job_type}</p>
                  </div>
                  {item.salary_min && <p className="text-green-400">{item.salary_min} - {item.salary_max} CHF</p>}
                </div>
              )}
            />
          )}

          {/* Applications/Postulations Tab */}
          {activeTab === 'applications' && (
            <ApplicationsSection 
              applications={applications} 
              onRefresh={fetchAllData} 
            />
          )}

          {/* Real Estate Tab */}
          {activeTab === 'realestate' && (
            <GenericSection
              title="Immobilier"
              icon={Home}
              items={realEstate}
              onAdd={() => openModal('realestate')}
              onDelete={(id) => handleDelete('realestate', id)}
              emptyText="Aucun bien immobilier"
              renderItem={(item) => (
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-white font-medium">{item.title}</p>
                    <p className="text-sm text-gray-400">{item.surface} m² • {item.city}</p>
                  </div>
                  <p className="text-[#D4AF37] font-semibold">{item.price} CHF/{item.price_period}</p>
                </div>
              )}
            />
          )}

          {/* Investments Tab */}
          {activeTab === 'investments' && (
            <GenericSection
              title="Investissements"
              icon={PieChart}
              items={investments}
              onAdd={() => openModal('investment')}
              onDelete={(id) => handleDelete('investment', id)}
              emptyText="Aucune opportunité d'investissement"
              renderItem={(item) => (
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-white font-medium">{item.title}</p>
                    <p className="text-sm text-gray-400">Min: {item.min_investment} CHF • {item.expected_return}% retour</p>
                  </div>
                  <span className={`px-2 py-1 rounded-full text-xs ${
                    item.risk_level === 'low' ? 'bg-green-500/20 text-green-400' :
                    item.risk_level === 'medium' ? 'bg-yellow-500/20 text-yellow-400' : 'bg-red-500/20 text-red-400'
                  }`}>
                    Risque {item.risk_level}
                  </span>
                </div>
              )}
            />
          )}

          {/* Stock Tab */}
          {activeTab === 'stock' && (
            <StockSection stock={stock} services={services} onRefresh={fetchAllData} />
          )}

          {/* Agenda Tab */}
          {activeTab === 'agenda' && (
            <AgendaSection agenda={agenda} onRefresh={fetchAllData} />
          )}

          {/* Team Tab */}
          {activeTab === 'team' && (
            <TeamSection team={team} teamOrders={teamOrders} onDelete={(id) => handleDelete('team', id)} onRefresh={fetchAllData} />
          )}

          {/* Permanent Orders Tab */}
          {activeTab === 'permanent' && (
            <GenericSection
              title="Commandes permanentes"
              icon={ClipboardList}
              items={permanentOrders}
              onAdd={() => openModal('permanent')}
              onDelete={(id) => handleDelete('permanent', id)}
              emptyText="Aucune commande permanente"
              renderItem={(item) => (
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-white font-medium">{item.client_name}</p>
                    <p className="text-sm text-gray-400">{item.frequency} • {item.items?.length || 0} article(s)</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <p className="text-[#D4AF37] font-semibold">{item.total} CHF</p>
                    <span className={`px-2 py-1 rounded-full text-xs ${item.is_active ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'}`}>
                      {item.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                </div>
              )}
            />
          )}

          {/* Documents Tab */}
          {activeTab === 'documents' && (
            <DocumentsSection documents={documents} onDelete={(id) => handleDelete('document', id)} onRefresh={fetchAllData} />
          )}

          {/* Development Tab */}
          {activeTab === 'development' && (
            <DevelopmentSection />
          )}

          {/* Finances Tab */}
          {activeTab === 'finances' && (
            <FinancesSection finances={finances} onRefresh={fetchAllData} />
          )}

          {/* Advertising Tab */}
          {activeTab === 'advertising' && (
            <AdvertisingSection advertising={advertising} onDelete={(id) => handleDelete('advertising', id)} onRefresh={fetchAllData} />
          )}

          {/* Settings Tab */}
          {activeTab === 'settings' && (
            <div className="space-y-6">
              <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
                Paramètres
              </h1>
              
              <div className="card-service rounded-xl p-6">
                <h2 className="text-lg font-semibold text-white mb-4">Abonnement</h2>
                <p className="text-gray-400 mb-4">Gérez votre abonnement et vos options</p>
                <button 
                  onClick={() => setActiveTab('subscriptions')} 
                  className="btn-primary flex items-center gap-2"
                >
                  <Crown className="w-4 h-4" />
                  Gérer mon abonnement
                </button>
              </div>

              <div className="card-service rounded-xl p-6">
                <h2 className="text-lg font-semibold text-white mb-4">Notifications</h2>
                <div className="space-y-3">
                  <label className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                    <span className="text-gray-300">Notifications par email</span>
                    <input type="checkbox" defaultChecked className="w-5 h-5 accent-[#0047AB]" />
                  </label>
                  <label className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                    <span className="text-gray-300">Notifications push</span>
                    <input type="checkbox" defaultChecked className="w-5 h-5 accent-[#0047AB]" />
                  </label>
                  <label className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                    <span className="text-gray-300">Résumé hebdomadaire</span>
                    <input type="checkbox" className="w-5 h-5 accent-[#0047AB]" />
                  </label>
                </div>
              </div>

              <div className="card-service rounded-xl p-6">
                <h2 className="text-lg font-semibold text-white mb-4">Sécurité</h2>
                <div className="space-y-4">
                  <button className="w-full p-3 bg-white/5 rounded-lg text-left hover:bg-white/10 transition-colors">
                    <p className="text-white font-medium">Changer le mot de passe</p>
                    <p className="text-sm text-gray-400">Sécurisez votre compte</p>
                  </button>
                  <button className="w-full p-3 bg-white/5 rounded-lg text-left hover:bg-white/10 transition-colors">
                    <p className="text-white font-medium">Authentification à deux facteurs</p>
                    <p className="text-sm text-gray-400">Ajouter une couche de sécurité</p>
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Fil d'actualité - Avis clients */}
          {activeTab === 'feed' && (
            <div className="space-y-6">
              <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
                Mon fil d'actualité
              </h1>
              <p className="text-gray-400">Les expériences partagées par vos clients</p>
              <div className="card-service rounded-xl p-8 text-center">
                <Rss className="w-12 h-12 text-gray-500 mx-auto mb-4" />
                <p className="text-gray-400 mb-2">Aucune publication récente</p>
                <p className="text-sm text-gray-500">Les avis et partages de vos clients apparaîtront ici</p>
              </div>
            </div>
          )}

          {/* Feed entreprises */}
          {activeTab === 'business_feed' && (
            <div className="space-y-6">
              <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
                Mon feed entreprises
              </h1>
              <p className="text-gray-400">Actualités et partages des autres entreprises</p>
              <div className="card-service rounded-xl p-8 text-center">
                <Newspaper className="w-12 h-12 text-gray-500 mx-auto mb-4" />
                <p className="text-gray-400 mb-2">Aucune publication</p>
                <p className="text-sm text-gray-500">Suivez d'autres entreprises pour voir leur actualité</p>
              </div>
            </div>
          )}

          {/* Livraisons */}
          {activeTab === 'deliveries' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
                  Mes livraisons
                </h1>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
                <div className="card-service rounded-xl p-4 text-center">
                  <p className="text-2xl font-bold text-white">{orders.filter(o => o.status === 'pending').length}</p>
                  <p className="text-sm text-gray-400">En attente</p>
                </div>
                <div className="card-service rounded-xl p-4 text-center">
                  <p className="text-2xl font-bold text-orange-500">{orders.filter(o => o.status === 'confirmed').length}</p>
                  <p className="text-sm text-gray-400">En cours</p>
                </div>
                <div className="card-service rounded-xl p-4 text-center">
                  <p className="text-2xl font-bold text-green-500">{orders.filter(o => o.status === 'completed').length}</p>
                  <p className="text-sm text-gray-400">Livrées</p>
                </div>
                <div className="card-service rounded-xl p-4 text-center">
                  <p className="text-2xl font-bold text-red-500">{orders.filter(o => o.status === 'cancelled').length}</p>
                  <p className="text-sm text-gray-400">Annulées</p>
                </div>
              </div>
              {orders.filter(o => o.items?.some(i => i.is_delivery)).length === 0 ? (
                <div className="card-service rounded-xl p-8 text-center">
                  <Truck className="w-12 h-12 text-gray-500 mx-auto mb-4" />
                  <p className="text-gray-400">Aucune livraison en cours</p>
                </div>
              ) : (
                <div className="card-service rounded-xl divide-y divide-white/5">
                  {orders.filter(o => o.items?.some(i => i.is_delivery)).map((order) => (
                    <div key={order.id} className="p-4 flex items-center justify-between">
                      <div>
                        <p className="text-white font-medium">#{order.id.slice(0, 8)}</p>
                        <p className="text-sm text-gray-400">{order.delivery_address || 'Adresse non spécifiée'}</p>
                      </div>
                      <span className={`px-3 py-1 rounded-full text-xs ${order.status === 'completed' ? 'bg-green-500/20 text-green-400' : 'bg-orange-500/20 text-orange-400'}`}>
                        {order.status === 'pending' ? 'En attente' : order.status === 'confirmed' ? 'En cours' : order.status === 'completed' ? 'Livré' : 'Annulé'}
                      </span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* Activités */}
          {activeTab === 'activities' && (
            <div className="space-y-6">
              <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
                Mes activités
              </h1>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
                <div className="card-service rounded-xl p-4">
                  <Activity className="w-6 h-6 text-green-500 mb-2" />
                  <p className="text-2xl font-bold text-white">{orders.filter(o => o.status === 'completed').length}</p>
                  <p className="text-sm text-gray-400">Ventes terminées</p>
                </div>
                <div className="card-service rounded-xl p-4">
                  <Clock className="w-6 h-6 text-orange-500 mb-2" />
                  <p className="text-2xl font-bold text-white">{orders.filter(o => o.status === 'confirmed').length}</p>
                  <p className="text-sm text-gray-400">En cours</p>
                </div>
                <div className="card-service rounded-xl p-4">
                  <AlertTriangle className="w-6 h-6 text-yellow-500 mb-2" />
                  <p className="text-2xl font-bold text-white">{orders.filter(o => o.status === 'pending').length}</p>
                  <p className="text-sm text-gray-400">En attente</p>
                </div>
                <div className="card-service rounded-xl p-4">
                  <ClipboardList className="w-6 h-6 text-[#0047AB] mb-2" />
                  <p className="text-2xl font-bold text-white">{permanentOrders.length}</p>
                  <p className="text-sm text-gray-400">Permanentes</p>
                </div>
              </div>
              <div className="card-service rounded-xl p-6">
                <h2 className="text-lg font-semibold text-white mb-4">Activité récente</h2>
                {orders.length > 0 ? (
                  <div className="space-y-3">
                    {orders.slice(0, 10).map((order) => (
                      <div key={order.id} className="flex items-center justify-between py-2 border-b border-white/5 last:border-0">
                        <div className="flex items-center gap-3">
                          <div className={`w-2 h-2 rounded-full ${order.status === 'completed' ? 'bg-green-500' : order.status === 'pending' ? 'bg-yellow-500' : 'bg-orange-500'}`} />
                          <div>
                            <p className="text-white text-sm">{order.items?.length || 0} article(s) - {order.total?.toFixed(2)} CHF</p>
                            <p className="text-xs text-gray-500">{new Date(order.created_at).toLocaleDateString('fr-FR')}</p>
                          </div>
                        </div>
                        <span className="text-sm text-gray-400 capitalize">{order.status}</span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-400 text-center py-4">Aucune activité récente</p>
                )}
              </div>
            </div>
          )}

          {/* Geste commercial */}
          {activeTab === 'commercial_gesture' && (
            <div className="space-y-6">
              <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
                Geste commercial
              </h1>
              <p className="text-gray-400">Offrez un geste commercial à vos nouveaux clients pour les fidéliser</p>
              <div className="card-service rounded-xl p-6">
                <h2 className="text-lg font-semibold text-white mb-4">Créer une offre de bienvenue</h2>
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm text-gray-400 mb-1">Type d'offre</label>
                    <select className="input-dark w-full">
                      <option>Réduction en pourcentage</option>
                      <option>Montant fixe offert</option>
                      <option>Service gratuit</option>
                      <option>Produit offert</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm text-gray-400 mb-1">Valeur</label>
                    <input type="number" placeholder="Ex: 10" className="input-dark w-full" />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-400 mb-1">Conditions</label>
                    <textarea placeholder="Ex: Valable pour la première commande" className="input-dark w-full" rows={3} />
                  </div>
                  <button className="btn-primary">
                    <Gift className="w-4 h-4 mr-2" />
                    Créer le geste commercial
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Tendances */}
          {activeTab === 'tendances' && (
            <div className="space-y-6">
              <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
                Tendances actuelles
              </h1>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {['Bien-être', 'Éco-responsable', 'Digital', 'Local', 'Premium'].map((trend, i) => (
                  <div key={i} className="card-service rounded-xl p-6">
                    <TrendingUp className="w-8 h-8 text-[#0047AB] mb-3" />
                    <h3 className="text-white font-semibold mb-2">{trend}</h3>
                    <p className="text-sm text-gray-400">Tendance forte dans votre secteur</p>
                    <div className="mt-4 flex items-center gap-2">
                      <div className="flex-1 h-2 bg-white/10 rounded-full overflow-hidden">
                        <div className="h-full bg-[#0047AB]" style={{ width: `${70 + i * 5}%` }} />
                      </div>
                      <span className="text-sm text-[#0047AB]">{70 + i * 5}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Guests du moment */}
          {activeTab === 'guests' && (
            <div className="space-y-6">
              <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
                Guests du moment
              </h1>
              <p className="text-gray-400">Les entreprises et personnalités mises en avant ce mois-ci</p>
              <div className="card-service rounded-xl p-8 text-center">
                <Star className="w-12 h-12 text-[#D4AF37] mx-auto mb-4" />
                <p className="text-gray-400 mb-2">Bientôt disponible</p>
                <p className="text-sm text-gray-500">Découvrez les guests du moment prochainement</p>
              </div>
            </div>
          )}

          {/* IA Ciblage Clients */}
          {activeTab === 'ia_clients' && (
            <IAClientsSection />
          )}

          {/* Influenceurs */}
          {activeTab === 'influencers' && (
            <InfluencersSection />
          )}

          {/* Invitations Clients */}
          {activeTab === 'invitations' && (
            <InvitationsSection />
          )}

          {/* Cartes de paiement */}
          {activeTab === 'cards' && (
            <div className="space-y-6">
              <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
                Mes cartes
              </h1>
              <div className="card-service rounded-xl p-8 text-center">
                <CreditCard className="w-12 h-12 text-gray-500 mx-auto mb-4" />
                <p className="text-gray-400 mb-4">Aucune carte de paiement enregistrée</p>
                <button className="btn-secondary">
                  <Plus className="w-4 h-4 mr-2" />
                  Ajouter une carte
                </button>
              </div>
            </div>
          )}

          {/* Donations */}
          {activeTab === 'donations' && (
            <div className="space-y-6">
              <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
                Donations
              </h1>
              <p className="text-gray-400">Gérez vos dons et contributions caritatives</p>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="card-service rounded-xl p-6">
                  <Heart className="w-8 h-8 text-red-500 mb-3" />
                  <h3 className="text-white font-semibold mb-2">Faire un don</h3>
                  <p className="text-sm text-gray-400 mb-4">Soutenez une cause qui vous tient à cœur</p>
                  <button className="btn-secondary w-full">Faire un don</button>
                </div>
                <div className="card-service rounded-xl p-6">
                  <FileText className="w-8 h-8 text-[#0047AB] mb-3" />
                  <h3 className="text-white font-semibold mb-2">Historique</h3>
                  <p className="text-sm text-gray-400 mb-4">Consultez vos donations passées</p>
                  <p className="text-2xl font-bold text-white">0 CHF</p>
                  <p className="text-xs text-gray-500">Total des dons</p>
                </div>
              </div>
            </div>
          )}

          {/* Business News */}
          {activeTab === 'business_news' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
                  Business News
                </h1>
                <div className="flex gap-2">
                  <select className="input-dark text-sm px-3 py-1">
                    <option>Tous les secteurs</option>
                    <option>Mon secteur</option>
                    <option>Finance</option>
                    <option>Marketing</option>
                    <option>Technologie</option>
                  </select>
                </div>
              </div>
              <div className="space-y-4">
                {[
                  { title: 'Les nouvelles tendances du commerce local', category: 'Commerce', date: 'Aujourd\'hui' },
                  { title: 'Comment optimiser sa présence en ligne', category: 'Digital', date: 'Hier' },
                  { title: 'Les aides aux entreprises en 2026', category: 'Finance', date: 'Il y a 2 jours' },
                ].map((news, i) => (
                  <div key={i} className="card-service rounded-xl p-4 flex items-start gap-4">
                    <div className="w-16 h-16 bg-[#0047AB]/20 rounded-lg flex items-center justify-center flex-shrink-0">
                      <Newspaper className="w-8 h-8 text-[#0047AB]" />
                    </div>
                    <div className="flex-1">
                      <h3 className="text-white font-medium mb-1">{news.title}</h3>
                      <div className="flex items-center gap-3 text-sm">
                        <span className="text-[#0047AB]">{news.category}</span>
                        <span className="text-gray-500">{news.date}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Messagerie */}
          {activeTab === 'messages' && (
            <MessagesSection />
          )}

          {/* Contacts */}
          {activeTab === 'contacts' && (
            <ContactsSection contacts={contacts} onRefresh={fetchAllData} />
          )}

          {/* Support */}
          {activeTab === 'support' && (
            <div className="space-y-6">
              <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
                Service client
              </h1>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="card-service rounded-xl p-6">
                  <MessageSquare className="w-8 h-8 text-[#0047AB] mb-3" />
                  <h3 className="text-white font-semibold mb-2">Chat en direct</h3>
                  <p className="text-sm text-gray-400 mb-4">Discutez avec notre équipe support</p>
                  <button className="btn-primary w-full">Démarrer un chat</button>
                </div>
                <div className="card-service rounded-xl p-6">
                  <Phone className="w-8 h-8 text-green-500 mb-3" />
                  <h3 className="text-white font-semibold mb-2">Nous appeler</h3>
                  <p className="text-sm text-gray-400 mb-4">Du lundi au vendredi, 9h-18h</p>
                  <p className="text-lg font-medium text-white">+41 21 123 45 67</p>
                </div>
              </div>
              <div className="card-service rounded-xl p-6">
                <h3 className="text-white font-semibold mb-4">Questions fréquentes</h3>
                <div className="space-y-3">
                  {['Comment modifier mon profil ?', 'Comment gérer mes commandes ?', 'Comment recevoir mes paiements ?'].map((q, i) => (
                    <div key={i} className="p-3 bg-white/5 rounded-lg hover:bg-white/10 cursor-pointer transition-colors">
                      <p className="text-gray-300">{q}</p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Partenaires */}
          {activeTab === 'partners' && (
            <div className="space-y-6">
              <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
                Partenaires
              </h1>
              <div className="card-service rounded-xl p-6">
                <h2 className="text-lg font-semibold text-white mb-4">Nos partenaires</h2>
                <p className="text-gray-400 mb-6">Découvrez les entreprises partenaires de Titelli</p>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  {[1, 2, 3, 4].map((i) => (
                    <div key={i} className="aspect-video bg-white/5 rounded-lg flex items-center justify-center">
                      <Handshake className="w-8 h-8 text-gray-500" />
                    </div>
                  ))}
                </div>
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <Link to="/mentions-legales" className="card-service rounded-xl p-4 flex items-center gap-3 hover:bg-white/10 transition-colors">
                  <FileText className="w-5 h-5 text-gray-400" />
                  <span className="text-gray-300">Mentions légales</span>
                </Link>
                <Link to="/cgv" className="card-service rounded-xl p-4 flex items-center gap-3 hover:bg-white/10 transition-colors">
                  <FileText className="w-5 h-5 text-gray-400" />
                  <span className="text-gray-300">CGV</span>
                </Link>
              </div>
            </div>
          )}

          {/* À propos */}
          {activeTab === 'about' && (
            <div className="space-y-6">
              <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
                À propos
              </h1>
              <div className="card-service rounded-xl p-6">
                <h2 className="text-lg font-semibold text-white mb-4">Titelli</h2>
                <p className="text-gray-400 mb-4">
                  Titelli est la marketplace de référence pour les prestataires de services et commerces locaux de la région lausannoise.
                </p>
                <p className="text-gray-400 mb-6">
                  Notre mission : connecter les entreprises locales avec leur communauté et faciliter le commerce de proximité.
                </p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Link to="/conditions-generales" className="card-service rounded-xl p-4 flex items-center gap-3 hover:bg-white/10 transition-colors">
                    <FileText className="w-5 h-5 text-gray-400" />
                    <span className="text-gray-300">Conditions générales</span>
                  </Link>
                  <Link to="/politique-confidentialite" className="card-service rounded-xl p-4 flex items-center gap-3 hover:bg-white/10 transition-colors">
                    <FileText className="w-5 h-5 text-gray-400" />
                    <span className="text-gray-300">Politique de confidentialité</span>
                  </Link>
                </div>
              </div>
            </div>
          )}

          {/* Subscriptions Tab */}
          {activeTab === 'subscriptions' && (
            <SubscriptionsSection />
          )}

          {/* Commandes Titelli Tab */}
          {activeTab === 'commandes-titelli' && (
            <CommandesTitelliSection enterpriseId={enterprise?.id} />
          )}
        </main>
      </div>

      {/* Modal */}
      {showModal && (
        <FormModal type={modalType} item={editItem} onClose={() => setShowModal(false)} onSuccess={() => { setShowModal(false); fetchAllData(); }} />
      )}
    </div>
  );
};

// Profile Section Component
const ProfileSection = ({ enterprise, onUpdate }) => {
  const [formData, setFormData] = useState({
    business_name: enterprise?.business_name || '',
    slogan: enterprise?.slogan || '',
    description: enterprise?.description || '',
    phone: enterprise?.phone || '',
    email: enterprise?.email || '',
    address: enterprise?.address || '',
    city: enterprise?.city || 'Lausanne',
    website: enterprise?.website || '',
    category: enterprise?.category || '',
    logo: enterprise?.logo || '',
    cover_image: enterprise?.cover_image || '',
  });
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadingCover, setUploadingCover] = useState(false);
  const [logoPreview, setLogoPreview] = useState(enterprise?.logo || null);
  const [coverPreview, setCoverPreview] = useState(enterprise?.cover_image || null);
  const logoInputRef = useRef(null);
  const coverInputRef = useRef(null);

  const handleLogoUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
      toast.error('Type de fichier non autorisé. Utilisez JPG, PNG, GIF ou WEBP.');
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      toast.error('Fichier trop volumineux (max 5MB)');
      return;
    }

    const reader = new FileReader();
    reader.onloadend = () => {
      setLogoPreview(reader.result);
    };
    reader.readAsDataURL(file);

    setUploading(true);
    try {
      const response = await uploadAPI.uploadImage(file);
      const logoUrl = process.env.REACT_APP_BACKEND_URL + response.data.url;
      setFormData(prev => ({ ...prev, logo: logoUrl }));
      toast.success('Logo uploadé !');
    } catch (error) {
      console.error('Upload error:', error);
      toast.error('Erreur lors de l\'upload du logo');
      setLogoPreview(enterprise?.logo || null);
    } finally {
      setUploading(false);
    }
  };

  const handleCoverUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
      toast.error('Type de fichier non autorisé. Utilisez JPG, PNG, GIF ou WEBP.');
      return;
    }

    if (file.size > 10 * 1024 * 1024) {
      toast.error('Fichier trop volumineux (max 10MB)');
      return;
    }

    const reader = new FileReader();
    reader.onloadend = () => {
      setCoverPreview(reader.result);
    };
    reader.readAsDataURL(file);

    setUploadingCover(true);
    try {
      const response = await uploadAPI.uploadImage(file);
      const coverUrl = process.env.REACT_APP_BACKEND_URL + response.data.url;
      setFormData(prev => ({ ...prev, cover_image: coverUrl }));
      toast.success('Image de couverture uploadée !');
    } catch (error) {
      console.error('Upload error:', error);
      toast.error('Erreur lors de l\'upload');
      setCoverPreview(enterprise?.cover_image || null);
    } finally {
      setUploadingCover(false);
    }
  };

  const removeLogo = () => {
    setLogoPreview(null);
    setFormData(prev => ({ ...prev, logo: '' }));
    if (logoInputRef.current) {
      logoInputRef.current.value = '';
    }
  };

  const removeCover = () => {
    setCoverPreview(null);
    setFormData(prev => ({ ...prev, cover_image: '' }));
    if (coverInputRef.current) {
      coverInputRef.current.value = '';
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    try {
      if (enterprise) {
        await enterpriseAPI.update(enterprise.id, formData);
      } else {
        await enterpriseAPI.create(formData);
      }
      toast.success('Profil enregistré !');
      onUpdate();
    } catch (error) {
      toast.error('Erreur lors de l\'enregistrement');
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
        Profil Entreprise
      </h1>
      <form onSubmit={handleSubmit} className="card-service rounded-xl p-6 space-y-6">
        {/* Logo Upload */}
        <div>
          <label className="block text-sm text-gray-400 mb-2">Logo de l'entreprise</label>
          <div className="flex items-center gap-6">
            <div className="w-24 h-24 rounded-xl overflow-hidden bg-white/5 flex items-center justify-center border-2 border-dashed border-white/20">
              {logoPreview || formData.logo ? (
                <div className="relative w-full h-full">
                  <img 
                    src={logoPreview || formData.logo} 
                    alt="Logo" 
                    className="w-full h-full object-cover"
                  />
                  {uploading && (
                    <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
                      <div className="w-6 h-6 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    </div>
                  )}
                </div>
              ) : (
                <Image className="w-8 h-8 text-gray-500" />
              )}
            </div>
            <div className="flex-1 space-y-2">
              <input
                ref={logoInputRef}
                type="file"
                accept="image/jpeg,image/png,image/gif,image/webp"
                onChange={handleLogoUpload}
                className="hidden"
                id="logo-upload"
              />
              <label 
                htmlFor="logo-upload" 
                className="btn-secondary inline-flex items-center gap-2 cursor-pointer"
              >
                <Upload className="w-4 h-4" />
                {formData.logo ? 'Changer le logo' : 'Ajouter un logo'}
              </label>
              {(logoPreview || formData.logo) && (
                <button type="button" onClick={removeLogo} className="text-red-400 hover:text-red-300 text-sm ml-4">
                  Supprimer
                </button>
              )}
              <p className="text-xs text-gray-500">JPG, PNG, GIF ou WEBP (max 5MB)</p>
            </div>
          </div>
        </div>

        {/* Cover Image Upload */}
        <div>
          <label className="block text-sm text-gray-400 mb-2">Image de couverture (bannière)</label>
          <div className="relative rounded-xl overflow-hidden border-2 border-dashed border-white/20 hover:border-[#0047AB]/50 transition-colors">
            {coverPreview || formData.cover_image ? (
              <div className="relative">
                <img 
                  src={coverPreview || formData.cover_image} 
                  alt="Couverture" 
                  className="w-full h-40 object-cover"
                />
                {uploadingCover && (
                  <div className="absolute inset-0 bg-black/50 flex items-center justify-center">
                    <div className="w-8 h-8 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  </div>
                )}
                <div className="absolute inset-0 bg-black/40 opacity-0 hover:opacity-100 transition-opacity flex items-center justify-center gap-4">
                  <label htmlFor="cover-upload" className="btn-secondary cursor-pointer">
                    <Camera className="w-4 h-4 mr-2 inline" />
                    Changer
                  </label>
                  <button type="button" onClick={removeCover} className="btn-secondary bg-red-500/20 text-red-400 hover:bg-red-500/30">
                    Supprimer
                  </button>
                </div>
              </div>
            ) : (
              <label htmlFor="cover-upload" className="block cursor-pointer">
                <div className="h-40 flex flex-col items-center justify-center">
                  <Camera className="w-10 h-10 text-gray-500 mb-2" />
                  <p className="text-gray-400 text-sm">Cliquez pour ajouter une image de couverture</p>
                  <p className="text-gray-500 text-xs mt-1">Format recommandé: 1200x400px (max 10MB)</p>
                </div>
              </label>
            )}
            <input
              ref={coverInputRef}
              type="file"
              accept="image/jpeg,image/png,image/gif,image/webp"
              onChange={handleCoverUpload}
              className="hidden"
              id="cover-upload"
            />
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm text-gray-400 mb-1">Nom de l'entreprise *</label>
            <input type="text" value={formData.business_name} onChange={(e) => setFormData({...formData, business_name: e.target.value})} className="input-dark w-full" required />
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-1">Slogan</label>
            <input type="text" value={formData.slogan} onChange={(e) => setFormData({...formData, slogan: e.target.value})} className="input-dark w-full" />
          </div>
        </div>
        <div>
          <label className="block text-sm text-gray-400 mb-1">Description *</label>
          <textarea value={formData.description} onChange={(e) => setFormData({...formData, description: e.target.value})} className="input-dark w-full h-24" required />
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm text-gray-400 mb-1">Téléphone *</label>
            <input type="tel" value={formData.phone} onChange={(e) => setFormData({...formData, phone: e.target.value})} className="input-dark w-full" required />
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-1">Email *</label>
            <input type="email" value={formData.email} onChange={(e) => setFormData({...formData, email: e.target.value})} className="input-dark w-full" required />
          </div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm text-gray-400 mb-1">Adresse *</label>
            <input type="text" value={formData.address} onChange={(e) => setFormData({...formData, address: e.target.value})} className="input-dark w-full" required />
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-1">Site web</label>
            <input type="url" value={formData.website} onChange={(e) => setFormData({...formData, website: e.target.value})} className="input-dark w-full" />
          </div>
        </div>
        <button type="submit" disabled={saving} className="btn-primary">
          {saving ? 'Enregistrement...' : 'Enregistrer'}
        </button>
      </form>
    </div>
  );
};

// Media Gallery Section Component
const MediaGallerySection = ({ enterprise, onUpdate }) => {
  const [photos, setPhotos] = useState(enterprise?.photos || []);
  const [photoTags, setPhotoTags] = useState(enterprise?.photo_tags || {}); // { photoIndex: [{ id, type, name, x, y }] }
  const [videos, setVideos] = useState(enterprise?.videos || []);
  const [uploading, setUploading] = useState(false);
  const [uploadType, setUploadType] = useState('photo');
  const [videoUrl, setVideoUrl] = useState('');
  const photoInputRef = useRef(null);
  
  // Tag system states
  const [selectedPhotoIndex, setSelectedPhotoIndex] = useState(null);
  const [showTagModal, setShowTagModal] = useState(false);
  const [tagPosition, setTagPosition] = useState({ x: 0, y: 0 });
  const [tagType, setTagType] = useState('client'); // 'client' | 'product' | 'service'
  const [tagSearch, setTagSearch] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [viewingPhoto, setViewingPhoto] = useState(null);

  // Search for clients, products or services to tag
  const handleTagSearch = async (query, type) => {
    if (!query.trim()) {
      setSearchResults([]);
      return;
    }
    
    setSearchLoading(true);
    try {
      let results = [];
      if (type === 'client') {
        // Search clients (contacts)
        const res = await enterpriseContactsAPI.list({ search: query });
        results = (res.data?.contacts || []).map(c => ({
          id: c.id,
          name: `${c.first_name} ${c.last_name}`,
          type: 'client',
          link: `/client/${c.id}`
        }));
      } else if (type === 'product' || type === 'service') {
        // Search products/services
        const res = await servicesProductsAPI.list({ 
          enterprise_id: enterprise.id, 
          search: query,
          type: type
        });
        results = (res.data?.items || []).map(p => ({
          id: p.id,
          name: p.name,
          type: type,
          link: `/item/${p.id}`
        }));
      }
      setSearchResults(results);
    } catch (error) {
      console.error('Search error:', error);
      setSearchResults([]);
    } finally {
      setSearchLoading(false);
    }
  };

  // Handle click on photo to add tag
  const handlePhotoClick = (e, photoIndex) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width) * 100;
    const y = ((e.clientY - rect.top) / rect.height) * 100;
    
    setSelectedPhotoIndex(photoIndex);
    setTagPosition({ x, y });
    setShowTagModal(true);
    setTagSearch('');
    setSearchResults([]);
  };

  // Add tag to photo
  const handleAddTag = async (item) => {
    const newTag = {
      id: item.id,
      type: item.type,
      name: item.name,
      link: item.link,
      x: tagPosition.x,
      y: tagPosition.y
    };
    
    const currentTags = photoTags[selectedPhotoIndex] || [];
    const updatedTags = {
      ...photoTags,
      [selectedPhotoIndex]: [...currentTags, newTag]
    };
    
    setPhotoTags(updatedTags);
    setShowTagModal(false);
    
    // Save to backend
    try {
      await enterpriseAPI.update(enterprise.id, { photo_tags: updatedTags });
      toast.success(`${item.name} tagué !`);
      onUpdate();
    } catch (error) {
      toast.error('Erreur lors du tag');
    }
  };

  // Remove tag from photo
  const handleRemoveTag = async (photoIndex, tagIndex) => {
    const currentTags = photoTags[photoIndex] || [];
    const updatedTags = {
      ...photoTags,
      [photoIndex]: currentTags.filter((_, i) => i !== tagIndex)
    };
    
    setPhotoTags(updatedTags);
    
    try {
      await enterpriseAPI.update(enterprise.id, { photo_tags: updatedTags });
      toast.success('Tag supprimé');
      onUpdate();
    } catch (error) {
      toast.error('Erreur');
    }
  };

  const handlePhotoUpload = async (e) => {
    const files = Array.from(e.target.files);
    if (files.length === 0) return;

    setUploading(true);
    try {
      const uploadedUrls = [];
      for (const file of files) {
        const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
        if (!allowedTypes.includes(file.type)) {
          toast.error(`${file.name}: Type de fichier non autorisé`);
          continue;
        }
        if (file.size > 10 * 1024 * 1024) {
          toast.error(`${file.name}: Fichier trop volumineux (max 10MB)`);
          continue;
        }
        
        const response = await uploadAPI.uploadImage(file);
        const imageUrl = process.env.REACT_APP_BACKEND_URL + response.data.url;
        uploadedUrls.push(imageUrl);
      }
      
      if (uploadedUrls.length > 0) {
        const newPhotos = [...photos, ...uploadedUrls];
        setPhotos(newPhotos);
        
        // Save to backend
        await enterpriseAPI.update(enterprise.id, { photos: newPhotos });
        toast.success(`${uploadedUrls.length} photo(s) ajoutée(s) !`);
        onUpdate();
      }
    } catch (error) {
      console.error('Upload error:', error);
      toast.error('Erreur lors de l\'upload');
    } finally {
      setUploading(false);
      if (photoInputRef.current) photoInputRef.current.value = '';
    }
  };

  const handleAddVideo = async () => {
    if (!videoUrl.trim()) {
      toast.error('Entrez une URL vidéo');
      return;
    }
    
    // Validate URL format
    const isValidUrl = videoUrl.includes('youtube.com') || videoUrl.includes('youtu.be') || 
                       videoUrl.includes('vimeo.com') || videoUrl.startsWith('https://');
    if (!isValidUrl) {
      toast.error('URL vidéo invalide');
      return;
    }
    
    setUploading(true);
    try {
      const newVideos = [...videos, videoUrl];
      setVideos(newVideos);
      await enterpriseAPI.update(enterprise.id, { videos: newVideos });
      toast.success('Vidéo ajoutée !');
      setVideoUrl('');
      onUpdate();
    } catch (error) {
      toast.error('Erreur lors de l\'ajout');
    } finally {
      setUploading(false);
    }
  };

  const handleDeletePhoto = async (index) => {
    const newPhotos = photos.filter((_, i) => i !== index);
    setPhotos(newPhotos);
    
    // Also remove tags for this photo and reindex
    const newTags = {};
    Object.keys(photoTags).forEach(key => {
      const keyNum = parseInt(key);
      if (keyNum < index) {
        newTags[keyNum] = photoTags[key];
      } else if (keyNum > index) {
        newTags[keyNum - 1] = photoTags[key];
      }
    });
    setPhotoTags(newTags);
    
    try {
      await enterpriseAPI.update(enterprise.id, { photos: newPhotos, photo_tags: newTags });
      toast.success('Photo supprimée');
      onUpdate();
    } catch (error) {
      toast.error('Erreur lors de la suppression');
    }
  };

  const handleDeleteVideo = async (index) => {
    const newVideos = videos.filter((_, i) => i !== index);
    setVideos(newVideos);
    try {
      await enterpriseAPI.update(enterprise.id, { videos: newVideos });
      toast.success('Vidéo supprimée');
      onUpdate();
    } catch (error) {
      toast.error('Erreur lors de la suppression');
    }
  };

  const getYouTubeEmbedUrl = (url) => {
    if (url.includes('youtube.com/watch?v=')) {
      const videoId = url.split('v=')[1]?.split('&')[0];
      return `https://www.youtube.com/embed/${videoId}`;
    }
    if (url.includes('youtu.be/')) {
      const videoId = url.split('youtu.be/')[1]?.split('?')[0];
      return `https://www.youtube.com/embed/${videoId}`;
    }
    return url;
  };

  return (
    <div className="space-y-6" data-testid="media-gallery-section">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
            Galerie Média
          </h1>
          <p className="text-gray-400 text-sm mt-1">Gérez les photos et vidéos • Cliquez sur une photo pour tagger des clients ou produits</p>
        </div>
      </div>

      {/* Upload Tabs */}
      <div className="card-service rounded-xl p-4">
        <div className="flex gap-2 mb-4">
          <button 
            onClick={() => setUploadType('photo')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
              uploadType === 'photo' ? 'bg-[#0047AB] text-white' : 'bg-white/10 text-gray-300 hover:bg-white/20'
            }`}
          >
            <Camera className="w-4 h-4" />
            Photos
          </button>
          <button 
            onClick={() => setUploadType('video')}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-colors ${
              uploadType === 'video' ? 'bg-[#0047AB] text-white' : 'bg-white/10 text-gray-300 hover:bg-white/20'
            }`}
          >
            <PlayCircle className="w-4 h-4" />
            Vidéos
          </button>
        </div>

        {uploadType === 'photo' ? (
          <div className="space-y-4">
            <div 
              className="border-2 border-dashed border-white/20 rounded-xl p-8 text-center hover:border-[#0047AB]/50 transition-colors cursor-pointer"
              onClick={() => photoInputRef.current?.click()}
            >
              {uploading ? (
                <div className="flex flex-col items-center">
                  <div className="w-8 h-8 border-2 border-[#0047AB] border-t-transparent rounded-full animate-spin mb-2" />
                  <p className="text-gray-400">Upload en cours...</p>
                </div>
              ) : (
                <>
                  <Upload className="w-10 h-10 text-gray-500 mx-auto mb-2" />
                  <p className="text-gray-400">Cliquez ou glissez vos photos ici</p>
                  <p className="text-xs text-gray-500 mt-1">JPG, PNG, GIF, WEBP • Max 10MB par fichier</p>
                </>
              )}
            </div>
            <input
              ref={photoInputRef}
              type="file"
              accept="image/jpeg,image/png,image/gif,image/webp"
              onChange={handlePhotoUpload}
              multiple
              className="hidden"
            />
          </div>
        ) : (
          <div className="flex gap-3">
            <input
              type="url"
              value={videoUrl}
              onChange={(e) => setVideoUrl(e.target.value)}
              placeholder="URL YouTube, Vimeo ou lien vidéo direct..."
              className="flex-1 input-dark"
            />
            <button 
              onClick={handleAddVideo}
              disabled={uploading}
              className="btn-primary flex items-center gap-2"
            >
              {uploading ? (
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
              ) : (
                <Plus className="w-4 h-4" />
              )}
              Ajouter
            </button>
          </div>
        )}
      </div>

      {/* Photos Grid with Tags */}
      <div className="card-service rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <Camera className="w-5 h-5 text-[#0047AB]" />
          Photos ({photos.length})
          <span className="text-xs text-gray-500 font-normal ml-2">• Cliquez sur une photo pour ajouter un tag</span>
        </h3>
        {photos.length > 0 ? (
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
            {photos.map((photo, index) => (
              <div 
                key={index} 
                className="relative group aspect-square rounded-xl overflow-hidden cursor-crosshair"
                onClick={(e) => handlePhotoClick(e, index)}
              >
                <img src={photo} alt={`Photo ${index + 1}`} className="w-full h-full object-cover" />
                
                {/* Tags on photo */}
                {(photoTags[index] || []).map((tag, tagIdx) => (
                  <div
                    key={tagIdx}
                    className="absolute group/tag"
                    style={{ left: `${tag.x}%`, top: `${tag.y}%`, transform: 'translate(-50%, -50%)' }}
                    onClick={(e) => e.stopPropagation()}
                  >
                    {/* Tag dot */}
                    <div className={`w-6 h-6 rounded-full border-2 border-white shadow-lg flex items-center justify-center cursor-pointer ${
                      tag.type === 'client' ? 'bg-[#0047AB]' : 
                      tag.type === 'product' ? 'bg-[#D4AF37]' : 'bg-green-500'
                    }`}>
                      {tag.type === 'client' ? (
                        <UserCircle className="w-3 h-3 text-white" />
                      ) : tag.type === 'product' ? (
                        <Package className="w-3 h-3 text-white" />
                      ) : (
                        <Sparkles className="w-3 h-3 text-white" />
                      )}
                    </div>
                    
                    {/* Tag tooltip on hover */}
                    <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 opacity-0 group-hover/tag:opacity-100 transition-opacity pointer-events-none group-hover/tag:pointer-events-auto z-20">
                      <div className="bg-black/90 backdrop-blur-sm rounded-lg px-3 py-2 whitespace-nowrap border border-white/10 shadow-xl">
                        <p className="text-white text-sm font-medium">{tag.name}</p>
                        <p className="text-xs text-gray-400 capitalize">{tag.type}</p>
                        <div className="flex items-center gap-2 mt-1">
                          <a 
                            href={tag.link} 
                            className="text-xs text-[#0047AB] hover:underline"
                            onClick={(e) => e.stopPropagation()}
                          >
                            Voir le profil →
                          </a>
                          <button 
                            onClick={() => handleRemoveTag(index, tagIdx)}
                            className="text-xs text-red-400 hover:text-red-300"
                          >
                            Supprimer
                          </button>
                        </div>
                      </div>
                      <div className="w-3 h-3 bg-black/90 rotate-45 absolute -bottom-1.5 left-1/2 -translate-x-1/2 border-r border-b border-white/10" />
                    </div>
                  </div>
                ))}
                
                {/* Hover overlay */}
                <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center gap-2">
                  <button
                    onClick={(e) => { e.stopPropagation(); setViewingPhoto(index); }}
                    className="p-2 bg-white/20 hover:bg-white/30 rounded-full text-white transition-colors"
                  >
                    <Eye className="w-5 h-5" />
                  </button>
                  <button
                    onClick={(e) => { e.stopPropagation(); handleDeletePhoto(index); }}
                    className="p-2 bg-red-500/80 hover:bg-red-500 rounded-full text-white transition-colors"
                  >
                    <Trash2 className="w-5 h-5" />
                  </button>
                </div>
                
                {/* Tags count badge */}
                {(photoTags[index] || []).length > 0 && (
                  <div className="absolute top-2 left-2 bg-black/70 backdrop-blur-sm rounded-full px-2 py-1 flex items-center gap-1">
                    <UserPlus className="w-3 h-3 text-[#0047AB]" />
                    <span className="text-xs text-white">{photoTags[index].length}</span>
                  </div>
                )}
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <Camera className="w-12 h-12 text-gray-500 mx-auto mb-3" />
            <p className="text-gray-400">Aucune photo ajoutée</p>
            <p className="text-sm text-gray-500">Ajoutez des photos pour présenter votre entreprise</p>
          </div>
        )}
      </div>

      {/* Videos Grid */}
      <div className="card-service rounded-xl p-6">
        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
          <PlayCircle className="w-5 h-5 text-[#D4AF37]" />
          Vidéos ({videos.length})
        </h3>
        {videos.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {videos.map((video, index) => (
              <div key={index} className="relative group">
                <div className="aspect-video rounded-xl overflow-hidden bg-black">
                  {video.includes('youtube.com') || video.includes('youtu.be') ? (
                    <iframe
                      src={getYouTubeEmbedUrl(video)}
                      className="w-full h-full"
                      allowFullScreen
                      title={`Video ${index + 1}`}
                    />
                  ) : (
                    <video src={video} controls className="w-full h-full object-cover" />
                  )}
                </div>
                <button
                  onClick={() => handleDeleteVideo(index)}
                  className="absolute top-2 right-2 p-2 bg-red-500/80 hover:bg-red-500 rounded-full text-white opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <PlayCircle className="w-12 h-12 text-gray-500 mx-auto mb-3" />
            <p className="text-gray-400">Aucune vidéo ajoutée</p>
            <p className="text-sm text-gray-500">Ajoutez des vidéos YouTube ou des liens directs</p>
          </div>
        )}
      </div>

      {/* Tag Modal */}
      {showTagModal && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4" onClick={() => setShowTagModal(false)}>
          <div className="bg-[#0F0F0F] rounded-2xl w-full max-w-md border border-white/10" onClick={(e) => e.stopPropagation()}>
            <div className="p-4 border-b border-white/10 flex items-center justify-between">
              <h3 className="text-lg font-semibold text-white">Ajouter un tag</h3>
              <button onClick={() => setShowTagModal(false)} className="text-gray-400 hover:text-white">
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <div className="p-4 space-y-4">
              {/* Tag type selector */}
              <div className="flex gap-2">
                <button
                  onClick={() => { setTagType('client'); setTagSearch(''); setSearchResults([]); }}
                  className={`flex-1 py-2 px-3 rounded-lg text-sm flex items-center justify-center gap-2 ${
                    tagType === 'client' ? 'bg-[#0047AB] text-white' : 'bg-white/10 text-gray-300'
                  }`}
                >
                  <UserCircle className="w-4 h-4" />
                  Client
                </button>
                <button
                  onClick={() => { setTagType('product'); setTagSearch(''); setSearchResults([]); }}
                  className={`flex-1 py-2 px-3 rounded-lg text-sm flex items-center justify-center gap-2 ${
                    tagType === 'product' ? 'bg-[#D4AF37] text-black' : 'bg-white/10 text-gray-300'
                  }`}
                >
                  <Package className="w-4 h-4" />
                  Produit
                </button>
                <button
                  onClick={() => { setTagType('service'); setTagSearch(''); setSearchResults([]); }}
                  className={`flex-1 py-2 px-3 rounded-lg text-sm flex items-center justify-center gap-2 ${
                    tagType === 'service' ? 'bg-green-500 text-white' : 'bg-white/10 text-gray-300'
                  }`}
                >
                  <Sparkles className="w-4 h-4" />
                  Service
                </button>
              </div>
              
              {/* Search input */}
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  value={tagSearch}
                  onChange={(e) => {
                    setTagSearch(e.target.value);
                    handleTagSearch(e.target.value, tagType);
                  }}
                  placeholder={`Rechercher un ${tagType === 'client' ? 'client' : tagType === 'product' ? 'produit' : 'service'}...`}
                  className="w-full pl-10 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder:text-gray-500 focus:outline-none focus:border-[#0047AB]/50"
                />
              </div>
              
              {/* Search results */}
              <div className="max-h-64 overflow-y-auto space-y-2">
                {searchLoading ? (
                  <div className="text-center py-4">
                    <div className="w-6 h-6 border-2 border-[#0047AB] border-t-transparent rounded-full animate-spin mx-auto" />
                  </div>
                ) : searchResults.length > 0 ? (
                  searchResults.map((item) => (
                    <button
                      key={item.id}
                      onClick={() => handleAddTag(item)}
                      className="w-full p-3 bg-white/5 hover:bg-white/10 rounded-xl text-left transition-colors flex items-center gap-3"
                    >
                      <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                        item.type === 'client' ? 'bg-[#0047AB]/20' : 
                        item.type === 'product' ? 'bg-[#D4AF37]/20' : 'bg-green-500/20'
                      }`}>
                        {item.type === 'client' ? (
                          <UserCircle className="w-5 h-5 text-[#0047AB]" />
                        ) : item.type === 'product' ? (
                          <Package className="w-5 h-5 text-[#D4AF37]" />
                        ) : (
                          <Sparkles className="w-5 h-5 text-green-500" />
                        )}
                      </div>
                      <div>
                        <p className="text-white font-medium">{item.name}</p>
                        <p className="text-xs text-gray-400">ID: {item.id.slice(0, 8)}...</p>
                      </div>
                    </button>
                  ))
                ) : tagSearch.trim() ? (
                  <p className="text-center text-gray-400 py-4">Aucun résultat</p>
                ) : (
                  <p className="text-center text-gray-500 py-4 text-sm">
                    Tapez pour rechercher un {tagType === 'client' ? 'client' : tagType === 'product' ? 'produit' : 'service'}
                  </p>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Photo Viewer Modal */}
      {viewingPhoto !== null && (
        <div className="fixed inset-0 bg-black/95 flex items-center justify-center z-50 p-4" onClick={() => setViewingPhoto(null)}>
          <button 
            onClick={() => setViewingPhoto(null)}
            className="absolute top-4 right-4 p-2 bg-white/10 hover:bg-white/20 rounded-full text-white"
          >
            <X className="w-6 h-6" />
          </button>
          <div className="relative max-w-4xl max-h-[90vh]" onClick={(e) => e.stopPropagation()}>
            <img 
              src={photos[viewingPhoto]} 
              alt="" 
              className="max-w-full max-h-[90vh] object-contain rounded-xl"
            />
            {/* Tags on enlarged photo */}
            {(photoTags[viewingPhoto] || []).map((tag, tagIdx) => (
              <div
                key={tagIdx}
                className="absolute group/tag"
                style={{ left: `${tag.x}%`, top: `${tag.y}%`, transform: 'translate(-50%, -50%)' }}
              >
                <div className={`w-8 h-8 rounded-full border-2 border-white shadow-lg flex items-center justify-center cursor-pointer ${
                  tag.type === 'client' ? 'bg-[#0047AB]' : 
                  tag.type === 'product' ? 'bg-[#D4AF37]' : 'bg-green-500'
                }`}>
                  {tag.type === 'client' ? (
                    <UserCircle className="w-4 h-4 text-white" />
                  ) : tag.type === 'product' ? (
                    <Package className="w-4 h-4 text-white" />
                  ) : (
                    <Sparkles className="w-4 h-4 text-white" />
                  )}
                </div>
                <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 opacity-0 group-hover/tag:opacity-100 transition-opacity z-20">
                  <div className="bg-black/90 backdrop-blur-sm rounded-lg px-4 py-3 whitespace-nowrap border border-white/10 shadow-xl">
                    <p className="text-white font-medium">{tag.name}</p>
                    <p className="text-sm text-gray-400 capitalize">{tag.type}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

// Services Section Component
const ServicesSection = ({ services, onAdd, onDelete, onRefresh }) => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
          Services & Produits
        </h1>
        <button onClick={onAdd} className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" /> Ajouter
        </button>
      </div>
      {services.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {services.map((item) => (
            <div key={item.id} className="card-service rounded-xl p-4">
              <div className="flex items-start justify-between mb-2">
                <span className={`px-2 py-1 rounded-full text-xs ${item.type === 'service' ? 'bg-[#0047AB]/20 text-[#0047AB]' : 'bg-[#D4AF37]/20 text-[#D4AF37]'}`}>
                  {item.type === 'service' ? 'Service' : 'Produit'}
                </span>
                <button onClick={() => onDelete(item.id)} className="text-red-400 hover:text-red-300">
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
              <h3 className="text-white font-medium mb-1">{item.name}</h3>
              <p className="text-sm text-gray-400 line-clamp-2 mb-2">{item.description}</p>
              <p className="text-lg font-bold text-[#D4AF37]">{item.price} CHF</p>
            </div>
          ))}
        </div>
      ) : (
        <div className="card-service rounded-xl p-12 text-center">
          <Package className="w-12 h-12 text-gray-500 mx-auto mb-4" />
          <p className="text-gray-400">Aucun service ou produit</p>
        </div>
      )}
    </div>
  );
};

// Orders Section Component
const OrdersSection = ({ orders, onRefresh }) => {
  const updateStatus = async (orderId, status) => {
    try {
      await orderAPI.updateStatus(orderId, status);
      toast.success('Statut mis à jour');
      onRefresh();
    } catch (error) {
      toast.error('Erreur');
    }
  };

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
        Commandes
      </h1>
      {orders.length > 0 ? (
        <div className="space-y-4">
          {orders.map((order) => (
            <div key={order.id} className="card-service rounded-xl p-4">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <p className="text-white font-medium">Commande #{order.id.slice(0, 8)}</p>
                  <p className="text-sm text-gray-400">{new Date(order.created_at).toLocaleDateString('fr-FR')}</p>
                </div>
                <div className="flex items-center gap-2">
                  <select 
                    value={order.status} 
                    onChange={(e) => updateStatus(order.id, e.target.value)}
                    className="input-dark text-sm"
                  >
                    <option value="pending">En attente</option>
                    <option value="confirmed">Confirmée</option>
                    <option value="completed">Terminée</option>
                    <option value="cancelled">Annulée</option>
                  </select>
                </div>
              </div>
              <div className="space-y-2 mb-4">
                {order.items?.map((item, i) => (
                  <div key={i} className="flex justify-between text-sm">
                    <span className="text-gray-400">{item.quantity}x {item.name}</span>
                    <span className="text-white">{(item.price * item.quantity).toFixed(2)} CHF</span>
                  </div>
                ))}
              </div>
              <div className="flex justify-between items-center pt-4 border-t border-white/10">
                <span className="text-gray-400">Total</span>
                <span className="text-xl font-bold text-[#D4AF37]">{order.total?.toFixed(2)} CHF</span>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="card-service rounded-xl p-12 text-center">
          <ShoppingCart className="w-12 h-12 text-gray-500 mx-auto mb-4" />
          <p className="text-gray-400">Aucune commande</p>
        </div>
      )}
    </div>
  );
};

// Generic Section Component for similar layouts
const GenericSection = ({ title, icon: Icon, items, onAdd, onDelete, emptyText, renderItem }) => {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
          {title}
        </h1>
        <button onClick={onAdd} className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" /> Ajouter
        </button>
      </div>
      {items.length > 0 ? (
        <div className="space-y-3">
          {items.map((item) => (
            <div key={item.id} className="card-service rounded-xl p-4">
              <div className="flex items-center gap-4">
                <div className="flex-1">{renderItem(item)}</div>
                <button onClick={() => onDelete(item.id)} className="text-red-400 hover:text-red-300">
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="card-service rounded-xl p-12 text-center">
          <Icon className="w-12 h-12 text-gray-500 mx-auto mb-4" />
          <p className="text-gray-400">{emptyText}</p>
          <button onClick={onAdd} className="btn-secondary mt-4">Ajouter</button>
        </div>
      )}
    </div>
  );
};

// Applications/Postulations Section Component
const ApplicationsSection = ({ applications, onRefresh }) => {
  const [filter, setFilter] = useState('all');
  const [selectedApp, setSelectedApp] = useState(null);
  const [updating, setUpdating] = useState(false);
  
  const { applications: appList = [], jobs = [], stats = {} } = applications || {};
  
  const filteredApps = filter === 'all' 
    ? appList 
    : appList.filter(app => app.status === filter);
  
  const updateStatus = async (applicationId, status) => {
    setUpdating(true);
    try {
      const { enterpriseApplicationsAPI } = await import('../services/api');
      await enterpriseApplicationsAPI.updateStatus(applicationId, status);
      toast.success('Statut mis à jour');
      onRefresh();
    } catch (error) {
      toast.error('Erreur lors de la mise à jour');
    } finally {
      setUpdating(false);
    }
  };
  
  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    return new Date(dateStr).toLocaleDateString('fr-CH', {
      day: 'numeric', month: 'short', year: 'numeric'
    });
  };

  return (
    <div className="space-y-6" data-testid="applications-section">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
            Postulations reçues
          </h1>
          <p className="text-gray-400 text-sm mt-1">
            {stats.total || 0} candidature(s) au total
          </p>
        </div>
        
        {/* Stats Cards */}
        <div className="flex flex-wrap gap-2">
          <button 
            onClick={() => setFilter('all')}
            className={`px-3 py-1.5 rounded-lg text-sm transition-colors ${filter === 'all' ? 'bg-[#0047AB] text-white' : 'bg-white/10 text-gray-300 hover:bg-white/20'}`}
          >
            Toutes ({stats.total || 0})
          </button>
          <button 
            onClick={() => setFilter('pending')}
            className={`px-3 py-1.5 rounded-lg text-sm transition-colors ${filter === 'pending' ? 'bg-yellow-500 text-black' : 'bg-yellow-500/20 text-yellow-400 hover:bg-yellow-500/30'}`}
          >
            En attente ({stats.pending || 0})
          </button>
          <button 
            onClick={() => setFilter('reviewed')}
            className={`px-3 py-1.5 rounded-lg text-sm transition-colors ${filter === 'reviewed' ? 'bg-blue-500 text-white' : 'bg-blue-500/20 text-blue-400 hover:bg-blue-500/30'}`}
          >
            En examen ({stats.reviewed || 0})
          </button>
          <button 
            onClick={() => setFilter('accepted')}
            className={`px-3 py-1.5 rounded-lg text-sm transition-colors ${filter === 'accepted' ? 'bg-green-500 text-black' : 'bg-green-500/20 text-green-400 hover:bg-green-500/30'}`}
          >
            Acceptées ({stats.accepted || 0})
          </button>
          <button 
            onClick={() => setFilter('rejected')}
            className={`px-3 py-1.5 rounded-lg text-sm transition-colors ${filter === 'rejected' ? 'bg-red-500 text-white' : 'bg-red-500/20 text-red-400 hover:bg-red-500/30'}`}
          >
            Refusées ({stats.rejected || 0})
          </button>
        </div>
      </div>

      {filteredApps.length > 0 ? (
        <div className="space-y-4">
          {filteredApps.map((app) => (
            <div 
              key={app.id} 
              className="card-service rounded-xl p-5 hover:border-[#0047AB]/30 transition-all"
              data-testid={`application-card-${app.id}`}
            >
              <div className="flex flex-col md:flex-row md:items-start justify-between gap-4">
                {/* Applicant Info */}
                <div className="flex items-start gap-4 flex-1">
                  <div className="w-12 h-12 rounded-full bg-[#0047AB]/20 flex items-center justify-center flex-shrink-0">
                    {app.applicant?.profile_image ? (
                      <img src={app.applicant.profile_image} alt="" className="w-12 h-12 rounded-full object-cover" />
                    ) : (
                      <UserCircle className="w-6 h-6 text-[#0047AB]" />
                    )}
                  </div>
                  <div className="flex-1">
                    <h3 className="text-white font-semibold">
                      {app.applicant?.first_name} {app.applicant?.last_name}
                    </h3>
                    <p className="text-[#D4AF37] text-sm">{app.job?.title || 'Poste inconnu'}</p>
                    <p className="text-gray-400 text-xs mt-1">
                      Candidature du {formatDate(app.created_at)}
                    </p>
                    
                    {/* Cover letter preview */}
                    {app.cover_letter && (
                      <div className="mt-3 p-3 bg-white/5 rounded-lg">
                        <p className="text-gray-300 text-sm line-clamp-2">{app.cover_letter}</p>
                      </div>
                    )}
                    
                    {/* Documents */}
                    {app.resume_url && (
                      <div className="mt-3 flex items-center gap-2">
                        <FileText className="w-4 h-4 text-[#0047AB]" />
                        <a 
                          href={app.resume_url.startsWith('http') ? app.resume_url : `${process.env.REACT_APP_BACKEND_URL}${app.resume_url}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-[#0047AB] text-sm hover:underline"
                        >
                          Voir le CV
                        </a>
                      </div>
                    )}
                    
                    {/* Additional documents */}
                    {app.documents && app.documents.length > 0 && (
                      <div className="mt-2">
                        <p className="text-xs text-gray-500 mb-1">Documents disponibles:</p>
                        <div className="flex flex-wrap gap-2">
                          {app.documents.slice(0, 3).map((doc, idx) => (
                            <a 
                              key={idx}
                              href={doc.file_path?.startsWith('http') ? doc.file_path : `${process.env.REACT_APP_BACKEND_URL}${doc.file_path}`}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="flex items-center gap-1 px-2 py-1 bg-white/10 rounded text-xs text-gray-300 hover:bg-white/20"
                            >
                              <FileText className="w-3 h-3" />
                              {doc.file_name?.substring(0, 15)}...
                            </a>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
                
                {/* Status & Actions */}
                <div className="flex flex-col items-end gap-3">
                  <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                    app.status === 'pending' ? 'bg-yellow-500/20 text-yellow-400' :
                    app.status === 'reviewed' ? 'bg-blue-500/20 text-blue-400' :
                    app.status === 'accepted' ? 'bg-green-500/20 text-green-400' :
                    app.status === 'rejected' ? 'bg-red-500/20 text-red-400' :
                    'bg-gray-500/20 text-gray-400'
                  }`}>
                    {app.status === 'pending' ? 'En attente' :
                     app.status === 'reviewed' ? 'En examen' :
                     app.status === 'accepted' ? 'Acceptée' :
                     app.status === 'rejected' ? 'Refusée' : app.status}
                  </span>
                  
                  {/* Action buttons */}
                  <div className="flex gap-2">
                    {app.status === 'pending' && (
                      <>
                        <button
                          onClick={() => updateStatus(app.id, 'reviewed')}
                          disabled={updating}
                          className="px-3 py-1.5 bg-blue-500/20 text-blue-400 rounded-lg text-xs hover:bg-blue-500/30 transition-colors"
                        >
                          Examiner
                        </button>
                        <button
                          onClick={() => updateStatus(app.id, 'accepted')}
                          disabled={updating}
                          className="px-3 py-1.5 bg-green-500/20 text-green-400 rounded-lg text-xs hover:bg-green-500/30 transition-colors"
                        >
                          <CheckCircle className="w-3 h-3 inline mr-1" />
                          Accepter
                        </button>
                        <button
                          onClick={() => updateStatus(app.id, 'rejected')}
                          disabled={updating}
                          className="px-3 py-1.5 bg-red-500/20 text-red-400 rounded-lg text-xs hover:bg-red-500/30 transition-colors"
                        >
                          <XCircle className="w-3 h-3 inline mr-1" />
                          Refuser
                        </button>
                      </>
                    )}
                    {app.status === 'reviewed' && (
                      <>
                        <button
                          onClick={() => updateStatus(app.id, 'accepted')}
                          disabled={updating}
                          className="px-3 py-1.5 bg-green-500/20 text-green-400 rounded-lg text-xs hover:bg-green-500/30 transition-colors"
                        >
                          <CheckCircle className="w-3 h-3 inline mr-1" />
                          Accepter
                        </button>
                        <button
                          onClick={() => updateStatus(app.id, 'rejected')}
                          disabled={updating}
                          className="px-3 py-1.5 bg-red-500/20 text-red-400 rounded-lg text-xs hover:bg-red-500/30 transition-colors"
                        >
                          <XCircle className="w-3 h-3 inline mr-1" />
                          Refuser
                        </button>
                      </>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="card-service rounded-xl p-12 text-center">
          <ClipboardList className="w-12 h-12 text-gray-500 mx-auto mb-4" />
          <p className="text-gray-400">
            {filter === 'all' ? "Aucune candidature reçue" : `Aucune candidature avec le statut "${filter}"`}
          </p>
          <p className="text-sm text-gray-500 mt-2">
            Les candidatures à vos offres d'emploi apparaîtront ici
          </p>
        </div>
      )}
    </div>
  );
};

// Stock Section Component
const StockSection = ({ stock, services, onRefresh }) => {
  const [showAdd, setShowAdd] = useState(false);
  const [formData, setFormData] = useState({ product_id: '', product_name: '', quantity: 0, min_quantity: 5, unit: 'pièce' });

  const addStock = async () => {
    try {
      await stockAPI.add(formData);
      toast.success('Produit ajouté au stock');
      setShowAdd(false);
      onRefresh();
    } catch (error) {
      toast.error('Erreur');
    }
  };

  const recordMovement = async (productId, type, qty) => {
    try {
      await stockAPI.movement({ product_id: productId, quantity: qty, movement_type: type });
      toast.success('Mouvement enregistré');
      onRefresh();
    } catch (error) {
      toast.error('Erreur');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
          Gestion des stocks
        </h1>
        <button onClick={() => setShowAdd(true)} className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" /> Ajouter produit
        </button>
      </div>

      {stock.alerts.length > 0 && (
        <div className="card-service rounded-xl p-4 border-red-500/50">
          <h3 className="text-red-400 font-medium mb-2 flex items-center gap-2">
            <AlertTriangle className="w-5 h-5" /> Alertes stock faible
          </h3>
          <div className="space-y-2">
            {stock.alerts.map((item) => (
              <div key={item.id} className="flex justify-between text-sm">
                <span className="text-white">{item.product_name}</span>
                <span className="text-red-400">{item.quantity} / {item.min_quantity} {item.unit}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {stock.items.length > 0 ? (
        <div className="space-y-3">
          {stock.items.map((item) => (
            <div key={item.id} className="card-service rounded-xl p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-white font-medium">{item.product_name}</p>
                  <p className="text-sm text-gray-400">SKU: {item.sku || 'N/A'}</p>
                </div>
                <div className="flex items-center gap-4">
                  <div className="text-center">
                    <p className={`text-xl font-bold ${item.quantity <= item.min_quantity ? 'text-red-400' : 'text-green-400'}`}>
                      {item.quantity}
                    </p>
                    <p className="text-xs text-gray-400">{item.unit}</p>
                  </div>
                  <div className="flex gap-1">
                    <button onClick={() => recordMovement(item.product_id, 'in', 1)} className="p-2 bg-green-500/20 text-green-400 rounded hover:bg-green-500/30">
                      <Plus className="w-4 h-4" />
                    </button>
                    <button onClick={() => recordMovement(item.product_id, 'out', 1)} className="p-2 bg-red-500/20 text-red-400 rounded hover:bg-red-500/30">
                      <ArrowUpDown className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="card-service rounded-xl p-12 text-center">
          <Box className="w-12 h-12 text-gray-500 mx-auto mb-4" />
          <p className="text-gray-400">Aucun produit en stock</p>
        </div>
      )}

      {showAdd && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="card-service rounded-xl p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold text-white mb-4">Ajouter au stock</h3>
            <div className="space-y-4">
              <select 
                value={formData.product_id} 
                onChange={(e) => {
                  const product = services.find(s => s.id === e.target.value);
                  setFormData({...formData, product_id: e.target.value, product_name: product?.name || ''});
                }}
                className="input-dark w-full"
              >
                <option value="">Sélectionner un produit</option>
                {services.filter(s => s.type === 'product').map(p => (
                  <option key={p.id} value={p.id}>{p.name}</option>
                ))}
              </select>
              <input type="number" placeholder="Quantité" value={formData.quantity} onChange={(e) => setFormData({...formData, quantity: parseInt(e.target.value)})} className="input-dark w-full" />
              <input type="number" placeholder="Quantité minimum" value={formData.min_quantity} onChange={(e) => setFormData({...formData, min_quantity: parseInt(e.target.value)})} className="input-dark w-full" />
              <div className="flex gap-2">
                <button onClick={() => setShowAdd(false)} className="btn-secondary flex-1">Annuler</button>
                <button onClick={addStock} className="btn-primary flex-1">Ajouter</button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Agenda Section Component
const AgendaSection = ({ agenda, onRefresh }) => {
  const [showAdd, setShowAdd] = useState(false);
  const [formData, setFormData] = useState({
    title: '', description: '', event_type: 'appointment', start_datetime: '', end_datetime: '', color: '#0047AB'
  });

  const addEvent = async () => {
    try {
      await agendaAPI.create(formData);
      toast.success('Événement ajouté');
      setShowAdd(false);
      setFormData({ title: '', description: '', event_type: 'appointment', start_datetime: '', end_datetime: '', color: '#0047AB' });
      onRefresh();
    } catch (error) {
      toast.error('Erreur');
    }
  };

  const deleteEvent = async (id) => {
    try {
      await agendaAPI.delete(id);
      toast.success('Événement supprimé');
      onRefresh();
    } catch (error) {
      toast.error('Erreur');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
          Agenda
        </h1>
        <button onClick={() => setShowAdd(true)} className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" /> Ajouter
        </button>
      </div>

      {agenda.length > 0 ? (
        <div className="space-y-3">
          {agenda.map((event) => (
            <div key={event.id} className="card-service rounded-xl p-4" style={{ borderLeftColor: event.color, borderLeftWidth: '4px' }}>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-white font-medium">{event.title}</p>
                  <p className="text-sm text-gray-400">
                    {new Date(event.start_datetime).toLocaleString('fr-FR')}
                  </p>
                  {event.client_name && <p className="text-sm text-[#0047AB]">Client: {event.client_name}</p>}
                </div>
                <button onClick={() => deleteEvent(event.id)} className="text-red-400 hover:text-red-300">
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="card-service rounded-xl p-12 text-center">
          <Calendar className="w-12 h-12 text-gray-500 mx-auto mb-4" />
          <p className="text-gray-400">Aucun événement</p>
        </div>
      )}

      {showAdd && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="card-service rounded-xl p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold text-white mb-4">Ajouter un événement</h3>
            <div className="space-y-4">
              <input type="text" placeholder="Titre" value={formData.title} onChange={(e) => setFormData({...formData, title: e.target.value})} className="input-dark w-full" />
              <select value={formData.event_type} onChange={(e) => setFormData({...formData, event_type: e.target.value})} className="input-dark w-full">
                <option value="appointment">Rendez-vous</option>
                <option value="availability">Disponibilité</option>
                <option value="blocked">Bloqué</option>
                <option value="task">Tâche</option>
              </select>
              <input type="datetime-local" value={formData.start_datetime} onChange={(e) => setFormData({...formData, start_datetime: e.target.value})} className="input-dark w-full" />
              <input type="datetime-local" value={formData.end_datetime} onChange={(e) => setFormData({...formData, end_datetime: e.target.value})} className="input-dark w-full" />
              <div className="flex gap-2">
                <button onClick={() => setShowAdd(false)} className="btn-secondary flex-1">Annuler</button>
                <button onClick={addEvent} className="btn-primary flex-1">Ajouter</button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Contacts Section Component
const ContactsSection = ({ contacts, onRefresh }) => {
  const [showAdd, setShowAdd] = useState(false);
  const [editingContact, setEditingContact] = useState(null);
  const [filterType, setFilterType] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [formData, setFormData] = useState({
    name: '', company: '', contact_type: 'client', email: '', phone: '', address: '', notes: '', tags: []
  });
  const [tagInput, setTagInput] = useState('');

  const contactTypes = [
    { id: 'client', label: 'Client', color: 'bg-green-500', icon: Users },
    { id: 'supplier', label: 'Fournisseur', color: 'bg-blue-500', icon: Truck },
    { id: 'partner', label: 'Partenaire', color: 'bg-purple-500', icon: Handshake },
    { id: 'other', label: 'Autre', color: 'bg-gray-500', icon: UserCircle }
  ];

  const resetForm = () => {
    setFormData({ name: '', company: '', contact_type: 'client', email: '', phone: '', address: '', notes: '', tags: [] });
    setTagInput('');
    setEditingContact(null);
    setShowAdd(false);
  };

  const addContact = async () => {
    if (!formData.name.trim()) {
      toast.error('Le nom est requis');
      return;
    }
    try {
      await enterpriseContactsAPI.create(formData);
      toast.success('Contact ajouté');
      resetForm();
      onRefresh();
    } catch (error) {
      toast.error('Erreur lors de l\'ajout');
    }
  };

  const updateContact = async () => {
    if (!formData.name.trim()) {
      toast.error('Le nom est requis');
      return;
    }
    try {
      await enterpriseContactsAPI.update(editingContact.id, formData);
      toast.success('Contact mis à jour');
      resetForm();
      onRefresh();
    } catch (error) {
      toast.error('Erreur lors de la mise à jour');
    }
  };

  const deleteContact = async (id) => {
    if (!window.confirm('Supprimer ce contact ?')) return;
    try {
      await enterpriseContactsAPI.delete(id);
      toast.success('Contact supprimé');
      onRefresh();
    } catch (error) {
      toast.error('Erreur lors de la suppression');
    }
  };

  const startEdit = (contact) => {
    setEditingContact(contact);
    setFormData({
      name: contact.name || '',
      company: contact.company || '',
      contact_type: contact.contact_type || 'client',
      email: contact.email || '',
      phone: contact.phone || '',
      address: contact.address || '',
      notes: contact.notes || '',
      tags: contact.tags || []
    });
    setShowAdd(true);
  };

  const addTag = () => {
    if (tagInput.trim() && !formData.tags.includes(tagInput.trim())) {
      setFormData({ ...formData, tags: [...formData.tags, tagInput.trim()] });
      setTagInput('');
    }
  };

  const removeTag = (tag) => {
    setFormData({ ...formData, tags: formData.tags.filter(t => t !== tag) });
  };

  const filteredContacts = (contacts.contacts || []).filter(c => {
    if (filterType && c.contact_type !== filterType) return false;
    if (searchTerm) {
      const search = searchTerm.toLowerCase();
      return c.name?.toLowerCase().includes(search) || 
             c.company?.toLowerCase().includes(search) ||
             c.email?.toLowerCase().includes(search);
    }
    return true;
  });

  const getTypeInfo = (type) => contactTypes.find(t => t.id === type) || contactTypes[3];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
          Contacts
        </h1>
        <button onClick={() => setShowAdd(true)} className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" /> Ajouter un contact
        </button>
      </div>

      {/* Stats by type */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {contactTypes.map(type => (
          <button
            key={type.id}
            onClick={() => setFilterType(filterType === type.id ? null : type.id)}
            className={`card-service rounded-xl p-4 text-left transition-all ${filterType === type.id ? 'ring-2 ring-[#0047AB]' : ''}`}
          >
            <div className={`w-10 h-10 ${type.color} rounded-lg flex items-center justify-center mb-2`}>
              <type.icon className="w-5 h-5 text-white" />
            </div>
            <p className="text-2xl font-bold text-white">{contacts.type_counts?.[type.id] || 0}</p>
            <p className="text-sm text-gray-400">{type.label}s</p>
          </button>
        ))}
      </div>

      {/* Search */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
        <input
          type="text"
          placeholder="Rechercher un contact..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="input-dark w-full pl-10"
        />
      </div>

      {/* Contact list */}
      {filteredContacts.length > 0 ? (
        <div className="space-y-3">
          {filteredContacts.map((contact) => {
            const typeInfo = getTypeInfo(contact.contact_type);
            return (
              <div key={contact.id} className="card-service rounded-xl p-4 hover:bg-white/5 transition-colors">
                <div className="flex items-start justify-between">
                  <div className="flex items-start gap-4">
                    <div className={`w-12 h-12 ${typeInfo.color} rounded-full flex items-center justify-center flex-shrink-0`}>
                      <span className="text-white font-bold text-lg">
                        {contact.name?.charAt(0)?.toUpperCase() || '?'}
                      </span>
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 flex-wrap">
                        <p className="text-white font-semibold">{contact.name}</p>
                        <span className={`px-2 py-0.5 ${typeInfo.color} rounded-full text-xs text-white`}>
                          {typeInfo.label}
                        </span>
                      </div>
                      {contact.company && (
                        <p className="text-gray-400 text-sm">{contact.company}</p>
                      )}
                      <div className="flex flex-wrap gap-4 mt-2 text-sm text-gray-400">
                        {contact.email && (
                          <a href={`mailto:${contact.email}`} className="flex items-center gap-1 hover:text-[#0047AB]">
                            <MessageSquare className="w-4 h-4" />
                            {contact.email}
                          </a>
                        )}
                        {contact.phone && (
                          <a href={`tel:${contact.phone}`} className="flex items-center gap-1 hover:text-green-400">
                            <Phone className="w-4 h-4" />
                            {contact.phone}
                          </a>
                        )}
                      </div>
                      {contact.tags?.length > 0 && (
                        <div className="flex flex-wrap gap-1 mt-2">
                          {contact.tags.map((tag, i) => (
                            <span key={i} className="px-2 py-0.5 bg-white/10 rounded text-xs text-gray-300">
                              {tag}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <button onClick={() => startEdit(contact)} className="p-2 hover:bg-white/10 rounded-lg text-gray-400 hover:text-white">
                      <Edit className="w-4 h-4" />
                    </button>
                    <button onClick={() => deleteContact(contact.id)} className="p-2 hover:bg-red-500/20 rounded-lg text-gray-400 hover:text-red-400">
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="card-service rounded-xl p-12 text-center">
          <Phone className="w-12 h-12 text-gray-500 mx-auto mb-4" />
          <p className="text-gray-400 mb-2">
            {searchTerm || filterType ? 'Aucun contact trouvé' : 'Aucun contact enregistré'}
          </p>
          <p className="text-sm text-gray-500">
            Ajoutez vos fournisseurs, partenaires et clients importants
          </p>
        </div>
      )}

      {/* Add/Edit Modal */}
      {showAdd && (
        <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-50 p-4">
          <div className="card-service rounded-xl p-6 w-full max-w-lg max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold text-white">
                {editingContact ? 'Modifier le contact' : 'Nouveau contact'}
              </h3>
              <button onClick={resetForm} className="p-2 hover:bg-white/10 rounded-lg">
                <X className="w-5 h-5 text-gray-400" />
              </button>
            </div>
            
            <div className="space-y-4">
              {/* Name */}
              <div>
                <label className="block text-sm text-gray-400 mb-1">Nom *</label>
                <input
                  type="text"
                  placeholder="Nom du contact"
                  value={formData.name}
                  onChange={(e) => setFormData({...formData, name: e.target.value})}
                  className="input-dark w-full"
                />
              </div>

              {/* Company */}
              <div>
                <label className="block text-sm text-gray-400 mb-1">Entreprise</label>
                <input
                  type="text"
                  placeholder="Nom de l'entreprise"
                  value={formData.company}
                  onChange={(e) => setFormData({...formData, company: e.target.value})}
                  className="input-dark w-full"
                />
              </div>

              {/* Type */}
              <div>
                <label className="block text-sm text-gray-400 mb-1">Type de contact</label>
                <div className="grid grid-cols-2 gap-2">
                  {contactTypes.map(type => (
                    <button
                      key={type.id}
                      type="button"
                      onClick={() => setFormData({...formData, contact_type: type.id})}
                      className={`p-3 rounded-lg flex items-center gap-2 transition-all ${
                        formData.contact_type === type.id
                          ? `${type.color} text-white`
                          : 'bg-white/5 text-gray-400 hover:bg-white/10'
                      }`}
                    >
                      <type.icon className="w-4 h-4" />
                      {type.label}
                    </button>
                  ))}
                </div>
              </div>

              {/* Email & Phone */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Email</label>
                  <input
                    type="email"
                    placeholder="email@exemple.com"
                    value={formData.email}
                    onChange={(e) => setFormData({...formData, email: e.target.value})}
                    className="input-dark w-full"
                  />
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Téléphone</label>
                  <input
                    type="tel"
                    placeholder="+41 21 123 45 67"
                    value={formData.phone}
                    onChange={(e) => setFormData({...formData, phone: e.target.value})}
                    className="input-dark w-full"
                  />
                </div>
              </div>

              {/* Address */}
              <div>
                <label className="block text-sm text-gray-400 mb-1">Adresse</label>
                <input
                  type="text"
                  placeholder="Adresse complète"
                  value={formData.address}
                  onChange={(e) => setFormData({...formData, address: e.target.value})}
                  className="input-dark w-full"
                />
              </div>

              {/* Tags */}
              <div>
                <label className="block text-sm text-gray-400 mb-1">Tags</label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    placeholder="Ajouter un tag"
                    value={tagInput}
                    onChange={(e) => setTagInput(e.target.value)}
                    onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addTag())}
                    className="input-dark flex-1"
                  />
                  <button type="button" onClick={addTag} className="btn-secondary px-4">
                    <Plus className="w-4 h-4" />
                  </button>
                </div>
                {formData.tags.length > 0 && (
                  <div className="flex flex-wrap gap-2 mt-2">
                    {formData.tags.map((tag, i) => (
                      <span key={i} className="px-2 py-1 bg-white/10 rounded flex items-center gap-1 text-sm text-gray-300">
                        {tag}
                        <button type="button" onClick={() => removeTag(tag)} className="hover:text-red-400">
                          <X className="w-3 h-3" />
                        </button>
                      </span>
                    ))}
                  </div>
                )}
              </div>

              {/* Notes */}
              <div>
                <label className="block text-sm text-gray-400 mb-1">Notes</label>
                <textarea
                  placeholder="Notes supplémentaires..."
                  value={formData.notes}
                  onChange={(e) => setFormData({...formData, notes: e.target.value})}
                  className="input-dark w-full h-24 resize-none"
                />
              </div>

              {/* Buttons */}
              <div className="flex gap-3 pt-4">
                <button onClick={resetForm} className="btn-secondary flex-1">
                  Annuler
                </button>
                <button 
                  onClick={editingContact ? updateContact : addContact} 
                  className="btn-primary flex-1"
                >
                  {editingContact ? 'Mettre à jour' : 'Ajouter'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Messages Section Component
const MessagesSection = () => {
  const [conversations, setConversations] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    fetchConversations();
  }, []);

  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  const fetchConversations = async () => {
    try {
      const res = await messagesAPI.getConversations();
      setConversations(res.data.conversations || []);
    } catch (error) {
      console.error('Error fetching conversations:', error);
    } finally {
      setLoading(false);
    }
  };

  const selectConversation = async (conv) => {
    setSelectedConversation(conv);
    try {
      const res = await messagesAPI.getMessages(conv.partner.id);
      setMessages(res.data.messages || []);
      // Refresh conversations to update unread count
      fetchConversations();
    } catch (error) {
      toast.error('Erreur lors du chargement des messages');
    }
  };

  const sendMessage = async () => {
    if (!newMessage.trim() || !selectedConversation) return;
    
    setSending(true);
    try {
      const res = await messagesAPI.send(selectedConversation.partner.id, newMessage.trim());
      setMessages([...messages, res.data]);
      setNewMessage('');
      fetchConversations();
    } catch (error) {
      toast.error('Erreur lors de l\'envoi');
    } finally {
      setSending(false);
    }
  };

  const formatTime = (dateStr) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diffDays = Math.floor((now - date) / (1000 * 60 * 60 * 24));
    
    if (diffDays === 0) {
      return date.toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' });
    } else if (diffDays === 1) {
      return 'Hier';
    } else if (diffDays < 7) {
      return date.toLocaleDateString('fr-FR', { weekday: 'short' });
    } else {
      return date.toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit' });
    }
  };

  const getInitial = (partner) => {
    if (!partner) return '?';
    return (partner.first_name || partner.business_name || '?').charAt(0).toUpperCase();
  };

  const getPartnerName = (partner) => {
    if (!partner) return 'Inconnu';
    if (partner.business_name) return partner.business_name;
    return `${partner.first_name || ''} ${partner.last_name || ''}`.trim() || 'Inconnu';
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="w-10 h-10 border-4 border-[#0047AB] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
        Messagerie
      </h1>

      <div className="card-service rounded-xl overflow-hidden" style={{ height: '600px' }}>
        <div className="flex h-full">
          {/* Conversation List */}
          <div className={`${selectedConversation ? 'hidden md:block' : ''} w-full md:w-1/3 border-r border-white/10 overflow-y-auto`}>
            {conversations.length > 0 ? (
              <div className="divide-y divide-white/10">
                {conversations.map((conv) => (
                  <button
                    key={conv.partner?.id}
                    onClick={() => selectConversation(conv)}
                    className={`w-full p-4 text-left hover:bg-white/5 transition-colors ${
                      selectedConversation?.partner?.id === conv.partner?.id ? 'bg-white/10' : ''
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-12 h-12 bg-gradient-to-br from-[#0047AB] to-[#D4AF37] rounded-full flex items-center justify-center flex-shrink-0">
                        <span className="text-white font-bold text-lg">
                          {getInitial(conv.partner)}
                        </span>
                      </div>
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center justify-between">
                          <p className="text-white font-medium truncate">
                            {getPartnerName(conv.partner)}
                          </p>
                          <span className="text-xs text-gray-500">
                            {formatTime(conv.last_message?.created_at)}
                          </span>
                        </div>
                        <div className="flex items-center justify-between">
                          <p className="text-sm text-gray-400 truncate pr-2">
                            {conv.last_message?.content || 'Pas de message'}
                          </p>
                          {conv.unread_count > 0 && (
                            <span className="bg-[#0047AB] text-white text-xs px-2 py-0.5 rounded-full">
                              {conv.unread_count}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            ) : (
              <div className="flex flex-col items-center justify-center h-full p-6 text-center">
                <MessageSquare className="w-12 h-12 text-gray-500 mb-4" />
                <p className="text-gray-400">Aucune conversation</p>
                <p className="text-sm text-gray-500 mt-1">
                  Vos échanges avec les clients apparaîtront ici
                </p>
              </div>
            )}
          </div>

          {/* Messages Area */}
          <div className={`${selectedConversation ? '' : 'hidden md:flex'} flex-1 flex flex-col`}>
            {selectedConversation ? (
              <>
                {/* Header */}
                <div className="p-4 border-b border-white/10 flex items-center gap-3">
                  <button 
                    onClick={() => setSelectedConversation(null)}
                    className="md:hidden p-2 hover:bg-white/10 rounded-lg"
                  >
                    <ChevronRight className="w-5 h-5 text-gray-400 rotate-180" />
                  </button>
                  <div className="w-10 h-10 bg-gradient-to-br from-[#0047AB] to-[#D4AF37] rounded-full flex items-center justify-center">
                    <span className="text-white font-bold">
                      {getInitial(selectedConversation.partner)}
                    </span>
                  </div>
                  <div>
                    <p className="text-white font-medium">
                      {getPartnerName(selectedConversation.partner)}
                    </p>
                    <p className="text-xs text-gray-400">
                      {selectedConversation.partner?.user_type === 'client' ? 'Client' : 'Utilisateur'}
                    </p>
                  </div>
                </div>

                {/* Messages */}
                <div className="flex-1 overflow-y-auto p-4 space-y-4">
                  {messages.map((msg) => {
                    const isOwn = msg.sender_id !== selectedConversation.partner?.id;
                    return (
                      <div
                        key={msg.id}
                        className={`flex ${isOwn ? 'justify-end' : 'justify-start'}`}
                      >
                        <div
                          className={`max-w-[70%] p-3 rounded-2xl ${
                            isOwn
                              ? 'bg-[#0047AB] text-white rounded-br-md'
                              : 'bg-white/10 text-white rounded-bl-md'
                          }`}
                        >
                          <p className="text-sm whitespace-pre-wrap">{msg.content}</p>
                          <p className={`text-xs mt-1 ${isOwn ? 'text-blue-200' : 'text-gray-500'}`}>
                            {formatTime(msg.created_at)}
                          </p>
                        </div>
                      </div>
                    );
                  })}
                  <div ref={messagesEndRef} />
                </div>

                {/* Input */}
                <div className="p-4 border-t border-white/10">
                  <div className="flex gap-2">
                    <input
                      type="text"
                      placeholder="Écrivez un message..."
                      value={newMessage}
                      onChange={(e) => setNewMessage(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && !e.shiftKey && sendMessage()}
                      className="input-dark flex-1"
                      disabled={sending}
                    />
                    <button
                      onClick={sendMessage}
                      disabled={!newMessage.trim() || sending}
                      className="btn-primary px-4 disabled:opacity-50"
                    >
                      <Send className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              </>
            ) : (
              <div className="flex flex-col items-center justify-center h-full p-6 text-center">
                <MessageSquare className="w-16 h-16 text-gray-500 mb-4" />
                <p className="text-gray-400 text-lg">Sélectionnez une conversation</p>
                <p className="text-sm text-gray-500 mt-1">
                  Choisissez une conversation dans la liste pour voir les messages
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

// Team Section Component
const TeamSection = ({ team, teamOrders, onDelete, onRefresh }) => {
  const [showAdd, setShowAdd] = useState(false);
  const [formData, setFormData] = useState({ first_name: '', last_name: '', email: '', phone: '', role: '', department: '' });

  const addMember = async () => {
    try {
      await teamAPI.add(formData);
      toast.success('Membre ajouté');
      setShowAdd(false);
      setFormData({ first_name: '', last_name: '', email: '', phone: '', role: '', department: '' });
      onRefresh();
    } catch (error) {
      toast.error('Erreur');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
          Mon équipe
        </h1>
        <button onClick={() => setShowAdd(true)} className="btn-primary flex items-center gap-2">
          <UserPlus className="w-4 h-4" /> Ajouter
        </button>
      </div>

      {team.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {team.map((member) => (
            <div key={member.id} className="card-service rounded-xl p-4">
              <div className="flex items-start justify-between mb-3">
                <div className="w-10 h-10 rounded-full bg-[#0047AB]/20 flex items-center justify-center text-[#0047AB] font-semibold">
                  {member.first_name[0]}{member.last_name[0]}
                </div>
                <button onClick={() => onDelete(member.id)} className="text-red-400 hover:text-red-300">
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
              <h3 className="text-white font-medium">{member.first_name} {member.last_name}</h3>
              <p className="text-sm text-[#D4AF37]">{member.role}</p>
              {member.department && <p className="text-xs text-gray-400">{member.department}</p>}
              {member.email && <p className="text-xs text-gray-400 mt-2">{member.email}</p>}
            </div>
          ))}
        </div>
      ) : (
        <div className="card-service rounded-xl p-12 text-center">
          <Users className="w-12 h-12 text-gray-500 mx-auto mb-4" />
          <p className="text-gray-400">Aucun membre d'équipe</p>
        </div>
      )}

      {showAdd && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="card-service rounded-xl p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold text-white mb-4">Ajouter un membre</h3>
            <div className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <input type="text" placeholder="Prénom" value={formData.first_name} onChange={(e) => setFormData({...formData, first_name: e.target.value})} className="input-dark w-full" />
                <input type="text" placeholder="Nom" value={formData.last_name} onChange={(e) => setFormData({...formData, last_name: e.target.value})} className="input-dark w-full" />
              </div>
              <input type="email" placeholder="Email" value={formData.email} onChange={(e) => setFormData({...formData, email: e.target.value})} className="input-dark w-full" />
              <input type="tel" placeholder="Téléphone" value={formData.phone} onChange={(e) => setFormData({...formData, phone: e.target.value})} className="input-dark w-full" />
              <input type="text" placeholder="Poste/Rôle" value={formData.role} onChange={(e) => setFormData({...formData, role: e.target.value})} className="input-dark w-full" />
              <input type="text" placeholder="Département" value={formData.department} onChange={(e) => setFormData({...formData, department: e.target.value})} className="input-dark w-full" />
              <div className="flex gap-2">
                <button onClick={() => setShowAdd(false)} className="btn-secondary flex-1">Annuler</button>
                <button onClick={addMember} className="btn-primary flex-1">Ajouter</button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Documents Section Component
const DocumentsSection = ({ documents, onDelete, onRefresh }) => {
  const [showAdd, setShowAdd] = useState(false);
  const [formData, setFormData] = useState({ title: '', category: 'other', file_url: '', file_type: 'pdf', is_important: false });

  const addDocument = async () => {
    try {
      await documentsAPI.add(formData);
      toast.success('Document ajouté');
      setShowAdd(false);
      onRefresh();
    } catch (error) {
      toast.error('Erreur');
    }
  };

  const categories = [
    { id: 'legal', name: 'Juridique', icon: FileText },
    { id: 'financial', name: 'Financier', icon: Wallet },
    { id: 'contract', name: 'Contrats', icon: ClipboardList },
    { id: 'certificate', name: 'Certificats', icon: CheckCircle },
    { id: 'other', name: 'Autre', icon: FolderOpen },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
          Documents
        </h1>
        <button onClick={() => setShowAdd(true)} className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" /> Ajouter
        </button>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        {categories.map((cat) => (
          <div key={cat.id} className="card-service rounded-xl p-4 text-center">
            <cat.icon className="w-8 h-8 text-[#0047AB] mx-auto mb-2" />
            <p className="text-white text-sm font-medium">{cat.name}</p>
            <p className="text-xs text-gray-400">{documents.filter(d => d.category === cat.id).length} fichier(s)</p>
          </div>
        ))}
      </div>

      {documents.length > 0 ? (
        <div className="space-y-3">
          {documents.map((doc) => (
            <div key={doc.id} className="card-service rounded-xl p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <FileText className="w-8 h-8 text-gray-400" />
                  <div>
                    <p className="text-white font-medium">{doc.title}</p>
                    <p className="text-xs text-gray-400">{doc.file_type.toUpperCase()} • {doc.category}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {doc.is_important && <Star className="w-4 h-4 text-[#D4AF37]" />}
                  <a href={doc.file_url} target="_blank" rel="noopener noreferrer" className="btn-secondary text-sm">Voir</a>
                  <button onClick={() => onDelete(doc.id)} className="text-red-400 hover:text-red-300">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="card-service rounded-xl p-12 text-center">
          <FolderOpen className="w-12 h-12 text-gray-500 mx-auto mb-4" />
          <p className="text-gray-400">Aucun document</p>
        </div>
      )}

      {showAdd && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="card-service rounded-xl p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold text-white mb-4">Ajouter un document</h3>
            <div className="space-y-4">
              <input type="text" placeholder="Titre" value={formData.title} onChange={(e) => setFormData({...formData, title: e.target.value})} className="input-dark w-full" />
              <select value={formData.category} onChange={(e) => setFormData({...formData, category: e.target.value})} className="input-dark w-full">
                {categories.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
              </select>
              <input type="url" placeholder="URL du fichier" value={formData.file_url} onChange={(e) => setFormData({...formData, file_url: e.target.value})} className="input-dark w-full" />
              <label className="flex items-center gap-2 text-gray-400">
                <input type="checkbox" checked={formData.is_important} onChange={(e) => setFormData({...formData, is_important: e.target.checked})} />
                Document important
              </label>
              <div className="flex gap-2">
                <button onClick={() => setShowAdd(false)} className="btn-secondary flex-1">Annuler</button>
                <button onClick={addDocument} className="btn-primary flex-1">Ajouter</button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Development Section Component
const DevelopmentSection = () => {
  const resources = [
    { id: '1', title: 'Guide du marketing digital', type: 'article', category: 'Marketing', duration: '15 min' },
    { id: '2', title: 'Optimisation fiscale pour entreprises', type: 'video', category: 'Finance', duration: '45 min' },
    { id: '3', title: 'Gestion de la relation client', type: 'course', category: 'Ventes', duration: '2 heures' },
    { id: '4', title: 'Réseaux sociaux pour les entreprises', type: 'webinar', category: 'Marketing', duration: '1 heure' },
  ];

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
        Développement & Formation
      </h1>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {resources.map((resource) => (
          <div key={resource.id} className="card-service rounded-xl p-4">
            <div className="flex items-start gap-4">
              <div className="w-12 h-12 rounded-lg bg-[#0047AB]/20 flex items-center justify-center">
                {resource.type === 'video' ? <PlayCircle className="w-6 h-6 text-[#0047AB]" /> : <BookOpen className="w-6 h-6 text-[#0047AB]" />}
              </div>
              <div className="flex-1">
                <h3 className="text-white font-medium">{resource.title}</h3>
                <p className="text-sm text-gray-400">{resource.category} • {resource.duration}</p>
                <span className="inline-block mt-2 px-2 py-1 bg-white/5 text-xs text-gray-400 rounded">{resource.type}</span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

// Finances Section Component
const FinancesSection = ({ finances, onRefresh }) => {
  const [showAdd, setShowAdd] = useState(false);
  const [formData, setFormData] = useState({ transaction_type: 'income', category: 'other', amount: 0, description: '', date: new Date().toISOString().split('T')[0] });

  const addTransaction = async () => {
    try {
      await financesAPI.addTransaction(formData);
      toast.success('Transaction ajoutée');
      setShowAdd(false);
      onRefresh();
    } catch (error) {
      toast.error('Erreur');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
          Finances
        </h1>
        <button onClick={() => setShowAdd(true)} className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" /> Transaction
        </button>
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="card-service rounded-xl p-4">
          <p className="text-sm text-gray-400 mb-1">Revenus totaux</p>
          <p className="text-2xl font-bold text-green-400">{finances.summary.total_income?.toFixed(2) || 0} CHF</p>
        </div>
        <div className="card-service rounded-xl p-4">
          <p className="text-sm text-gray-400 mb-1">Dépenses totales</p>
          <p className="text-2xl font-bold text-red-400">{finances.summary.total_expenses?.toFixed(2) || 0} CHF</p>
        </div>
        <div className="card-service rounded-xl p-4">
          <p className="text-sm text-gray-400 mb-1">Bénéfice net</p>
          <p className="text-2xl font-bold text-[#D4AF37]">{finances.summary.net_profit?.toFixed(2) || 0} CHF</p>
        </div>
        <div className="card-service rounded-xl p-4">
          <p className="text-sm text-gray-400 mb-1">Commissions Titelli</p>
          <p className="text-2xl font-bold text-gray-400">{finances.summary.commission_paid?.toFixed(2) || 0} CHF</p>
        </div>
      </div>

      {/* Transactions */}
      <div className="card-service rounded-xl p-6">
        <h2 className="text-lg font-semibold text-white mb-4">Dernières transactions</h2>
        {finances.transactions?.length > 0 ? (
          <div className="space-y-3">
            {finances.transactions.slice(0, 10).map((t) => (
              <div key={t.id} className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                <div>
                  <p className="text-white">{t.description}</p>
                  <p className="text-xs text-gray-400">{t.date} • {t.category}</p>
                </div>
                <p className={`font-semibold ${t.transaction_type === 'income' ? 'text-green-400' : 'text-red-400'}`}>
                  {t.transaction_type === 'income' ? '+' : '-'}{t.amount.toFixed(2)} CHF
                </p>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-400 text-center py-8">Aucune transaction</p>
        )}
      </div>

      {showAdd && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="card-service rounded-xl p-6 w-full max-w-md">
            <h3 className="text-lg font-semibold text-white mb-4">Ajouter une transaction</h3>
            <div className="space-y-4">
              <select value={formData.transaction_type} onChange={(e) => setFormData({...formData, transaction_type: e.target.value})} className="input-dark w-full">
                <option value="income">Revenu</option>
                <option value="expense">Dépense</option>
              </select>
              <input type="number" placeholder="Montant" value={formData.amount} onChange={(e) => setFormData({...formData, amount: parseFloat(e.target.value)})} className="input-dark w-full" />
              <input type="text" placeholder="Description" value={formData.description} onChange={(e) => setFormData({...formData, description: e.target.value})} className="input-dark w-full" />
              <input type="date" value={formData.date} onChange={(e) => setFormData({...formData, date: e.target.value})} className="input-dark w-full" />
              <div className="flex gap-2">
                <button onClick={() => setShowAdd(false)} className="btn-secondary flex-1">Annuler</button>
                <button onClick={addTransaction} className="btn-primary flex-1">Ajouter</button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Advertising Section Component
const AdvertisingSection = ({ advertising, onDelete, onRefresh }) => {
  const [showAdd, setShowAdd] = useState(false);
  const [payingAd, setPayingAd] = useState(null);
  const [formData, setFormData] = useState({
    title: '', ad_type: 'banner', placement: 'homepage', budget: 50,
    start_date: new Date().toISOString().split('T')[0],
    end_date: new Date(Date.now() + 30*24*60*60*1000).toISOString().split('T')[0],
    schedule_time: '12:00'
  });

  const adPrices = {
    banner: { name: 'Bannière', price: 50, desc: 'Bannière sur la page d\'accueil' },
    featured: { name: 'Mise en avant', price: 100, desc: 'Votre annonce en tête de liste' },
    spotlight: { name: 'Spotlight', price: 200, desc: 'Mise en lumière premium' },
    video: { name: 'Vidéo publicitaire', price: 150, desc: 'Vidéo de 3-9 secondes' },
    ia_clients: { name: 'IA Clients', price: 75, desc: 'Ciblage intelligent' },
    influencer: { name: 'Influenceurs', price: 250, desc: 'Partenariat influenceur' },
  };

  const createAd = async () => {
    try {
      const priceInfo = adPrices[formData.ad_type];
      const adData = {
        ...formData,
        budget: priceInfo?.price || formData.budget
      };
      const response = await advertisingAPI.create(adData);
      toast.success('Campagne créée - Procédez au paiement pour l\'activer');
      setShowAdd(false);
      setPayingAd(response.data);
      onRefresh();
    } catch (error) {
      toast.error('Erreur lors de la création');
    }
  };

  const handlePayment = async (adId) => {
    try {
      const response = await advertisingAPI.pay(adId);
      if (response.data.checkout_url) {
        // Open Stripe checkout in new tab
        window.open(response.data.checkout_url, '_blank');
        toast.success('Redirection vers le paiement...');
      }
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erreur lors du paiement');
    }
  };

  const handleToggle = async (adId, isPaid) => {
    if (!isPaid) {
      toast.error('Vous devez payer cette publicité avant de l\'activer');
      return;
    }
    try {
      await advertisingAPI.toggle(adId);
      toast.success('Statut modifié');
      onRefresh();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erreur');
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
          Mes publicités
        </h1>
        <button onClick={() => setShowAdd(true)} className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" /> Nouvelle campagne
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="card-service rounded-xl p-4">
          <p className="text-sm text-gray-400 mb-1">Campagnes actives</p>
          <p className="text-2xl font-bold text-[#0047AB]">{advertising.stats?.active_campaigns || 0}</p>
        </div>
        <div className="card-service rounded-xl p-4">
          <p className="text-sm text-gray-400 mb-1">Impressions</p>
          <p className="text-2xl font-bold text-white">{advertising.stats?.total_impressions || 0}</p>
        </div>
        <div className="card-service rounded-xl p-4">
          <p className="text-sm text-gray-400 mb-1">Clics</p>
          <p className="text-2xl font-bold text-green-400">{advertising.stats?.total_clicks || 0}</p>
        </div>
        <div className="card-service rounded-xl p-4">
          <p className="text-sm text-gray-400 mb-1">Budget dépensé</p>
          <p className="text-2xl font-bold text-[#D4AF37]">{advertising.stats?.total_spent || 0} CHF</p>
        </div>
      </div>

      {/* Ad Types Selection */}
      <div className="card-service rounded-xl p-6">
        <h2 className="text-lg font-semibold text-white mb-4">Types de publicité disponibles</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Object.entries(adPrices).map(([type, info]) => (
            <div key={type} className="p-4 bg-white/5 rounded-xl hover:bg-white/10 transition-colors cursor-pointer border border-transparent hover:border-[#0047AB]/50"
                 onClick={() => { setFormData({...formData, ad_type: type, budget: info.price}); setShowAdd(true); }}>
              <div className="flex items-center justify-between mb-2">
                <p className="text-white font-medium">{info.name}</p>
                <span className="text-[#D4AF37] font-bold">{info.price} CHF</span>
              </div>
              <p className="text-sm text-gray-400">{info.desc}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Campaigns List */}
      {advertising.campaigns?.length > 0 ? (
        <div className="space-y-3">
          <h2 className="text-lg font-semibold text-white">Mes campagnes</h2>
          {advertising.campaigns.map((campaign) => (
            <div key={campaign.id} className="card-service rounded-xl p-4">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-1">
                    <p className="text-white font-medium">{campaign.title}</p>
                    {!campaign.is_paid && (
                      <span className="px-2 py-0.5 rounded-full text-xs bg-red-500/20 text-red-400">
                        Non payée
                      </span>
                    )}
                  </div>
                  <p className="text-sm text-gray-400">{adPrices[campaign.ad_type]?.name || campaign.ad_type} • {campaign.placement} • {campaign.budget || 0} CHF</p>
                </div>
                <div className="flex items-center gap-3">
                  {!campaign.is_paid ? (
                    <button 
                      onClick={() => handlePayment(campaign.id)} 
                      className="px-4 py-2 bg-[#D4AF37] text-black rounded-lg text-sm font-medium hover:bg-[#B8860B] transition-colors flex items-center gap-2"
                    >
                      <CreditCard className="w-4 h-4" />
                      Payer pour activer
                    </button>
                  ) : (
                    <button 
                      onClick={() => handleToggle(campaign.id, campaign.is_paid)}
                      className={`px-3 py-1.5 rounded-lg text-sm flex items-center gap-2 ${
                        campaign.is_active 
                          ? 'bg-green-500/20 text-green-400 hover:bg-green-500/30' 
                          : 'bg-gray-500/20 text-gray-400 hover:bg-gray-500/30'
                      }`}
                    >
                      {campaign.is_active ? <PlayCircle className="w-4 h-4" /> : <Pause className="w-4 h-4" />}
                      {campaign.is_active ? 'Active' : 'Inactive'}
                    </button>
                  )}
                  <button onClick={() => onDelete(campaign.id)} className="text-red-400 hover:text-red-300 p-2">
                    <Trash2 className="w-4 h-4" />
                  </button>
                </div>
              </div>
              {campaign.is_paid && (
                <div className="mt-3 pt-3 border-t border-white/10 flex gap-6 text-sm">
                  <div>
                    <span className="text-gray-500">Impressions:</span>
                    <span className="text-white ml-2">{campaign.impressions || 0}</span>
                  </div>
                  <div>
                    <span className="text-gray-500">Clics:</span>
                    <span className="text-white ml-2">{campaign.clicks || 0}</span>
                  </div>
                  <div>
                    <span className="text-gray-500">CTR:</span>
                    <span className="text-white ml-2">{campaign.impressions > 0 ? ((campaign.clicks / campaign.impressions) * 100).toFixed(1) : 0}%</span>
                  </div>
                </div>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="card-service rounded-xl p-12 text-center">
          <Megaphone className="w-12 h-12 text-gray-500 mx-auto mb-4" />
          <p className="text-gray-400 mb-2">Aucune campagne publicitaire</p>
          <p className="text-sm text-gray-500">Créez votre première campagne pour augmenter votre visibilité</p>
        </div>
      )}

      {/* Create Ad Modal */}
      {showAdd && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="card-service rounded-xl p-6 w-full max-w-lg max-h-[90vh] overflow-y-auto">
            <h3 className="text-lg font-semibold text-white mb-4">Nouvelle campagne publicitaire</h3>
            
            <div className="space-y-4">
              {/* Selected Ad Type Info */}
              <div className="p-4 bg-[#0047AB]/10 border border-[#0047AB]/30 rounded-xl">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-white font-medium">{adPrices[formData.ad_type]?.name}</p>
                    <p className="text-sm text-gray-400">{adPrices[formData.ad_type]?.desc}</p>
                  </div>
                  <p className="text-2xl font-bold text-[#D4AF37]">{adPrices[formData.ad_type]?.price} CHF</p>
                </div>
              </div>

              <div>
                <label className="block text-sm text-gray-400 mb-1">Titre de la campagne *</label>
                <input type="text" placeholder="Ex: Promotion été 2026" value={formData.title} onChange={(e) => setFormData({...formData, title: e.target.value})} className="input-dark w-full" />
              </div>

              <div>
                <label className="block text-sm text-gray-400 mb-1">Type de publicité *</label>
                <select value={formData.ad_type} onChange={(e) => setFormData({...formData, ad_type: e.target.value, budget: adPrices[e.target.value]?.price || 50})} className="input-dark w-full">
                  {Object.entries(adPrices).map(([type, info]) => (
                    <option key={type} value={type}>{info.name} - {info.price} CHF</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm text-gray-400 mb-1">Emplacement *</label>
                <select value={formData.placement} onChange={(e) => setFormData({...formData, placement: e.target.value})} className="input-dark w-full">
                  <option value="homepage">Page d'accueil</option>
                  <option value="category">Page catégorie</option>
                  <option value="search">Résultats recherche</option>
                  <option value="sidebar">Barre latérale</option>
                  <option value="feed">Fil d'actualité</option>
                </select>
              </div>

              <div>
                <label className="block text-sm text-gray-400 mb-1">Horaire de diffusion</label>
                <select value={formData.schedule_time} onChange={(e) => setFormData({...formData, schedule_time: e.target.value})} className="input-dark w-full">
                  <option value="all_day">Toute la journée</option>
                  <option value="morning">Matin (6h-12h)</option>
                  <option value="afternoon">Après-midi (12h-18h)</option>
                  <option value="evening">Soir (18h-23h)</option>
                  <option value="peak">Heures de pointe (12h-14h, 18h-20h)</option>
                </select>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Date de début</label>
                  <input type="date" value={formData.start_date} onChange={(e) => setFormData({...formData, start_date: e.target.value})} className="input-dark w-full" />
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Date de fin</label>
                  <input type="date" value={formData.end_date} onChange={(e) => setFormData({...formData, end_date: e.target.value})} className="input-dark w-full" />
                </div>
              </div>

              <div className="p-3 bg-yellow-500/10 border border-yellow-500/30 rounded-lg">
                <p className="text-sm text-yellow-400">
                  <strong>Note :</strong> Votre publicité sera créée mais inactive. Vous devrez procéder au paiement pour l'activer.
                </p>
              </div>

              <div className="flex gap-2 pt-2">
                <button onClick={() => setShowAdd(false)} className="btn-secondary flex-1">Annuler</button>
                <button onClick={createAd} disabled={!formData.title} className="btn-primary flex-1 disabled:opacity-50">
                  Créer la campagne
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Form Modal Component for adding items
const FormModal = ({ type, item, onClose, onSuccess }) => {
  const [formData, setFormData] = useState(() => {
    // Initialiser avec des valeurs par défaut selon le type
    switch(type) {
      case 'service':
        return { type: 'service', category: 'soins_esthetiques', is_delivery: false, images: [] };
      case 'offer':
        return { discount_type: 'percentage', is_active: true };
      case 'training':
        return { training_type: 'on_site', category: 'Marketing', downloadable_files: [] };
      case 'job':
        return { job_type: 'full_time', location: 'Lausanne' };
      case 'realestate':
        return { property_type: 'commercial', city: 'Lausanne', transaction_type: 'rent', price_period: 'month' };
      case 'investment':
        return { risk_level: 'medium', investment_type: 'equity' };
      default:
        return {};
    }
  });
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [imagePreview, setImagePreview] = useState(null);
  const fileInputRef = useRef(null);
  const trainingFileInputRef = useRef(null);

  const serviceCategories = [
    { id: 'restauration', name: 'Restauration' },
    { id: 'soins_esthetiques', name: 'Soins esthétiques' },
    { id: 'coiffure_barber', name: 'Coiffure/Barber' },
    { id: 'cours_sport', name: 'Cours de sport' },
    { id: 'activites_loisirs', name: 'Loisirs & Événements' },
    { id: 'nettoyage', name: 'Nettoyage' },
    { id: 'multiservices', name: 'Multiservices' },
    { id: 'petits_travaux', name: 'Petits travaux' },
    { id: 'formation', name: 'Formation' },
    { id: 'sante', name: 'Santé' },
    { id: 'expert_tech', name: 'Technologie' },
    { id: 'expert_fiscal', name: 'Fiscalité' },
    { id: 'expert_juridique', name: 'Juridique' },
  ];

  const productCategories = [
    { id: 'courses_alimentaires', name: 'Alimentaire' },
    { id: 'vetements_mode', name: 'Vêtements & Mode' },
    { id: 'maquillage_beaute', name: 'Beauté' },
    { id: 'sport', name: 'Sport' },
    { id: 'electronique', name: 'Électronique' },
    { id: 'ameublement_deco', name: 'Décoration' },
    { id: 'bricolage_jardinage', name: 'Bricolage' },
  ];

  const handleImageUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
      toast.error('Type de fichier non autorisé. Utilisez JPG, PNG, GIF ou WEBP.');
      return;
    }

    // Validate file size (5MB max)
    if (file.size > 5 * 1024 * 1024) {
      toast.error('Fichier trop volumineux (max 5MB)');
      return;
    }

    // Show preview
    const reader = new FileReader();
    reader.onloadend = () => {
      setImagePreview(reader.result);
    };
    reader.readAsDataURL(file);

    // Upload file
    setUploading(true);
    try {
      const response = await uploadAPI.uploadImage(file);
      const imageUrl = process.env.REACT_APP_BACKEND_URL + response.data.url;
      setFormData(prev => ({ ...prev, images: [imageUrl] }));
      toast.success('Image uploadée !');
    } catch (error) {
      console.error('Upload error:', error);
      toast.error('Erreur lors de l\'upload de l\'image');
      setImagePreview(null);
    } finally {
      setUploading(false);
    }
  };

  const removeImage = () => {
    setImagePreview(null);
    setFormData(prev => ({ ...prev, images: [] }));
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const handleSubmit = async () => {
    setLoading(true);
    try {
      switch(type) {
        case 'offer':
          if (!formData.title) throw new Error('Titre requis');
          await offersAPI.create({ ...formData, discount_type: 'percentage', is_active: true });
          break;
        case 'training':
          if (!formData.title) throw new Error('Titre requis');
          await trainingsAPI.create({ ...formData, category: formData.category || 'Marketing' });
          break;
        case 'job':
          if (!formData.title) throw new Error('Titre requis');
          await jobsAPI.create(formData);
          break;
        case 'realestate':
          if (!formData.title) throw new Error('Titre requis');
          await realEstateAPI.create({ ...formData, city: formData.city || 'Lausanne' });
          break;
        case 'investment':
          if (!formData.title) throw new Error('Titre requis');
          await investmentsAPI.create({ ...formData, investment_type: formData.investment_type || 'equity' });
          break;
        case 'service':
          if (!enterprise) throw new Error('Veuillez d\'abord créer votre profil entreprise dans la section "Mon Entreprise"');
          if (!formData.name) throw new Error('Nom requis');
          if (!formData.description) throw new Error('Description requise');
          if (!formData.price) throw new Error('Prix requis');
          await servicesProductsAPI.create({ 
            ...formData, 
            currency: 'CHF',
            category: formData.category || 'soins_esthetiques',
            type: formData.type || 'service',
            images: formData.images || []
          });
          break;
        default:
          break;
      }
      toast.success('Créé avec succès !');
      onSuccess();
    } catch (error) {
      console.error('Error creating:', error);
      // Afficher le message d'erreur du serveur si disponible
      const errorMessage = error.response?.data?.detail || error.message || 'Erreur lors de la création';
      toast.error(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  // Image Upload Component
  const ImageUploadSection = () => (
    <div className="mb-4">
      <label className="block text-sm text-gray-400 mb-2">Image de l'annonce</label>
      <div className="border-2 border-dashed border-white/20 rounded-xl p-4 text-center hover:border-[#0047AB]/50 transition-colors">
        {imagePreview || (formData.images && formData.images.length > 0) ? (
          <div className="relative inline-block">
            <img 
              src={imagePreview || formData.images[0]} 
              alt="Aperçu" 
              className="max-h-48 rounded-lg object-cover mx-auto"
            />
            <button
              type="button"
              onClick={removeImage}
              className="absolute -top-2 -right-2 w-6 h-6 bg-red-500 text-white rounded-full flex items-center justify-center hover:bg-red-600 transition-colors"
            >
              <X className="w-4 h-4" />
            </button>
            {uploading && (
              <div className="absolute inset-0 bg-black/50 rounded-lg flex items-center justify-center">
                <div className="w-8 h-8 border-2 border-white border-t-transparent rounded-full animate-spin" />
              </div>
            )}
          </div>
        ) : (
          <label className="cursor-pointer block">
            <input
              ref={fileInputRef}
              type="file"
              accept="image/jpeg,image/png,image/gif,image/webp"
              onChange={handleImageUpload}
              className="hidden"
            />
            <div className="py-6">
              <Upload className="w-10 h-10 text-gray-500 mx-auto mb-2" />
              <p className="text-gray-400 text-sm">Cliquez pour choisir une image</p>
              <p className="text-gray-500 text-xs mt-1">JPG, PNG, GIF ou WEBP (max 5MB)</p>
            </div>
          </label>
        )}
      </div>
    </div>
  );

  const renderForm = () => {
    switch(type) {
      case 'offer':
        return (
          <>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Titre de l'offre *</label>
              <input type="text" placeholder="Ex: Promotion été -20%" value={formData.title || ''} onChange={(e) => setFormData({...formData, title: e.target.value})} className="input-dark w-full" required />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Description</label>
              <textarea placeholder="Décrivez votre offre" value={formData.description || ''} onChange={(e) => setFormData({...formData, description: e.target.value})} className="input-dark w-full" rows={3} />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Réduction (%) *</label>
              <input type="number" placeholder="Ex: 20" min="1" max="100" value={formData.discount_value || ''} onChange={(e) => setFormData({...formData, discount_value: parseFloat(e.target.value)})} className="input-dark w-full" required />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">Date début</label>
                <input type="date" value={formData.valid_from || ''} onChange={(e) => setFormData({...formData, valid_from: e.target.value})} className="input-dark w-full" />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Date fin</label>
                <input type="date" value={formData.valid_until || ''} onChange={(e) => setFormData({...formData, valid_until: e.target.value})} className="input-dark w-full" />
              </div>
            </div>
          </>
        );
      case 'training':
        return (
          <>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Titre de la formation *</label>
              <input type="text" placeholder="Ex: Formation Marketing Digital" value={formData.title || ''} onChange={(e) => setFormData({...formData, title: e.target.value})} className="input-dark w-full" required />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Description *</label>
              <textarea placeholder="Décrivez le contenu de la formation" value={formData.description || ''} onChange={(e) => setFormData({...formData, description: e.target.value})} className="input-dark w-full" rows={3} required />
            </div>
            
            {/* Training Type Selection */}
            <div>
              <label className="block text-sm text-gray-400 mb-2">Type de formation *</label>
              <div className="grid grid-cols-2 gap-3">
                <button
                  type="button"
                  onClick={() => setFormData({...formData, training_type: 'online'})}
                  className={`p-4 rounded-xl border-2 transition-all ${formData.training_type === 'online' ? 'border-[#0047AB] bg-[#0047AB]/20' : 'border-white/10 hover:border-white/30'}`}
                >
                  <div className="text-2xl mb-2">💻</div>
                  <p className="text-white font-medium">En ligne</p>
                  <p className="text-xs text-gray-400 mt-1">Fichiers téléchargeables</p>
                </button>
                <button
                  type="button"
                  onClick={() => setFormData({...formData, training_type: 'on_site'})}
                  className={`p-4 rounded-xl border-2 transition-all ${formData.training_type === 'on_site' ? 'border-[#0047AB] bg-[#0047AB]/20' : 'border-white/10 hover:border-white/30'}`}
                >
                  <div className="text-2xl mb-2">🏢</div>
                  <p className="text-white font-medium">Présentiel</p>
                  <p className="text-xs text-gray-400 mt-1">Sur site avec dates</p>
                </button>
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">Durée *</label>
                <input type="text" placeholder="Ex: 2 heures" value={formData.duration || ''} onChange={(e) => setFormData({...formData, duration: e.target.value})} className="input-dark w-full" required />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Prix (CHF) *</label>
                <input type="number" placeholder="Ex: 150" min="0" value={formData.price || ''} onChange={(e) => setFormData({...formData, price: parseFloat(e.target.value)})} className="input-dark w-full" required />
              </div>
            </div>
            
            {/* On-site specific fields */}
            {formData.training_type === 'on_site' && (
              <>
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Lieu de la formation</label>
                  <input type="text" placeholder="Ex: Centre de formation, Lausanne" value={formData.location || ''} onChange={(e) => setFormData({...formData, location: e.target.value})} className="input-dark w-full" />
                </div>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm text-gray-400 mb-1">Date de début</label>
                    <input type="date" value={formData.start_date || ''} onChange={(e) => setFormData({...formData, start_date: e.target.value})} className="input-dark w-full" />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-400 mb-1">Date de fin</label>
                    <input type="date" value={formData.end_date || ''} onChange={(e) => setFormData({...formData, end_date: e.target.value})} className="input-dark w-full" />
                  </div>
                </div>
                <div>
                  <label className="block text-sm text-gray-400 mb-1">Nombre max. de participants</label>
                  <input type="number" placeholder="Ex: 20" min="1" value={formData.max_participants || ''} onChange={(e) => setFormData({...formData, max_participants: parseInt(e.target.value)})} className="input-dark w-full" />
                </div>
              </>
            )}

            {/* Online specific fields - File uploads */}
            {formData.training_type === 'online' && (
              <div>
                <label className="block text-sm text-gray-400 mb-2">Fichiers téléchargeables (vidéos, PDF, images)</label>
                <div className="border-2 border-dashed border-white/20 rounded-xl p-4">
                  {formData.downloadable_files && formData.downloadable_files.length > 0 && (
                    <div className="space-y-2 mb-4">
                      {formData.downloadable_files.map((file, idx) => (
                        <div key={idx} className="flex items-center justify-between bg-white/5 rounded-lg p-3">
                          <div className="flex items-center gap-3">
                            <span className="text-xl">
                              {file.type?.includes('video') ? '🎬' : file.type?.includes('pdf') ? '📄' : file.type?.includes('image') ? '🖼️' : '📁'}
                            </span>
                            <span className="text-white text-sm truncate max-w-[200px]">{file.name}</span>
                          </div>
                          <button
                            type="button"
                            onClick={() => {
                              const newFiles = formData.downloadable_files.filter((_, i) => i !== idx);
                              setFormData({...formData, downloadable_files: newFiles});
                            }}
                            className="text-red-400 hover:text-red-300"
                          >
                            <X className="w-4 h-4" />
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                  <input
                    ref={trainingFileInputRef}
                    type="file"
                    accept="video/*,application/pdf,image/*,.doc,.docx,.ppt,.pptx"
                    multiple
                    className="hidden"
                    onChange={async (e) => {
                      const files = Array.from(e.target.files);
                      setUploading(true);
                      try {
                        const uploadPromises = files.map(async (file) => {
                          const formDataUpload = new FormData();
                          formDataUpload.append('file', file);
                          const res = await uploadAPI.uploadImage(file);
                          return {
                            name: file.name,
                            url: res.data.url,
                            type: file.type
                          };
                        });
                        const uploadedFiles = await Promise.all(uploadPromises);
                        setFormData({
                          ...formData,
                          downloadable_files: [...(formData.downloadable_files || []), ...uploadedFiles]
                        });
                        toast.success(`${files.length} fichier(s) uploadé(s)`);
                      } catch (err) {
                        toast.error('Erreur lors de l\'upload');
                      } finally {
                        setUploading(false);
                      }
                    }}
                  />
                  <button
                    type="button"
                    onClick={() => trainingFileInputRef.current?.click()}
                    disabled={uploading}
                    className="w-full py-3 border border-white/20 rounded-lg text-gray-400 hover:text-white hover:border-[#0047AB] transition-colors flex items-center justify-center gap-2"
                  >
                    {uploading ? (
                      <>
                        <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                        Upload en cours...
                      </>
                    ) : (
                      <>
                        <Upload className="w-4 h-4" />
                        Ajouter des fichiers
                      </>
                    )}
                  </button>
                  <p className="text-xs text-gray-500 mt-2 text-center">Vidéos, PDF, Images, Documents (max 50MB chacun)</p>
                </div>
              </div>
            )}

            <div>
              <label className="block text-sm text-gray-400 mb-1">Catégorie</label>
              <select value={formData.category || 'Marketing'} onChange={(e) => setFormData({...formData, category: e.target.value})} className="input-dark w-full">
                <option value="Marketing">Marketing</option>
                <option value="Finance">Finance</option>
                <option value="Management">Management</option>
                <option value="Ventes">Ventes</option>
                <option value="Technologie">Technologie</option>
                <option value="Communication">Communication</option>
                <option value="Développement personnel">Développement personnel</option>
                <option value="Langues">Langues</option>
              </select>
            </div>
            
            <div>
              <label className="block text-sm text-gray-400 mb-1">Prérequis (optionnel)</label>
              <input type="text" placeholder="Ex: Connaissances de base en marketing" value={formData.prerequisites || ''} onChange={(e) => setFormData({...formData, prerequisites: e.target.value})} className="input-dark w-full" />
            </div>
            
            <label className="flex items-center gap-2 text-gray-400">
              <input type="checkbox" checked={formData.certificate || false} onChange={(e) => setFormData({...formData, certificate: e.target.checked})} className="rounded" /> Certificat délivré
            </label>
          </>
        );
      case 'job':
        return (
          <>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Titre du poste *</label>
              <input type="text" placeholder="Ex: Développeur Web" value={formData.title || ''} onChange={(e) => setFormData({...formData, title: e.target.value})} className="input-dark w-full" required />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Description *</label>
              <textarea placeholder="Décrivez le poste et les responsabilités" value={formData.description || ''} onChange={(e) => setFormData({...formData, description: e.target.value})} className="input-dark w-full" rows={3} required />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">Type de contrat *</label>
                <select value={formData.job_type || 'full_time'} onChange={(e) => setFormData({...formData, job_type: e.target.value})} className="input-dark w-full">
                  <option value="full_time">Temps plein</option>
                  <option value="part_time">Temps partiel</option>
                  <option value="freelance">Freelance</option>
                  <option value="internship">Stage</option>
                </select>
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Lieu *</label>
                <input type="text" placeholder="Ex: Lausanne" value={formData.location || 'Lausanne'} onChange={(e) => setFormData({...formData, location: e.target.value})} className="input-dark w-full" required />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">Salaire min (CHF)</label>
                <input type="number" placeholder="Ex: 4000" min="0" value={formData.salary_min || ''} onChange={(e) => setFormData({...formData, salary_min: parseFloat(e.target.value) || null})} className="input-dark w-full" />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Salaire max (CHF)</label>
                <input type="number" placeholder="Ex: 6000" min="0" value={formData.salary_max || ''} onChange={(e) => setFormData({...formData, salary_max: parseFloat(e.target.value) || null})} className="input-dark w-full" />
              </div>
            </div>
          </>
        );
      case 'realestate':
        return (
          <>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Titre *</label>
              <input type="text" placeholder="Ex: Bureau moderne centre-ville" value={formData.title || ''} onChange={(e) => setFormData({...formData, title: e.target.value})} className="input-dark w-full" required />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Description *</label>
              <textarea placeholder="Décrivez le bien immobilier" value={formData.description || ''} onChange={(e) => setFormData({...formData, description: e.target.value})} className="input-dark w-full" rows={3} required />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">Type de bien *</label>
                <select value={formData.property_type || 'commercial'} onChange={(e) => setFormData({...formData, property_type: e.target.value})} className="input-dark w-full">
                  <option value="commercial">Commercial</option>
                  <option value="office">Bureau</option>
                  <option value="storage">Stockage</option>
                  <option value="land">Terrain</option>
                  <option value="apartment">Appartement</option>
                </select>
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Transaction *</label>
                <select value={formData.transaction_type || 'rent'} onChange={(e) => setFormData({...formData, transaction_type: e.target.value})} className="input-dark w-full">
                  <option value="rent">Location</option>
                  <option value="sale">Vente</option>
                </select>
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">Surface (m²) *</label>
                <input type="number" placeholder="Ex: 80" min="1" value={formData.surface || ''} onChange={(e) => setFormData({...formData, surface: parseFloat(e.target.value)})} className="input-dark w-full" required />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Prix (CHF) *</label>
                <input type="number" placeholder="Ex: 2500" min="0" value={formData.price || ''} onChange={(e) => setFormData({...formData, price: parseFloat(e.target.value)})} className="input-dark w-full" required />
              </div>
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Adresse *</label>
              <input type="text" placeholder="Ex: Rue du Grand-Pont 12" value={formData.address || ''} onChange={(e) => setFormData({...formData, address: e.target.value})} className="input-dark w-full" required />
            </div>
          </>
        );
      case 'investment':
        return (
          <>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Titre *</label>
              <input type="text" placeholder="Ex: Expansion du restaurant" value={formData.title || ''} onChange={(e) => setFormData({...formData, title: e.target.value})} className="input-dark w-full" required />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Description *</label>
              <textarea placeholder="Décrivez l'opportunité d'investissement" value={formData.description || ''} onChange={(e) => setFormData({...formData, description: e.target.value})} className="input-dark w-full" rows={3} required />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">Investissement min (CHF) *</label>
                <input type="number" placeholder="Ex: 5000" min="1" value={formData.min_investment || ''} onChange={(e) => setFormData({...formData, min_investment: parseFloat(e.target.value)})} className="input-dark w-full" required />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Retour attendu (%) *</label>
                <input type="number" placeholder="Ex: 8" min="0" step="0.1" value={formData.expected_return || ''} onChange={(e) => setFormData({...formData, expected_return: parseFloat(e.target.value)})} className="input-dark w-full" required />
              </div>
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">Type d'investissement</label>
                <select value={formData.investment_type || 'equity'} onChange={(e) => setFormData({...formData, investment_type: e.target.value})} className="input-dark w-full">
                  <option value="equity">Capital</option>
                  <option value="loan">Prêt</option>
                  <option value="revenue_share">Partage de revenus</option>
                </select>
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Niveau de risque *</label>
                <select value={formData.risk_level || 'medium'} onChange={(e) => setFormData({...formData, risk_level: e.target.value})} className="input-dark w-full">
                  <option value="low">Risque faible</option>
                  <option value="medium">Risque moyen</option>
                  <option value="high">Risque élevé</option>
                </select>
              </div>
            </div>
          </>
        );
      case 'service':
        return (
          <>
            <ImageUploadSection />
            <div>
              <label className="block text-sm text-gray-400 mb-1">Nom du service/produit *</label>
              <input type="text" placeholder="Ex: Massage relaxant 60 min" value={formData.name || ''} onChange={(e) => setFormData({...formData, name: e.target.value})} className="input-dark w-full" required />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Description *</label>
              <textarea placeholder="Décrivez votre service ou produit en détail" value={formData.description || ''} onChange={(e) => setFormData({...formData, description: e.target.value})} className="input-dark w-full" rows={3} required />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">Type *</label>
                <select value={formData.type || 'service'} onChange={(e) => setFormData({...formData, type: e.target.value})} className="input-dark w-full">
                  <option value="service">Service</option>
                  <option value="product">Produit</option>
                </select>
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Catégorie *</label>
                <select value={formData.category || 'soins_esthetiques'} onChange={(e) => setFormData({...formData, category: e.target.value})} className="input-dark w-full">
                  {(formData.type === 'product' ? productCategories : serviceCategories).map(cat => (
                    <option key={cat.id} value={cat.id}>{cat.name}</option>
                  ))}
                </select>
              </div>
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-1">Prix (CHF) *</label>
              <input type="number" placeholder="Ex: 120" min="0" step="0.01" value={formData.price || ''} onChange={(e) => setFormData({...formData, price: parseFloat(e.target.value)})} className="input-dark w-full" required />
            </div>
            <label className="flex items-center gap-2 text-gray-400">
              <input type="checkbox" checked={formData.is_delivery || false} onChange={(e) => setFormData({...formData, is_delivery: e.target.checked})} className="rounded" /> Livraison disponible
            </label>
          </>
        );
      default:
        return null;
    }
  };

  const titles = {
    offer: 'Nouvelle offre',
    training: 'Nouvelle formation',
    job: 'Nouvelle offre d\'emploi',
    realestate: 'Nouveau bien immobilier',
    investment: 'Nouvel investissement',
    service: 'Nouveau service/produit',
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="card-service rounded-xl p-6 w-full max-w-md max-h-[90vh] overflow-y-auto">
        <h3 className="text-lg font-semibold text-white mb-4">{titles[type]}</h3>
        <div className="space-y-4">
          {renderForm()}
          <div className="flex gap-2 pt-4">
            <button onClick={onClose} className="btn-secondary flex-1">Annuler</button>
            <button onClick={handleSubmit} disabled={loading} className="btn-primary flex-1">
              {loading ? 'Création...' : 'Créer'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};


export default EnterpriseDashboard;
