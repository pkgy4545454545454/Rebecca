import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import {
  LayoutDashboard, User, MessageSquare, Bell, Settings, LogOut,
  Star, TrendingUp, DollarSign, Users, Eye, Heart, Share2,
  Instagram, Facebook, Video, CheckCircle, XCircle, Clock,
  ChevronRight, Camera, Edit, Briefcase, Calendar,
  BarChart3, Award, Target, Sparkles, Gift, UserPlus, Trash2, Send
} from 'lucide-react';
import { influencersAPI, notificationsAPI, friendsAPI, messagesAPI } from '../services/api';
import { toast } from 'sonner';

const InfluencerDashboard = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [activeSection, setActiveSection] = useState('dashboard');
  const [profile, setProfile] = useState(null);
  const [collaborations, setCollaborations] = useState([]);
  const [stats, setStats] = useState({});
  const [notifications, setNotifications] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showEditProfile, setShowEditProfile] = useState(false);
  const [editForm, setEditForm] = useState({});
  
  // Friends states
  const [friends, setFriends] = useState([]);
  const [friendRequests, setFriendRequests] = useState({ received: [], sent: [] });
  const [suggestedFriends, setSuggestedFriends] = useState([]);

  useEffect(() => {
    if (user?.user_type !== 'influencer') {
      navigate('/');
      return;
    }
    fetchData();
  }, [user, navigate]);

  const fetchData = async () => {
    try {
      const [profileRes, notifRes] = await Promise.all([
        influencersAPI.getProfile(),
        notificationsAPI.list()
      ]);
      setProfile(profileRes.data.profile);
      setCollaborations(profileRes.data.collaborations || []);
      setStats(profileRes.data.stats || {});
      setNotifications(notifRes.data.notifications || []);
      setEditForm(profileRes.data.profile || {});
    } catch (error) {
      console.error('Error fetching data:', error);
      setProfile(null);
    } finally {
      setLoading(false);
    }
  };

  const fetchFriendsData = async () => {
    try {
      const [friendsRes, requestsRes, suggestionsRes] = await Promise.all([
        friendsAPI.list(),
        friendsAPI.getRequests(),
        friendsAPI.getSuggestions()
      ]);
      setFriends(friendsRes.data.friends || []);
      setFriendRequests(requestsRes.data || { received: [], sent: [] });
      setSuggestedFriends(suggestionsRes.data.suggestions || []);
    } catch (error) {
      console.error('Error fetching friends:', error);
    }
  };

  useEffect(() => {
    if (activeSection === 'amis') {
      fetchFriendsData();
    }
  }, [activeSection]);

  const handleUpdateProfile = async () => {
    try {
      const response = await influencersAPI.updateProfile(editForm);
      setProfile(response.data);
      setShowEditProfile(false);
      toast.success('Profil mis à jour avec succès');
    } catch (error) {
      toast.error('Erreur lors de la mise à jour');
    }
  };

  const handleRespondToCollab = async (collabId, accept) => {
    try {
      await influencersAPI.respondToCollaboration(collabId, accept);
      toast.success(accept ? 'Collaboration acceptée !' : 'Collaboration déclinée');
      fetchData();
    } catch (error) {
      toast.error('Erreur lors de la réponse');
    }
  };

  const handleSendFriendRequest = async (friendId) => {
    try {
      await friendsAPI.sendRequest(friendId);
      toast.success('Demande d\'ami envoyée');
      fetchFriendsData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erreur');
    }
  };

  const handleRespondToFriendRequest = async (friendshipId, accept) => {
    try {
      await friendsAPI.respond(friendshipId, accept);
      toast.success(accept ? 'Ami ajouté' : 'Demande refusée');
      fetchFriendsData();
    } catch (error) {
      toast.error('Erreur');
    }
  };

  const handleRemoveFriend = async (friendshipId) => {
    try {
      await friendsAPI.remove(friendshipId);
      toast.success('Ami supprimé');
      fetchFriendsData();
    } catch (error) {
      toast.error('Erreur');
    }
  };

  const formatNumber = (num) => {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num?.toString() || '0';
  };

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  // Get active collaboration
  const activeCollab = collaborations.find(c => c.status === 'active');
  const pendingCollabs = collaborations.filter(c => c.status === 'pending');

  const menuItems = [
    { id: 'dashboard', label: 'Tableau de bord', icon: LayoutDashboard },
    { id: 'statistiques', label: 'Statistiques', icon: BarChart3 },
    { id: 'amis', label: 'Amis', icon: Users },
    { id: 'offres', label: 'Offres reçues', icon: Gift, badge: pendingCollabs.length },
    { id: 'statut', label: 'Statut en cours', icon: Briefcase },
    { id: 'profile', label: 'Mon profil', icon: User },
    { id: 'messages', label: 'Messages', icon: MessageSquare },
    { id: 'settings', label: 'Paramètres', icon: Settings },
  ];

  if (loading) {
    return (
      <div className="min-h-screen bg-[#050505] flex items-center justify-center">
        <div className="w-12 h-12 border-4 border-purple-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#050505] flex" data-testid="influencer-dashboard">
      {/* Sidebar */}
      <aside className="w-64 border-r border-white/5 bg-[#0A0A0A] flex flex-col">
        <div className="p-6 border-b border-white/5">
          <Link to="/" className="flex items-center gap-3">
            <img src="/logo_titelli.png" alt="Titelli" className="w-10 h-10 object-contain" />
            <span className="text-xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
              Titelli
            </span>
          </Link>
        </div>

        {/* Profile Card */}
        <div className="p-4 border-b border-white/5">
          <div className="flex items-center gap-3">
            <div className="relative">
              <img
                src={profile?.image || `https://ui-avatars.com/api/?name=${user?.first_name || 'I'}&background=9333ea&color=fff`}
                alt="Profile"
                className="w-12 h-12 rounded-full object-cover border-2 border-purple-500/50"
              />
              <div className="absolute -bottom-1 -right-1 w-5 h-5 bg-purple-500 rounded-full flex items-center justify-center">
                <Star className="w-3 h-3 text-white fill-white" />
              </div>
            </div>
            <div className="flex-1 min-w-0">
              <p className="text-white font-medium truncate">{profile?.name || user?.first_name}</p>
              <p className="text-xs text-purple-400">{profile?.category || 'Influenceur'}</p>
            </div>
          </div>
          <div className="mt-3 flex items-center gap-2 text-sm">
            <span className="text-gray-400">{formatNumber(profile?.followers || 0)} abonnés</span>
            <span className="text-gray-600">•</span>
            <span className="text-green-400">{profile?.engagement_rate || 0}% engagement</span>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 p-4 space-y-1">
          {menuItems.map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveSection(item.id)}
              className={`w-full flex items-center justify-between px-4 py-3 rounded-xl transition-all ${
                activeSection === item.id
                  ? 'bg-purple-500/20 text-purple-400'
                  : 'text-gray-400 hover:bg-white/5 hover:text-white'
              }`}
              data-testid={`menu-${item.id}`}
            >
              <div className="flex items-center gap-3">
                <item.icon className="w-5 h-5" />
                <span>{item.label}</span>
              </div>
              {item.badge > 0 && (
                <span className="w-5 h-5 bg-purple-500 rounded-full text-xs flex items-center justify-center text-white">
                  {item.badge}
                </span>
              )}
            </button>
          ))}
        </nav>

        {/* Logout */}
        <div className="p-4 border-t border-white/5">
          <button
            onClick={handleLogout}
            className="w-full flex items-center gap-3 px-4 py-3 rounded-xl text-red-400 hover:bg-red-500/10 transition-all"
          >
            <LogOut className="w-5 h-5" />
            <span>Déconnexion</span>
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 p-8 overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
              {activeSection === 'dashboard' && 'Tableau de bord'}
              {activeSection === 'statistiques' && 'Statistiques'}
              {activeSection === 'amis' && 'Mes Amis'}
              {activeSection === 'offres' && 'Offres reçues'}
              {activeSection === 'statut' && 'Statut en cours'}
              {activeSection === 'profile' && 'Mon profil'}
              {activeSection === 'messages' && 'Messages'}
              {activeSection === 'settings' && 'Paramètres'}
            </h1>
            <p className="text-gray-400 mt-1">
              Bienvenue, {user?.first_name || 'Influenceur'} !
            </p>
          </div>
          <div className="flex items-center gap-4">
            <button className="relative p-3 bg-white/5 rounded-xl text-gray-400 hover:text-white transition-colors">
              <Bell className="w-5 h-5" />
              {notifications.filter(n => !n.is_read).length > 0 && (
                <span className="absolute -top-1 -right-1 w-5 h-5 bg-purple-500 rounded-full text-xs flex items-center justify-center text-white">
                  {notifications.filter(n => !n.is_read).length}
                </span>
              )}
            </button>
          </div>
        </div>

        {/* Dashboard Section */}
        {activeSection === 'dashboard' && (
          <div className="space-y-6">
            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="card-service rounded-xl p-6 border-purple-500/20 bg-gradient-to-br from-purple-500/10 to-transparent">
                <div className="flex items-center justify-between mb-4">
                  <DollarSign className="w-8 h-8 text-purple-400" />
                  <span className="text-xs text-purple-400 bg-purple-500/20 px-2 py-1 rounded-full">Ce mois</span>
                </div>
                <p className="text-3xl font-bold text-white">{stats.total_investment || 0} CHF</p>
                <p className="text-sm text-gray-400 mt-1">Revenus des collaborations</p>
              </div>

              <div className="card-service rounded-xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <Eye className="w-8 h-8 text-blue-400" />
                </div>
                <p className="text-3xl font-bold text-white">{formatNumber(profile?.total_views || 0)}</p>
                <p className="text-sm text-gray-400 mt-1">Vues totales</p>
              </div>

              <div className="card-service rounded-xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <Heart className="w-8 h-8 text-red-400" />
                </div>
                <p className="text-3xl font-bold text-white">{formatNumber(profile?.total_likes || 0)}</p>
                <p className="text-sm text-gray-400 mt-1">Likes totaux</p>
              </div>

              <div className="card-service rounded-xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <Briefcase className="w-8 h-8 text-green-400" />
                </div>
                <p className="text-3xl font-bold text-white">{stats.total_collaborations || 0}</p>
                <p className="text-sm text-gray-400 mt-1">Collaborations réalisées</p>
              </div>
            </div>

            {/* Current Status Alert */}
            {activeCollab ? (
              <div className="card-service rounded-xl p-6 border-green-500/30 bg-gradient-to-r from-green-500/10 to-transparent">
                <div className="flex items-center gap-3 mb-2">
                  <CheckCircle className="w-6 h-6 text-green-400" />
                  <h2 className="text-lg font-semibold text-white">En collaboration active</h2>
                </div>
                <p className="text-gray-400 mb-4">
                  Vous êtes actuellement en collaboration avec <span className="text-white font-medium">{activeCollab.enterprise_name}</span>
                </p>
                <div className="flex items-center gap-4 text-sm">
                  <span className="text-purple-400 font-semibold">{activeCollab.budget} CHF</span>
                  {activeCollab.end_date && (
                    <span className="text-gray-500 flex items-center gap-1">
                      <Clock className="w-4 h-4" />
                      Fin: {new Date(activeCollab.end_date).toLocaleDateString('fr-FR')}
                    </span>
                  )}
                </div>
              </div>
            ) : (
              <div className="card-service rounded-xl p-6 border-gray-500/30">
                <div className="flex items-center gap-3">
                  <Clock className="w-6 h-6 text-gray-400" />
                  <div>
                    <h2 className="text-lg font-semibold text-white">Pas de collaboration en cours</h2>
                    <p className="text-gray-400 text-sm">Vous êtes disponible pour de nouvelles opportunités</p>
                  </div>
                </div>
              </div>
            )}

            {/* Pending Offers */}
            {pendingCollabs.length > 0 && (
              <div className="card-service rounded-xl p-6 border-yellow-500/30">
                <div className="flex items-center gap-3 mb-4">
                  <Gift className="w-5 h-5 text-yellow-400" />
                  <h2 className="text-lg font-semibold text-white">Offres en attente</h2>
                  <span className="px-2 py-0.5 bg-yellow-500/20 text-yellow-400 text-xs rounded-full">
                    {pendingCollabs.length}
                  </span>
                </div>
                <div className="space-y-3">
                  {pendingCollabs.slice(0, 3).map((collab) => (
                    <div key={collab.id} className="p-4 bg-white/5 rounded-xl">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-full flex items-center justify-center text-white font-bold">
                            {collab.enterprise_name?.[0] || 'E'}
                          </div>
                          <div>
                            <p className="text-white font-medium">{collab.enterprise_name || 'Entreprise'}</p>
                            <p className="text-sm text-gray-400">{collab.message?.substring(0, 40)}...</p>
                          </div>
                        </div>
                        <div className="flex items-center gap-3">
                          <span className="text-purple-400 font-semibold">{collab.budget} CHF</span>
                          <button
                            onClick={() => handleRespondToCollab(collab.id, true)}
                            className="p-2 bg-green-500/20 text-green-400 rounded-lg hover:bg-green-500/30 transition-colors"
                          >
                            <CheckCircle className="w-5 h-5" />
                          </button>
                          <button
                            onClick={() => handleRespondToCollab(collab.id, false)}
                            className="p-2 bg-red-500/20 text-red-400 rounded-lg hover:bg-red-500/30 transition-colors"
                          >
                            <XCircle className="w-5 h-5" />
                          </button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
                {pendingCollabs.length > 3 && (
                  <button 
                    onClick={() => setActiveSection('offres')}
                    className="w-full mt-4 text-purple-400 text-sm hover:text-purple-300 transition-colors"
                  >
                    Voir toutes les offres ({pendingCollabs.length})
                  </button>
                )}
              </div>
            )}

            {/* Social Networks */}
            <div className="card-service rounded-xl p-6">
              <h2 className="text-lg font-semibold text-white mb-4">Mes réseaux sociaux</h2>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 bg-gradient-to-r from-pink-500/10 to-purple-500/10 rounded-xl border border-pink-500/20">
                  <div className="flex items-center gap-3 mb-3">
                    <Instagram className="w-6 h-6 text-pink-500" />
                    <span className="text-white font-medium">Instagram</span>
                  </div>
                  <p className="text-gray-400">{profile?.instagram || 'Non connecté'}</p>
                </div>
                <div className="p-4 bg-gradient-to-r from-white/5 to-white/10 rounded-xl border border-white/10">
                  <div className="flex items-center gap-3 mb-3">
                    <Video className="w-6 h-6 text-white" />
                    <span className="text-white font-medium">TikTok</span>
                  </div>
                  <p className="text-gray-400">{profile?.tiktok || 'Non connecté'}</p>
                </div>
                <div className="p-4 bg-gradient-to-r from-blue-500/10 to-blue-600/10 rounded-xl border border-blue-500/20">
                  <div className="flex items-center gap-3 mb-3">
                    <Facebook className="w-6 h-6 text-blue-500" />
                    <span className="text-white font-medium">Facebook</span>
                  </div>
                  <p className="text-gray-400">{profile?.facebook || 'Non connecté'}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Statistiques Section */}
        {activeSection === 'statistiques' && (
          <div className="space-y-6">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="card-service rounded-xl p-6">
                <div className="flex items-center gap-3 mb-4">
                  <Eye className="w-6 h-6 text-blue-400" />
                  <span className="text-gray-400">Vues totales</span>
                </div>
                <p className="text-4xl font-bold text-white">{formatNumber(profile?.total_views || 0)}</p>
                <p className="text-sm text-green-400 mt-2">+12% ce mois</p>
              </div>
              <div className="card-service rounded-xl p-6">
                <div className="flex items-center gap-3 mb-4">
                  <Heart className="w-6 h-6 text-red-400" />
                  <span className="text-gray-400">Likes totaux</span>
                </div>
                <p className="text-4xl font-bold text-white">{formatNumber(profile?.total_likes || 0)}</p>
                <p className="text-sm text-green-400 mt-2">+8% ce mois</p>
              </div>
              <div className="card-service rounded-xl p-6">
                <div className="flex items-center gap-3 mb-4">
                  <Share2 className="w-6 h-6 text-purple-400" />
                  <span className="text-gray-400">Partages</span>
                </div>
                <p className="text-4xl font-bold text-white">{formatNumber(profile?.total_shares || 0)}</p>
                <p className="text-sm text-green-400 mt-2">+15% ce mois</p>
              </div>
            </div>

            <div className="card-service rounded-xl p-6">
              <h2 className="text-lg font-semibold text-white mb-4">Performance des collaborations</h2>
              <div className="space-y-4">
                <div className="flex items-center justify-between p-4 bg-white/5 rounded-xl">
                  <span className="text-gray-400">Collaborations totales</span>
                  <span className="text-white font-semibold">{stats.total_collaborations || 0}</span>
                </div>
                <div className="flex items-center justify-between p-4 bg-white/5 rounded-xl">
                  <span className="text-gray-400">Collaborations actives</span>
                  <span className="text-green-400 font-semibold">{stats.active_collaborations || 0}</span>
                </div>
                <div className="flex items-center justify-between p-4 bg-white/5 rounded-xl">
                  <span className="text-gray-400">Demandes en attente</span>
                  <span className="text-yellow-400 font-semibold">{stats.pending_requests || 0}</span>
                </div>
                <div className="flex items-center justify-between p-4 bg-white/5 rounded-xl">
                  <span className="text-gray-400">Revenus totaux</span>
                  <span className="text-purple-400 font-semibold">{stats.total_investment || 0} CHF</span>
                </div>
              </div>
            </div>

            <div className="card-service rounded-xl p-6">
              <h2 className="text-lg font-semibold text-white mb-4">Taux d'engagement</h2>
              <div className="flex items-center gap-8">
                <div className="relative w-32 h-32">
                  <svg className="w-full h-full transform -rotate-90">
                    <circle cx="64" cy="64" r="56" fill="none" stroke="#1F1F1F" strokeWidth="8" />
                    <circle 
                      cx="64" cy="64" r="56" fill="none" 
                      stroke="#9333ea" strokeWidth="8"
                      strokeDasharray={`${(profile?.engagement_rate || 0) * 3.52} 352`}
                      strokeLinecap="round"
                    />
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-2xl font-bold text-white">{profile?.engagement_rate || 0}%</span>
                  </div>
                </div>
                <div>
                  <p className="text-gray-400 mb-2">Votre taux d'engagement est <span className="text-green-400">excellent</span></p>
                  <p className="text-sm text-gray-500">Moyenne du secteur: 3.5%</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Amis Section */}
        {activeSection === 'amis' && (
          <div className="space-y-6">
            {/* Friend Requests */}
            {friendRequests.received.length > 0 && (
              <div className="card-service rounded-xl p-6 border-yellow-500/30">
                <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                  <Bell className="w-5 h-5 text-yellow-500" />
                  Demandes d'amis ({friendRequests.received.length})
                </h2>
                <div className="space-y-3">
                  {friendRequests.received.map((request) => (
                    <div key={request.id} className="flex items-center justify-between p-4 bg-white/5 rounded-xl">
                      <div className="flex items-center gap-3">
                        <div className="w-12 h-12 rounded-full bg-purple-500/30 flex items-center justify-center text-white font-bold">
                          {request.sender?.first_name?.[0]}{request.sender?.last_name?.[0]}
                        </div>
                        <div>
                          <p className="text-white font-medium">{request.sender?.first_name} {request.sender?.last_name}</p>
                          <p className="text-sm text-gray-400">{request.message || 'Souhaite vous ajouter'}</p>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleRespondToFriendRequest(request.id, true)}
                          className="p-2 bg-green-500/20 text-green-400 rounded-lg hover:bg-green-500/30"
                        >
                          <CheckCircle className="w-5 h-5" />
                        </button>
                        <button
                          onClick={() => handleRespondToFriendRequest(request.id, false)}
                          className="p-2 bg-red-500/20 text-red-400 rounded-lg hover:bg-red-500/30"
                        >
                          <XCircle className="w-5 h-5" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Friends List */}
            <div className="card-service rounded-xl p-6">
              <h2 className="text-lg font-semibold text-white mb-4">Mes amis ({friends.length})</h2>
              {friends.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {friends.map((friend) => (
                    <div key={friend.id} className="flex items-center justify-between p-4 bg-white/5 rounded-xl">
                      <div className="flex items-center gap-3">
                        <div className="w-12 h-12 rounded-full bg-purple-500/30 flex items-center justify-center text-white font-bold overflow-hidden">
                          {friend.avatar ? (
                            <img src={friend.avatar.startsWith('http') ? friend.avatar : `${process.env.REACT_APP_BACKEND_URL}${friend.avatar}`} alt="" className="w-full h-full object-cover" />
                          ) : (
                            <>{friend.first_name?.[0]}{friend.last_name?.[0]}</>
                          )}
                        </div>
                        <div>
                          <p className="text-white font-medium">{friend.first_name} {friend.last_name}</p>
                          <p className="text-sm text-gray-400">{friend.city || 'Lausanne'}</p>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <button className="p-2 bg-purple-500/20 text-purple-400 rounded-lg hover:bg-purple-500/30">
                          <MessageSquare className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => handleRemoveFriend(friend.friendship_id)}
                          className="p-2 bg-red-500/10 text-red-400 rounded-lg hover:bg-red-500/20"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-center py-8">
                  <Users className="w-12 h-12 text-gray-600 mx-auto mb-3" />
                  <p className="text-gray-400">Aucun ami pour le moment</p>
                </div>
              )}
            </div>

            {/* Suggested Friends */}
            {suggestedFriends.length > 0 && (
              <div className="card-service rounded-xl p-6">
                <h2 className="text-lg font-semibold text-white mb-4">Suggestions d'amis</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {suggestedFriends.map((suggestion) => (
                    <div key={suggestion.id} className="p-4 bg-white/5 rounded-xl">
                      <div className="flex items-center gap-3 mb-3">
                        <div className="w-12 h-12 rounded-full bg-gray-600 flex items-center justify-center text-white font-bold">
                          {suggestion.first_name?.[0]}{suggestion.last_name?.[0]}
                        </div>
                        <div>
                          <p className="text-white font-medium">{suggestion.first_name} {suggestion.last_name}</p>
                          <p className="text-sm text-gray-400">{suggestion.city || 'Lausanne'}</p>
                        </div>
                      </div>
                      <button
                        onClick={() => handleSendFriendRequest(suggestion.id)}
                        className="w-full btn-secondary text-sm flex items-center justify-center gap-2"
                      >
                        <UserPlus className="w-4 h-4" />
                        Ajouter
                      </button>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Offres reçues Section */}
        {activeSection === 'offres' && (
          <div className="space-y-6">
            {pendingCollabs.length > 0 ? (
              <div className="space-y-4">
                {pendingCollabs.map((collab) => (
                  <div key={collab.id} className="card-service rounded-xl p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex items-center gap-4">
                        <div className="w-14 h-14 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl flex items-center justify-center text-white text-lg font-bold">
                          {collab.enterprise_name?.[0] || 'E'}
                        </div>
                        <div>
                          <h3 className="text-white font-semibold">{collab.enterprise_name || 'Entreprise'}</h3>
                          <p className="text-gray-400 text-sm mt-1">{collab.message || 'Demande de collaboration'}</p>
                          <div className="flex items-center gap-4 mt-2 text-xs text-gray-500">
                            <span className="flex items-center gap-1">
                              <Calendar className="w-3 h-3" />
                              {new Date(collab.created_at).toLocaleDateString('fr-FR')}
                            </span>
                          </div>
                        </div>
                      </div>
                      <div className="text-right">
                        <p className="text-xl font-bold text-purple-400">{collab.budget} CHF</p>
                      </div>
                    </div>
                    <div className="flex gap-3 mt-4 pt-4 border-t border-white/10">
                      <button
                        onClick={() => handleRespondToCollab(collab.id, true)}
                        className="flex-1 py-2 bg-green-500/20 text-green-400 rounded-lg hover:bg-green-500/30 transition-colors flex items-center justify-center gap-2"
                      >
                        <CheckCircle className="w-4 h-4" /> Accepter
                      </button>
                      <button
                        onClick={() => handleRespondToCollab(collab.id, false)}
                        className="flex-1 py-2 bg-red-500/20 text-red-400 rounded-lg hover:bg-red-500/30 transition-colors flex items-center justify-center gap-2"
                      >
                        <XCircle className="w-4 h-4" /> Décliner
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="card-service rounded-xl p-12 text-center">
                <Gift className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-white mb-2">Aucune offre en attente</h3>
                <p className="text-gray-400">Les demandes de collaboration des entreprises apparaîtront ici.</p>
              </div>
            )}
          </div>
        )}

        {/* Statut en cours Section */}
        {activeSection === 'statut' && (
          <div className="space-y-6">
            {activeCollab ? (
              <div className="card-service rounded-xl p-8 border-green-500/30">
                <div className="flex items-center gap-4 mb-6">
                  <div className="w-16 h-16 bg-gradient-to-br from-green-500 to-emerald-600 rounded-2xl flex items-center justify-center">
                    <CheckCircle className="w-8 h-8 text-white" />
                  </div>
                  <div>
                    <h2 className="text-2xl font-bold text-white">Collaboration en cours</h2>
                    <p className="text-green-400">Statut: Actif</p>
                  </div>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="p-4 bg-white/5 rounded-xl">
                    <p className="text-gray-400 text-sm mb-1">Entreprise</p>
                    <p className="text-white font-semibold text-lg">{activeCollab.enterprise_name}</p>
                  </div>
                  <div className="p-4 bg-white/5 rounded-xl">
                    <p className="text-gray-400 text-sm mb-1">Budget</p>
                    <p className="text-purple-400 font-semibold text-lg">{activeCollab.budget} CHF</p>
                  </div>
                  <div className="p-4 bg-white/5 rounded-xl">
                    <p className="text-gray-400 text-sm mb-1">Date de début</p>
                    <p className="text-white font-semibold">
                      {activeCollab.updated_at ? new Date(activeCollab.updated_at).toLocaleDateString('fr-FR') : 'N/A'}
                    </p>
                  </div>
                  <div className="p-4 bg-white/5 rounded-xl">
                    <p className="text-gray-400 text-sm mb-1">Date de fin prévue</p>
                    <p className="text-white font-semibold">
                      {activeCollab.end_date ? new Date(activeCollab.end_date).toLocaleDateString('fr-FR') : 'À définir'}
                    </p>
                  </div>
                </div>

                <div className="mt-6 p-4 bg-white/5 rounded-xl">
                  <p className="text-gray-400 text-sm mb-2">Description du projet</p>
                  <p className="text-white">{activeCollab.message || 'Aucune description fournie'}</p>
                </div>
              </div>
            ) : (
              <div className="card-service rounded-xl p-12 text-center">
                <Clock className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                <h3 className="text-xl font-semibold text-white mb-2">Pas de collaboration active</h3>
                <p className="text-gray-400 mb-6">Vous êtes actuellement disponible pour de nouvelles opportunités</p>
                <div className="inline-flex items-center gap-2 px-4 py-2 bg-green-500/20 text-green-400 rounded-full">
                  <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                  Disponible
                </div>
              </div>
            )}

            {/* Collaboration History */}
            <div className="card-service rounded-xl p-6">
              <h2 className="text-lg font-semibold text-white mb-4">Historique des collaborations</h2>
              {collaborations.filter(c => c.status === 'completed').length > 0 ? (
                <div className="space-y-3">
                  {collaborations.filter(c => c.status === 'completed').map((collab) => (
                    <div key={collab.id} className="p-4 bg-white/5 rounded-xl flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-gray-600 rounded-lg flex items-center justify-center text-white font-bold">
                          {collab.enterprise_name?.[0] || 'E'}
                        </div>
                        <div>
                          <p className="text-white font-medium">{collab.enterprise_name}</p>
                          <p className="text-sm text-gray-500">
                            {collab.updated_at ? new Date(collab.updated_at).toLocaleDateString('fr-FR') : 'N/A'}
                          </p>
                        </div>
                      </div>
                      <span className="text-purple-400 font-semibold">{collab.budget} CHF</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-gray-500 text-center py-4">Aucune collaboration terminée</p>
              )}
            </div>
          </div>
        )}

        {/* Profile Section */}
        {activeSection === 'profile' && (
          <div className="max-w-2xl space-y-6">
            <div className="card-service rounded-xl p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-lg font-semibold text-white">Informations du profil</h2>
                <button
                  onClick={() => setShowEditProfile(!showEditProfile)}
                  className="btn-secondary text-sm"
                >
                  {showEditProfile ? 'Annuler' : 'Modifier'}
                </button>
              </div>

              {showEditProfile ? (
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm text-gray-400 mb-2">Nom d'affichage</label>
                    <input
                      type="text"
                      value={editForm.name || ''}
                      onChange={(e) => setEditForm({...editForm, name: e.target.value})}
                      className="input-dark w-full"
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-400 mb-2">Catégorie</label>
                    <select
                      value={editForm.category || ''}
                      onChange={(e) => setEditForm({...editForm, category: e.target.value})}
                      className="input-dark w-full"
                    >
                      <option value="Lifestyle">Lifestyle</option>
                      <option value="Food">Food & Gastronomie</option>
                      <option value="Beauty">Beauté & Mode</option>
                      <option value="Tech">Tech & Gaming</option>
                      <option value="Sport">Sport & Fitness</option>
                      <option value="Travel">Voyage</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm text-gray-400 mb-2">Bio</label>
                    <textarea
                      value={editForm.bio || ''}
                      onChange={(e) => setEditForm({...editForm, bio: e.target.value})}
                      className="input-dark w-full h-24"
                      placeholder="Décrivez-vous en quelques mots..."
                    />
                  </div>
                  <div>
                    <label className="block text-sm text-gray-400 mb-2">Tarif par collaboration (CHF)</label>
                    <input
                      type="number"
                      value={editForm.price || ''}
                      onChange={(e) => setEditForm({...editForm, price: parseFloat(e.target.value)})}
                      className="input-dark w-full"
                    />
                  </div>
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                      <label className="block text-sm text-gray-400 mb-2">Instagram</label>
                      <input
                        type="text"
                        value={editForm.instagram || ''}
                        onChange={(e) => setEditForm({...editForm, instagram: e.target.value})}
                        className="input-dark w-full"
                        placeholder="@username"
                      />
                    </div>
                    <div>
                      <label className="block text-sm text-gray-400 mb-2">TikTok</label>
                      <input
                        type="text"
                        value={editForm.tiktok || ''}
                        onChange={(e) => setEditForm({...editForm, tiktok: e.target.value})}
                        className="input-dark w-full"
                        placeholder="@username"
                      />
                    </div>
                    <div>
                      <label className="block text-sm text-gray-400 mb-2">Facebook</label>
                      <input
                        type="text"
                        value={editForm.facebook || ''}
                        onChange={(e) => setEditForm({...editForm, facebook: e.target.value})}
                        className="input-dark w-full"
                        placeholder="Page Facebook"
                      />
                    </div>
                  </div>
                  <button onClick={handleUpdateProfile} className="btn-primary w-full">
                    Enregistrer les modifications
                  </button>
                </div>
              ) : (
                <div className="space-y-4">
                  <div className="flex items-center gap-6">
                    <div className="relative">
                      <img
                        src={profile?.image || `https://ui-avatars.com/api/?name=${profile?.name || 'I'}&background=9333ea&color=fff&size=128`}
                        alt="Profile"
                        className="w-24 h-24 rounded-full object-cover border-4 border-purple-500/30"
                      />
                      <button className="absolute bottom-0 right-0 p-2 bg-purple-500 rounded-full text-white">
                        <Camera className="w-4 h-4" />
                      </button>
                    </div>
                    <div>
                      <h3 className="text-xl font-bold text-white">{profile?.name}</h3>
                      <p className="text-purple-400">{profile?.category}</p>
                      <div className="flex items-center gap-4 mt-2 text-sm text-gray-400">
                        <span>{formatNumber(profile?.followers || 0)} abonnés</span>
                        <span>{profile?.engagement_rate || 0}% engagement</span>
                      </div>
                    </div>
                  </div>

                  <div className="p-4 bg-white/5 rounded-xl">
                    <h4 className="text-sm text-gray-400 mb-2">Bio</h4>
                    <p className="text-white">{profile?.bio || 'Aucune bio ajoutée'}</p>
                  </div>

                  <div className="p-4 bg-white/5 rounded-xl">
                    <h4 className="text-sm text-gray-400 mb-2">Tarif par collaboration</h4>
                    <p className="text-2xl font-bold text-purple-400">{profile?.price || 0} CHF</p>
                  </div>
                </div>
              )}
            </div>
          </div>
        )}

        {/* Messages Section */}
        {activeSection === 'messages' && (
          <div className="card-service rounded-xl p-12 text-center">
            <MessageSquare className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold text-white mb-2">Messagerie</h3>
            <p className="text-gray-400">Cette fonctionnalité arrive bientôt !</p>
          </div>
        )}

        {/* Settings Section */}
        {activeSection === 'settings' && (
          <div className="max-w-2xl space-y-6">
            <div className="card-service rounded-xl p-6">
              <h2 className="text-lg font-semibold text-white mb-4">Paramètres du compte</h2>
              <div className="space-y-4">
                <label className="flex items-center justify-between p-4 bg-white/5 rounded-xl">
                  <div>
                    <p className="text-white">Notifications email</p>
                    <p className="text-sm text-gray-400">Recevoir les nouvelles demandes par email</p>
                  </div>
                  <button className="w-12 h-6 bg-purple-500 rounded-full relative">
                    <span className="absolute right-1 top-1 w-4 h-4 bg-white rounded-full" />
                  </button>
                </label>
                <label className="flex items-center justify-between p-4 bg-white/5 rounded-xl">
                  <div>
                    <p className="text-white">Profil public</p>
                    <p className="text-sm text-gray-400">Apparaître dans la liste des influenceurs</p>
                  </div>
                  <button className="w-12 h-6 bg-purple-500 rounded-full relative">
                    <span className="absolute right-1 top-1 w-4 h-4 bg-white rounded-full" />
                  </button>
                </label>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default InfluencerDashboard;
