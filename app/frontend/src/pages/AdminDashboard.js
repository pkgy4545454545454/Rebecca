import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { 
  LayoutDashboard, Users, Building2, ShoppingCart, CreditCard, BarChart3,
  CheckCircle, Award, Crown, TrendingUp, DollarSign, Eye, Settings, Wallet,
  Download, Clock, XCircle, AlertCircle, FileText, FileSpreadsheet, 
  ArrowUpRight, ArrowDownRight, Filter, RefreshCw, UserPlus, Mail, Phone, MapPin,
  Cpu, Zap, Shield, Search, Target, TrendingDown, Sparkles, Calendar, Edit2, Save,
  Image as ImageIcon, Palette
} from 'lucide-react';
import { adminAPI } from '../services/api';
import axios from 'axios';
import { toast } from 'sonner';

const API_URL = `${process.env.REACT_APP_BACKEND_URL}/api`;

// List of admin emails
const ADMIN_EMAILS = ['admin@titelli.com', 'spa.luxury@titelli.com', 'admin@titelli.ch'];

const AdminDashboard = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  
  // Withdrawals state
  const [withdrawals, setWithdrawals] = useState([]);
  const [withdrawalStats, setWithdrawalStats] = useState({});
  const [withdrawalFilter, setWithdrawalFilter] = useState(null);
  const [selectedWithdrawal, setSelectedWithdrawal] = useState(null);

  // Enterprises state
  const [enterprises, setEnterprises] = useState([]);
  
  // Orders state  
  const [allOrders, setAllOrders] = useState([]);
  
  // Payments state
  const [payments, setPayments] = useState([]);
  
  // Registration requests state
  const [registrationRequests, setRegistrationRequests] = useState([]);
  const [registrationLoading, setRegistrationLoading] = useState(false);

  // Algorithms state
  const [algorithms, setAlgorithms] = useState([]);
  const [algorithmsLoading, setAlgorithmsLoading] = useState(false);

  // Subscription plans state
  const [subscriptionPlans, setSubscriptionPlans] = useState([]);
  const [subscriptionLoading, setSubscriptionLoading] = useState(false);
  const [editingPlan, setEditingPlan] = useState(null);

  // Pub Media orders state
  const [pubMediaOrders, setPubMediaOrders] = useState([]);
  const [pubMediaStats, setPubMediaStats] = useState({});
  const [pubMediaLoading, setPubMediaLoading] = useState(false);
  const [pubMediaFilter, setPubMediaFilter] = useState('all');

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [statsRes, usersRes] = await Promise.all([
          adminAPI.stats(),
          adminAPI.users()
        ]);
        setStats(statsRes.data);
        setEnterprises(statsRes.data.recent_enterprises || []);
        setAllOrders(statsRes.data.recent_orders || []);
        setUsers(usersRes.data.users);
      } catch (error) {
        console.error('Error fetching admin data:', error);
        toast.error('Accès non autorisé');
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  // Fetch registration requests
  const fetchRegistrationRequests = async () => {
    try {
      setRegistrationLoading(true);
      const response = await axios.get(`${API_URL}/admin/registration-requests`, { 
        params: { status: 'pending' },
        headers: { Authorization: `Bearer ${localStorage.getItem('titelli_token')}` }
      });
      setRegistrationRequests(response.data.requests || []);
    } catch (error) {
      console.error('Error fetching registration requests:', error);
    } finally {
      setRegistrationLoading(false);
    }
  };

  useEffect(() => {
    fetchRegistrationRequests();
  }, []);

  const handleApproveRegistration = async (requestId) => {
    try {
      await axios.post(`${API_URL}/admin/registration-requests/${requestId}/approve`, null, {
        headers: { Authorization: `Bearer ${localStorage.getItem('titelli_token')}` }
      });
      toast.success('Inscription approuvée avec succès !');
      fetchRegistrationRequests();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erreur lors de l\'approbation');
    }
  };

  const handleRejectRegistration = async (requestId) => {
    const reason = prompt('Raison du rejet (optionnel):');
    try {
      await axios.post(`${API_URL}/admin/registration-requests/${requestId}/reject`, null, { 
        params: { reason },
        headers: { Authorization: `Bearer ${localStorage.getItem('titelli_token')}` }
      });
      toast.success('Inscription rejetée');
      fetchRegistrationRequests();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erreur lors du rejet');
    }
  };

  // Fetch algorithms
  const fetchAlgorithms = async () => {
    try {
      setAlgorithmsLoading(true);
      const response = await axios.get(`${API_URL}/admin/algorithms`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('titelli_token')}` }
      });
      setAlgorithms(response.data.algorithms || []);
    } catch (error) {
      console.error('Error fetching algorithms:', error);
    } finally {
      setAlgorithmsLoading(false);
    }
  };

  const handleToggleAlgorithm = async (algorithmId, enabled) => {
    try {
      await axios.put(`${API_URL}/admin/algorithms/${algorithmId}`, null, {
        params: { enabled: !enabled },
        headers: { Authorization: `Bearer ${localStorage.getItem('titelli_token')}` }
      });
      toast.success(`Algorithme ${!enabled ? 'activé' : 'désactivé'}`);
      fetchAlgorithms();
    } catch (error) {
      toast.error('Erreur lors de la modification');
    }
  };

  // Fetch subscription plans
  const fetchSubscriptionPlans = async () => {
    try {
      setSubscriptionLoading(true);
      const response = await axios.get(`${API_URL}/admin/subscription-plans`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('titelli_token')}` }
      });
      setSubscriptionPlans(response.data.plans || []);
    } catch (error) {
      console.error('Error fetching subscription plans:', error);
    } finally {
      setSubscriptionLoading(false);
    }
  };

  const handleUpdatePlan = async (planId, data) => {
    try {
      await axios.put(`${API_URL}/admin/subscription-plans/${planId}`, data, {
        headers: { Authorization: `Bearer ${localStorage.getItem('titelli_token')}` }
      });
      toast.success('Plan mis à jour');
      setEditingPlan(null);
      fetchSubscriptionPlans();
    } catch (error) {
      toast.error('Erreur lors de la mise à jour');
    }
  };

  useEffect(() => {
    fetchAlgorithms();
    fetchSubscriptionPlans();
  }, []);

  const handleVerifyUser = async (userId, isCertified = false, isLabeled = false) => {
    try {
      await adminAPI.verifyUser(userId, isCertified, isLabeled);
      toast.success('Utilisateur vérifié !');
      // Refresh users
      const response = await adminAPI.users();
      setUsers(response.data.users);
    } catch (error) {
      toast.error('Erreur lors de la vérification');
    }
  };

  const menuItems = [
    { id: 'overview', label: 'Vue d\'ensemble', icon: LayoutDashboard },
    { id: 'registrations', label: 'Inscriptions en attente', icon: UserPlus, badge: registrationRequests.length },
    { id: 'pub-media', label: 'Pub Média IA', icon: Palette },
    { id: 'algorithms', label: 'Algorithmes', icon: Cpu },
    { id: 'subscriptions', label: 'Abonnements', icon: CreditCard },
    { id: 'accounting', label: 'Comptabilité', icon: BarChart3 },
    { id: 'withdrawals', label: 'Retraits', icon: Wallet },
    { id: 'users', label: 'Utilisateurs', icon: Users },
    { id: 'enterprises', label: 'Entreprises', icon: Building2 },
    { id: 'orders', label: 'Commandes', icon: ShoppingCart },
    { id: 'payments', label: 'Paiements', icon: CreditCard },
    { id: 'settings', label: 'Paramètres', icon: Settings },
  ];

  // Accounting state
  const [accountingSummary, setAccountingSummary] = useState(null);
  const [accountingTransactions, setAccountingTransactions] = useState([]);
  const [transactionFilter, setTransactionFilter] = useState(null);
  const [dateRange, setDateRange] = useState({ start: '', end: '' });
  const [loadingAccounting, setLoadingAccounting] = useState(false);

  // Fetch accounting when tab changes
  useEffect(() => {
    if (activeTab === 'accounting') {
      fetchAccountingData();
    }
  }, [activeTab]);

  const fetchAccountingData = async () => {
    setLoadingAccounting(true);
    try {
      const [summaryRes, txRes] = await Promise.all([
        adminAPI.accountingSummary(dateRange.start || null, dateRange.end || null),
        adminAPI.accountingTransactions(transactionFilter, dateRange.start || null, dateRange.end || null, 200)
      ]);
      setAccountingSummary(summaryRes.data);
      setAccountingTransactions(txRes.data.transactions || []);
    } catch (error) {
      console.error('Error fetching accounting:', error);
      toast.error('Erreur lors du chargement des données comptables');
    } finally {
      setLoadingAccounting(false);
    }
  };

  const handleExportExcel = async () => {
    const token = localStorage.getItem('titelli_token');
    const url = adminAPI.exportAccountingExcel(dateRange.start || null, dateRange.end || null);
    window.open(`${url}&token=${token}`, '_blank');
    toast.success('Export Excel en cours...');
  };

  const handleExportPDF = async () => {
    const token = localStorage.getItem('titelli_token');
    const url = adminAPI.exportAccountingPDF(dateRange.start || null, dateRange.end || null);
    window.open(`${url}&token=${token}`, '_blank');
    toast.success('Export PDF en cours...');
  };

  // Fetch withdrawals when tab changes
  useEffect(() => {
    if (activeTab === 'withdrawals') {
      fetchWithdrawals();
    }
  }, [activeTab, withdrawalFilter]);

  const fetchWithdrawals = async () => {
    try {
      const res = await adminAPI.withdrawals(withdrawalFilter);
      setWithdrawals(res.data.withdrawals || []);
      setWithdrawalStats(res.data.status_counts || {});
    } catch (error) {
      console.error('Error fetching withdrawals:', error);
    }
  };

  const handleUpdateWithdrawalStatus = async (withdrawalId, newStatus, adminNote = null) => {
    try {
      await adminAPI.updateWithdrawalStatus(withdrawalId, newStatus, adminNote);
      toast.success(`Statut mis à jour: ${newStatus}`);
      fetchWithdrawals();
      setSelectedWithdrawal(null);
    } catch (error) {
      toast.error('Erreur lors de la mise à jour');
    }
  };

  const handleExportCSV = () => {
    const token = localStorage.getItem('titelli_token');
    const url = adminAPI.exportWithdrawalsCSV(withdrawalFilter);
    // Open in new window with auth header workaround
    window.open(`${url}&token=${token}`, '_blank');
  };

  // Fetch Pub Media orders when tab changes
  useEffect(() => {
    if (activeTab === 'pub-media') {
      fetchPubMediaOrders();
    }
  }, [activeTab, pubMediaFilter]);

  const fetchPubMediaOrders = async () => {
    setPubMediaLoading(true);
    try {
      const params = new URLSearchParams();
      if (pubMediaFilter && pubMediaFilter !== 'all') {
        params.append('status', pubMediaFilter);
      }
      params.append('limit', '100');
      
      const response = await axios.get(`${API_URL}/media-pub/admin/orders?${params.toString()}`);
      setPubMediaOrders(response.data.orders || []);
      setPubMediaStats(response.data.stats || {});
    } catch (error) {
      console.error('Error fetching pub media orders:', error);
      toast.error('Erreur chargement commandes Pub Média');
    } finally {
      setPubMediaLoading(false);
    }
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed': return 'bg-green-500/20 text-green-400';
      case 'pending': return 'bg-yellow-500/20 text-yellow-400';
      case 'processing': return 'bg-blue-500/20 text-blue-400';
      case 'failed': return 'bg-red-500/20 text-red-400';
      case 'cancelled': return 'bg-gray-500/20 text-gray-400';
      default: return 'bg-gray-500/20 text-gray-400';
    }
  };

  const getPaymentStatusColor = (status) => {
    switch (status) {
      case 'paid': return 'bg-emerald-500/20 text-emerald-400';
      case 'pending': return 'bg-orange-500/20 text-orange-400';
      default: return 'bg-gray-500/20 text-gray-400';
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#050505] pt-24 flex items-center justify-center">
        <div className="w-16 h-16 border-4 border-[#0047AB] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!ADMIN_EMAILS.includes(user?.email)) {
    return (
      <div className="min-h-screen bg-[#050505] pt-24 flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-white mb-4">Accès refusé</h1>
          <p className="text-gray-400">Vous n&apos;avez pas les droits d&apos;accès à cette page.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#050505] pt-20" data-testid="admin-dashboard">
      <div className="flex">
        {/* Sidebar */}
        <aside className="w-64 min-h-screen bg-[#0A0A0A] border-r border-white/5 fixed left-0 top-20 bottom-0 overflow-y-auto hidden lg:block">
          <div className="p-6">
            <div className="flex items-center gap-3 mb-8">
              <div className="w-12 h-12 rounded-xl bg-red-500/20 flex items-center justify-center">
                <Crown className="w-6 h-6 text-red-500" />
              </div>
              <div>
                <p className="font-semibold text-white">Admin</p>
                <p className="text-xs text-gray-500">Tableau de bord</p>
              </div>
            </div>

            <nav className="space-y-1">
              {menuItems.map((item) => (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all ${
                    activeTab === item.id
                      ? 'bg-red-500/20 text-red-500'
                      : 'text-gray-400 hover:bg-white/5 hover:text-white'
                  }`}
                >
                  <item.icon className="w-5 h-5" />
                  {item.label}
                </button>
              ))}
            </nav>
          </div>
        </aside>

        {/* Main Content */}
        <main className="flex-1 lg:ml-64 p-6 lg:p-8">
          {activeTab === 'overview' && stats && (
            <div className="space-y-8">
              <h1 className="text-2xl md:text-3xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
                Tableau de bord Admin
              </h1>

              {/* Stats */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="card-service rounded-xl p-6">
                  <div className="p-3 rounded-xl bg-[#0047AB]/20 w-fit mb-4">
                    <Users className="w-5 h-5 text-[#0047AB]" />
                  </div>
                  <p className="text-2xl font-bold text-white">{stats.stats.total_users}</p>
                  <p className="text-sm text-gray-400 mt-1">Utilisateurs</p>
                </div>
                <div className="card-service rounded-xl p-6">
                  <div className="p-3 rounded-xl bg-[#D4AF37]/20 w-fit mb-4">
                    <Building2 className="w-5 h-5 text-[#D4AF37]" />
                  </div>
                  <p className="text-2xl font-bold text-white">{stats.stats.total_enterprises}</p>
                  <p className="text-sm text-gray-400 mt-1">Entreprises</p>
                </div>
                <div className="card-service rounded-xl p-6">
                  <div className="p-3 rounded-xl bg-green-500/20 w-fit mb-4">
                    <ShoppingCart className="w-5 h-5 text-green-500" />
                  </div>
                  <p className="text-2xl font-bold text-white">{stats.stats.total_orders}</p>
                  <p className="text-sm text-gray-400 mt-1">Commandes</p>
                </div>
                <div className="card-service rounded-xl p-6">
                  <div className="p-3 rounded-xl bg-purple-500/20 w-fit mb-4">
                    <BarChart3 className="w-5 h-5 text-purple-500" />
                  </div>
                  <p className="text-2xl font-bold text-white">{stats.stats.total_reviews}</p>
                  <p className="text-sm text-gray-400 mt-1">Avis</p>
                </div>
              </div>

              {/* Recent Activity */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="card-service rounded-xl p-6">
                  <h2 className="text-lg font-bold text-white mb-4">Utilisateurs récents</h2>
                  <div className="space-y-3">
                    {stats.recent_users?.slice(0, 5).map((u) => (
                      <div key={u.id} className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                        <div>
                          <p className="text-white font-medium">{u.first_name} {u.last_name}</p>
                          <p className="text-sm text-gray-400">{u.email}</p>
                        </div>
                        <span className={`px-2 py-1 rounded-full text-xs ${
                          u.user_type === 'entreprise' ? 'bg-[#D4AF37]/20 text-[#D4AF37]' : 'bg-[#0047AB]/20 text-[#0047AB]'
                        }`}>
                          {u.user_type}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="card-service rounded-xl p-6">
                  <h2 className="text-lg font-bold text-white mb-4">Commandes récentes</h2>
                  <div className="space-y-3">
                    {stats.recent_orders?.length > 0 ? stats.recent_orders.slice(0, 5).map((o) => (
                      <div key={o.id} className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                        <div>
                          <p className="text-white font-medium">#{o.id.slice(0, 8)}</p>
                          <p className="text-sm text-gray-400">{o.items?.length || 0} articles</p>
                        </div>
                        <p className="text-white font-medium">{o.total?.toFixed(2)} CHF</p>
                      </div>
                    )) : (
                      <p className="text-gray-500 text-center py-4">Aucune commande</p>
                    )}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* ===== INSCRIPTIONS EN ATTENTE TAB ===== */}
          {activeTab === 'registrations' && (
            <div>
              <div className="flex items-center justify-between mb-8">
                <div>
                  <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
                    Inscriptions en attente
                  </h1>
                  <p className="text-gray-400 text-sm mt-1">
                    {registrationRequests.length} demande(s) en attente de validation
                  </p>
                </div>
                <button
                  onClick={fetchRegistrationRequests}
                  className="flex items-center gap-2 px-4 py-2 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-colors"
                >
                  <RefreshCw className={`w-4 h-4 ${registrationLoading ? 'animate-spin' : ''}`} />
                  Actualiser
                </button>
              </div>

              {registrationLoading ? (
                <div className="flex justify-center py-12">
                  <div className="w-12 h-12 border-4 border-[#0047AB] border-t-transparent rounded-full animate-spin" />
                </div>
              ) : registrationRequests.length === 0 ? (
                <div className="text-center py-12">
                  <UserPlus className="w-16 h-16 mx-auto mb-4 text-gray-600" />
                  <p className="text-gray-400">Aucune demande d'inscription en attente</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {registrationRequests.map((request) => (
                    <div key={request.id} className="bg-white/5 border border-white/10 rounded-xl p-6">
                      <div className="flex flex-col lg:flex-row lg:items-start gap-6">
                        {/* Enterprise Info */}
                        <div className="flex items-start gap-4 flex-1">
                          <img
                            src={request.enterprise?.image || `https://ui-avatars.com/api/?name=${request.enterprise_name}&background=0047AB&color=fff`}
                            alt={request.enterprise_name}
                            className="w-16 h-16 rounded-lg object-cover"
                          />
                          <div>
                            <h3 className="text-white font-semibold text-lg">{request.enterprise_name}</h3>
                            <p className="text-[#D4AF37] text-sm">{request.enterprise?.category}</p>
                            <p className="text-gray-400 text-sm flex items-center gap-1 mt-1">
                              <MapPin className="w-4 h-4" />
                              {request.enterprise?.address}
                            </p>
                          </div>
                        </div>

                        {/* User Info */}
                        <div className="flex-1 bg-white/5 rounded-lg p-4">
                          <h4 className="text-white font-medium mb-3">Informations du demandeur</h4>
                          <div className="space-y-2 text-sm">
                            <p className="text-gray-300 flex items-center gap-2">
                              <Users className="w-4 h-4 text-gray-500" />
                              {request.user_info?.first_name} {request.user_info?.last_name}
                            </p>
                            <p className="text-gray-300 flex items-center gap-2">
                              <Mail className="w-4 h-4 text-gray-500" />
                              {request.user_info?.email}
                            </p>
                            <p className="text-gray-300 flex items-center gap-2">
                              <Phone className="w-4 h-4 text-gray-500" />
                              {request.user_info?.phone}
                            </p>
                          </div>
                        </div>

                        {/* Documents */}
                        <div className="flex-1 bg-white/5 rounded-lg p-4">
                          <h4 className="text-white font-medium mb-3">Documents fournis</h4>
                          <div className="space-y-2 text-sm">
                            <p className="text-gray-300">
                              <span className="text-gray-500">Registre du commerce:</span>{' '}
                              <span className="text-[#D4AF37] font-mono">{request.commerce_register_id}</span>
                            </p>
                            <p className="text-gray-300">
                              <span className="text-gray-500">Manager référent:</span>{' '}
                              {request.manager_id}
                            </p>
                            <p className="text-gray-300">
                              <span className="text-gray-500">Pièce d'identité:</span>{' '}
                              {request.identity_document ? (
                                <span className="text-green-400">✓ Téléchargée</span>
                              ) : (
                                <span className="text-yellow-400">Non fournie</span>
                              )}
                            </p>
                            <p className="text-gray-500 text-xs mt-2">
                              Demande reçue le {new Date(request.created_at).toLocaleDateString('fr-FR', {
                                day: 'numeric',
                                month: 'long',
                                year: 'numeric',
                                hour: '2-digit',
                                minute: '2-digit'
                              })}
                            </p>
                          </div>
                        </div>
                      </div>

                      {/* Actions */}
                      <div className="flex justify-end gap-3 mt-6 pt-4 border-t border-white/10">
                        <button
                          onClick={() => handleRejectRegistration(request.id)}
                          className="flex items-center gap-2 px-4 py-2 bg-red-500/20 text-red-400 rounded-lg hover:bg-red-500/30 transition-colors"
                        >
                          <XCircle className="w-4 h-4" />
                          Rejeter
                        </button>
                        <button
                          onClick={() => handleApproveRegistration(request.id)}
                          className="flex items-center gap-2 px-6 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600 transition-colors font-medium"
                        >
                          <CheckCircle className="w-4 h-4" />
                          Valider l'inscription
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* ===== PUB MÉDIA IA TAB ===== */}
          {activeTab === 'pub-media' && (
            <div data-testid="admin-pub-media">
              <div className="flex items-center justify-between mb-8">
                <div>
                  <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
                    Commandes Pub Média IA
                  </h1>
                  <p className="text-gray-400 text-sm mt-1">
                    Gérez toutes les commandes de publicités générées par IA
                  </p>
                </div>
                <button
                  onClick={fetchPubMediaOrders}
                  className="flex items-center gap-2 px-4 py-2 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-colors"
                >
                  <RefreshCw className={`w-4 h-4 ${pubMediaLoading ? 'animate-spin' : ''}`} />
                  Actualiser
                </button>
              </div>

              {/* Stats Cards */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                <div className="bg-white/5 border border-white/10 rounded-xl p-4">
                  <div className="flex items-center gap-3 mb-2">
                    <div className="w-10 h-10 rounded-lg bg-amber-500/20 flex items-center justify-center">
                      <Palette className="w-5 h-5 text-amber-400" />
                    </div>
                    <span className="text-gray-400 text-sm">Total</span>
                  </div>
                  <p className="text-2xl font-bold text-white">{pubMediaStats.total || 0}</p>
                </div>
                <div className="bg-white/5 border border-white/10 rounded-xl p-4">
                  <div className="flex items-center gap-3 mb-2">
                    <div className="w-10 h-10 rounded-lg bg-green-500/20 flex items-center justify-center">
                      <CheckCircle className="w-5 h-5 text-green-400" />
                    </div>
                    <span className="text-gray-400 text-sm">Complétées</span>
                  </div>
                  <p className="text-2xl font-bold text-white">{pubMediaStats.completed || 0}</p>
                </div>
                <div className="bg-white/5 border border-white/10 rounded-xl p-4">
                  <div className="flex items-center gap-3 mb-2">
                    <div className="w-10 h-10 rounded-lg bg-emerald-500/20 flex items-center justify-center">
                      <DollarSign className="w-5 h-5 text-emerald-400" />
                    </div>
                    <span className="text-gray-400 text-sm">Revenus</span>
                  </div>
                  <p className="text-2xl font-bold text-white">{(pubMediaStats.total_revenue || 0).toFixed(2)} <span className="text-sm text-gray-400">CHF</span></p>
                </div>
                <div className="bg-white/5 border border-white/10 rounded-xl p-4">
                  <div className="flex items-center gap-3 mb-2">
                    <div className="w-10 h-10 rounded-lg bg-red-500/20 flex items-center justify-center">
                      <XCircle className="w-5 h-5 text-red-400" />
                    </div>
                    <span className="text-gray-400 text-sm">Échouées</span>
                  </div>
                  <p className="text-2xl font-bold text-white">{pubMediaStats.failed || 0}</p>
                </div>
              </div>

              {/* Filters */}
              <div className="flex gap-2 mb-6 flex-wrap">
                {['all', 'pending', 'processing', 'completed', 'failed'].map(status => (
                  <button
                    key={status}
                    onClick={() => setPubMediaFilter(status)}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                      pubMediaFilter === status 
                        ? 'bg-amber-500 text-black' 
                        : 'bg-white/10 text-gray-400 hover:bg-white/20'
                    }`}
                  >
                    {status === 'all' ? 'Toutes' : status.charAt(0).toUpperCase() + status.slice(1)}
                  </button>
                ))}
              </div>

              {/* Orders Table */}
              {pubMediaLoading ? (
                <div className="flex justify-center py-12">
                  <div className="w-12 h-12 border-4 border-amber-500 border-t-transparent rounded-full animate-spin" />
                </div>
              ) : pubMediaOrders.length === 0 ? (
                <div className="text-center py-12 bg-white/5 rounded-xl">
                  <ImageIcon className="w-16 h-16 mx-auto mb-4 text-gray-600" />
                  <p className="text-gray-400">Aucune commande Pub Média</p>
                </div>
              ) : (
                <div className="bg-white/5 border border-white/10 rounded-xl overflow-hidden">
                  <div className="overflow-x-auto">
                    <table className="w-full">
                      <thead className="bg-white/5">
                        <tr>
                          <th className="text-left p-4 text-gray-400 font-medium text-sm">ID</th>
                          <th className="text-left p-4 text-gray-400 font-medium text-sm">Template</th>
                          <th className="text-left p-4 text-gray-400 font-medium text-sm">Entreprise</th>
                          <th className="text-left p-4 text-gray-400 font-medium text-sm">Prix</th>
                          <th className="text-left p-4 text-gray-400 font-medium text-sm">Statut</th>
                          <th className="text-left p-4 text-gray-400 font-medium text-sm">Paiement</th>
                          <th className="text-left p-4 text-gray-400 font-medium text-sm">Date</th>
                          <th className="text-left p-4 text-gray-400 font-medium text-sm">Image</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-white/5">
                        {pubMediaOrders.map(order => (
                          <tr key={order.id} className="hover:bg-white/5 transition-colors">
                            <td className="p-4">
                              <span className="font-mono text-sm text-white">#{order.id?.slice(0, 8)}</span>
                            </td>
                            <td className="p-4">
                              <span className="text-white text-sm">{order.template_name || 'Sur Mesure'}</span>
                              {order.template_id === 'sur_mesure' && (
                                <span className="ml-2 px-2 py-0.5 bg-purple-500/20 text-purple-400 text-xs rounded">Custom</span>
                              )}
                            </td>
                            <td className="p-4">
                              <span className="text-gray-300 text-sm">{order.enterprise_id?.slice(0, 8) || 'N/A'}</span>
                            </td>
                            <td className="p-4">
                              <span className="text-amber-400 font-medium">{order.price?.toFixed(2)} CHF</span>
                            </td>
                            <td className="p-4">
                              <span className={`px-3 py-1 rounded-full text-xs font-medium ${getStatusColor(order.status)}`}>
                                {order.status}
                              </span>
                            </td>
                            <td className="p-4">
                              <span className={`px-3 py-1 rounded-full text-xs font-medium ${getPaymentStatusColor(order.payment_status)}`}>
                                {order.payment_status || 'pending'}
                              </span>
                            </td>
                            <td className="p-4">
                              <span className="text-gray-400 text-sm">
                                {order.created_at ? new Date(order.created_at).toLocaleDateString('fr-CH') : 'N/A'}
                              </span>
                            </td>
                            <td className="p-4">
                              {order.image_url ? (
                                <a 
                                  href={order.image_url} 
                                  target="_blank" 
                                  rel="noopener noreferrer"
                                  className="flex items-center gap-1 text-amber-400 hover:text-amber-300 text-sm"
                                >
                                  <Eye className="w-4 h-4" />
                                  Voir
                                </a>
                              ) : (
                                <span className="text-gray-500 text-sm">-</span>
                              )}
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* ===== ALGORITHMES TAB ===== */}
          {activeTab === 'algorithms' && (
            <div>
              <div className="flex items-center justify-between mb-8">
                <div>
                  <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
                    Algorithmes de la Plateforme
                  </h1>
                  <p className="text-gray-400 text-sm mt-1">
                    Gérez les algorithmes qui optimisent l'expérience utilisateur
                  </p>
                </div>
                <button
                  onClick={fetchAlgorithms}
                  className="flex items-center gap-2 px-4 py-2 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-colors"
                >
                  <RefreshCw className={`w-4 h-4 ${algorithmsLoading ? 'animate-spin' : ''}`} />
                  Actualiser
                </button>
              </div>

              {algorithmsLoading ? (
                <div className="flex justify-center py-12">
                  <div className="w-12 h-12 border-4 border-[#0047AB] border-t-transparent rounded-full animate-spin" />
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {algorithms.map((algo) => {
                    const categoryIcons = {
                      'Personnalisation': <Sparkles className="w-5 h-5" />,
                      'Recherche': <Search className="w-5 h-5" />,
                      'Monétisation': <DollarSign className="w-5 h-5" />,
                      'Sécurité': <Shield className="w-5 h-5" />,
                      'Qualité': <Award className="w-5 h-5" />,
                      'Marketing': <Target className="w-5 h-5" />,
                      'Planification': <Calendar className="w-5 h-5" />
                    };
                    
                    return (
                      <div 
                        key={algo.id} 
                        className={`bg-white/5 border rounded-xl p-5 transition-all ${
                          algo.enabled ? 'border-green-500/30' : 'border-white/10 opacity-60'
                        }`}
                      >
                        <div className="flex items-start justify-between mb-3">
                          <div className="flex items-center gap-3">
                            <div className={`p-2 rounded-lg ${algo.enabled ? 'bg-green-500/20 text-green-400' : 'bg-white/10 text-gray-400'}`}>
                              {categoryIcons[algo.category] || <Cpu className="w-5 h-5" />}
                            </div>
                            <div>
                              <h3 className="text-white font-semibold">{algo.name}</h3>
                              <span className="text-xs text-[#D4AF37]">{algo.category}</span>
                            </div>
                          </div>
                          <button
                            onClick={() => handleToggleAlgorithm(algo.id, algo.enabled)}
                            className={`relative w-12 h-6 rounded-full transition-colors ${
                              algo.enabled ? 'bg-green-500' : 'bg-gray-600'
                            }`}
                          >
                            <div className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-transform ${
                              algo.enabled ? 'left-7' : 'left-1'
                            }`} />
                          </button>
                        </div>
                        <p className="text-gray-400 text-sm">{algo.description}</p>
                        <div className="flex items-center gap-2 mt-3">
                          <span className={`px-2 py-0.5 rounded-full text-xs ${
                            algo.enabled ? 'bg-green-500/20 text-green-400' : 'bg-gray-500/20 text-gray-400'
                          }`}>
                            {algo.enabled ? 'Actif' : 'Inactif'}
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          )}

          {/* ===== ABONNEMENTS TAB ===== */}
          {activeTab === 'subscriptions' && (
            <div>
              <div className="flex items-center justify-between mb-8">
                <div>
                  <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
                    Plans d'Abonnement
                  </h1>
                  <p className="text-gray-400 text-sm mt-1">
                    Gérez les prix et fonctionnalités des abonnements
                  </p>
                </div>
                <button
                  onClick={fetchSubscriptionPlans}
                  className="flex items-center gap-2 px-4 py-2 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-colors"
                >
                  <RefreshCw className={`w-4 h-4 ${subscriptionLoading ? 'animate-spin' : ''}`} />
                  Actualiser
                </button>
              </div>

              {subscriptionLoading ? (
                <div className="flex justify-center py-12">
                  <div className="w-12 h-12 border-4 border-[#0047AB] border-t-transparent rounded-full animate-spin" />
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {subscriptionPlans.map((plan) => (
                    <div 
                      key={plan.id} 
                      className={`bg-white/5 border rounded-xl p-6 transition-all ${
                        plan.id === 'premium' ? 'border-[#D4AF37]/50 ring-1 ring-[#D4AF37]/20' : 
                        plan.id === 'enterprise' ? 'border-[#0047AB]/50' : 'border-white/10'
                      }`}
                    >
                      {editingPlan === plan.id ? (
                        // Edit mode
                        <div className="space-y-4">
                          <input
                            type="text"
                            defaultValue={plan.name}
                            className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white"
                            id={`plan-name-${plan.id}`}
                          />
                          <div className="grid grid-cols-2 gap-2">
                            <div>
                              <label className="text-xs text-gray-400">Prix mensuel (CHF)</label>
                              <input
                                type="number"
                                step="0.01"
                                defaultValue={plan.price_monthly}
                                className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white"
                                id={`plan-monthly-${plan.id}`}
                              />
                            </div>
                            <div>
                              <label className="text-xs text-gray-400">Prix annuel (CHF)</label>
                              <input
                                type="number"
                                step="0.01"
                                defaultValue={plan.price_yearly}
                                className="w-full px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white"
                                id={`plan-yearly-${plan.id}`}
                              />
                            </div>
                          </div>
                          <div className="flex gap-2">
                            <button
                              onClick={() => {
                                const name = document.getElementById(`plan-name-${plan.id}`).value;
                                const monthly = document.getElementById(`plan-monthly-${plan.id}`).value;
                                const yearly = document.getElementById(`plan-yearly-${plan.id}`).value;
                                handleUpdatePlan(plan.id, { name, price_monthly: monthly, price_yearly: yearly });
                              }}
                              className="flex-1 flex items-center justify-center gap-2 px-4 py-2 bg-green-500 text-white rounded-lg hover:bg-green-600"
                            >
                              <Save className="w-4 h-4" />
                              Sauvegarder
                            </button>
                            <button
                              onClick={() => setEditingPlan(null)}
                              className="px-4 py-2 bg-white/10 text-white rounded-lg hover:bg-white/20"
                            >
                              Annuler
                            </button>
                          </div>
                        </div>
                      ) : (
                        // View mode
                        <>
                          <div className="flex items-center justify-between mb-4">
                            <div>
                              <h3 className="text-white font-bold text-lg">{plan.name}</h3>
                              <p className="text-gray-400 text-sm">{plan.description}</p>
                            </div>
                            <button
                              onClick={() => setEditingPlan(plan.id)}
                              className="p-2 text-gray-400 hover:text-white hover:bg-white/10 rounded-lg transition-colors"
                            >
                              <Edit2 className="w-4 h-4" />
                            </button>
                          </div>
                          
                          <div className="mb-4">
                            <div className="flex items-baseline gap-1">
                              <span className="text-3xl font-bold text-white">{plan.price_monthly.toFixed(2)}</span>
                              <span className="text-gray-400">CHF/mois</span>
                            </div>
                            <p className="text-gray-500 text-sm">ou {plan.price_yearly.toFixed(2)} CHF/an</p>
                          </div>
                          
                          <ul className="space-y-2 mb-4">
                            {plan.features?.map((feature, idx) => (
                              <li key={idx} className="flex items-center gap-2 text-gray-300 text-sm">
                                <CheckCircle className="w-4 h-4 text-green-500 flex-shrink-0" />
                                {feature}
                              </li>
                            ))}
                          </ul>
                          
                          <div className="flex items-center justify-between pt-4 border-t border-white/10">
                            <span className={`px-2 py-0.5 rounded-full text-xs ${
                              plan.is_active ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                            }`}>
                              {plan.is_active ? 'Actif' : 'Inactif'}
                            </span>
                            <button
                              onClick={() => handleUpdatePlan(plan.id, { is_active: !plan.is_active })}
                              className="text-sm text-gray-400 hover:text-white"
                            >
                              {plan.is_active ? 'Désactiver' : 'Activer'}
                            </button>
                          </div>
                        </>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}

          {/* ===== COMPTABILITÉ TAB ===== */}
          {activeTab === 'accounting' && (
            <div>
              {/* Header with export buttons */}
              <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 mb-8">
                <div>
                  <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
                    Comptabilité
                  </h1>
                  <p className="text-gray-400 text-sm mt-1">Vue complète des finances de la plateforme</p>
                </div>
                <div className="flex gap-3">
                  <button
                    onClick={handleExportExcel}
                    className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg font-medium hover:bg-green-700 transition-colors"
                  >
                    <FileSpreadsheet className="w-4 h-4" />
                    Excel
                  </button>
                  <button
                    onClick={handleExportPDF}
                    className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-lg font-medium hover:bg-red-700 transition-colors"
                  >
                    <FileText className="w-4 h-4" />
                    PDF
                  </button>
                </div>
              </div>

              {/* Date Range Filter */}
              <div className="card-service rounded-xl p-4 mb-6">
                <div className="flex flex-wrap items-center gap-4">
                  <div className="flex items-center gap-2">
                    <Filter className="w-4 h-4 text-gray-400" />
                    <span className="text-gray-400 text-sm">Période:</span>
                  </div>
                  <input
                    type="date"
                    value={dateRange.start}
                    onChange={(e) => setDateRange({...dateRange, start: e.target.value})}
                    className="px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white text-sm"
                  />
                  <span className="text-gray-400">à</span>
                  <input
                    type="date"
                    value={dateRange.end}
                    onChange={(e) => setDateRange({...dateRange, end: e.target.value})}
                    className="px-3 py-2 bg-white/10 border border-white/20 rounded-lg text-white text-sm"
                  />
                  <button
                    onClick={fetchAccountingData}
                    className="flex items-center gap-2 px-4 py-2 bg-[#0047AB] text-white rounded-lg font-medium hover:bg-[#003d91] transition-colors"
                  >
                    <RefreshCw className={`w-4 h-4 ${loadingAccounting ? 'animate-spin' : ''}`} />
                    Actualiser
                  </button>
                </div>
              </div>

              {loadingAccounting ? (
                <div className="flex items-center justify-center py-20">
                  <div className="w-12 h-12 border-4 border-[#0047AB] border-t-transparent rounded-full animate-spin" />
                </div>
              ) : accountingSummary && (
                <>
                  {/* Key Metrics Cards */}
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                    {/* Total Revenue */}
                    <div className="card-service rounded-xl p-6">
                      <div className="flex items-center justify-between mb-4">
                        <div className="p-3 rounded-xl bg-green-500/20">
                          <TrendingUp className="w-6 h-6 text-green-500" />
                        </div>
                        <ArrowUpRight className="w-5 h-5 text-green-500" />
                      </div>
                      <p className="text-3xl font-bold text-white">{accountingSummary.revenue?.total_revenue?.toFixed(2)} CHF</p>
                      <p className="text-sm text-gray-400 mt-1">Chiffre d'affaires total</p>
                    </div>

                    {/* Commissions */}
                    <div className="card-service rounded-xl p-6">
                      <div className="flex items-center justify-between mb-4">
                        <div className="p-3 rounded-xl bg-[#D4AF37]/20">
                          <DollarSign className="w-6 h-6 text-[#D4AF37]" />
                        </div>
                        <ArrowUpRight className="w-5 h-5 text-[#D4AF37]" />
                      </div>
                      <p className="text-3xl font-bold text-white">{accountingSummary.commissions?.total_commissions?.toFixed(2)} CHF</p>
                      <p className="text-sm text-gray-400 mt-1">Commissions Titelli</p>
                    </div>

                    {/* Cashback Liability */}
                    <div className="card-service rounded-xl p-6">
                      <div className="flex items-center justify-between mb-4">
                        <div className="p-3 rounded-xl bg-orange-500/20">
                          <Wallet className="w-6 h-6 text-orange-500" />
                        </div>
                        <ArrowDownRight className="w-5 h-5 text-orange-500" />
                      </div>
                      <p className="text-3xl font-bold text-white">{accountingSummary.cashback?.net_liability?.toFixed(2)} CHF</p>
                      <p className="text-sm text-gray-400 mt-1">Passif cashback</p>
                    </div>

                    {/* Orders */}
                    <div className="card-service rounded-xl p-6">
                      <div className="flex items-center justify-between mb-4">
                        <div className="p-3 rounded-xl bg-blue-500/20">
                          <ShoppingCart className="w-6 h-6 text-blue-500" />
                        </div>
                      </div>
                      <p className="text-3xl font-bold text-white">{accountingSummary.orders?.total_count}</p>
                      <p className="text-sm text-gray-400 mt-1">Commandes ({accountingSummary.orders?.average_order_value?.toFixed(2)} CHF moy.)</p>
                    </div>
                  </div>

                  {/* Detailed Breakdown */}
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                    {/* Revenue Breakdown */}
                    <div className="card-service rounded-xl p-6">
                      <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                        <TrendingUp className="w-5 h-5 text-green-500" />
                        Détail des Revenus
                      </h3>
                      <div className="space-y-3">
                        <div className="flex justify-between items-center p-3 bg-white/5 rounded-lg">
                          <span className="text-gray-300">Ventes (commandes)</span>
                          <span className="text-white font-medium">{accountingSummary.revenue?.total_orders_revenue?.toFixed(2)} CHF</span>
                        </div>
                        <div className="flex justify-between items-center p-3 bg-white/5 rounded-lg">
                          <span className="text-gray-300">Abonnements</span>
                          <span className="text-white font-medium">{accountingSummary.revenue?.subscription_revenue?.toFixed(2)} CHF</span>
                        </div>
                        <div className="flex justify-between items-center p-3 bg-green-500/10 rounded-lg border border-green-500/30">
                          <span className="text-green-400 font-medium">Total</span>
                          <span className="text-green-400 font-bold">{accountingSummary.revenue?.total_revenue?.toFixed(2)} CHF</span>
                        </div>
                      </div>
                    </div>

                    {/* Commissions Breakdown */}
                    <div className="card-service rounded-xl p-6">
                      <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                        <DollarSign className="w-5 h-5 text-[#D4AF37]" />
                        Détail des Commissions
                      </h3>
                      <div className="space-y-3">
                        <div className="flex justify-between items-center p-3 bg-white/5 rounded-lg">
                          <span className="text-gray-300">Commission 5% (commandes)</span>
                          <span className="text-white font-medium">{accountingSummary.commissions?.order_commissions_5pct?.toFixed(2)} CHF</span>
                        </div>
                        <div className="flex justify-between items-center p-3 bg-white/5 rounded-lg">
                          <span className="text-gray-300">Frais de gestion</span>
                          <span className="text-white font-medium">{accountingSummary.commissions?.management_fees?.toFixed(2)} CHF</span>
                        </div>
                        <div className="flex justify-between items-center p-3 bg-white/5 rounded-lg">
                          <span className="text-gray-300">Commission 12% (investissements)</span>
                          <span className="text-white font-medium">{accountingSummary.commissions?.investment_commissions_12pct?.toFixed(2)} CHF</span>
                        </div>
                        <div className="flex justify-between items-center p-3 bg-[#D4AF37]/10 rounded-lg border border-[#D4AF37]/30">
                          <span className="text-[#D4AF37] font-medium">Total</span>
                          <span className="text-[#D4AF37] font-bold">{accountingSummary.commissions?.total_commissions?.toFixed(2)} CHF</span>
                        </div>
                      </div>
                    </div>

                    {/* Cashback Breakdown */}
                    <div className="card-service rounded-xl p-6">
                      <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                        <Wallet className="w-5 h-5 text-orange-500" />
                        Cashback
                      </h3>
                      <div className="space-y-3">
                        <div className="flex justify-between items-center p-3 bg-white/5 rounded-lg">
                          <span className="text-gray-300">Distribué aux clients</span>
                          <span className="text-green-400 font-medium">+{accountingSummary.cashback?.total_distributed?.toFixed(2)} CHF</span>
                        </div>
                        <div className="flex justify-between items-center p-3 bg-white/5 rounded-lg">
                          <span className="text-gray-300">Utilisé (achats)</span>
                          <span className="text-red-400 font-medium">-{accountingSummary.cashback?.total_used?.toFixed(2)} CHF</span>
                        </div>
                        <div className="flex justify-between items-center p-3 bg-white/5 rounded-lg">
                          <span className="text-gray-300">Retiré (virements)</span>
                          <span className="text-red-400 font-medium">-{accountingSummary.cashback?.total_withdrawn?.toFixed(2)} CHF</span>
                        </div>
                        <div className="flex justify-between items-center p-3 bg-orange-500/10 rounded-lg border border-orange-500/30">
                          <span className="text-orange-400 font-medium">Passif (à provisionner)</span>
                          <span className="text-orange-400 font-bold">{accountingSummary.cashback?.net_liability?.toFixed(2)} CHF</span>
                        </div>
                      </div>
                    </div>

                    {/* Withdrawals & Subscriptions */}
                    <div className="card-service rounded-xl p-6">
                      <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                        <CreditCard className="w-5 h-5 text-purple-500" />
                        Retraits & Abonnements
                      </h3>
                      <div className="space-y-3">
                        <div className="flex justify-between items-center p-3 bg-white/5 rounded-lg">
                          <span className="text-gray-300">Retraits en attente</span>
                          <span className="text-yellow-400 font-medium">{accountingSummary.withdrawals?.pending_amount?.toFixed(2)} CHF</span>
                        </div>
                        <div className="flex justify-between items-center p-3 bg-white/5 rounded-lg">
                          <span className="text-gray-300">Retraits effectués</span>
                          <span className="text-green-400 font-medium">{accountingSummary.withdrawals?.completed_amount?.toFixed(2)} CHF</span>
                        </div>
                        <div className="flex justify-between items-center p-3 bg-white/5 rounded-lg">
                          <span className="text-gray-300">Abonnements actifs</span>
                          <span className="text-white font-medium">{accountingSummary.subscriptions?.active_count}</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Transactions Table */}
                  <div className="card-service rounded-xl overflow-hidden">
                    <div className="p-6 border-b border-white/10">
                      <div className="flex items-center justify-between">
                        <h3 className="text-lg font-bold text-white">Historique des Transactions</h3>
                        <div className="flex gap-2">
                          <button
                            onClick={() => { setTransactionFilter(null); fetchAccountingData(); }}
                            className={`px-3 py-1 rounded-lg text-sm ${!transactionFilter ? 'bg-[#0047AB] text-white' : 'bg-white/10 text-gray-300'}`}
                          >
                            Tous
                          </button>
                          <button
                            onClick={() => { setTransactionFilter('order'); fetchAccountingData(); }}
                            className={`px-3 py-1 rounded-lg text-sm ${transactionFilter === 'order' ? 'bg-[#0047AB] text-white' : 'bg-white/10 text-gray-300'}`}
                          >
                            Commandes
                          </button>
                          <button
                            onClick={() => { setTransactionFilter('subscription'); fetchAccountingData(); }}
                            className={`px-3 py-1 rounded-lg text-sm ${transactionFilter === 'subscription' ? 'bg-[#0047AB] text-white' : 'bg-white/10 text-gray-300'}`}
                          >
                            Abonnements
                          </button>
                          <button
                            onClick={() => { setTransactionFilter('cashback'); fetchAccountingData(); }}
                            className={`px-3 py-1 rounded-lg text-sm ${transactionFilter === 'cashback' ? 'bg-[#0047AB] text-white' : 'bg-white/10 text-gray-300'}`}
                          >
                            Cashback
                          </button>
                        </div>
                      </div>
                    </div>
                    <table className="w-full">
                      <thead className="bg-white/5">
                        <tr>
                          <th className="text-left px-6 py-4 text-sm font-medium text-gray-400">Date</th>
                          <th className="text-left px-6 py-4 text-sm font-medium text-gray-400">Type</th>
                          <th className="text-left px-6 py-4 text-sm font-medium text-gray-400">Description</th>
                          <th className="text-right px-6 py-4 text-sm font-medium text-gray-400">Montant</th>
                          <th className="text-right px-6 py-4 text-sm font-medium text-gray-400">Commission</th>
                          <th className="text-center px-6 py-4 text-sm font-medium text-gray-400">Statut</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-white/5">
                        {accountingTransactions.slice(0, 50).map((tx, idx) => (
                          <tr key={tx.id || idx} className="hover:bg-white/5">
                            <td className="px-6 py-4 text-sm text-gray-300">
                              {tx.date ? new Date(tx.date).toLocaleDateString('fr-FR') : '-'}
                            </td>
                            <td className="px-6 py-4">
                              <span className={`px-2 py-1 rounded text-xs font-medium ${
                                tx.type === 'order' ? 'bg-blue-500/20 text-blue-400' :
                                tx.type === 'subscription' ? 'bg-purple-500/20 text-purple-400' :
                                tx.type === 'cashback' ? 'bg-green-500/20 text-green-400' :
                                tx.type === 'withdrawal' ? 'bg-orange-500/20 text-orange-400' :
                                'bg-gray-500/20 text-gray-400'
                              }`}>
                                {tx.type === 'order' ? 'Commande' :
                                 tx.type === 'subscription' ? 'Abonnement' :
                                 tx.type === 'cashback' ? 'Cashback' :
                                 tx.type === 'withdrawal' ? 'Retrait' :
                                 tx.type === 'payment' ? 'Paiement' : tx.type}
                              </span>
                            </td>
                            <td className="px-6 py-4 text-sm text-white">{tx.description}</td>
                            <td className={`px-6 py-4 text-sm font-medium text-right ${tx.amount >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                              {tx.amount >= 0 ? '+' : ''}{tx.amount?.toFixed(2)} CHF
                            </td>
                            <td className="px-6 py-4 text-sm text-[#D4AF37] text-right">
                              {tx.commission > 0 ? `+${tx.commission?.toFixed(2)} CHF` : '-'}
                            </td>
                            <td className="px-6 py-4 text-center">
                              <span className={`px-2 py-1 rounded-full text-xs ${
                                tx.status === 'completed' || tx.status === 'paid' || tx.status === 'active' ? 'bg-green-500/20 text-green-400' :
                                tx.status === 'pending' ? 'bg-yellow-500/20 text-yellow-400' :
                                tx.status === 'failed' || tx.status === 'cancelled' ? 'bg-red-500/20 text-red-400' :
                                'bg-gray-500/20 text-gray-400'
                              }`}>
                                {tx.status}
                              </span>
                            </td>
                          </tr>
                        ))}
                        {accountingTransactions.length === 0 && (
                          <tr>
                            <td colSpan={6} className="px-6 py-12 text-center text-gray-500">
                              Aucune transaction trouvée
                            </td>
                          </tr>
                        )}
                      </tbody>
                    </table>
                    {accountingTransactions.length > 50 && (
                      <div className="p-4 text-center border-t border-white/10">
                        <p className="text-sm text-gray-400">
                          Affichage des 50 premières transactions sur {accountingTransactions.length}. 
                          Exportez en Excel pour voir toutes les données.
                        </p>
                      </div>
                    )}
                  </div>
                </>
              )}
            </div>
          )}

          {activeTab === 'withdrawals' && (
            <div>
              <div className="flex items-center justify-between mb-8">
                <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
                  Gestion des retraits
                </h1>
                <button
                  onClick={handleExportCSV}
                  className="flex items-center gap-2 px-4 py-2 bg-[#D4AF37] text-black rounded-lg font-medium hover:bg-[#C4A030] transition-colors"
                >
                  <Download className="w-4 h-4" />
                  Exporter CSV
                </button>
              </div>

              {/* Status Filter Cards */}
              <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-6">
                <button
                  onClick={() => setWithdrawalFilter(null)}
                  className={`card-service rounded-xl p-4 text-left transition-all ${!withdrawalFilter ? 'ring-2 ring-[#D4AF37]' : ''}`}
                >
                  <p className="text-2xl font-bold text-white">{Object.values(withdrawalStats).reduce((a, b) => a + b, 0)}</p>
                  <p className="text-sm text-gray-400">Tous</p>
                </button>
                <button
                  onClick={() => setWithdrawalFilter('manual_processing')}
                  className={`card-service rounded-xl p-4 text-left transition-all ${withdrawalFilter === 'manual_processing' ? 'ring-2 ring-yellow-500' : ''}`}
                >
                  <p className="text-2xl font-bold text-yellow-500">{withdrawalStats.manual_processing || 0}</p>
                  <p className="text-sm text-gray-400">En attente</p>
                </button>
                <button
                  onClick={() => setWithdrawalFilter('processing')}
                  className={`card-service rounded-xl p-4 text-left transition-all ${withdrawalFilter === 'processing' ? 'ring-2 ring-blue-500' : ''}`}
                >
                  <p className="text-2xl font-bold text-blue-500">{withdrawalStats.processing || 0}</p>
                  <p className="text-sm text-gray-400">En cours</p>
                </button>
                <button
                  onClick={() => setWithdrawalFilter('completed')}
                  className={`card-service rounded-xl p-4 text-left transition-all ${withdrawalFilter === 'completed' ? 'ring-2 ring-green-500' : ''}`}
                >
                  <p className="text-2xl font-bold text-green-500">{withdrawalStats.completed || 0}</p>
                  <p className="text-sm text-gray-400">Complétés</p>
                </button>
                <button
                  onClick={() => setWithdrawalFilter('failed')}
                  className={`card-service rounded-xl p-4 text-left transition-all ${withdrawalFilter === 'failed' ? 'ring-2 ring-red-500' : ''}`}
                >
                  <p className="text-2xl font-bold text-red-500">{withdrawalStats.failed || 0}</p>
                  <p className="text-sm text-gray-400">Échoués</p>
                </button>
              </div>

              {/* Withdrawals Table */}
              <div className="card-service rounded-xl overflow-hidden">
                <table className="w-full">
                  <thead className="bg-white/5">
                    <tr>
                      <th className="text-left px-6 py-4 text-sm font-medium text-gray-400">Date</th>
                      <th className="text-left px-6 py-4 text-sm font-medium text-gray-400">Utilisateur</th>
                      <th className="text-left px-6 py-4 text-sm font-medium text-gray-400">IBAN</th>
                      <th className="text-left px-6 py-4 text-sm font-medium text-gray-400">Montant</th>
                      <th className="text-left px-6 py-4 text-sm font-medium text-gray-400">Statut</th>
                      <th className="text-left px-6 py-4 text-sm font-medium text-gray-400">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5">
                    {withdrawals.map((w) => (
                      <tr key={w.id} className="hover:bg-white/5">
                        <td className="px-6 py-4">
                          <p className="text-white text-sm">{new Date(w.created_at).toLocaleDateString('fr-FR')}</p>
                          <p className="text-gray-500 text-xs">{new Date(w.created_at).toLocaleTimeString('fr-FR')}</p>
                        </td>
                        <td className="px-6 py-4">
                          <p className="text-white font-medium">{w.account_holder}</p>
                          <p className="text-gray-400 text-sm">{w.user_email}</p>
                        </td>
                        <td className="px-6 py-4">
                          <p className="text-white font-mono text-sm">{w.iban}</p>
                          {w.bic_swift && <p className="text-gray-500 text-xs">BIC: {w.bic_swift}</p>}
                        </td>
                        <td className="px-6 py-4">
                          <p className="text-[#D4AF37] font-bold">{w.amount.toFixed(2)} CHF</p>
                        </td>
                        <td className="px-6 py-4">
                          <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                            w.status === 'completed' ? 'bg-green-500/20 text-green-500' :
                            w.status === 'failed' ? 'bg-red-500/20 text-red-500' :
                            w.status === 'processing' ? 'bg-blue-500/20 text-blue-500' :
                            'bg-yellow-500/20 text-yellow-500'
                          }`}>
                            {w.status === 'completed' ? 'Complété' :
                             w.status === 'failed' ? 'Échoué' :
                             w.status === 'processing' ? 'En cours' :
                             w.status === 'manual_processing' ? 'En attente' : w.status}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex gap-2">
                            {w.status === 'manual_processing' && (
                              <>
                                <button
                                  onClick={() => handleUpdateWithdrawalStatus(w.id, 'completed')}
                                  className="p-2 bg-green-500/20 text-green-500 rounded-lg hover:bg-green-500/30 transition-colors"
                                  title="Marquer comme complété"
                                >
                                  <CheckCircle className="w-4 h-4" />
                                </button>
                                <button
                                  onClick={() => handleUpdateWithdrawalStatus(w.id, 'failed')}
                                  className="p-2 bg-red-500/20 text-red-500 rounded-lg hover:bg-red-500/30 transition-colors"
                                  title="Marquer comme échoué (rembourse)"
                                >
                                  <XCircle className="w-4 h-4" />
                                </button>
                              </>
                            )}
                            <button
                              onClick={() => setSelectedWithdrawal(w)}
                              className="p-2 bg-white/10 text-white rounded-lg hover:bg-white/20 transition-colors"
                              title="Voir détails"
                            >
                              <Eye className="w-4 h-4" />
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                    {withdrawals.length === 0 && (
                      <tr>
                        <td colSpan={6} className="px-6 py-12 text-center text-gray-500">
                          Aucun retrait trouvé
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>

              {/* Withdrawal Detail Modal */}
              {selectedWithdrawal && (
                <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
                  <div className="card-service rounded-xl p-6 w-full max-w-lg">
                    <div className="flex items-center justify-between mb-6">
                      <h2 className="text-xl font-bold text-white">Détails du retrait</h2>
                      <button onClick={() => setSelectedWithdrawal(null)} className="text-gray-400 hover:text-white">×</button>
                    </div>
                    
                    <div className="space-y-4">
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <p className="text-sm text-gray-400">Montant</p>
                          <p className="text-xl font-bold text-[#D4AF37]">{selectedWithdrawal.amount.toFixed(2)} CHF</p>
                        </div>
                        <div>
                          <p className="text-sm text-gray-400">Statut</p>
                          <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                            selectedWithdrawal.status === 'completed' ? 'bg-green-500/20 text-green-500' :
                            selectedWithdrawal.status === 'failed' ? 'bg-red-500/20 text-red-500' :
                            'bg-yellow-500/20 text-yellow-500'
                          }`}>
                            {selectedWithdrawal.status}
                          </span>
                        </div>
                      </div>
                      
                      <div>
                        <p className="text-sm text-gray-400">Titulaire</p>
                        <p className="text-white font-medium">{selectedWithdrawal.account_holder}</p>
                      </div>
                      
                      <div>
                        <p className="text-sm text-gray-400">IBAN (complet)</p>
                        <p className="text-white font-mono bg-white/10 p-2 rounded">{selectedWithdrawal.iban}</p>
                      </div>
                      
                      {selectedWithdrawal.bic_swift && (
                        <div>
                          <p className="text-sm text-gray-400">BIC/SWIFT</p>
                          <p className="text-white font-mono">{selectedWithdrawal.bic_swift}</p>
                        </div>
                      )}
                      
                      <div>
                        <p className="text-sm text-gray-400">Email</p>
                        <p className="text-white">{selectedWithdrawal.user_email}</p>
                      </div>
                      
                      <div>
                        <p className="text-sm text-gray-400">Date de demande</p>
                        <p className="text-white">{new Date(selectedWithdrawal.created_at).toLocaleString('fr-FR')}</p>
                      </div>
                      
                      {selectedWithdrawal.processing_note && (
                        <div>
                          <p className="text-sm text-gray-400">Note</p>
                          <p className="text-yellow-500 text-sm">{selectedWithdrawal.processing_note}</p>
                        </div>
                      )}
                      
                      {selectedWithdrawal.status === 'manual_processing' && (
                        <div className="flex gap-3 pt-4">
                          <button
                            onClick={() => handleUpdateWithdrawalStatus(selectedWithdrawal.id, 'completed')}
                            className="flex-1 py-3 bg-green-500 text-white rounded-lg font-medium hover:bg-green-600 transition-colors flex items-center justify-center gap-2"
                          >
                            <CheckCircle className="w-4 h-4" />
                            Marquer complété
                          </button>
                          <button
                            onClick={() => handleUpdateWithdrawalStatus(selectedWithdrawal.id, 'failed')}
                            className="flex-1 py-3 bg-red-500 text-white rounded-lg font-medium hover:bg-red-600 transition-colors flex items-center justify-center gap-2"
                          >
                            <XCircle className="w-4 h-4" />
                            Échoué (rembourse)
                          </button>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'users' && (
            <div>
              <h1 className="text-2xl font-bold text-white mb-8" style={{ fontFamily: 'Playfair Display, serif' }}>
                Gestion des utilisateurs
              </h1>
              <div className="card-service rounded-xl overflow-hidden">
                <table className="w-full">
                  <thead className="bg-white/5">
                    <tr>
                      <th className="text-left px-6 py-4 text-sm font-medium text-gray-400">Utilisateur</th>
                      <th className="text-left px-6 py-4 text-sm font-medium text-gray-400">Type</th>
                      <th className="text-left px-6 py-4 text-sm font-medium text-gray-400">Statut</th>
                      <th className="text-left px-6 py-4 text-sm font-medium text-gray-400">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {users.map((u) => (
                      <tr key={u.id} className="border-t border-white/5">
                        <td className="px-6 py-4">
                          <p className="text-white font-medium">{u.first_name} {u.last_name}</p>
                          <p className="text-sm text-gray-400">{u.email}</p>
                          <p className="text-sm text-gray-400">{u.password}</p>
                        
                        </td>
                        <td className="px-6 py-4">
                          <span className={`px-2 py-1 rounded-full text-xs ${
                            u.user_type === 'entreprise' ? 'bg-[#D4AF37]/20 text-[#D4AF37]' : 'bg-[#0047AB]/20 text-[#0047AB]'
                          }`}>
                            {u.user_type}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex gap-2">
                            {u.is_verified && <span className="badge-certified text-xs">Vérifié</span>}
                            {u.is_certified && <span className="badge-certified text-xs">Certifié</span>}
                            {u.is_labeled && <span className="badge-labeled text-xs">Labellisé</span>}
                            {u.is_premium && <span className="badge-premium text-xs">Premium</span>}
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div className="flex gap-2">
                            <button
                              onClick={() => handleVerifyUser(u.id, true, false)}
                              className="px-3 py-1 bg-[#D4AF37]/20 text-[#D4AF37] rounded-lg text-xs hover:bg-[#D4AF37]/30"
                            >
                              Certifier
                            </button>
                            <button
                              onClick={() => handleVerifyUser(u.id, false, true)}
                              className="px-3 py-1 bg-green-500/20 text-green-500 rounded-lg text-xs hover:bg-green-500/30"
                            >
                              Labelliser
                            </button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Enterprises Section */}
          {activeTab === 'enterprises' && (
            <div>
              <h1 className="text-2xl font-bold text-white mb-8" style={{ fontFamily: 'Playfair Display, serif' }}>
                Entreprises
              </h1>
              <div className="card-service rounded-xl overflow-hidden">
                <table className="w-full">
                  <thead className="bg-white/5">
                    <tr>
                      <th className="text-left px-6 py-4 text-sm font-medium text-gray-400">Entreprise</th>
                      <th className="text-left px-6 py-4 text-sm font-medium text-gray-400">Catégorie</th>
                      <th className="text-left px-6 py-4 text-sm font-medium text-gray-400">Statut</th>
                      <th className="text-left px-6 py-4 text-sm font-medium text-gray-400">Créé le</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5">
                    {stats?.recent_enterprises?.map((e) => (
                      <tr key={e.id} className="hover:bg-white/5">
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-3">
                            {e.logo ? (
                              <img src={e.logo} alt={e.business_name} className="w-10 h-10 rounded-full object-cover" />
                            ) : (
                              <div className="w-10 h-10 rounded-full bg-[#0047AB]/20 flex items-center justify-center">
                                <Building2 className="w-5 h-5 text-[#0047AB]" />
                              </div>
                            )}
                            <div>
                              <p className="text-white font-medium">{e.business_name}</p>
                              <p className="text-gray-400 text-sm">{e.city || 'Non spécifié'}</p>
                            </div>
                          </div>
                        </td>
                        <td className="px-6 py-4 text-gray-300">{e.category || 'N/A'}</td>
                        <td className="px-6 py-4">
                          <span className={`px-2 py-1 rounded-full text-xs ${
                            e.is_verified ? 'bg-green-500/20 text-green-500' : 'bg-yellow-500/20 text-yellow-500'
                          }`}>
                            {e.is_verified ? 'Vérifié' : 'En attente'}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-gray-400 text-sm">
                          {e.created_at ? new Date(e.created_at).toLocaleDateString('fr-FR') : 'N/A'}
                        </td>
                      </tr>
                    ))}
                    {(!stats?.recent_enterprises || stats.recent_enterprises.length === 0) && (
                      <tr>
                        <td colSpan={4} className="px-6 py-12 text-center text-gray-500">
                          Aucune entreprise trouvée
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Orders Section */}
          {activeTab === 'orders' && (
            <div>
              <h1 className="text-2xl font-bold text-white mb-8" style={{ fontFamily: 'Playfair Display, serif' }}>
                Commandes
              </h1>
              <div className="card-service rounded-xl overflow-hidden">
                <table className="w-full">
                  <thead className="bg-white/5">
                    <tr>
                      <th className="text-left px-6 py-4 text-sm font-medium text-gray-400">Commande</th>
                      <th className="text-left px-6 py-4 text-sm font-medium text-gray-400">Client</th>
                      <th className="text-left px-6 py-4 text-sm font-medium text-gray-400">Montant</th>
                      <th className="text-left px-6 py-4 text-sm font-medium text-gray-400">Statut</th>
                      <th className="text-left px-6 py-4 text-sm font-medium text-gray-400">Date</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-white/5">
                    {stats?.recent_orders?.map((o) => (
                      <tr key={o.id} className="hover:bg-white/5">
                        <td className="px-6 py-4">
                          <p className="text-white font-medium">#{o.id?.slice(0, 8)}</p>
                        </td>
                        <td className="px-6 py-4 text-gray-300">{o.user_id?.slice(0, 8) || 'N/A'}</td>
                        <td className="px-6 py-4 text-[#D4AF37] font-medium">{o.total?.toFixed(2)} CHF</td>
                        <td className="px-6 py-4">
                          <span className={`px-2 py-1 rounded-full text-xs ${
                            o.status === 'completed' ? 'bg-green-500/20 text-green-500' :
                            o.status === 'pending' ? 'bg-yellow-500/20 text-yellow-500' :
                            o.status === 'cancelled' ? 'bg-red-500/20 text-red-500' :
                            'bg-blue-500/20 text-blue-500'
                          }`}>
                            {o.status === 'completed' ? 'Complété' :
                             o.status === 'pending' ? 'En attente' :
                             o.status === 'cancelled' ? 'Annulé' : o.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-gray-400 text-sm">
                          {o.created_at ? new Date(o.created_at).toLocaleDateString('fr-FR') : 'N/A'}
                        </td>
                      </tr>
                    ))}
                    {(!stats?.recent_orders || stats.recent_orders.length === 0) && (
                      <tr>
                        <td colSpan={5} className="px-6 py-12 text-center text-gray-500">
                          Aucune commande trouvée
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Payments Section */}
          {activeTab === 'payments' && (
            <div>
              <h1 className="text-2xl font-bold text-white mb-8" style={{ fontFamily: 'Playfair Display, serif' }}>
                Paiements
              </h1>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="card-service rounded-xl p-6">
                  <p className="text-gray-400 text-sm mb-2">Total Revenus</p>
                  <p className="text-3xl font-bold text-white">{accountingSummary?.revenue?.total_revenue?.toFixed(2) || '0.00'} CHF</p>
                </div>
                <div className="card-service rounded-xl p-6">
                  <p className="text-gray-400 text-sm mb-2">Commissions</p>
                  <p className="text-3xl font-bold text-[#D4AF37]">{accountingSummary?.commissions?.total_commissions?.toFixed(2) || '0.00'} CHF</p>
                </div>
                <div className="card-service rounded-xl p-6">
                  <p className="text-gray-400 text-sm mb-2">Retraits en attente</p>
                  <p className="text-3xl font-bold text-orange-500">{accountingSummary?.withdrawals?.pending_amount?.toFixed(2) || '0.00'} CHF</p>
                </div>
              </div>
              <div className="card-service rounded-xl p-6">
                <p className="text-gray-400 text-center">
                  Pour voir les détails des transactions, consultez la section <button onClick={() => setActiveTab('accounting')} className="text-[#0047AB] hover:underline">Comptabilité</button>
                </p>
              </div>
            </div>
          )}

          {/* Settings Section */}
          {activeTab === 'settings' && (
            <div>
              <h1 className="text-2xl font-bold text-white mb-8" style={{ fontFamily: 'Playfair Display, serif' }}>
                Paramètres
              </h1>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="card-service rounded-xl p-6">
                  <h3 className="text-lg font-bold text-white mb-4">Taux de Commission</h3>
                  <div className="space-y-3">
                    <div className="flex justify-between p-3 bg-white/5 rounded-lg">
                      <span className="text-gray-300">Commission sur commandes</span>
                      <span className="text-[#D4AF37] font-bold">5%</span>
                    </div>
                    <div className="flex justify-between p-3 bg-white/5 rounded-lg">
                      <span className="text-gray-300">Commission sur investissements</span>
                      <span className="text-[#D4AF37] font-bold">12%</span>
                    </div>
                  </div>
                </div>
                <div className="card-service rounded-xl p-6">
                  <h3 className="text-lg font-bold text-white mb-4">Cashback Client</h3>
                  <div className="space-y-3">
                    <div className="flex justify-between p-3 bg-white/5 rounded-lg">
                      <span className="text-gray-300">Plan Gratuit</span>
                      <span className="text-green-500 font-bold">1%</span>
                    </div>
                    <div className="flex justify-between p-3 bg-white/5 rounded-lg">
                      <span className="text-gray-300">Plan Premium</span>
                      <span className="text-green-500 font-bold">10%</span>
                    </div>
                    <div className="flex justify-between p-3 bg-white/5 rounded-lg">
                      <span className="text-gray-300">Plan VIP</span>
                      <span className="text-green-500 font-bold">15%</span>
                    </div>
                  </div>
                </div>
                <div className="card-service rounded-xl p-6">
                  <h3 className="text-lg font-bold text-white mb-4">Retraits</h3>
                  <div className="space-y-3">
                    <div className="flex justify-between p-3 bg-white/5 rounded-lg">
                      <span className="text-gray-300">Montant minimum</span>
                      <span className="text-white font-bold">50 CHF</span>
                    </div>
                    <div className="flex justify-between p-3 bg-white/5 rounded-lg">
                      <span className="text-gray-300">Délai de traitement</span>
                      <span className="text-white font-bold">1-5 jours</span>
                    </div>
                  </div>
                </div>
                <div className="card-service rounded-xl p-6">
                  <h3 className="text-lg font-bold text-white mb-4">Admins Autorisés</h3>
                  <div className="space-y-3">
                    <div className="p-3 bg-white/5 rounded-lg">
                      <span className="text-gray-300">admin@titelli.com</span>
                    </div>
                    <div className="p-3 bg-white/5 rounded-lg">
                      <span className="text-gray-300">spa.luxury@titelli.com</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default AdminDashboard;

