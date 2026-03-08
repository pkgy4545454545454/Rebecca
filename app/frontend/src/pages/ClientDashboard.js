import React, { useState, useEffect, useRef } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { useNotificationWebSocket } from '../hooks/useWebSocket';
import { 
  LayoutDashboard, User, Heart, ShoppingCart, CreditCard, Wallet, Calendar, 
  MessageSquare, FileText, Settings, Gift, Crown, TrendingUp, MapPin,
  ChevronRight, Star, Bell, Search, Rss, Newspaper, PieChart, Briefcase,
  GraduationCap, FolderOpen, Phone, Truck, Package, Users, HelpCircle, 
  Handshake, Info, Target, Building2, Menu, X, Camera, Edit, Trash2, Plus, Minus,
  CheckCircle, XCircle, Send, Linkedin, Eye, UserPlus, ArrowLeftRight,
  Upload, Clock, ChevronDown, DollarSign, Bookmark, Store, ThumbsUp,
  Home, Zap, Award, Sparkles, MessageCircle, Share2, ExternalLink, Mail
} from 'lucide-react';
import { 
  orderAPI, cashbackAPI, featuredAPI, clientProfileAPI, friendsAPI, 
  paymentCardsAPI, clientDocumentsAPI, messagesAPI, notificationsAPI, uploadAPI,
  trainingsAPI, onlineStatusAPI, clientAgendaAPI, clientFinancesAPI, 
  clientDonationsAPI, wishlistAPI, clientSuggestionsAPI, clientProvidersAPI,
  activityFeedAPI, lifestyleAPI, clientInvitationsAPI, currentOffersAPI,
  guestsAPI, clientInvestmentsAPI, premiumAPI
} from '../services/api';
import api, { getImageUrl } from '../services/api';
import { toast } from 'sonner';
import EnterpriseCard from '../components/EnterpriseCard';
import ReferralSection from '../components/ReferralSection';
import EmailPreferences from '../components/EmailPreferences';
import { useCart } from '../context/CartContext';



const ClientDashboard = () => {
  const { user, isClient, updateUser } = useAuth();
  const { items: cartItems, removeItem: removeCartItem, updateQuantity: updateCartQuantity, getTotal: getCartTotal, getItemsByEnterprise } = useCart();
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [activeTab, setActiveTab] = useState(() => {
    const tabParam = searchParams.get('tab');
    return tabParam || 'overview';
  });
  
  // Get returnToJob parameter for CV upload flow
  const returnToJobId = searchParams.get('returnToJob');
  

  const [orders, setOrders] = useState([]);
  const [cashback, setCashback] = useState(0);
  const [tendances, setTendances] = useState([]);
  const [loading, setLoading] = useState(true);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  

  // Profile states
  const [profileStats, setProfileStats] = useState({ profile_views: 0, friends_count: 0, orders_count: 0 });
  const [editProfile, setEditProfile] = useState(false);
  const [profileForm, setProfileForm] = useState({});
  const fileInputRef = useRef(null);
  const coverInputRef = useRef(null);
  

  // Friends states
  const [friends, setFriends] = useState([]);
  const [friendRequests, setFriendRequests] = useState({ received: [], sent: [] });
  const [suggestedFriends, setSuggestedFriends] = useState([]);
  

  // Cards states
  const [cards, setCards] = useState([]);
  const [showAddCard, setShowAddCard] = useState(false);
  const [cardForm, setCardForm] = useState({ card_holder: '', card_number_last4: '', card_type: 'visa', expiry_month: 1, expiry_year: 2026, is_default: false });
  

  
  // Documents states
  const [documents, setDocuments] = useState([]);
  const [showAddDocument, setShowAddDocument] = useState(false);
  const [documentForm, setDocumentForm] = useState({ name: '', category: 'cv', url: '' });
  
  // Pre-select CV category if coming from job application
  useEffect(() => {
    if (returnToJobId && activeTab === 'documents') {
      setDocumentForm(prev => ({ ...prev, category: 'cv' }));
    }
  }, [returnToJobId, activeTab]);
  
  // Messages states
  const [conversations, setConversations] = useState([]);
  const [selectedConversation, setSelectedConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  
  // Notifications
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);

  // Trainings/Formations states
  const [myTrainings, setMyTrainings] = useState({ enrollments: [], stats: { total: 0, in_progress: 0, completed: 0 } });
  const [trainingsFilter, setTrainingsFilter] = useState('all'); // 'all', 'in_progress', 'completed'
  const [loadingTrainings, setLoadingTrainings] = useState(false);

  // Online status
  const [friendsOnlineData, setFriendsOnlineData] = useState({ friends: [], online_count: 0, total_count: 0 });

  // Training review state
  const [showReviewModal, setShowReviewModal] = useState(false);
  const [reviewingTraining, setReviewingTraining] = useState(null);
  const [reviewForm, setReviewForm] = useState({ rating: 5, comment: '' });
  const [submittingReview, setSubmittingReview] = useState(false);

  // Cashback history state
  const [cashbackHistory, setCashbackHistory] = useState([]);
  const [cashbackStats, setCashbackStats] = useState({ total_earned: 0, total_used: 0, cashback_rate: '10%', transaction_count: 0 });
  
  // Cashback withdrawal state
  const [withdrawalInfo, setWithdrawalInfo] = useState({ balance: 0, minimum_withdrawal: 50, can_withdraw: false, has_bank_info: false });
  const [showWithdrawModal, setShowWithdrawModal] = useState(false);
  const [showBankForm, setShowBankForm] = useState(false);
  const [bankForm, setBankForm] = useState({ iban: '', bank_account_holder: '', bic_swift: '' });
  const [withdrawing, setWithdrawing] = useState(false);
  const [withdrawalHistory, setWithdrawalHistory] = useState([]);

  // Agenda state
  const [agendaEvents, setAgendaEvents] = useState([]);
  const [showAddEvent, setShowAddEvent] = useState(false);
  const [eventForm, setEventForm] = useState({
    title: '', description: '', start_datetime: '', end_datetime: '',
    location: '', event_type: 'appointment', notes: ''
  });

  // Finances state
  const [finances, setFinances] = useState({ statistics: {}, recent_orders: [], recent_cashback: [] });

  // Donations state
  const [donations, setDonations] = useState({ donations: [], total_donated: 0, donations_count: 0 });
  const [showAddDonation, setShowAddDonation] = useState(false);
  const [donationForm, setDonationForm] = useState({
    amount: '', recipient_type: 'charity', recipient_id: '', recipient_name: '', message: '', is_anonymous: false
  });

  // Wishlist state
  const [wishlistItems, setWishlistItems] = useState([]);

  // Suggestions from friends state
  const [friendsSuggestions, setFriendsSuggestions] = useState([]);

  // Personal providers state
  const [personalProviders, setPersonalProviders] = useState([]);

  // Activity Feed state
  const [activityFeed, setActivityFeed] = useState([]);
  const [myFeed, setMyFeed] = useState([]);

  // Lifestyle state
  const [lifestyle, setLifestyle] = useState({ wishlist: [], personal_providers: [], liked_items: [], preferences: {} });

  // Invitations state
  const [invitations, setInvitations] = useState([]);

  // Current offers state
  const [currentOffers, setCurrentOffers] = useState([]);

  // Guests state
  const [favoriteGuests, setFavoriteGuests] = useState([]);

  // Investments state
  const [investments, setInvestments] = useState({ investments: [], statistics: {} });
  const [showAddInvestment, setShowAddInvestment] = useState(false);
  const [investmentForm, setInvestmentForm] = useState({
    investment_type: 'real_estate', title: '', description: '', amount_invested: '',
    current_value: '', roi_percent: '', investment_date: '', property_address: '', status: 'active'
  });

  // Premium state
  const [premiumData, setPremiumData] = useState({ current_plan: 'free', is_premium: false, benefits: {} });

  // Cart is from CartContext - cartItems

  // WebSocket notifications hook for real-time updates
  const { 
    notifications: wsNotifications, 
    unreadCount: wsUnreadCount,
    isConnected: wsConnected,
    fetchNotifications: refreshNotifications 
  } = useNotificationWebSocket();

  // Sync WebSocket notifications with local state
  useEffect(() => {
    if (wsNotifications && wsNotifications.length > 0) {
      setNotifications(wsNotifications);
    }
  }, [wsNotifications]);

  useEffect(() => {
    if (wsUnreadCount !== undefined) {
      setUnreadCount(wsUnreadCount);
    }
  }, [wsUnreadCount]);

  useEffect(() => {
    if (!isClient) {
      navigate('/');
      return;
    }
    fetchInitialData();
    
    // Start heartbeat for online status
    const heartbeatInterval = setInterval(() => {
      onlineStatusAPI.heartbeat().catch(() => {});
    }, 60000); // Every minute
    
    // Send initial heartbeat
    onlineStatusAPI.heartbeat().catch(() => {});
    
    // Cleanup on unmount
    return () => {
      clearInterval(heartbeatInterval);
      onlineStatusAPI.setOffline().catch(() => {});
    };
  }, [isClient, navigate]);

  const fetchInitialData = async () => {
    try {
      const [ordersRes, cashbackRes, tendancesRes, notifRes] = await Promise.all([
        orderAPI.list(),
        cashbackAPI.balance(),
        featuredAPI.tendances(),
        notificationsAPI.list()
      ]);
      setOrders(ordersRes.data);
      setCashback(cashbackRes.data.balance);
      setTendances(tendancesRes.data);
      setNotifications(notifRes.data.notifications || []);
      setUnreadCount(notifRes.data.unread_count || 0);
      setProfileForm(user || {});
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  };

  // Fetch profile data when switching to profile tab
  useEffect(() => {
    if (activeTab === 'profile') {
      fetchProfileData();
    } else if (activeTab === 'contacts' || activeTab === 'demandes') {
      fetchFriendsData();
    } else if (activeTab === 'cartes') {
      fetchCards();
    } else if (activeTab === 'documents') {
      fetchDocuments();
    } else if (activeTab === 'messages') {
      fetchConversations();
    } else if (activeTab === 'formations') {
      fetchMyTrainings();
    } else if (activeTab === 'cashback') {
      fetchCashbackHistory();
    } else if (activeTab === 'agenda') {
      fetchAgenda();
    } else if (activeTab === 'finances') {
      fetchFinances();
    } else if (activeTab === 'donations') {
      fetchDonations();
    } else if (activeTab === 'wishlist') {
      fetchWishlist();
    } else if (activeTab === 'suggestions') {
      fetchFriendsSuggestions();
    } else if (activeTab === 'prestataires') {
      fetchPersonalProviders();
    } else if (activeTab === 'feed') {
      fetchActivityFeed();
    } else if (activeTab === 'my_feed') {
      fetchMyFeed();
    } else if (activeTab === 'mode_vie') {
      fetchLifestyle();
    } else if (activeTab === 'invitations') {
      fetchInvitations();
    } else if (activeTab === 'offres') {
      fetchCurrentOffers();
    } else if (activeTab === 'guests') {
      fetchFavoriteGuests();
    } else if (activeTab === 'investments') {
      fetchInvestments();
    } else if (activeTab === 'premium') {
      fetchPremiumStatus();
    }
  }, [activeTab]);

  // New fetch functions
  const fetchAgenda = async () => {
    try {
      const res = await clientAgendaAPI.list();
      setAgendaEvents(res.data.events || []);
    } catch (error) {
      console.error('Error fetching agenda:', error);
    }
  };

  const fetchFinances = async () => {
    try {
      const res = await clientFinancesAPI.getStats();
      setFinances(res.data);
    } catch (error) {
      console.error('Error fetching finances:', error);
    }
  };

  const fetchDonations = async () => {
    try {
      const res = await clientDonationsAPI.list();
      setDonations(res.data);
    } catch (error) {
      console.error('Error fetching donations:', error);
    }
  };

  const fetchWishlist = async () => {
    try {
      const res = await wishlistAPI.list();
      setWishlistItems(res.data.items || []);
    } catch (error) {
      console.error('Error fetching wishlist:', error);
    }
  };

  const fetchFriendsSuggestions = async () => {
    try {
      const res = await clientSuggestionsAPI.fromFriends();
      setFriendsSuggestions(res.data.suggestions || []);
    } catch (error) {
      console.error('Error fetching suggestions:', error);
    }
  };

  const fetchPersonalProviders = async () => {
    try {
      const res = await clientProvidersAPI.list();
      setPersonalProviders(res.data.providers || []);
    } catch (error) {
      console.error('Error fetching providers:', error);
    }
  };

  const fetchActivityFeed = async () => {
    try {
      const res = await activityFeedAPI.getFeed(50);
      setActivityFeed(res.data.activities || []);
    } catch (error) {
      console.error('Error fetching activity feed:', error);
    }
  };

  const fetchMyFeed = async () => {
    try {
      const res = await activityFeedAPI.getMyFeed(50);
      setMyFeed(res.data.activities || []);
    } catch (error) {
      console.error('Error fetching my feed:', error);
    }
  };

  const fetchLifestyle = async () => {
    try {
      const res = await lifestyleAPI.get();
      setLifestyle(res.data);
    } catch (error) {
      console.error('Error fetching lifestyle:', error);
    }
  };

  const fetchInvitations = async () => {
    try {
      const res = await clientInvitationsAPI.list();
      setInvitations(res.data.invitations || []);
    } catch (error) {
      console.error('Error fetching invitations:', error);
    }
  };

  const fetchCurrentOffers = async () => {
    try {
      const res = await currentOffersAPI.list();
      setCurrentOffers(res.data.offers || []);
    } catch (error) {
      console.error('Error fetching offers:', error);
    }
  };

  const fetchFavoriteGuests = async () => {
    try {
      const res = await guestsAPI.list();
      setFavoriteGuests(res.data.guests || []);
    } catch (error) {
      console.error('Error fetching guests:', error);
    }
  };

  const fetchInvestments = async () => {
    try {
      const res = await clientInvestmentsAPI.list();
      setInvestments(res.data);
    } catch (error) {
      console.error('Error fetching investments:', error);
    }
  };

  const fetchPremiumStatus = async () => {
    try {
      const res = await premiumAPI.getStatus();
      setPremiumData(res.data);
    } catch (error) {
      console.error('Error fetching premium status:', error);
    }
  };

  const fetchProfileData = async () => {
    try {
      const res = await clientProfileAPI.get();
      setProfileStats(res.data.stats || {});
      setProfileForm(res.data.user || user);
    } catch (error) {
      console.error('Error fetching profile:', error);
    }
  };

  const fetchFriendsData = async () => {
    try {
      const [friendsRes, requestsRes, suggestionsRes, onlineRes] = await Promise.all([
        friendsAPI.list(),
        friendsAPI.getRequests(),
        friendsAPI.getSuggestions(),
        onlineStatusAPI.getFriendsOnline()
      ]);
      setFriends(friendsRes.data.friends || []);
      setFriendRequests(requestsRes.data || { received: [], sent: [] });
      setSuggestedFriends(suggestionsRes.data.suggestions || []);
      setFriendsOnlineData(onlineRes.data || { friends: [], online_count: 0, total_count: 0 });
    } catch (error) {
      console.error('Error fetching friends:', error);
    }
  };

  const fetchCards = async () => {
    try {
      const res = await paymentCardsAPI.list();
      setCards(res.data.cards || []);
    } catch (error) {
      console.error('Error fetching cards:', error);
    }
  };

  const fetchDocuments = async () => {
    try {
      const res = await clientDocumentsAPI.list();
      setDocuments(res.data.documents || []);
    } catch (error) {
      console.error('Error fetching documents:', error);
    }
  };

  const fetchCashbackHistory = async () => {
    try {
      const [historyRes, infoRes, withdrawalsRes] = await Promise.all([
        cashbackAPI.history(),
        cashbackAPI.withdrawalInfo(),
        cashbackAPI.withdrawalHistory()
      ]);
      setCashback(historyRes.data.balance || 0);
      setCashbackHistory(historyRes.data.transactions || []);
      setCashbackStats(historyRes.data.statistics || { total_earned: 0, total_used: 0, cashback_rate: '10%', transaction_count: 0 });
      setWithdrawalInfo(infoRes.data);
      setWithdrawalHistory(withdrawalsRes.data.withdrawals || []);
      
      // Pre-fill bank form if user has bank info
      if (infoRes.data.account_holder) {
        setBankForm(prev => ({ ...prev, bank_account_holder: infoRes.data.account_holder }));
      }
    } catch (error) {
      console.error('Error fetching cashback history:', error);
    }
  };

  const handleSaveBankInfo = async () => {
    if (!bankForm.iban || !bankForm.bank_account_holder) {
      toast.error('Veuillez remplir l\'IBAN et le nom du titulaire');
      return;
    }
    
    try {
      await clientProfileAPI.update({
        iban: bankForm.iban,
        bank_account_holder: bankForm.bank_account_holder,
        bic_swift: bankForm.bic_swift || null
      });
      toast.success('Coordonnées bancaires enregistrées');
      setShowBankForm(false);
      fetchCashbackHistory(); // Refresh to update withdrawal info
    } catch (error) {
      toast.error('Erreur lors de l\'enregistrement');
    }
  };

  const handleWithdraw = async () => {
    if (!withdrawalInfo.can_withdraw) {
      toast.error(withdrawalInfo.reason_cannot_withdraw || 'Retrait impossible');
      return;
    }
    
    setWithdrawing(true);
    try {
      const res = await cashbackAPI.withdraw(); // Withdraw full balance
      toast.success(res.data.message);
      setShowWithdrawModal(false);
      setCashback(res.data.new_balance);
      fetchCashbackHistory(); // Refresh all data
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erreur lors du retrait');
    } finally {
      setWithdrawing(false);
    }
  };

  const fetchConversations = async () => {
    try {
      const res = await messagesAPI.getConversations();
      setConversations(res.data.conversations || []);
    } catch (error) {
      console.error('Error fetching conversations:', error);
    }
  };

  // Trainings/Formations handlers
  const fetchMyTrainings = async () => {
    setLoadingTrainings(true);
    try {
      const statusParam = trainingsFilter === 'all' ? null : trainingsFilter;
      const res = await trainingsAPI.getMyTrainings(statusParam);
      setMyTrainings(res.data || { enrollments: [], stats: { total: 0, in_progress: 0, completed: 0 } });
    } catch (error) {
      console.error('Error fetching trainings:', error);
    } finally {
      setLoadingTrainings(false);
    }
  };

  const handleMarkTrainingComplete = async (enrollmentId) => {
    try {
      await trainingsAPI.markComplete(enrollmentId);
      toast.success('Formation marquée comme terminée');
      fetchMyTrainings();
    } catch (error) {
      toast.error('Erreur lors de la mise à jour');
    }
  };

  // Training review handler
  const handleSubmitReview = async () => {
    if (!reviewingTraining) return;
    setSubmittingReview(true);
    try {
      await trainingsAPI.createReview(reviewingTraining.training_id, {
        training_id: reviewingTraining.training_id,
        rating: reviewForm.rating,
        comment: reviewForm.comment
      });
      toast.success('Merci pour votre avis !');
      setShowReviewModal(false);
      setReviewingTraining(null);
      setReviewForm({ rating: 5, comment: '' });
    } catch (error) {
      const msg = error.response?.data?.detail || 'Erreur lors de l\'envoi';
      toast.error(msg);
    } finally {
      setSubmittingReview(false);
    }
  };

  // Refetch trainings when filter changes
  useEffect(() => {
    if (activeTab === 'formations') {
      fetchMyTrainings();
    }
  }, [trainingsFilter]);

  // Profile handlers
  const handleProfileUpdate = async () => {
    try {
      const res = await clientProfileAPI.update(profileForm);
      if (updateUser) updateUser(res.data);
      setEditProfile(false);
      toast.success('Profil mis à jour');
    } catch (error) {
      toast.error('Erreur lors de la mise à jour');
    }
  };

  const handleAvatarUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    try {
      const res = await uploadAPI.uploadImage(file);
      const avatarUrl = res.data.url;
      setProfileForm({ ...profileForm, avatar: avatarUrl });
      await clientProfileAPI.update({ avatar: avatarUrl });
      toast.success('Photo de profil mise à jour');
    } catch (error) {
      toast.error('Erreur lors de l\'upload');
    }
  };

  const handleCoverUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    try {
      const res = await uploadAPI.uploadImage(file);
      const coverUrl = res.data.url;
      setProfileForm({ ...profileForm, cover_image: coverUrl });
      await clientProfileAPI.update({ cover_image: coverUrl });
      toast.success('Image de couverture mise à jour');
    } catch (error) {
      toast.error('Erreur lors de l\'upload');
    }
  };

  // Agenda handlers
  const handleAddAgendaEvent = async () => {
    if (!eventForm.title || !eventForm.start_datetime) {
      toast.error('Titre et date de début requis');
      return;
    }
    try {
      await clientAgendaAPI.create(eventForm);
      toast.success('Événement ajouté');
      setShowAddEvent(false);
      setEventForm({ title: '', description: '', start_datetime: '', end_datetime: '', location: '', event_type: 'appointment', notes: '' });
      fetchAgenda();
    } catch (error) {
      toast.error('Erreur lors de l\'ajout');
    }
  };

  const handleDeleteAgendaEvent = async (eventId) => {
    try {
      await clientAgendaAPI.delete(eventId);
      toast.success('Événement supprimé');
      fetchAgenda();
    } catch (error) {
      toast.error('Erreur lors de la suppression');
    }
  };

  // Donation handlers
  const handleAddDonation = async () => {
    if (!donationForm.amount || !donationForm.recipient_name) {
      toast.error('Montant et bénéficiaire requis');
      return;
    }
    try {
      await clientDonationsAPI.create({
        ...donationForm,
        amount: parseFloat(donationForm.amount),
        recipient_id: donationForm.recipient_id || 'charity_' + Date.now()
      });
      toast.success('Don effectué avec succès');
      setShowAddDonation(false);
      setDonationForm({ amount: '', recipient_type: 'charity', recipient_id: '', recipient_name: '', message: '', is_anonymous: false });
      fetchDonations();
    } catch (error) {
      toast.error('Erreur lors du don');
    }
  };

  // Wishlist handlers
  const handleRemoveFromWishlist = async (itemId) => {
    try {
      await wishlistAPI.remove(itemId);
      toast.success('Retiré de la liste de souhaits');
      fetchWishlist();
    } catch (error) {
      toast.error('Erreur');
    }
  };

  // Personal providers handlers
  const handleRemoveProvider = async (providerId) => {
    try {
      await clientProvidersAPI.remove(providerId);
      toast.success('Prestataire retiré');
      fetchPersonalProviders();
    } catch (error) {
      toast.error('Erreur');
    }
  };

  // Investment handlers
  const handleAddInvestment = async () => {
    if (!investmentForm.title || !investmentForm.amount_invested || !investmentForm.investment_date) {
      toast.error('Titre, montant et date requis');
      return;
    }
    try {
      await clientInvestmentsAPI.create({
        ...investmentForm,
        amount_invested: parseFloat(investmentForm.amount_invested),
        current_value: investmentForm.current_value ? parseFloat(investmentForm.current_value) : null,
        roi_percent: investmentForm.roi_percent ? parseFloat(investmentForm.roi_percent) : null
      });
      toast.success('Investissement ajouté');
      setShowAddInvestment(false);
      setInvestmentForm({
        investment_type: 'real_estate', title: '', description: '', amount_invested: '',
        current_value: '', roi_percent: '', investment_date: '', property_address: '', status: 'active'
      });
      fetchInvestments();
    } catch (error) {
      toast.error('Erreur');
    }
  };

  const handleDeleteInvestment = async (investmentId) => {
    try {
      await clientInvestmentsAPI.delete(investmentId);
      toast.success('Investissement supprimé');
      fetchInvestments();
    } catch (error) {
      toast.error('Erreur');
    }
  };

  // Invitation handlers
  const handleRespondToInvitation = async (invitationId, accepted) => {
    try {
      await clientInvitationsAPI.respond(invitationId, accepted);
      toast.success(accepted ? 'Offre acceptée' : 'Offre refusée');
      fetchInvitations();
    } catch (error) {
      toast.error('Erreur');
    }
  };

  // Guest handlers
  const handleRemoveGuest = async (guestId) => {
    try {
      await guestsAPI.remove(guestId);
      toast.success('Guest retiré');
      fetchFavoriteGuests();
    } catch (error) {
      toast.error('Erreur');
    }
  };

  // Premium handlers
  const handleUpgradePremium = async (plan) => {
    try {
      toast.loading('Redirection vers le paiement Stripe...');
      const res = await premiumAPI.checkout(plan);
      // Store session_id for confirmation after return from Stripe
      localStorage.setItem('stripe_session_id', res.data.session_id);
      // Redirect to Stripe checkout
      window.location.href = res.data.checkout_url;
    } catch (error) {
      toast.dismiss();
      toast.error(error.response?.data?.detail || 'Erreur lors de la mise à niveau');
    }
  };

  // Handle payment confirmation from URL params
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const success = params.get('success');
    const plan = params.get('plan');
    const cancelled = params.get('cancelled');
    
    if (success === 'true' && plan) {
      // Payment successful, confirm subscription
      const sessionId = localStorage.getItem('stripe_session_id');
      if (sessionId) {
        premiumAPI.confirm(sessionId).then(() => {
          toast.success(`Félicitations ! Vous êtes maintenant ${plan.toUpperCase()} !`);
          fetchPremiumStatus();
          localStorage.removeItem('stripe_session_id');
          // Clean URL
          window.history.replaceState({}, '', '/dashboard/client?tab=premium');
        }).catch(() => {
          toast.success(`Abonnement ${plan.toUpperCase()} activé !`);
          fetchPremiumStatus();
        });
      } else {
        toast.success(`Abonnement ${plan.toUpperCase()} activé !`);
        fetchPremiumStatus();
      }
    } else if (cancelled === 'true') {
      toast.info('Paiement annulé');
      window.history.replaceState({}, '', '/dashboard/client?tab=premium');
    }
  }, []);

  const handleCancelPremium = async () => {
    if (!window.confirm('Êtes-vous sûr de vouloir annuler votre abonnement ?')) return;
    try {
      await premiumAPI.cancel();
      toast.success('Abonnement annulé');
      fetchPremiumStatus();
    } catch (error) {
      toast.error('Erreur lors de l\'annulation');
    }
  };

  // Friends handlers
  const handleSendFriendRequest = async (friendId) => {
    try {
      await friendsAPI.sendRequest(friendId);
      toast.success('Demande d\'ami envoyée');
      fetchFriendsData();
    } catch (error) {
      toast.error(error.response?.data?.detail || 'Erreur');
    }
  };

  const handleRespondToRequest = async (friendshipId, accept) => {
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

  // Cards handlers
  const handleAddCard = async () => {
    if (!cardForm.card_holder || !cardForm.card_number_last4) {
      toast.error('Veuillez remplir tous les champs');
      return;
    }
    try {
      await paymentCardsAPI.add(cardForm);
      toast.success('Carte ajoutée');
      setShowAddCard(false);
      setCardForm({ card_holder: '', card_number_last4: '', card_type: 'visa', expiry_month: 1, expiry_year: 2026, is_default: false });
      fetchCards();
    } catch (error) {
      toast.error('Erreur lors de l\'ajout');
    }
  };

  const handleDeleteCard = async (cardId) => {
    try {
      await paymentCardsAPI.delete(cardId);
      toast.success('Carte supprimée');
      fetchCards();
    } catch (error) {
      toast.error('Erreur');
    }
  };

  const handleSetDefaultCard = async (cardId) => {
    try {
      await paymentCardsAPI.setDefault(cardId);
      toast.success('Carte par défaut mise à jour');
      fetchCards();
    } catch (error) {
      toast.error('Erreur');
    }
  };

  // Documents handlers
  const handleAddDocument = async () => {
    // Auto-set name from uploaded file if empty
    const finalName = documentForm.name || (documentForm.url ? 'Mon document' : '');
    
    if (!finalName || !documentForm.url) {
      toast.error('Veuillez uploader un fichier');
      return;
    }
    try {
      await clientDocumentsAPI.add({
        ...documentForm,
        name: finalName
      });
      toast.success('Document ajouté');
      setShowAddDocument(false);
      setDocumentForm({ name: '', category: 'cv', url: '' });
      fetchDocuments();
    } catch (error) {
      toast.error('Erreur lors de l\'ajout');
    }
  };

  const handleDocumentUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    
    // Show uploading state
    toast.info('Upload en cours...');
    
    try {
      const res = await uploadAPI.uploadImage(file);
      // Auto-set name from file if not already set
      const fileName = file.name.replace(/\.[^/.]+$/, ''); // Remove extension
      setDocumentForm({ 
        ...documentForm, 
        url: res.data.url, 
        name: documentForm.name || fileName 
      });
      toast.success('Fichier uploadé avec succès !');
    } catch (error) {
      console.error('Upload error:', error);
      const msg = error.response?.data?.detail || 'Erreur lors de l\'upload';
      toast.error(msg);
    }
  };

  const handleDeleteDocument = async (docId) => {
    try {
      await clientDocumentsAPI.delete(docId);
      toast.success('Document supprimé');
      fetchDocuments();
    } catch (error) {
      toast.error('Erreur');
    }
  };

  // Messages handlers
  const handleSelectConversation = async (partnerId) => {
    try {
      const res = await messagesAPI.getMessages(partnerId);
      setMessages(res.data.messages || []);
      setSelectedConversation(res.data.partner);
    } catch (error) {
      console.error('Error fetching messages:', error);
    }
  };

  const handleSendMessage = async () => {
    if (!newMessage.trim() || !selectedConversation) return;
    
    try {
      await messagesAPI.send(selectedConversation.id, newMessage);
      setNewMessage('');
      handleSelectConversation(selectedConversation.id);
    } catch (error) {
      toast.error('Erreur lors de l\'envoi');
    }
  };

  // Switch to particulier account (former entrepreneur)
  const handleSwitchAccount = async () => {
    // Check if user has a "particulier" profile
    try {
      const res = await api.get('/client/particulier-check');
      if (res.data?.has_particulier) {
        // User has a particulier account, switch view
        setActiveTab('particulier');
        toast.success('Basculé vers votre espace particulier');
      } else {
        toast.info('Créez un compte particulier depuis le menu pour accéder à cette fonctionnalité');
      }
    } catch (error) {
      // API doesn't exist yet, just switch to the particulier tab
      setActiveTab('particulier');
    }
  };

  const menuSections = [
    {
      title: 'Principal',
      gradient: 'from-blue-500/20 to-blue-600/10',
      borderColor: 'border-blue-500/30',
      items: [
        { id: 'overview', label: 'Accueil', icon: LayoutDashboard },
        { id: 'profile', label: 'Mon Profil', icon: User },
   
        { id: 'feed', label: 'Mon fil d\'actualité', icon: Rss, notifKey: 'feed' },
   
      ]
    },
    {
      title: 'Avantages',
      gradient: 'from-purple-500/20 to-purple-600/10',
      borderColor: 'border-purple-500/30',
      items: [
        { id: 'cashback', label: 'Mon cash-back', icon: Wallet, notifKey: 'cashback' },
        { id: 'parrainage', label: 'Parrainage', icon: Gift, notifKey: 'referral' },
        { id: 'premium', label: 'Mon Premium', icon: Crown, notifKey: 'premium' },
        { id: 'offres', label: 'Mes offres du moment', icon: Target, notifKey: 'offers' },
      ]
    },
    {
      title: 'Postulations',
      gradient: 'from-green-500/20 to-green-600/10',
      borderColor: 'border-green-500/30',
      items: [
      
       
        { id: 'Postulation', label: 'Mes postulations', icon: GraduationCap, notifKey: 'trainings' },
      ]
    },
    {
      title: 'Gestion',
      gradient: 'from-yellow-500/20 to-yellow-600/10',
      borderColor: 'border-yellow-500/30',
      items: [
        { id: 'agenda', label: 'Mon agenda', icon: Calendar, notifKey: 'agenda' },
        { id: 'cartes', label: 'Mes cartes', icon: CreditCard },
        { id: 'documents', label: 'Mes documents', icon: FolderOpen },
      ]
    },
    {
      title: 'Communication',
      gradient: 'from-pink-500/20 to-pink-600/10',
      borderColor: 'border-pink-500/30',
      items: [
        { id: 'messages', label: 'Messagerie', icon: MessageSquare, notifKey: 'messages' },
        { id: 'contacts', label: 'Contacts & Amis', icon: Users, notifKey: 'contacts' },
        { id: 'demandes', label: 'Demandes en cours', icon: UserPlus, notifKey: 'friend_requests' },
   
      ]
    },
    {
      title: 'Recommandations',
      gradient: 'from-cyan-500/20 to-cyan-600/10',
      borderColor: 'border-cyan-500/30',
      items: [
        { id: 'suggestions', label: 'Suggestions de mes contacts', icon: Users },
       
        { id: 'wishlist', label: 'Ma liste de souhaits', icon: Heart, notifKey: 'wishlist' },
      ]
    },
    {
      title: 'Commandes',
      gradient: 'from-orange-500/20 to-orange-600/10',
      borderColor: 'border-orange-500/30',
      items: [
        { id: 'orders', label: 'Mes commandes', icon: ShoppingCart, notifKey: 'orders' },
        { id: 'panier', label: 'Mon panier', icon: ShoppingCart, notifKey: 'cart' },

      ]
    },

  ];

  // Notification counts for menu items
  // Notification count for menu items - reactive based on real data
  const getNotificationCount = (key) => {
    switch(key) {
      case 'messages':
        // Count unread messages from conversations
        return conversations.reduce((count, conv) => count + (conv.unread_count || 0), 0);
      case 'friend_requests':
        // Count pending friend requests received
        return friendRequests.received?.length || 0;
      case 'contacts':
        // Show notification for new friend requests
        return friendRequests.received?.length || 0;
      case 'orders':
        // Count orders with new status or pending
        return orders.filter(o => o.status === 'pending' || o.status === 'confirmed').length;
      case 'deliveries':
        // Count orders being delivered
        return orders.filter(o => o.status === 'shipped' || o.status === 'delivering').length;
      case 'cart':
        // Count items in cart
        return cartItems.length || 0;
      case 'invitations':
        // Count new invitations
        return notifications.filter(n => n.notification_type === 'invitation' && !n.is_read).length;
      case 'offers':
        // Count new offers
        return notifications.filter(n => n.notification_type === 'new_offer' && !n.is_read).length;
      case 'gifts':
        // Count new gifts/rewards
        return notifications.filter(n => n.notification_type === 'gift' && !n.is_read).length;
      case 'cashback':
        // Show if cashback is available
        return cashback > 0 ? 1 : 0;
      case 'premium':
        // Show if premium benefits available
        return premiumData?.current_plan !== 'free' && notifications.filter(n => n.notification_type === 'premium' && !n.is_read).length;
      case 'investments':
        // Count investment notifications
        return notifications.filter(n => n.notification_type === 'investment' && !n.is_read).length;
      case 'jobs':
        // Count job application updates
        return notifications.filter(n => (n.notification_type === 'job_application' || n.notification_type === 'job_response') && !n.is_read).length;
      case 'trainings':
        // Count training notifications
        return notifications.filter(n => n.notification_type === 'training' && !n.is_read).length;
      case 'agenda':
        // Count upcoming events today
        const today = new Date().toDateString();
        return agendaEvents.filter(e => new Date(e.date).toDateString() === today).length;
      case 'feed':
        // Count new feed activity
        return notifications.filter(n => (n.notification_type === 'like' || n.notification_type === 'comment' || n.notification_type === 'share') && !n.is_read).length;
      case 'wishlist':
        // Count wishlist items with price drops or availability
        return notifications.filter(n => n.notification_type === 'wishlist_alert' && !n.is_read).length;
      default:
        return 0;
    }
  };

  const quickStats = [
    { 
      label: 'Cash-back disponible', 
      value: `${cashback.toFixed(2)} CHF`, 
      icon: Wallet, 
      gradient: 'from-green-500/20 to-green-600/10',
      borderColor: 'border-green-500/30',
      iconBg: 'bg-green-500/20',
      iconColor: 'text-green-400'
    },
    { 
      label: 'Commandes', 
      value: orders.length.toString(), 
      icon: ShoppingCart,
      notifCount: orders.filter(o => o.status === 'pending').length,
      gradient: 'from-blue-500/20 to-blue-600/10',
      borderColor: 'border-blue-500/30',
      iconBg: 'bg-blue-500/20',
      iconColor: 'text-blue-400'
    },
    { 
      label: 'Vues profil', 
      value: profileStats.profile_views?.toString() || '0', 
      icon: Eye, 
      gradient: 'from-purple-500/20 to-purple-600/10',
      borderColor: 'border-purple-500/30',
      iconBg: 'bg-purple-500/20',
      iconColor: 'text-purple-400'
    },
    { 
      label: 'Amis', 
      value: profileStats.friends_count?.toString() || '0', 
      icon: Users,
      notifCount: friendRequests.received?.length || 0, 
      gradient: 'from-yellow-500/20 to-yellow-600/10',
      borderColor: 'border-yellow-500/30',
      iconBg: 'bg-yellow-500/20',
      iconColor: 'text-yellow-400'
    },
  ];

  if (loading) {
    return (
      <div className="min-h-screen bg-[#050505] pt-24 flex items-center justify-center">
        <div className="w-16 h-16 border-4 border-[#0047AB] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#050505] pt-20" data-testid="client-dashboard">
      {/* Mobile Menu Overlay - Must be rendered before sidebar */}
      {mobileMenuOpen && (
        <div 
          className="lg:hidden fixed inset-0 bg-black/90 z-[40]"
          onClick={() => setMobileMenuOpen(false)}
        />
      )}

      {/* Sidebar - Mobile: Slide-in panel, Desktop: Fixed sidebar */}
      <aside 
        className={`
          fixed top-0 bottom-0 z-[55]
          bg-[#111111] border-r border-white/10 
          overflow-y-auto overflow-x-hidden 
          transition-all duration-300 ease-in-out
          dashboard-sidebar pt-4
          w-[280px] sm:w-[300px] lg:w-64 lg:top-20
          ${mobileMenuOpen ? 'mobile-sidebar-open' : 'mobile-sidebar-closed'}
        `}
        style={{ backgroundColor: '#111111' }}
      >
        <div className="p-4 hide-scrollbar overflow-x-hidden pb-24">
          {/* Profile Header with Switch Button */}
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-[#0047AB] flex items-center justify-center text-white font-bold text-sm overflow-hidden">
                {profileForm?.avatar ? (
                  <img src={profileForm.avatar.startsWith('http') ? profileForm.avatar : `${process.env.REACT_APP_BACKEND_URL}${profileForm.avatar}`} alt="" className="w-full h-full object-cover" />
                ) : (
                  <>{user?.first_name?.[0]}{user?.last_name?.[0]}</>
                )}
              </div>
              <div>
                <p className="font-semibold text-white text-sm">{user?.first_name} {user?.last_name}</p>
                  <p className="text-xs text-gray-500">Espace client</p>
                </div>
              </div>
              <button 
                onClick={handleSwitchAccount}
                className="p-2 bg-white/5 rounded-lg hover:bg-[#0047AB]/20 transition-colors group"
                title="Basculer vers compte particulier"
              >
                <ArrowLeftRight className="w-4 h-4 text-gray-400 group-hover:text-[#0047AB] transition-colors" />
              </button>
            </div>

            {/* Notifications Badge */}
            {unreadCount > 0 && (
              <div className="mb-4 p-3 bg-[#0047AB]/10 rounded-lg flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Bell className="w-4 h-4 text-[#0047AB]" />
                  <span className="text-sm text-white">{unreadCount} notification{unreadCount > 1 ? 's' : ''}</span>
                </div>
                <span className="w-2 h-2 bg-[#0047AB] rounded-full animate-pulse" />
              </div>
            )}

            {/* Search Bar */}
            <div className="relative mb-6">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
              <input 
                type="text" 
                placeholder="Rechercher..."
                className="w-full pl-10 pr-4 py-2 bg-white/5 border border-white/10 rounded-lg text-sm text-white placeholder-gray-500 focus:border-[#0047AB]/50 focus:outline-none"
              />
            </div>

            <nav className="space-y-4 overflow-hidden">
              {menuSections.map((section) => (
                <div key={section.title} className={`rounded-xl p-3 bg-gradient-to-br ${section.gradient} border ${section.borderColor} mb-3 menu-section`}>
                  <h3 className="text-xs font-semibold text-gray-300 uppercase tracking-wider mb-2 px-2 truncate">
                    {section.title}
                  </h3>
                  <div className="space-y-0.5">
                    {section.items.map((item) => {
                      const notifCount = item.notifKey ? getNotificationCount(item.notifKey) : 0;
                      const hasNotif = notifCount > 0;
                      
                      return (
                        <button
                          key={item.id}
                          onClick={() => { setActiveTab(item.id); setMobileMenuOpen(false); }}
                          className={`w-full flex items-center justify-between gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all relative overflow-hidden ${
                            activeTab === item.id
                              ? 'bg-white/20 text-white shadow-lg'
                              : 'text-gray-300 hover:bg-white/10 hover:text-white'
                          } ${hasNotif ? 'animate-pulse-border' : ''}`}
                          data-testid={`menu-${item.id}`}
                          style={hasNotif ? {
                            boxShadow: '0 0 0 2px rgba(34, 197, 94, 0.5)',
                            animation: 'pulse-green 2s infinite'
                          } : {}}
                        >
                          <div className="flex items-center gap-2 min-w-0 flex-1">
                            <item.icon className="w-4 h-4 flex-shrink-0" />
                            <span className="truncate text-left">{item.label}</span>
                          </div>
                          {hasNotif && (
                            <span className="flex items-center justify-center min-w-[20px] h-5 px-1.5 bg-green-500 text-white text-xs font-bold rounded-full animate-bounce flex-shrink-0">
                              {notifCount}
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

      {/* Mobile Menu Button - Fixed at top */}
      <button 
        onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
        className="lg:hidden fixed top-24 left-4 z-[60] w-12 h-12 bg-[#0047AB] rounded-xl flex items-center justify-center shadow-lg border border-white/10"
        data-testid="mobile-menu-toggle"
      >
        {mobileMenuOpen ? <X className="w-5 h-5 text-white" /> : <Menu className="w-5 h-5 text-white" />}
      </button>

        {/* Main Content */}
        <main className="flex-1 lg:ml-64 p-4 md:p-6 lg:p-8 pt-16 lg:pt-4">
          {/* Overview Tab */}
          {activeTab === 'overview' && (
            <div className="space-y-6 md:space-y-8">
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
                <div>
                  <h1 className="text-xl md:text-2xl lg:text-3xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
                    Bonjour, {user?.first_name} !
                  </h1>
                  <p className="text-gray-400 mt-1 text-sm md:text-base">Bienvenue sur votre espace Clients</p>
                </div>
                <Link to="/" className="btn-primary flex items-center justify-center gap-2 text-sm md:text-base">
                  <Search className="w-4 h-4 md:w-5 md:h-5" />
                  Explorer
                </Link>
              </div>

              {/* Quick Stats */}
              <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 md:gap-4">
                {quickStats.map((stat, index) => (
                  <div 
                    key={index} 
                    className={`rounded-xl p-4 md:p-6 bg-gradient-to-br ${stat.gradient} border ${stat.borderColor} relative overflow-hidden`}
                    style={stat.notifCount > 0 ? {
                      animation: 'pulse-green 2s infinite'
                    } : {}}
                  >
                    <div className={`w-12 h-12 rounded-xl ${stat.iconBg} flex items-center justify-center mb-4`}>
                      <stat.icon className={`w-6 h-6 ${stat.iconColor}`} />
                    </div>
                    <p className="text-2xl font-bold text-white">{stat.value}</p>
                    <p className="text-sm text-gray-400 mt-1">{stat.label}</p>
                    {stat.notifCount > 0 && (
                      <span className="absolute top-3 right-3 w-6 h-6 bg-green-500 text-white text-xs font-bold rounded-full flex items-center justify-center animate-bounce">
                        {stat.notifCount}
                      </span>
                    )}
                  </div>
                ))}
              </div>

              {/* Premium CTA */}
              {!user?.is_premium && (
                <div className="card-service rounded-xl p-8 bg-gradient-to-r from-[#0047AB]/20 to-[#D4AF37]/20 border border-[#D4AF37]/30">
                  <div className="flex items-center gap-6">
                    <div className="p-4 rounded-2xl bg-gradient-to-br from-[#D4AF37] to-[#0047AB]">
                      <Crown className="w-8 h-8 text-white" />
                    </div>
                    <div className="flex-1">
                      <h2 className="text-xl font-bold text-yellow-400 mb-2">Passez V.I.P</h2>
                      <p className="text-gray-400">Accédez à des offres exclusives, un service premium et jusqu'à 15% de cashback.</p>
                    </div>
                    <button 
                      onClick={() => setActiveTab('premium')} 
                      className="btn-primary" 
                      data-testid="upgrade-premium"
                    >
                      Découvrir
                    </button>
                  </div>
                </div>
              )}

              {/* Recent Orders */}
              <div className="card-service rounded-xl p-6">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
                    Mes dernières commandes
                  </h2>
                  <button onClick={() => setActiveTab('orders')} className="text-[#0047AB] text-sm font-medium flex items-center gap-1">
                    Voir tout <ChevronRight className="w-4 h-4" />
                  </button>
                </div>
                {orders.length > 0 ? (
                  <div className="space-y-4">
                    {orders.slice(0, 3).map((order) => (
                      <div key={order.id} className="flex items-center justify-between p-4 bg-white/5 rounded-xl">
                        <div>
                          <p className="text-white font-medium">Commande #{order.id.slice(0, 8)}</p>
                          <p className="text-sm text-gray-400">{new Date(order.created_at).toLocaleDateString('fr-FR')}</p>
                        </div>
                        <div className="text-right">
                          <p className="text-white font-medium">{order.total?.toFixed(2)} CHF</p>
                          <span className={`text-xs px-2 py-1 rounded-full ${
                            order.status === 'completed' ? 'bg-green-500/20 text-green-500' :
                            order.status === 'pending' ? 'bg-yellow-500/20 text-yellow-500' :
                            'bg-gray-500/20 text-gray-500'
                          }`}>
                            {order.status === 'pending' ? 'En cours' : order.status}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-gray-500 text-center py-8">Aucune commande pour le moment</p>
                )}
              </div>

              {/* Recommendations */}
              <div>
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
                    Tendances pour vous
                  </h2>
                  <Link to="/labellises" className="text-[#D4AF37] text-sm font-medium flex items-center gap-1">
                    Voir tout <ChevronRight className="w-4 h-4" />
                  </Link>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {tendances.slice(0, 3).map((enterprise) => (
                    <EnterpriseCard key={enterprise.id} enterprise={enterprise} />
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Profile Tab - Enhanced with Cover Image */}
          {activeTab === 'profile' && (
            <div className="max-w-3xl">
              <div className="flex items-center justify-between mb-6">
                <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
                  Mon Profil
                </h1>
                <button 
                  onClick={() => setEditProfile(!editProfile)}
                  className="btn-secondary flex items-center gap-2"
                >
                  <Edit className="w-4 h-4" />
                  {editProfile ? 'Annuler' : 'Modifier'}
                </button>
              </div>
              
              <div className="card-service rounded-xl overflow-hidden">
                {/* Cover Image Section */}
                <div className="relative h-40 md:h-56 bg-gradient-to-br from-[#0047AB]/30 to-[#1a1a2e]">
                  {profileForm?.cover_image ? (
                    <img 
                      src={profileForm.cover_image.startsWith('http') ? profileForm.cover_image : `${process.env.REACT_APP_BACKEND_URL}${profileForm.cover_image}`}
                      alt="Cover"
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full bg-gradient-to-br from-[#0047AB]/20 via-[#1a1a2e] to-[#050505]" />
                  )}
                  
                  {editProfile && (
                    <button 
                      onClick={() => coverInputRef.current?.click()}
                      className="absolute top-4 right-4 px-4 py-2 bg-black/50 backdrop-blur-sm rounded-lg text-white text-sm hover:bg-black/70 transition-colors flex items-center gap-2"
                    >
                      <Camera className="w-4 h-4" />
                      Changer la couverture
                    </button>
                  )}
                  <input 
                    ref={coverInputRef}
                    type="file" 
                    accept="image/*" 
                    onChange={handleCoverUpload}
                    className="hidden" 
                  />
                </div>

                {/* Profile Content */}
                <div className="p-6 md:p-8 -mt-16 relative">
                  {/* Avatar Section */}
                  <div className="flex flex-col md:flex-row items-start md:items-end gap-4 mb-6">
                    <div className="relative">
                      <div className="w-28 h-28 rounded-full border-4 border-[#0F0F0F] bg-[#0047AB] flex items-center justify-center text-white text-2xl font-bold overflow-hidden shadow-xl">
                        {profileForm?.avatar ? (
                          <img 
                            src={profileForm.avatar.startsWith('http') ? profileForm.avatar : `${process.env.REACT_APP_BACKEND_URL}${profileForm.avatar}`} 
                            alt="" 
                            className="w-full h-full object-cover" 
                          />
                        ) : (
                          <>{user?.first_name?.[0]}{user?.last_name?.[0]}</>
                        )}
                      </div>
                      {editProfile && (
                        <button 
                          onClick={() => fileInputRef.current?.click()}
                          className="absolute -bottom-2 -right-2 p-2 bg-[#0047AB] rounded-full text-white hover:bg-[#0047AB]/80 transition-colors shadow-lg"
                        >
                          <Camera className="w-4 h-4" />
                        </button>
                      )}
                      <input 
                        ref={fileInputRef}
                        type="file" 
                        accept="image/*" 
                        onChange={handleAvatarUpload}
                        className="hidden" 
                      />
                    </div>
                    <div className="flex-1">
                      {editProfile ? (
                        <div className="grid grid-cols-2 gap-3">
                          <input
                            type="text"
                            value={profileForm.first_name || ''}
                            onChange={(e) => setProfileForm({...profileForm, first_name: e.target.value})}
                            placeholder="Prénom"
                            className="input-dark"
                          />
                          <input
                            type="text"
                            value={profileForm.last_name || ''}
                            onChange={(e) => setProfileForm({...profileForm, last_name: e.target.value})}
                            placeholder="Nom"
                            className="input-dark"
                          />
                        </div>
                      ) : (
                        <>
                          <h2 className="text-xl font-bold text-white">{user?.first_name} {user?.last_name}</h2>
                          <p className="text-gray-400">{user?.email}</p>
                          <div className="flex items-center gap-2 mt-2">
                            <MapPin className="w-4 h-4 text-gray-500" />
                            <span className="text-gray-500">{profileForm?.city || 'Lausanne'}</span>
                          </div>
                        </>
                      )}
                    </div>
                  </div>

                {/* Stats Row */}
                <div className="grid grid-cols-3 gap-4 mb-8 p-4 bg-white/5 rounded-xl">
                  <div className="text-center">
                    <p className="text-2xl font-bold text-white">{profileStats.profile_views || 0}</p>
                    <p className="text-xs text-gray-500">Vues du profil</p>
                  </div>
                  <div className="text-center border-x border-white/10">
                    <p className="text-2xl font-bold text-white">{profileStats.friends_count || 0}</p>
                    <p className="text-xs text-gray-500">Amis</p>
                  </div>
                  <div className="text-center">
                    <p className="text-2xl font-bold text-white">{profileStats.orders_count || 0}</p>
                    <p className="text-xs text-gray-500">Commandes</p>
                  </div>
                </div>

                {/* Profile Details */}
                <div className="space-y-4">
                  <div className="flex justify-between py-3 border-b border-white/10">
                    <span className="text-gray-400">Email</span>
                    {editProfile ? (
                      <span className="text-gray-500">{user?.email} (non modifiable)</span>
                    ) : (
                      <span className="text-white">{user?.email}</span>
                    )}
                  </div>
                  
                  <div className="flex justify-between py-3 border-b border-white/10">
                    <span className="text-gray-400">Téléphone</span>
                    {editProfile ? (
                      <input
                        type="tel"
                        value={profileForm.phone || ''}
                        onChange={(e) => setProfileForm({...profileForm, phone: e.target.value})}
                        className="input-dark text-right w-48"
                        placeholder="+41 XX XXX XX XX"
                      />
                    ) : (
                      <span className="text-white">{user?.phone || 'Non renseigné'}</span>
                    )}
                  </div>

                  <div className="flex justify-between py-3 border-b border-white/10">
                    <span className="text-gray-400 flex items-center gap-2">
                      <Linkedin className="w-4 h-4" /> LinkedIn
                    </span>
                    {editProfile ? (
                      <input
                        type="url"
                        value={profileForm.linkedin || ''}
                        onChange={(e) => setProfileForm({...profileForm, linkedin: e.target.value})}
                        className="input-dark text-right w-64"
                        placeholder="https://linkedin.com/in/..."
                      />
                    ) : (
                      <span className="text-white">
                        {user?.linkedin ? (
                          <a href={user.linkedin} target="_blank" rel="noopener noreferrer" className="text-[#0047AB] hover:underline">
                            Voir le profil
                          </a>
                        ) : 'Non connecté'}
                      </span>
                    )}
                  </div>

                  <div className="flex justify-between py-3 border-b border-white/10">
                    <span className="text-gray-400">Ville</span>
                    {editProfile ? (
                      <input
                        type="text"
                        value={profileForm.city || ''}
                        onChange={(e) => setProfileForm({...profileForm, city: e.target.value})}
                        className="input-dark text-right w-48"
                        placeholder="Lausanne"
                      />
                    ) : (
                      <span className="text-white">{user?.city || 'Non renseigné'}</span>
                    )}
                  </div>

                  <div className="flex justify-between py-3 border-b border-white/10">
                    <span className="text-gray-400">Compte Premium</span>
                    <span className={user?.is_premium ? 'text-[#D4AF37]' : 'text-gray-500'}>
                      {user?.is_premium ? 'Actif' : 'Inactif'}
                    </span>
                  </div>
                  
                  <div className="flex justify-between py-3 border-b border-white/10">
                    <span className="text-gray-400">Cash-back disponible</span>
                    <span className="text-green-500">{cashback.toFixed(2)} CHF</span>
                  </div>
                </div>

                {editProfile && (
                  <button onClick={handleProfileUpdate} className="btn-primary w-full mt-6">
                    Enregistrer les modifications
                  </button>
                )}
                </div>
              </div>
            </div>
          )}

          {/* Contacts & Friends Tab */}
          {activeTab === 'contacts' && (
            <div className="space-y-6">
              <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
                Contacts & Amis
              </h1>

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
                          <div className="w-12 h-12 rounded-full bg-[#0047AB] flex items-center justify-center text-white font-bold">
                            {request.sender?.first_name?.[0]}{request.sender?.last_name?.[0]}
                          </div>
                          <div>
                            <p className="text-white font-medium">{request.sender?.first_name} {request.sender?.last_name}</p>
                            <p className="text-sm text-gray-400">{request.message || 'Souhaite vous ajouter'}</p>
                          </div>
                        </div>
                        <div className="flex gap-2">
                          <button
                            onClick={() => handleRespondToRequest(request.id, true)}
                            className="p-2 bg-green-500/20 text-green-400 rounded-lg hover:bg-green-500/30"
                          >
                            <CheckCircle className="w-5 h-5" />
                          </button>
                          <button
                            onClick={() => handleRespondToRequest(request.id, false)}
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
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-lg font-semibold text-white">Mes amis ({friends.length})</h2>
                  {friendsOnlineData.online_count > 0 && (
                    <span className="flex items-center gap-2 text-sm text-green-400">
                      <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
                      {friendsOnlineData.online_count} en ligne
                    </span>
                  )}
                </div>
                
                {/* Online Friends Section */}
                {friendsOnlineData.friends.filter(f => f.is_online).length > 0 && (
                  <div className="mb-6 p-4 bg-green-500/10 border border-green-500/20 rounded-xl">
                    <h3 className="text-sm font-medium text-green-400 mb-3 flex items-center gap-2">
                      <span className="w-2 h-2 rounded-full bg-green-400 animate-pulse" />
                      En ligne maintenant
                    </h3>
                    <div className="flex flex-wrap gap-3">
                      {friendsOnlineData.friends.filter(f => f.is_online).map((friend) => (
                        <Link
                          key={friend.id}
                          to={`/profil/${friend.id}`}
                          className="flex items-center gap-2 px-3 py-2 bg-white/5 rounded-lg hover:bg-white/10 transition-colors"
                        >
                          <div className="relative">
                            <div className="w-8 h-8 rounded-full bg-[#0047AB]/50 flex items-center justify-center text-white text-xs font-bold overflow-hidden">
                              {friend.avatar ? (
                                <img src={friend.avatar.startsWith('http') ? friend.avatar : `${process.env.REACT_APP_BACKEND_URL}${friend.avatar}`} alt="" className="w-full h-full object-cover" />
                              ) : (
                                <>{friend.first_name?.[0]}{friend.last_name?.[0]}</>
                              )}
                            </div>
                            <span className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-green-500 rounded-full border-2 border-[#0A0A0A]" />
                          </div>
                          <span className="text-sm text-white">{friend.first_name}</span>
                        </Link>
                      ))}
                    </div>
                  </div>
                )}
                
                {friends.length > 0 ? (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {friends.map((friend) => {
                      const onlineInfo = friendsOnlineData.friends.find(f => f.id === friend.id);
                      const isOnline = onlineInfo?.is_online || false;
                      
                      return (
                        <div key={friend.id} className="flex items-center justify-between p-4 bg-white/5 rounded-xl hover:bg-white/10 transition-colors group">
                          <Link to={`/profil/${friend.id}`} className="flex items-center gap-3 flex-1">
                            <div className="relative">
                              <div className="w-12 h-12 rounded-full bg-[#0047AB]/50 flex items-center justify-center text-white font-bold overflow-hidden group-hover:ring-2 group-hover:ring-[#0047AB] transition-all">
                                {friend.avatar ? (
                                  <img src={friend.avatar.startsWith('http') ? friend.avatar : `${process.env.REACT_APP_BACKEND_URL}${friend.avatar}`} alt="" className="w-full h-full object-cover" />
                                ) : (
                                  <>{friend.first_name?.[0]}{friend.last_name?.[0]}</>
                                )}
                              </div>
                              {/* Online indicator */}
                              <span className={`absolute bottom-0 right-0 w-3.5 h-3.5 rounded-full border-2 border-[#0F0F0F] ${isOnline ? 'bg-green-500' : 'bg-gray-500'}`} />
                            </div>
                            <div>
                              <div className="flex items-center gap-2">
                                <p className="text-white font-medium group-hover:text-[#0047AB] transition-colors">{friend.first_name} {friend.last_name}</p>
                                {isOnline && (
                                  <span className="text-xs text-green-400">En ligne</span>
                                )}
                              </div>
                              <p className="text-sm text-gray-400">{friend.city || 'Lausanne'}</p>
                            </div>
                          </Link>
                          <div className="flex gap-2">
                            <button
                              onClick={(e) => { e.preventDefault(); setSelectedConversation(friend); setActiveTab('messages'); }}
                              className="p-2 bg-[#0047AB]/20 text-[#0047AB] rounded-lg hover:bg-[#0047AB]/30"
                              title="Envoyer un message"
                            >
                              <MessageSquare className="w-4 h-4" />
                            </button>
                            <button
                              onClick={(e) => { e.preventDefault(); handleRemoveFriend(friend.friendship_id); }}
                              className="p-2 bg-red-500/10 text-red-400 rounded-lg hover:bg-red-500/20"
                              title="Supprimer de mes amis"
                            >
                              <Trash2 className="w-4 h-4" />
                            </button>
                          </div>
                        </div>
                      );
                    })}
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

          {/* Demandes en cours Tab */}
          {activeTab === 'demandes' && (
            <div className="space-y-6">
              <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
                Demandes en cours
              </h1>

              {/* Demandes envoyées */}
              {friendRequests.sent.length > 0 ? (
                <div className="card-service rounded-xl p-6">
                  <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                    <Send className="w-5 h-5 text-[#0047AB]" />
                    Demandes envoyées ({friendRequests.sent.length})
                  </h2>
                  <div className="space-y-3">
                    {friendRequests.sent.map((request) => (
                      <div key={request.id} className="p-4 bg-white/5 rounded-xl">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <div className="w-12 h-12 rounded-full bg-[#0047AB]/30 flex items-center justify-center text-white font-bold overflow-hidden">
                              {request.recipient?.avatar ? (
                                <img 
                                  src={request.recipient.avatar.startsWith('http') ? request.recipient.avatar : `${process.env.REACT_APP_BACKEND_URL}${request.recipient.avatar}`} 
                                  alt="" 
                                  className="w-full h-full object-cover" 
                                />
                              ) : (
                                <>{request.recipient?.first_name?.[0]}{request.recipient?.last_name?.[0]}</>
                              )}
                            </div>
                            <div>
                              <p className="text-white font-medium">{request.recipient?.first_name} {request.recipient?.last_name}</p>
                              <p className="text-sm text-gray-500">{request.recipient?.city || 'Lausanne'}</p>
                            </div>
                          </div>
                          <div className="text-right">
                            <span className="px-3 py-1 bg-yellow-500/20 text-yellow-400 text-xs rounded-full">
                              En attente
                            </span>
                            <p className="text-xs text-gray-500 mt-1">
                              {new Date(request.created_at).toLocaleDateString('fr-FR')}
                            </p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              ) : (
                <div className="card-service rounded-xl p-12 text-center">
                  <Send className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold text-white mb-2">Aucune demande en cours</h3>
                  <p className="text-gray-400">Vos demandes d'ami en attente apparaîtront ici</p>
                </div>
              )}

              {/* Demandes reçues en attente */}
              {friendRequests.received.length > 0 && (
                <div className="card-service rounded-xl p-6 border-[#D4AF37]/30">
                  <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                    <Bell className="w-5 h-5 text-[#D4AF37]" />
                    Demandes reçues ({friendRequests.received.length})
                  </h2>
                  <div className="space-y-3">
                    {friendRequests.received.map((request) => (
                      <div key={request.id} className="p-4 bg-white/5 rounded-xl">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center gap-3">
                            <div className="w-12 h-12 rounded-full bg-[#D4AF37]/30 flex items-center justify-center text-white font-bold overflow-hidden">
                              {request.sender?.avatar ? (
                                <img 
                                  src={request.sender.avatar.startsWith('http') ? request.sender.avatar : `${process.env.REACT_APP_BACKEND_URL}${request.sender.avatar}`} 
                                  alt="" 
                                  className="w-full h-full object-cover" 
                                />
                              ) : (
                                <>{request.sender?.first_name?.[0]}{request.sender?.last_name?.[0]}</>
                              )}
                            </div>
                            <div>
                              <p className="text-white font-medium">{request.sender?.first_name} {request.sender?.last_name}</p>
                              <p className="text-sm text-gray-400">{request.message || 'Souhaite vous ajouter comme ami'}</p>
                              <p className="text-xs text-gray-500 mt-1">{request.sender?.city || 'Lausanne'}</p>
                            </div>
                          </div>
                          <div className="flex gap-2">
                            <button
                              onClick={() => handleRespondToRequest(request.id, true)}
                              className="p-2 bg-green-500/20 text-green-400 rounded-lg hover:bg-green-500/30"
                            >
                              <CheckCircle className="w-5 h-5" />
                            </button>
                            <button
                              onClick={() => handleRespondToRequest(request.id, false)}
                              className="p-2 bg-red-500/20 text-red-400 rounded-lg hover:bg-red-500/30"
                            >
                              <XCircle className="w-5 h-5" />
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Amis acceptés récemment */}
              {friends.length > 0 && (
                <div className="card-service rounded-xl p-6 border-green-500/30">
                  <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                    <CheckCircle className="w-5 h-5 text-green-400" />
                    Amis acceptés ({friends.length})
                  </h2>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {friends.slice(0, 6).map((friend) => (
                      <div key={friend.id} className="p-4 bg-white/5 rounded-xl">
                        <div className="flex items-center gap-3 mb-3">
                          <div className="w-14 h-14 rounded-full bg-green-500/20 flex items-center justify-center text-white font-bold overflow-hidden">
                            {friend.avatar ? (
                              <img 
                                src={friend.avatar.startsWith('http') ? friend.avatar : `${process.env.REACT_APP_BACKEND_URL}${friend.avatar}`} 
                                alt="" 
                                className="w-full h-full object-cover" 
                              />
                            ) : (
                              <>{friend.first_name?.[0]}{friend.last_name?.[0]}</>
                            )}
                          </div>
                          <div>
                            <p className="text-white font-medium">{friend.first_name} {friend.last_name}</p>
                            <p className="text-sm text-gray-400">{friend.city || 'Lausanne'}</p>
                            {friend.since && (
                              <p className="text-xs text-green-400">Ami depuis {new Date(friend.since).toLocaleDateString('fr-FR')}</p>
                            )}
                          </div>
                        </div>
                        <div className="flex gap-2">
                          <button
                            onClick={() => { setSelectedConversation(friend); setActiveTab('messages'); }}
                            className="flex-1 btn-secondary text-sm flex items-center justify-center gap-2"
                          >
                            <MessageSquare className="w-4 h-4" />
                            Message
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Cards Tab - Production Ready */}
          {activeTab === 'cartes' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
                  Mes Cartes de Paiement
                </h1>
                <button onClick={() => setShowAddCard(true)} className="btn-primary flex items-center gap-2">
                  <Plus className="w-4 h-4" />
                  Ajouter une carte
                </button>
              </div>

              {/* Security Notice */}
              <div className="card-service rounded-xl p-4 border-[#0047AB]/30">
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-white text-sm font-medium">Paiements sécurisés</p>
                    <p className="text-gray-400 text-xs">Vos données bancaires sont cryptées et sécurisées via Stripe. Nous ne stockons jamais votre numéro complet.</p>
                  </div>
                </div>
              </div>

              {cards.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {cards.map((card) => (
                    <div key={card.id} className={`card-service rounded-xl p-6 relative overflow-hidden ${card.is_default ? 'border-[#0047AB]' : ''}`}>
                      {/* Card Background Gradient */}
                      <div className={`absolute inset-0 opacity-20 ${
                        card.card_type === 'visa' ? 'bg-gradient-to-br from-blue-600 to-blue-900' :
                        card.card_type === 'mastercard' ? 'bg-gradient-to-br from-orange-500 to-red-600' :
                        'bg-gradient-to-br from-gray-600 to-gray-900'
                      }`} />
                      
                      <div className="relative">
                        <div className="flex items-start justify-between mb-6">
                          <div className="flex items-center gap-3">
                            <CreditCard className={`w-10 h-10 ${
                              card.card_type === 'visa' ? 'text-blue-400' : 
                              card.card_type === 'mastercard' ? 'text-orange-400' : 
                              'text-gray-400'
                            }`} />
                            <div>
                              <p className="text-white font-bold uppercase text-lg">{card.card_type}</p>
                              {card.is_default && (
                                <span className="inline-flex items-center gap-1 text-xs text-[#0047AB] bg-[#0047AB]/20 px-2 py-0.5 rounded-full">
                                  <Star className="w-3 h-3" /> Par défaut
                                </span>
                              )}
                            </div>
                          </div>
                          <button
                            onClick={() => handleDeleteCard(card.id)}
                            className="p-2 text-red-400 hover:bg-red-500/20 rounded-lg transition-colors"
                          >
                            <Trash2 className="w-5 h-5" />
                          </button>
                        </div>
                        
                        <p className="text-2xl text-white font-mono tracking-wider mb-4">
                          •••• •••• •••• {card.card_number_last4}
                        </p>
                        
                        <div className="flex justify-between items-end">
                          <div>
                            <p className="text-xs text-gray-500 uppercase mb-1">Titulaire</p>
                            <p className="text-white font-medium uppercase">{card.card_holder}</p>
                          </div>
                          <div className="text-right">
                            <p className="text-xs text-gray-500 uppercase mb-1">Expire</p>
                            <p className="text-white font-medium">{String(card.expiry_month).padStart(2, '0')}/{card.expiry_year}</p>
                          </div>
                        </div>
                        
                        {!card.is_default && (
                          <button
                            onClick={() => handleSetDefaultCard(card.id)}
                            className="mt-4 w-full py-2 bg-white/10 text-white text-sm rounded-lg hover:bg-white/20 transition-colors"
                          >
                            Définir par défaut
                          </button>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="card-service rounded-xl p-12 text-center">
                  <CreditCard className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                  <p className="text-gray-400 mb-4">Aucune carte enregistrée</p>
                  <p className="text-sm text-gray-500 mb-6">Ajoutez une carte pour faciliter vos paiements</p>
                  <button onClick={() => setShowAddCard(true)} className="btn-secondary">
                    Ajouter une carte
                  </button>
                </div>
              )}

              {/* Add Card Modal - Production Ready */}
              {showAddCard && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
                  <div className="card-service rounded-xl p-6 w-full max-w-md">
                    <div className="flex items-center justify-between mb-6">
                      <h3 className="text-lg font-semibold text-white">Ajouter une carte</h3>
                      <button onClick={() => setShowAddCard(false)} className="text-gray-400 hover:text-white">
                        <X className="w-5 h-5" />
                      </button>
                    </div>
                    
                    {/* Card Preview */}
                    <div className={`rounded-xl p-5 mb-6 relative overflow-hidden ${
                      cardForm.card_type === 'visa' ? 'bg-gradient-to-br from-blue-600 to-blue-900' :
                      cardForm.card_type === 'mastercard' ? 'bg-gradient-to-br from-orange-500 to-red-600' :
                      'bg-gradient-to-br from-gray-700 to-gray-900'
                    }`}>
                      <div className="flex justify-between items-start mb-8">
                        <CreditCard className="w-8 h-8 text-white/80" />
                        <span className="text-white/80 uppercase font-bold">{cardForm.card_type}</span>
                      </div>
                      <p className="text-xl text-white font-mono tracking-wider mb-4">
                        {cardForm.card_number ? cardForm.card_number.replace(/(\d{4})/g, '$1 ').trim() : '•••• •••• •••• ••••'}
                      </p>
                      <div className="flex justify-between">
                        <span className="text-white/80 uppercase text-sm">{cardForm.card_holder || 'NOM DU TITULAIRE'}</span>
                        <span className="text-white/80 text-sm">
                          {String(cardForm.expiry_month).padStart(2, '0')}/{cardForm.expiry_year}
                        </span>
                      </div>
                    </div>
                    
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm text-gray-400 mb-2">Nom du titulaire *</label>
                        <input
                          type="text"
                          value={cardForm.card_holder}
                          onChange={(e) => setCardForm({...cardForm, card_holder: e.target.value.toUpperCase()})}
                          className="input-dark w-full"
                          placeholder="NOM PRÉNOM"
                        />
                      </div>
                      <div>
                        <label className="block text-sm text-gray-400 mb-2">Numéro de carte *</label>
                        <input
                          type="text"
                          maxLength={19}
                          value={cardForm.card_number || ''}
                          onChange={(e) => {
                            const value = e.target.value.replace(/\D/g, '').slice(0, 16);
                            const last4 = value.slice(-4);
                            setCardForm({...cardForm, card_number: value, card_number_last4: last4 || ''});
                          }}
                          className="input-dark w-full font-mono"
                          placeholder="1234 5678 9012 3456"
                        />
                      </div>
                      <div className="grid grid-cols-3 gap-4">
                        <div>
                          <label className="block text-sm text-gray-400 mb-2">Mois *</label>
                          <select
                            value={cardForm.expiry_month}
                            onChange={(e) => setCardForm({...cardForm, expiry_month: parseInt(e.target.value)})}
                            className="input-dark w-full"
                          >
                            {[...Array(12)].map((_, i) => (
                              <option key={i+1} value={i+1}>{String(i+1).padStart(2, '0')}</option>
                            ))}
                          </select>
                        </div>
                        <div>
                          <label className="block text-sm text-gray-400 mb-2">Année *</label>
                          <select
                            value={cardForm.expiry_year}
                            onChange={(e) => setCardForm({...cardForm, expiry_year: parseInt(e.target.value)})}
                            className="input-dark w-full"
                          >
                            {[2024, 2025, 2026, 2027, 2028, 2029, 2030, 2031, 2032].map((year) => (
                              <option key={year} value={year}>{year}</option>
                            ))}
                          </select>
                        </div>
                        <div>
                          <label className="block text-sm text-gray-400 mb-2">CVV *</label>
                          <input
                            type="password"
                            maxLength={4}
                            value={cardForm.cvv || ''}
                            onChange={(e) => setCardForm({...cardForm, cvv: e.target.value.replace(/\D/g, '')})}
                            className="input-dark w-full font-mono"
                            placeholder="•••"
                          />
                        </div>
                      </div>
                      <div>
                        <label className="block text-sm text-gray-400 mb-2">Type de carte</label>
                        <div className="flex gap-3">
                          {['visa', 'mastercard', 'amex'].map((type) => (
                            <button
                              key={type}
                              type="button"
                              onClick={() => setCardForm({...cardForm, card_type: type})}
                              className={`flex-1 py-3 px-4 rounded-lg border transition-colors ${
                                cardForm.card_type === type
                                  ? 'border-[#0047AB] bg-[#0047AB]/20 text-white'
                                  : 'border-white/10 bg-white/5 text-gray-400 hover:border-white/30'
                              }`}
                            >
                              {type.charAt(0).toUpperCase() + type.slice(1)}
                            </button>
                          ))}
                        </div>
                      </div>
                      <label className="flex items-center gap-2 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={cardForm.is_default}
                          onChange={(e) => setCardForm({...cardForm, is_default: e.target.checked})}
                          className="w-4 h-4 accent-[#0047AB]"
                        />
                        <span className="text-sm text-gray-400">Définir comme carte par défaut</span>
                      </label>
                    </div>
                    
                    <div className="mt-4 p-3 bg-white/5 rounded-lg">
                      <p className="text-xs text-gray-500 flex items-center gap-2">
                        <CheckCircle className="w-4 h-4 text-green-500" />
                        Vos données sont sécurisées et cryptées
                      </p>
                    </div>
                    
                    <div className="flex gap-3 mt-6">
                      <button onClick={() => setShowAddCard(false)} className="btn-secondary flex-1">Annuler</button>
                      <button onClick={handleAddCard} className="btn-primary flex-1">Ajouter la carte</button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Documents Tab - Fixed */}
          {activeTab === 'documents' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
                  Mes Documents
                </h1>
                <button onClick={() => setShowAddDocument(true)} className="btn-primary flex items-center gap-2">
                  <Upload className="w-4 h-4" />
                  Ajouter un document
                </button>
              </div>

              {/* Return to Job Alert */}
              {returnToJobId && (
                <div className="bg-[#0047AB]/20 border border-[#0047AB]/50 rounded-xl p-4 flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-full bg-[#0047AB]/30 flex items-center justify-center">
                      <Briefcase className="w-5 h-5 text-[#0047AB]" />
                    </div>
                    <div>
                      <p className="text-white font-medium">Vous souhaitez postuler à une offre</p>
                      <p className="text-sm text-gray-400">Ajoutez votre CV puis retournez postuler</p>
                    </div>
                  </div>
                  <Link 
                    to={`/emploi/${returnToJobId}`}
                    className="btn-primary text-sm"
                  >
                    Voir l'offre
                  </Link>
                </div>
              )}

              {documents.length > 0 ? (
                <div className="space-y-3">
                  {documents.map((doc) => (
                    <div key={doc.id} className="card-service rounded-xl p-4 flex items-center justify-between">
                      <div className="flex items-center gap-4">
                        <div className="w-12 h-12 bg-[#0047AB]/20 rounded-xl flex items-center justify-center">
                          <FolderOpen className="w-6 h-6 text-[#0047AB]" />
                        </div>
                        <div>
                          <p className="text-white font-medium">{doc.name}</p>
                          <p className="text-sm text-gray-500">{doc.category} • {new Date(doc.created_at).toLocaleDateString('fr-FR')}</p>
                        </div>
                      </div>
                      <div className="flex gap-2">
                        <a
                          href={doc.url.startsWith('http') ? doc.url : `${process.env.REACT_APP_BACKEND_URL}${doc.url}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="p-2 bg-[#0047AB]/20 text-[#0047AB] rounded-lg hover:bg-[#0047AB]/30"
                        >
                          <Eye className="w-4 h-4" />
                        </a>
                        <button
                          onClick={() => handleDeleteDocument(doc.id)}
                          className="p-2 bg-red-500/10 text-red-400 rounded-lg hover:bg-red-500/20"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  ))}
                  
                  {/* After adding CV, show button to return to job */}
                  {returnToJobId && documents.some(d => d.category === 'cv') && (
                    <div className="mt-4 text-center">
                      <Link 
                        to={`/emploi/${returnToJobId}`}
                        className="btn-primary inline-flex items-center gap-2"
                      >
                        <Briefcase className="w-4 h-4" />
                        Retourner postuler à l'offre
                      </Link>
                    </div>
                  )}
                </div>
              ) : (
                <div className="card-service rounded-xl p-12 text-center">
                  <FolderOpen className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                  <p className="text-gray-400 mb-4">Aucun document</p>
                  <button onClick={() => setShowAddDocument(true)} className="btn-secondary">
                    Ajouter un document
                  </button>
                </div>
              )}

              {/* Add Document Modal */}
              {showAddDocument && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
                  <div className="card-service rounded-xl p-6 w-full max-w-md">
                    <h3 className="text-lg font-semibold text-white mb-6">Ajouter un document</h3>
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm text-gray-400 mb-2">Nom du document</label>
                        <input
                          type="text"
                          value={documentForm.name}
                          onChange={(e) => setDocumentForm({...documentForm, name: e.target.value})}
                          className="input-dark w-full"
                          placeholder="Mon document"
                        />
                      </div>
                      <div>
                        <label className="block text-sm text-gray-400 mb-2">Catégorie</label>
                        <select
                          value={documentForm.category}
                          onChange={(e) => setDocumentForm({...documentForm, category: e.target.value})}
                          className="input-dark w-full"
                        >
                          <option value="cv">📄 CV / Curriculum Vitae</option>
                          <option value="general">Général</option>
                          <option value="factures">Factures</option>
                          <option value="contrats">Contrats</option>
                          <option value="autres">Autres</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm text-gray-400 mb-2">Fichier</label>
                        <input
                          type="file"
                          onChange={handleDocumentUpload}
                          className="w-full text-gray-400"
                          accept=".pdf,.doc,.docx"
                        />
                        {documentForm.url && (
                          <p className="text-sm text-green-400 mt-2">Fichier uploadé ✓</p>
                        )}
                      </div>
                    </div>
                    <div className="flex gap-3 mt-6">
                      <button onClick={() => { setShowAddDocument(false); setDocumentForm({ name: '', category: 'cv', url: '' }); }} className="btn-secondary flex-1">Annuler</button>
                      <button onClick={handleAddDocument} className="btn-primary flex-1">Ajouter</button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Messages Tab - Production Ready */}
          {activeTab === 'messages' && (
            <div className="h-[calc(100vh-180px)]">
              <h1 className="text-2xl font-bold text-white mb-6" style={{ fontFamily: 'Playfair Display, serif' }}>
                Messagerie
              </h1>
              
              <div className="flex gap-6 h-[calc(100%-60px)]">
                {/* Conversations List */}
                <div className="w-80 card-service rounded-xl p-4 overflow-y-auto">
                  <h3 className="text-sm font-semibold text-gray-400 mb-4">Conversations</h3>
                  {conversations.length > 0 ? (
                    <div className="space-y-2">
                      {conversations.map((conv) => (
                        <button
                          key={conv.partner?.id}
                          onClick={() => handleSelectConversation(conv.partner?.id)}
                          className={`w-full p-3 rounded-xl text-left transition-colors ${
                            selectedConversation?.id === conv.partner?.id
                              ? 'bg-[#0047AB]/20'
                              : 'bg-white/5 hover:bg-white/10'
                          }`}
                        >
                          <div className="flex items-center gap-3">
                            <div className="w-10 h-10 rounded-full bg-[#0047AB]/50 flex items-center justify-center text-white font-bold text-sm">
                              {conv.partner?.first_name?.[0]}{conv.partner?.last_name?.[0]}
                            </div>
                            <div className="flex-1 min-w-0">
                              <div className="flex items-center justify-between">
                                <p className="text-white font-medium truncate">{conv.partner?.first_name} {conv.partner?.last_name}</p>
                                {conv.unread_count > 0 && (
                                  <span className="w-5 h-5 bg-[#0047AB] rounded-full text-xs flex items-center justify-center text-white">
                                    {conv.unread_count}
                                  </span>
                                )}
                              </div>
                              <p className="text-sm text-gray-500 truncate">{conv.last_message?.content}</p>
                            </div>
                          </div>
                        </button>
                      ))}
                    </div>
                  ) : (
                    <div className="text-center py-8">
                      <MessageSquare className="w-10 h-10 text-gray-600 mx-auto mb-2" />
                      <p className="text-sm text-gray-500">Aucune conversation</p>
                    </div>
                  )}
                  
                  {/* Start new conversation with friends */}
                  {friends.length > 0 && (
                    <div className="mt-6 pt-4 border-t border-white/10">
                      <h4 className="text-xs font-semibold text-gray-500 mb-3">Démarrer une conversation</h4>
                      {friends.slice(0, 5).map((friend) => (
                        <button
                          key={friend.id}
                          onClick={() => handleSelectConversation(friend.id)}
                          className="w-full p-2 rounded-lg text-left bg-white/5 hover:bg-white/10 mb-2 flex items-center gap-2"
                        >
                          <div className="w-8 h-8 rounded-full bg-gray-600 flex items-center justify-center text-white text-xs font-bold">
                            {friend.first_name?.[0]}{friend.last_name?.[0]}
                          </div>
                          <span className="text-sm text-gray-300">{friend.first_name}</span>
                        </button>
                      ))}
                    </div>
                  )}
                </div>

                {/* Chat Area */}
                <div className="flex-1 card-service rounded-xl flex flex-col">
                  {selectedConversation ? (
                    <>
                      {/* Chat Header */}
                      <div className="p-4 border-b border-white/10 flex items-center gap-3">
                        <div className="w-10 h-10 rounded-full bg-[#0047AB]/50 flex items-center justify-center text-white font-bold">
                          {selectedConversation.first_name?.[0]}{selectedConversation.last_name?.[0]}
                        </div>
                        <div>
                          <p className="text-white font-medium">{selectedConversation.first_name} {selectedConversation.last_name}</p>
                          <p className="text-sm text-gray-500">{selectedConversation.user_type === 'entreprise' ? 'Entreprise' : 'Client'}</p>
                        </div>
                      </div>

                      {/* Messages */}
                      <div className="flex-1 p-4 overflow-y-auto space-y-4">
                        {messages.map((msg) => (
                          <div
                            key={msg.id}
                            className={`flex ${msg.sender_id === user?.id ? 'justify-end' : 'justify-start'}`}
                          >
                            <div
                              className={`max-w-xs px-4 py-2 rounded-2xl ${
                                msg.sender_id === user?.id
                                  ? 'bg-[#0047AB] text-white rounded-br-none'
                                  : 'bg-white/10 text-white rounded-bl-none'
                              }`}
                            >
                              <p>{msg.content}</p>
                              <p className={`text-xs mt-1 ${msg.sender_id === user?.id ? 'text-white/60' : 'text-gray-500'}`}>
                                {new Date(msg.created_at).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}
                              </p>
                            </div>
                          </div>
                        ))}
                      </div>

                      {/* Input */}
                      <div className="p-4 border-t border-white/10">
                        <div className="flex gap-3">
                          <input
                            type="text"
                            value={newMessage}
                            onChange={(e) => setNewMessage(e.target.value)}
                            onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                            placeholder="Écrivez votre message..."
                            className="input-dark flex-1"
                          />
                          <button
                            onClick={handleSendMessage}
                            disabled={!newMessage.trim()}
                            className="btn-primary px-4 disabled:opacity-50"
                          >
                            <Send className="w-5 h-5" />
                          </button>
                        </div>
                      </div>
                    </>
                  ) : (
                    <div className="flex-1 flex items-center justify-center">
                      <div className="text-center">
                        <MessageSquare className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                        <p className="text-gray-400">Sélectionnez une conversation</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Compte Particulier (Switch) */}
          {activeTab === 'particulier' && (
            <div className="max-w-md mx-auto">
              <h1 className="text-2xl font-bold text-white mb-8 text-center" style={{ fontFamily: 'Playfair Display, serif' }}>
                Compte Particulier
              </h1>
              <div className="card-service rounded-xl p-8 text-center">
                <Building2 className="w-16 h-16 text-[#0047AB] mx-auto mb-6" />
                <h2 className="text-xl font-bold text-white mb-4">Créez votre compte particulier</h2>
                <p className="text-gray-400 mb-6">
                  Avec un compte particulier, vous pouvez proposer vos propres services sur Titelli.
                </p>
                <button 
                  onClick={() => navigate('/auth?type=entreprise')}
                  className="btn-primary w-full"
                >
                  Créer un compte particulier
                </button>
              </div>
            </div>
          )}

          {/* Orders Tab */}
          {activeTab === 'orders' && (
            <div>
              <h1 className="text-2xl font-bold text-white mb-8" style={{ fontFamily: 'Playfair Display, serif' }}>
                Mes commandes
              </h1>
              {orders.length > 0 ? (
                <div className="space-y-4">
                  {orders.map((order) => (
                    <div key={order.id} className="card-service rounded-xl p-6">
                      <div className="flex items-center justify-between mb-4">
                        <div>
                          <p className="text-white font-semibold">Commande #{order.id.slice(0, 8)}</p>
                          <p className="text-sm text-gray-400">{new Date(order.created_at).toLocaleDateString('fr-FR')}</p>
                        </div>
                        <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                          order.status === 'completed' ? 'bg-green-500/20 text-green-500' :
                          order.status === 'pending' ? 'bg-yellow-500/20 text-yellow-500' :
                          'bg-gray-500/20 text-gray-500'
                        }`}>
                          {order.status === 'pending' ? 'En cours' : order.status}
                        </span>
                      </div>
                      <div className="space-y-2 mb-4">
                        {order.items?.map((item, i) => (
                          <div key={i} className="flex justify-between text-sm">
                            <span className="text-gray-400">{item.name} x{item.quantity}</span>
                            <span className="text-white">{(item.price * item.quantity).toFixed(2)} CHF</span>
                          </div>
                        ))}
                      </div>
                      <div className="flex justify-between pt-4 border-t border-white/10">
                        <span className="text-gray-400">Total</span>
                        <span className="text-xl font-bold text-white">{order.total?.toFixed(2)} CHF</span>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="card-service rounded-xl p-12 text-center">
                  <ShoppingCart className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                  <h2 className="text-xl font-bold text-white mb-2">Aucune commande</h2>
                  <p className="text-gray-400 mb-6">Explorez nos prestataires et passez votre première commande</p>
                  <Link to="/" className="btn-primary">Explorer</Link>
                </div>
              )}
            </div>
          )}

          {/* Cashback Tab */}
          {activeTab === 'cashback' && (
            <div>
              <h1 className="text-2xl font-bold text-white mb-8" style={{ fontFamily: 'Playfair Display, serif' }}>
                Mon Cash-back
              </h1>
              
              {/* Balance Card with Withdraw Button */}
              <div className="card-service rounded-xl p-8 text-center mb-8">
                <div className="w-20 h-20 rounded-full bg-green-500/20 flex items-center justify-center mx-auto mb-6">
                  <Wallet className="w-10 h-10 text-green-500" />
                </div>
                <p className="text-5xl font-bold text-white mb-2">{cashback.toFixed(2)} CHF</p>
                <p className="text-gray-400 mb-4">Solde cash-back disponible</p>
                <div className="inline-flex items-center gap-2 px-4 py-2 bg-green-500/20 rounded-full mb-6">
                  <TrendingUp className="w-4 h-4 text-green-500" />
                  <span className="text-green-500 font-semibold">10% de cashback sur tous vos achats !</span>
                </div>
                
                {/* Withdraw Button */}
                <div className="flex flex-col sm:flex-row gap-4 justify-center mt-6">
                  <button
                    onClick={() => withdrawalInfo.has_bank_info ? setShowWithdrawModal(true) : setShowBankForm(true)}
                    disabled={cashback < 50}
                    className={`px-8 py-3 rounded-xl font-semibold flex items-center justify-center gap-2 transition-all ${
                      cashback >= 50 
                        ? 'bg-[#D4AF37] text-black hover:bg-[#C4A030]' 
                        : 'bg-gray-600 text-gray-400 cursor-not-allowed'
                    }`}
                  >
                    <CreditCard className="w-5 h-5" />
                    Retirer vers mon compte
                  </button>
                  {!withdrawalInfo.has_bank_info && (
                    <button
                      onClick={() => setShowBankForm(true)}
                      className="px-6 py-3 rounded-xl font-semibold bg-white/10 text-white hover:bg-white/20 transition-all flex items-center gap-2"
                    >
                      <Plus className="w-5 h-5" />
                      Ajouter mon IBAN
                    </button>
                  )}
                </div>
                
                {cashback < 50 && (
                  <p className="text-sm text-gray-500 mt-4">
                    Minimum de retrait : 50 CHF (il vous manque {(50 - cashback).toFixed(2)} CHF)
                  </p>
                )}
                
                {withdrawalInfo.has_bank_info && (
                  <p className="text-sm text-gray-400 mt-4">
                    Compte enregistré : {withdrawalInfo.iban_masked} ({withdrawalInfo.account_holder})
                    <button 
                      onClick={() => setShowBankForm(true)}
                      className="ml-2 text-[#0047AB] hover:underline"
                    >
                      Modifier
                    </button>
                  </p>
                )}
              </div>

              {/* Bank Account Form Modal */}
              {showBankForm && (
                <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
                  <div className="card-service rounded-xl p-6 w-full max-w-md">
                    <div className="flex items-center justify-between mb-6">
                      <h2 className="text-xl font-bold text-white">Coordonnées bancaires</h2>
                      <button onClick={() => setShowBankForm(false)} className="text-gray-400 hover:text-white">
                        <X className="w-6 h-6" />
                      </button>
                    </div>
                    
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm text-gray-400 mb-2">Nom du titulaire du compte *</label>
                        <input
                          type="text"
                          value={bankForm.bank_account_holder}
                          onChange={(e) => setBankForm({ ...bankForm, bank_account_holder: e.target.value })}
                          placeholder="Jean Dupont"
                          className="w-full px-4 py-3 rounded-xl bg-white/10 border border-white/20 text-white focus:border-[#D4AF37] focus:outline-none"
                        />
                      </div>
                      
                      <div>
                        <label className="block text-sm text-gray-400 mb-2">IBAN *</label>
                        <input
                          type="text"
                          value={bankForm.iban}
                          onChange={(e) => setBankForm({ ...bankForm, iban: e.target.value.toUpperCase() })}
                          placeholder="CH93 0076 2011 6238 5295 7"
                          className="w-full px-4 py-3 rounded-xl bg-white/10 border border-white/20 text-white focus:border-[#D4AF37] focus:outline-none font-mono"
                        />
                        <p className="text-xs text-gray-500 mt-1">Format suisse: CH + 19 chiffres</p>
                      </div>
                      
                      <div>
                        <label className="block text-sm text-gray-400 mb-2">BIC/SWIFT (optionnel)</label>
                        <input
                          type="text"
                          value={bankForm.bic_swift}
                          onChange={(e) => setBankForm({ ...bankForm, bic_swift: e.target.value.toUpperCase() })}
                          placeholder="POFICHBEXXX"
                          className="w-full px-4 py-3 rounded-xl bg-white/10 border border-white/20 text-white focus:border-[#D4AF37] focus:outline-none font-mono"
                        />
                      </div>
                      
                      <div className="p-4 bg-blue-500/10 rounded-xl border border-blue-500/30">
                        <p className="text-sm text-blue-400 flex items-start gap-2">
                          <Info className="w-4 h-4 mt-0.5 flex-shrink-0" />
                          Vos coordonnées bancaires sont sécurisées et utilisées uniquement pour les retraits de cashback.
                        </p>
                      </div>
                      
                      <button
                        onClick={handleSaveBankInfo}
                        className="w-full py-3 rounded-xl bg-[#D4AF37] text-black font-semibold hover:bg-[#C4A030] transition-colors"
                      >
                        Enregistrer
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {/* Withdraw Confirmation Modal */}
              {showWithdrawModal && (
                <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 p-4">
                  <div className="card-service rounded-xl p-6 w-full max-w-md">
                    <div className="flex items-center justify-between mb-6">
                      <h2 className="text-xl font-bold text-white">Confirmer le retrait</h2>
                      <button onClick={() => setShowWithdrawModal(false)} className="text-gray-400 hover:text-white">
                        <X className="w-6 h-6" />
                      </button>
                    </div>
                    
                    <div className="text-center mb-6">
                      <div className="w-16 h-16 rounded-full bg-green-500/20 flex items-center justify-center mx-auto mb-4">
                        <CreditCard className="w-8 h-8 text-green-500" />
                      </div>
                      <p className="text-3xl font-bold text-white mb-2">{cashback.toFixed(2)} CHF</p>
                      <p className="text-gray-400">sera transféré vers</p>
                      <p className="text-white font-medium mt-2">
                        {withdrawalInfo.iban_masked}<br />
                        <span className="text-sm text-gray-400">{withdrawalInfo.account_holder}</span>
                      </p>
                    </div>
                    
                    <div className="p-4 bg-yellow-500/10 rounded-xl border border-yellow-500/30 mb-6">
                      <p className="text-sm text-yellow-400 flex items-start gap-2">
                        <Clock className="w-4 h-4 mt-0.5 flex-shrink-0" />
                        Délai de traitement : 1 à 5 jours ouvrables
                      </p>
                    </div>
                    
                    <div className="flex gap-4">
                      <button
                        onClick={() => setShowWithdrawModal(false)}
                        className="flex-1 py-3 rounded-xl bg-white/10 text-white font-semibold hover:bg-white/20 transition-colors"
                      >
                        Annuler
                      </button>
                      <button
                        onClick={handleWithdraw}
                        disabled={withdrawing}
                        className="flex-1 py-3 rounded-xl bg-green-500 text-white font-semibold hover:bg-green-600 transition-colors disabled:opacity-50 flex items-center justify-center gap-2"
                      >
                        {withdrawing ? (
                          <>
                            <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                            Traitement...
                          </>
                        ) : (
                          <>
                            <CheckCircle className="w-5 h-5" />
                            Confirmer
                          </>
                        )}
                      </button>
                    </div>
                  </div>
                </div>
              )}
              
              {/* Stats Cards */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
                <div className="card-service rounded-xl p-6">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-full bg-green-500/20 flex items-center justify-center">
                      <TrendingUp className="w-6 h-6 text-green-500" />
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">Total gagné</p>
                      <p className="text-xl font-bold text-green-500">{cashbackStats.total_earned.toFixed(2)} CHF</p>
                    </div>
                  </div>
                </div>
                <div className="card-service rounded-xl p-6">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-full bg-orange-500/20 flex items-center justify-center">
                      <ShoppingCart className="w-6 h-6 text-orange-500" />
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">Total utilisé</p>
                      <p className="text-xl font-bold text-orange-500">{cashbackStats.total_used.toFixed(2)} CHF</p>
                    </div>
                  </div>
                </div>
                <div className="card-service rounded-xl p-6">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-full bg-blue-500/20 flex items-center justify-center">
                      <Gift className="w-6 h-6 text-blue-500" />
                    </div>
                    <div>
                      <p className="text-sm text-gray-400">Transactions</p>
                      <p className="text-xl font-bold text-blue-500">{cashbackStats.transaction_count}</p>
                    </div>
                  </div>
                </div>
              </div>
              
              {/* Withdrawal History */}
              {withdrawalHistory.length > 0 && (
                <div className="card-service rounded-xl p-6 mb-8">
                  <h2 className="text-lg font-semibold text-white mb-4">Historique des retraits</h2>
                  <div className="space-y-3">
                    {withdrawalHistory.map((w) => (
                      <div key={w.id} className="flex items-center justify-between p-4 bg-white/5 rounded-xl">
                        <div className="flex items-center gap-4">
                          <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                            w.status === 'completed' ? 'bg-green-500/20' : 
                            w.status === 'failed' ? 'bg-red-500/20' : 'bg-yellow-500/20'
                          }`}>
                            {w.status === 'completed' ? (
                              <CheckCircle className="w-5 h-5 text-green-500" />
                            ) : w.status === 'failed' ? (
                              <XCircle className="w-5 h-5 text-red-500" />
                            ) : (
                              <Clock className="w-5 h-5 text-yellow-500" />
                            )}
                          </div>
                          <div>
                            <p className="text-white font-medium">Retrait vers {w.iban}</p>
                            <p className="text-sm text-gray-400">
                              {new Date(w.created_at).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' })}
                            </p>
                          </div>
                        </div>
                        <div className="text-right">
                          <span className="font-semibold text-[#D4AF37]">-{w.amount.toFixed(2)} CHF</span>
                          <p className={`text-xs ${
                            w.status === 'completed' ? 'text-green-500' : 
                            w.status === 'failed' ? 'text-red-500' : 'text-yellow-500'
                          }`}>
                            {w.status === 'completed' ? 'Terminé' : 
                             w.status === 'failed' ? 'Échoué' : 'En cours'}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
              
              {/* Transaction History */}
              <div className="card-service rounded-xl p-6">
                <h2 className="text-lg font-semibold text-white mb-4">Historique des transactions</h2>
                {cashbackHistory.length > 0 ? (
                  <div className="space-y-3">
                    {cashbackHistory.map((tx) => (
                      <div key={tx.id} className="flex items-center justify-between p-4 bg-white/5 rounded-xl">
                        <div className="flex items-center gap-4">
                          <div className={`w-10 h-10 rounded-full flex items-center justify-center ${tx.amount > 0 ? 'bg-green-500/20' : 'bg-red-500/20'}`}>
                            {tx.amount > 0 ? (
                              <TrendingUp className="w-5 h-5 text-green-500" />
                            ) : (
                              <ShoppingCart className="w-5 h-5 text-red-500" />
                            )}
                          </div>
                          <div>
                            <p className="text-white font-medium">{tx.description}</p>
                            <p className="text-sm text-gray-400">
                              {new Date(tx.created_at).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' })}
                            </p>
                          </div>
                        </div>
                        <span className={`font-semibold ${tx.amount > 0 ? 'text-green-500' : 'text-red-500'}`}>
                          {tx.amount > 0 ? '+' : ''}{tx.amount.toFixed(2)} CHF
                        </span>
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <Wallet className="w-12 h-12 text-gray-600 mx-auto mb-3" />
                    <p className="text-gray-400">Aucune transaction pour le moment</p>
                    <p className="text-sm text-gray-500 mt-1">Faites des achats pour gagner du cashback !</p>
                  </div>
                )}
              </div>
              
              {/* Info Section */}
              <div className="mt-8 card-service rounded-xl p-6 border border-[#0047AB]/30">
                <h3 className="text-lg font-semibold text-white mb-3 flex items-center gap-2">
                  <Info className="w-5 h-5 text-[#0047AB]" />
                  Comment fonctionne le cashback ?
                </h3>
                <ul className="space-y-2 text-sm text-gray-400">
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                    <span><strong className="text-white">10% de cashback</strong> sur chaque commande et formation achetée</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                    <span>Le cashback est <strong className="text-white">crédité automatiquement</strong> après chaque achat</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                    <span>Utilisez votre cashback pour <strong className="text-white">réduire vos prochains achats</strong></span>
                  </li>
                  <li className="flex items-start gap-2">
                    <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                    <span>Votre cashback <strong className="text-white">n'expire jamais</strong></span>
                  </li>
                </ul>
              </div>
            </div>
          )}

          {/* Parrainage Tab */}
          {activeTab === 'parrainage' && (
            <div>
              <h1 className="text-2xl font-bold text-white mb-8" style={{ fontFamily: 'Playfair Display, serif' }}>
                Parrainage
              </h1>
              <ReferralSection />
            </div>
          )}

          {/* Email Preferences Tab */}
          {activeTab === 'email-prefs' && (
            <div>
              <h1 className="text-2xl font-bold text-white mb-8" style={{ fontFamily: 'Playfair Display, serif' }}>
                Préférences Email
              </h1>
              <EmailPreferences />
            </div>
          )}

          {/* Settings Tab */}
          {activeTab === 'settings' && (
            <div>
              <h1 className="text-2xl font-bold text-white mb-8" style={{ fontFamily: 'Playfair Display, serif' }}>
                Paramètres
              </h1>
              <div className="space-y-6">
                <div className="card-service rounded-xl p-6">
                  <h3 className="text-lg font-semibold text-white mb-4">Notifications</h3>
                  <div className="space-y-4">
                    <label className="flex items-center justify-between">
                      <span className="text-gray-400">Notifications par email</span>
                      <input type="checkbox" defaultChecked className="toggle" />
                    </label>
                    <label className="flex items-center justify-between">
                      <span className="text-gray-400">Notifications push</span>
                      <input type="checkbox" defaultChecked className="toggle" />
                    </label>
                    <label className="flex items-center justify-between">
                      <span className="text-gray-400">Demandes d'amis</span>
                      <input type="checkbox" defaultChecked className="toggle" />
                    </label>
                    <label className="flex items-center justify-between">
                      <span className="text-gray-400">Offres promotionnelles</span>
                      <input type="checkbox" className="toggle" />
                    </label>
                  </div>
                </div>
                <div className="card-service rounded-xl p-6">
                  <h3 className="text-lg font-semibold text-white mb-4">Confidentialité</h3>
                  <div className="space-y-4">
                    <label className="flex items-center justify-between">
                      <span className="text-gray-400">Profil visible publiquement</span>
                      <input type="checkbox" className="toggle" />
                    </label>
                    <label className="flex items-center justify-between">
                      <span className="text-gray-400">Partager mes avis</span>
                      <input type="checkbox" defaultChecked className="toggle" />
                    </label>
                    <label className="flex items-center justify-between">
                      <span className="text-gray-400">Recevoir des suggestions d'amis</span>
                      <input type="checkbox" defaultChecked className="toggle" />
                    </label>
                  </div>
                </div>
                <div className="card-service rounded-xl p-6">
                  <h3 className="text-lg font-semibold text-white mb-4 text-red-500">Zone de danger</h3>
                  <button className="text-red-400 hover:text-red-300 text-sm">
                    Supprimer mon compte
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Formations Tab - Production Ready */}
          {activeTab === 'formations' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
                  Mes Formations
                </h1>
              </div>

              {/* Stats Cards */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="card-service rounded-xl p-4 flex items-center gap-4">
                  <div className="w-12 h-12 rounded-xl bg-[#0047AB]/20 flex items-center justify-center">
                    <GraduationCap className="w-6 h-6 text-[#0047AB]" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-white">{myTrainings.stats?.total || 0}</p>
                    <p className="text-sm text-gray-400">Total formations</p>
                  </div>
                </div>
                <div className="card-service rounded-xl p-4 flex items-center gap-4">
                  <div className="w-12 h-12 rounded-xl bg-yellow-500/20 flex items-center justify-center">
                    <Clock className="w-6 h-6 text-yellow-500" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-white">{myTrainings.stats?.in_progress || 0}</p>
                    <p className="text-sm text-gray-400">En cours</p>
                  </div>
                </div>
                <div className="card-service rounded-xl p-4 flex items-center gap-4">
                  <div className="w-12 h-12 rounded-xl bg-green-500/20 flex items-center justify-center">
                    <CheckCircle className="w-6 h-6 text-green-500" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-white">{myTrainings.stats?.completed || 0}</p>
                    <p className="text-sm text-gray-400">Terminées</p>
                  </div>
                </div>
              </div>

              {/* Filter Tabs */}
              <div className="flex gap-2 border-b border-white/10 pb-2">
                {[
                  { id: 'all', label: 'Toutes' },
                  { id: 'in_progress', label: 'En cours' },
                  { id: 'completed', label: 'Terminées' }
                ].map((filter) => (
                  <button
                    key={filter.id}
                    onClick={() => setTrainingsFilter(filter.id)}
                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                      trainingsFilter === filter.id 
                        ? 'bg-[#0047AB] text-white' 
                        : 'text-gray-400 hover:text-white hover:bg-white/5'
                    }`}
                  >
                    {filter.label}
                  </button>
                ))}
              </div>

              {/* Trainings List */}
              {loadingTrainings ? (
                <div className="flex justify-center py-12">
                  <div className="w-10 h-10 border-4 border-[#0047AB] border-t-transparent rounded-full animate-spin" />
                </div>
              ) : myTrainings.enrollments?.length > 0 ? (
                <div className="space-y-4">
                  {myTrainings.enrollments.map((enrollment) => (
                    <div key={enrollment.id} className="card-service rounded-xl overflow-hidden">
                      <div className="p-6">
                        <div className="flex items-start justify-between gap-4">
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-2">
                              <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                                enrollment.training_type === 'online' 
                                  ? 'bg-purple-500/20 text-purple-400' 
                                  : 'bg-blue-500/20 text-blue-400'
                              }`}>
                                {enrollment.training_type === 'online' ? '💻 En ligne' : '🏢 Présentiel'}
                              </span>
                              <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                                enrollment.status === 'completed' 
                                  ? 'bg-green-500/20 text-green-400' 
                                  : 'bg-yellow-500/20 text-yellow-400'
                              }`}>
                                {enrollment.status === 'completed' ? 'Terminée' : 'En cours'}
                              </span>
                            </div>
                            <h3 className="text-lg font-semibold text-white mb-1">{enrollment.training_title}</h3>
                            <p className="text-sm text-[#D4AF37]">{enrollment.enterprise_name}</p>
                            
                            {/* Training Details */}
                            <div className="flex flex-wrap gap-4 mt-3 text-sm text-gray-400">
                              <span>💰 {enrollment.price_paid} CHF</span>
                              {enrollment.start_date && (
                                <span>📅 {new Date(enrollment.start_date).toLocaleDateString('fr-FR')}</span>
                              )}
                              <span>📆 Inscrit le {new Date(enrollment.enrolled_at).toLocaleDateString('fr-FR')}</span>
                            </div>
                          </div>

                          {/* Action Buttons */}
                          <div className="flex flex-col gap-2">
                            {enrollment.status === 'in_progress' && (
                              <button
                                onClick={() => handleMarkTrainingComplete(enrollment.id)}
                                className="px-4 py-2 bg-green-500/20 text-green-400 rounded-lg hover:bg-green-500/30 text-sm flex items-center gap-2"
                              >
                                <CheckCircle className="w-4 h-4" />
                                Terminer
                              </button>
                            )}
                            {enrollment.status === 'completed' && !enrollment.has_reviewed && (
                              <button
                                onClick={() => {
                                  setReviewingTraining(enrollment);
                                  setShowReviewModal(true);
                                }}
                                className="px-4 py-2 bg-yellow-500/20 text-yellow-400 rounded-lg hover:bg-yellow-500/30 text-sm flex items-center gap-2"
                              >
                                <Star className="w-4 h-4" />
                                Donner un avis
                              </button>
                            )}
                          </div>
                        </div>

                        {/* Downloadable Files for Online Trainings */}
                        {enrollment.training_type === 'online' && enrollment.downloadable_files?.length > 0 && (
                          <div className="mt-4 pt-4 border-t border-white/10">
                            <p className="text-sm text-gray-400 mb-3">📂 Fichiers téléchargeables :</p>
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                              {enrollment.downloadable_files.map((file, idx) => (
                                <a
                                  key={idx}
                                  href={file.url?.startsWith('http') ? file.url : `${process.env.REACT_APP_BACKEND_URL}${file.url}`}
                                  target="_blank"
                                  rel="noopener noreferrer"
                                  className="flex items-center gap-3 p-3 bg-white/5 rounded-lg hover:bg-white/10 transition-colors"
                                >
                                  <span className="text-xl">
                                    {file.type?.includes('video') ? '🎬' : file.type?.includes('pdf') ? '📄' : file.type?.includes('image') ? '🖼️' : '📁'}
                                  </span>
                                  <span className="text-white text-sm truncate flex-1">{file.name}</span>
                                  <Eye className="w-4 h-4 text-gray-400" />
                                </a>
                              ))}
                            </div>
                          </div>
                        )}

                        {/* Progress Bar */}
                        {enrollment.status === 'in_progress' && (
                          <div className="mt-4">
                            <div className="flex justify-between text-xs text-gray-400 mb-1">
                              <span>Progression</span>
                              <span>{enrollment.progress || 0}%</span>
                            </div>
                            <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                              <div 
                                className="h-full bg-[#0047AB] transition-all duration-500"
                                style={{ width: `${enrollment.progress || 0}%` }}
                              />
                            </div>
                          </div>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="card-service rounded-xl p-12 text-center">
                  <GraduationCap className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                  <h2 className="text-xl font-bold text-white mb-2">Aucune formation</h2>
                  <p className="text-gray-400 mb-6">
                    {trainingsFilter === 'all' 
                      ? "Vous n'êtes inscrit à aucune formation" 
                      : trainingsFilter === 'in_progress' 
                        ? "Aucune formation en cours" 
                        : "Aucune formation terminée"}
                  </p>
                  <Link to="/" className="btn-primary">
                    Découvrir les formations
                  </Link>
                </div>
              )}
            </div>
          )}

          {/* Agenda Tab */}
          {activeTab === 'agenda' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
                  Mon Agenda
                </h1>
                <button onClick={() => setShowAddEvent(true)} className="btn-primary flex items-center gap-2">
                  <Plus className="w-4 h-4" />
                  Nouveau rendez-vous
                </button>
              </div>

              {agendaEvents.length > 0 ? (
                <div className="space-y-4">
                  {agendaEvents.map((event) => (
                    <div key={event.id} className="card-service rounded-xl p-5 hover:border-[#0047AB]/30 transition-colors">
                      <div className="flex items-start justify-between">
                        <div className="flex gap-4">
                          <div className="w-14 h-14 rounded-xl bg-[#0047AB]/20 flex flex-col items-center justify-center">
                            <span className="text-xs text-[#0047AB]">
                              {new Date(event.start_datetime).toLocaleDateString('fr-FR', { weekday: 'short' })}
                            </span>
                            <span className="text-lg font-bold text-white">
                              {new Date(event.start_datetime).getDate()}
                            </span>
                          </div>
                          <div>
                            <h3 className="text-white font-semibold">{event.title}</h3>
                            <div className="flex flex-wrap items-center gap-3 mt-1 text-sm text-gray-400">
                              <span className="flex items-center gap-1">
                                <Clock className="w-3 h-3" />
                                {new Date(event.start_datetime).toLocaleTimeString('fr-FR', { hour: '2-digit', minute: '2-digit' })}
                              </span>
                              {event.location && (
                                <span className="flex items-center gap-1">
                                  <MapPin className="w-3 h-3" />
                                  {event.location}
                                </span>
                              )}
                              <span className={`px-2 py-0.5 rounded-full text-xs ${
                                event.event_type === 'appointment' ? 'bg-blue-500/20 text-blue-400' :
                                event.event_type === 'meeting' ? 'bg-purple-500/20 text-purple-400' :
                                'bg-yellow-500/20 text-yellow-400'
                              }`}>
                                {event.event_type === 'appointment' ? 'RDV' : event.event_type === 'meeting' ? 'Réunion' : 'Rappel'}
                              </span>
                            </div>
                            {event.description && (
                              <p className="text-sm text-gray-500 mt-2">{event.description}</p>
                            )}
                          </div>
                        </div>
                        <button onClick={() => handleDeleteAgendaEvent(event.id)} className="p-2 text-red-400 hover:bg-red-500/20 rounded-lg">
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="card-service rounded-xl p-12 text-center">
                  <Calendar className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                  <p className="text-gray-400 mb-4">Aucun rendez-vous planifié</p>
                  <button onClick={() => setShowAddEvent(true)} className="btn-secondary">
                    Ajouter un rendez-vous
                  </button>
                </div>
              )}

              {/* Add Event Modal */}
              {showAddEvent && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
                  <div className="card-service rounded-xl p-6 w-full max-w-md max-h-[90vh] overflow-y-auto">
                    <h3 className="text-lg font-semibold text-white mb-6">Nouveau rendez-vous</h3>
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm text-gray-400 mb-2">Titre *</label>
                        <input type="text" value={eventForm.title} onChange={(e) => setEventForm({...eventForm, title: e.target.value})} className="input-dark w-full" placeholder="Ex: RDV Coiffeur" />
                      </div>
                      <div>
                        <label className="block text-sm text-gray-400 mb-2">Type</label>
                        <select value={eventForm.event_type} onChange={(e) => setEventForm({...eventForm, event_type: e.target.value})} className="input-dark w-full">
                          <option value="appointment">Rendez-vous</option>
                          <option value="meeting">Réunion</option>
                          <option value="reminder">Rappel</option>
                        </select>
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm text-gray-400 mb-2">Date & Heure début *</label>
                          <input type="datetime-local" value={eventForm.start_datetime} onChange={(e) => setEventForm({...eventForm, start_datetime: e.target.value})} className="input-dark w-full" />
                        </div>
                        <div>
                          <label className="block text-sm text-gray-400 mb-2">Date & Heure fin</label>
                          <input type="datetime-local" value={eventForm.end_datetime} onChange={(e) => setEventForm({...eventForm, end_datetime: e.target.value})} className="input-dark w-full" />
                        </div>
                      </div>
                      <div>
                        <label className="block text-sm text-gray-400 mb-2">Lieu</label>
                        <input type="text" value={eventForm.location} onChange={(e) => setEventForm({...eventForm, location: e.target.value})} className="input-dark w-full" placeholder="Adresse ou lieu" />
                      </div>
                      <div>
                        <label className="block text-sm text-gray-400 mb-2">Description</label>
                        <textarea value={eventForm.description} onChange={(e) => setEventForm({...eventForm, description: e.target.value})} className="input-dark w-full h-20 resize-none" placeholder="Notes supplémentaires..." />
                      </div>
                    </div>
                    <div className="flex gap-3 mt-6">
                      <button onClick={() => setShowAddEvent(false)} className="btn-secondary flex-1">Annuler</button>
                      <button onClick={handleAddAgendaEvent} className="btn-primary flex-1">Ajouter</button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Finances Tab */}
          {activeTab === 'finances' && (
            <div className="space-y-6">
              <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
                Mes Finances
              </h1>

              {/* Stats Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                <div className="card-service rounded-xl p-5">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-red-500/20 flex items-center justify-center">
                      <DollarSign className="w-6 h-6 text-red-500" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-white">{finances.statistics?.total_spent?.toFixed(2) || '0.00'} CHF</p>
                      <p className="text-sm text-gray-400">Total dépensé</p>
                    </div>
                  </div>
                </div>
                <div className="card-service rounded-xl p-5">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-green-500/20 flex items-center justify-center">
                      <Wallet className="w-6 h-6 text-green-500" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-green-500">{finances.statistics?.current_cashback_balance?.toFixed(2) || '0.00'} CHF</p>
                      <p className="text-sm text-gray-400">Cashback disponible</p>
                    </div>
                  </div>
                </div>
                <div className="card-service rounded-xl p-5">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-[#D4AF37]/20 flex items-center justify-center">
                      <TrendingUp className="w-6 h-6 text-[#D4AF37]" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-[#D4AF37]">{finances.statistics?.total_cashback_earned?.toFixed(2) || '0.00'} CHF</p>
                      <p className="text-sm text-gray-400">Cashback gagné</p>
                    </div>
                  </div>
                </div>
                <div className="card-service rounded-xl p-5">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-[#0047AB]/20 flex items-center justify-center">
                      <PieChart className="w-6 h-6 text-[#0047AB]" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-[#0047AB]">{finances.statistics?.savings_percentage || 0}%</p>
                      <p className="text-sm text-gray-400">Économies</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Details */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="card-service rounded-xl p-6">
                  <h3 className="text-lg font-semibold text-white mb-4">Détails des dépenses</h3>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                      <span className="text-gray-400 flex items-center gap-2"><ShoppingCart className="w-4 h-4" /> Commandes</span>
                      <span className="text-white font-semibold">{finances.statistics?.total_spent_orders?.toFixed(2) || '0.00'} CHF</span>
                    </div>
                    <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                      <span className="text-gray-400 flex items-center gap-2"><GraduationCap className="w-4 h-4" /> Formations</span>
                      <span className="text-white font-semibold">{finances.statistics?.total_spent_trainings?.toFixed(2) || '0.00'} CHF</span>
                    </div>
                    <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                      <span className="text-gray-400 flex items-center gap-2"><Package className="w-4 h-4" /> Nombre de commandes</span>
                      <span className="text-white font-semibold">{finances.statistics?.orders_count || 0}</span>
                    </div>
                    <div className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                      <span className="text-gray-400 flex items-center gap-2"><GraduationCap className="w-4 h-4" /> Nombre de formations</span>
                      <span className="text-white font-semibold">{finances.statistics?.trainings_count || 0}</span>
                    </div>
                  </div>
                </div>

                <div className="card-service rounded-xl p-6">
                  <h3 className="text-lg font-semibold text-white mb-4">Dernières transactions</h3>
                  {finances.recent_orders?.length > 0 ? (
                    <div className="space-y-3">
                      {finances.recent_orders.map((order) => (
                        <div key={order.id} className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                          <div>
                            <p className="text-white text-sm">Commande #{order.id?.slice(0, 8)}</p>
                            <p className="text-xs text-gray-500">{new Date(order.created_at).toLocaleDateString('fr-FR')}</p>
                          </div>
                          <span className="text-red-400 font-semibold">-{order.total?.toFixed(2)} CHF</span>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="text-gray-500 text-center py-4">Aucune transaction récente</p>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Donations Tab */}
          {activeTab === 'donations' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
                  Mes Donations
                </h1>
                <button onClick={() => setShowAddDonation(true)} className="btn-primary flex items-center gap-2">
                  <Heart className="w-4 h-4" />
                  Faire un don
                </button>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="card-service rounded-xl p-5">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-pink-500/20 flex items-center justify-center">
                      <Heart className="w-6 h-6 text-pink-500" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-white">{donations.total_donated?.toFixed(2) || '0.00'} CHF</p>
                      <p className="text-sm text-gray-400">Total donné</p>
                    </div>
                  </div>
                </div>
                <div className="card-service rounded-xl p-5">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-purple-500/20 flex items-center justify-center">
                      <Gift className="w-6 h-6 text-purple-500" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-white">{donations.donations_count || 0}</p>
                      <p className="text-sm text-gray-400">Donations effectuées</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Donations List */}
              {donations.donations?.length > 0 ? (
                <div className="space-y-4">
                  {donations.donations.map((donation) => (
                    <div key={donation.id} className="card-service rounded-xl p-5">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-4">
                          <div className="w-12 h-12 rounded-full bg-pink-500/20 flex items-center justify-center">
                            <Heart className="w-6 h-6 text-pink-500" />
                          </div>
                          <div>
                            <p className="text-white font-semibold">{donation.recipient_name}</p>
                            <p className="text-sm text-gray-400">{new Date(donation.created_at).toLocaleDateString('fr-FR')}</p>
                            {donation.message && <p className="text-sm text-gray-500 mt-1">"{donation.message}"</p>}
                          </div>
                        </div>
                        <p className="text-xl font-bold text-pink-500">{donation.amount?.toFixed(2)} CHF</p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="card-service rounded-xl p-12 text-center">
                  <Heart className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                  <p className="text-gray-400 mb-4">Vous n'avez pas encore fait de don</p>
                  <button onClick={() => setShowAddDonation(true)} className="btn-secondary">
                    Faire un premier don
                  </button>
                </div>
              )}

              {/* Add Donation Modal */}
              {showAddDonation && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
                  <div className="card-service rounded-xl p-6 w-full max-w-md">
                    <h3 className="text-lg font-semibold text-white mb-6">Faire un don</h3>
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm text-gray-400 mb-2">Montant (CHF) *</label>
                        <input type="number" value={donationForm.amount} onChange={(e) => setDonationForm({...donationForm, amount: e.target.value})} className="input-dark w-full" placeholder="50" />
                      </div>
                      <div>
                        <label className="block text-sm text-gray-400 mb-2">Bénéficiaire *</label>
                        <input type="text" value={donationForm.recipient_name} onChange={(e) => setDonationForm({...donationForm, recipient_name: e.target.value})} className="input-dark w-full" placeholder="Nom de l'association ou entreprise" />
                      </div>
                      <div>
                        <label className="block text-sm text-gray-400 mb-2">Message (optionnel)</label>
                        <textarea value={donationForm.message} onChange={(e) => setDonationForm({...donationForm, message: e.target.value})} className="input-dark w-full h-20 resize-none" placeholder="Un petit mot..." />
                      </div>
                      <label className="flex items-center gap-2 cursor-pointer">
                        <input type="checkbox" checked={donationForm.is_anonymous} onChange={(e) => setDonationForm({...donationForm, is_anonymous: e.target.checked})} className="w-4 h-4 accent-[#0047AB]" />
                        <span className="text-sm text-gray-400">Don anonyme</span>
                      </label>
                    </div>
                    <div className="flex gap-3 mt-6">
                      <button onClick={() => setShowAddDonation(false)} className="btn-secondary flex-1">Annuler</button>
                      <button onClick={handleAddDonation} className="btn-primary flex-1">Donner</button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Wishlist Tab */}
          {activeTab === 'wishlist' && (
            <div className="space-y-6">
              <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
                Ma Liste de Souhaits
              </h1>

              {wishlistItems.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {wishlistItems.map((item) => (
                    <div key={item.id} className="card-service rounded-xl overflow-hidden group">
                      <div className="aspect-video bg-white/5 relative">
                        {item.item_image ? (
                          <img src={item.item_image} alt={item.item_name} className="w-full h-full object-cover" />
                        ) : (
                          <div className="w-full h-full flex items-center justify-center">
                            <Package className="w-12 h-12 text-gray-600" />
                          </div>
                        )}
                        <button onClick={() => handleRemoveFromWishlist(item.item_id)} className="absolute top-2 right-2 p-2 bg-black/50 rounded-full text-red-400 hover:text-red-300 opacity-0 group-hover:opacity-100 transition-opacity">
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                      <div className="p-4">
                        <span className="text-xs text-[#0047AB] mb-1 block">{item.enterprise_name}</span>
                        <h3 className="text-white font-semibold mb-2">{item.item_name}</h3>
                        <div className="flex items-center justify-between">
                          <p className="text-lg font-bold text-[#D4AF37]">{item.item_price?.toFixed(2)} CHF</p>
                          <Link to={`/${item.item_type === 'service' ? 'service' : 'product'}/${item.item_id}`} className="text-sm text-[#0047AB] hover:underline">
                            Voir le détail
                          </Link>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="card-service rounded-xl p-12 text-center">
                  <Bookmark className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                  <p className="text-gray-400 mb-4">Votre liste de souhaits est vide</p>
                  <p className="text-sm text-gray-500 mb-6">Ajoutez des produits ou services en cliquant sur le cœur</p>
                  <Link to="/" className="btn-secondary">
                    Découvrir nos prestataires
                  </Link>
                </div>
              )}
            </div>
          )}

          {/* Suggestions from Friends Tab */}
          {activeTab === 'suggestions' && (
            <div className="space-y-6">
              <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
                Suggestions de mes contacts
              </h1>
              <p className="text-gray-400">Découvrez ce que vos amis ont aimé et ajouté à leurs favoris</p>

              {friendsSuggestions.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {friendsSuggestions.map((suggestion, index) => (
                    <div key={index} className="card-service rounded-xl p-5 hover:border-[#0047AB]/30 transition-colors">
                      <div className="flex items-start gap-4">
                        <div className="w-12 h-12 rounded-xl bg-[#0047AB]/20 flex items-center justify-center flex-shrink-0">
                          {suggestion.type === 'wishlist' ? <Heart className="w-6 h-6 text-pink-500" /> : <Star className="w-6 h-6 text-[#D4AF37]" />}
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <span className="text-sm text-[#0047AB]">{suggestion.recommended_by}</span>
                            <span className="text-xs text-gray-500">• {suggestion.reason}</span>
                          </div>
                          <h3 className="text-white font-semibold">{suggestion.item_name}</h3>
                          {suggestion.enterprise_name && <p className="text-sm text-gray-400">{suggestion.enterprise_name}</p>}
                          {suggestion.item_price && (
                            <p className="text-[#D4AF37] font-semibold mt-2">{suggestion.item_price.toFixed(2)} CHF</p>
                          )}
                          {suggestion.comment && (
                            <p className="text-sm text-gray-500 mt-2 italic">"{suggestion.comment}"</p>
                          )}
                        </div>
                        <Link to={suggestion.item_type === 'enterprise' ? `/entreprise/${suggestion.item_id}` : `/${suggestion.item_type}/${suggestion.item_id}`} className="p-2 bg-[#0047AB] rounded-lg text-white hover:bg-[#2E74D6]">
                          <ChevronRight className="w-4 h-4" />
                        </Link>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="card-service rounded-xl p-12 text-center">
                  <Users className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                  <p className="text-gray-400 mb-4">Aucune suggestion disponible</p>
                  <p className="text-sm text-gray-500">Ajoutez des amis pour voir leurs recommandations</p>
                </div>
              )}
            </div>
          )}

          {/* Personal Providers Tab */}
          {activeTab === 'prestataires' && (
            <div className="space-y-6">
              <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
                Mes Prestataires Personnels
              </h1>
              <p className="text-gray-400">Vos prestataires favoris pour un accès rapide</p>

              {personalProviders.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {personalProviders.map((provider) => (
                    <div key={provider.id} className="card-service rounded-xl p-5 hover:border-[#D4AF37]/30 transition-colors group">
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center gap-3">
                          <div className="w-12 h-12 rounded-full bg-[#D4AF37]/20 flex items-center justify-center overflow-hidden">
                            {provider.enterprise_logo ? (
                              <img src={provider.enterprise_logo} alt="" className="w-full h-full object-cover" />
                            ) : (
                              <Store className="w-6 h-6 text-[#D4AF37]" />
                            )}
                          </div>
                          <div>
                            <h3 className="text-white font-semibold">{provider.enterprise_name}</h3>
                            <p className="text-sm text-gray-400">{provider.category}</p>
                          </div>
                        </div>
                        <button onClick={() => handleRemoveProvider(provider.id)} className="p-2 text-red-400 hover:bg-red-500/20 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity">
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                      {provider.rating > 0 && (
                        <div className="flex items-center gap-2 mb-3">
                          <Star className="w-4 h-4 text-[#D4AF37] fill-[#D4AF37]" />
                          <span className="text-white">{provider.rating?.toFixed(1)}</span>
                          <span className="text-gray-500 text-sm">({provider.review_count} avis)</span>
                        </div>
                      )}
                      {provider.city && (
                        <p className="text-sm text-gray-500 flex items-center gap-1">
                          <MapPin className="w-3 h-3" /> {provider.city}
                        </p>
                      )}
                      <Link to={`/entreprise/${provider.enterprise_id}`} className="mt-4 btn-secondary w-full text-center block">
                        Voir le profil
                      </Link>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="card-service rounded-xl p-12 text-center">
                  <Store className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                  <p className="text-gray-400 mb-4">Aucun prestataire enregistré</p>
                  <p className="text-sm text-gray-500 mb-6">Ajoutez vos prestataires préférés depuis leur page</p>
                  <Link to="/" className="btn-secondary">
                    Découvrir nos prestataires
                  </Link>
                </div>
              )}
            </div>
          )}

          {/* Activity Feed Tab - Mon fil d'actualité */}
          {activeTab === 'feed' && (
            <div className="space-y-6">
              <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
                Mon Fil d'Actualité
              </h1>
              <p className="text-gray-400">Découvrez ce que font vos contacts</p>

              {activityFeed.length > 0 ? (
                <div className="space-y-4">
                  {activityFeed.map((activity, index) => (
                    <div key={index} className="card-service rounded-xl p-5 hover:border-[#0047AB]/30 transition-colors">
                      <div className="flex gap-4">
                        <div className="w-12 h-12 rounded-full bg-gradient-to-br from-[#0047AB] to-[#D4AF37] flex items-center justify-center flex-shrink-0 overflow-hidden">
                          {activity.user_avatar ? (
                            <img src={getImageUrl(activity.user_avatar)} alt="" className="w-full h-full object-cover" />
                          ) : (
                            <User className="w-6 h-6 text-white" />
                          )}
                        </div>
                        <div className="flex-1">
                          <p className="text-white">
                            <span className="font-semibold text-[#0047AB]">{activity.user_name}</span>
                            <span className="text-gray-400 mx-2">{activity.action}</span>
                            <span className="font-medium text-[#D4AF37]">{activity.target}</span>
                          </p>
                          {activity.comment && (
                            <p className="text-sm text-gray-500 mt-1 italic">"{activity.comment}"</p>
                          )}
                          {activity.rating && (
                            <div className="flex items-center gap-1 mt-2">
                              {[...Array(5)].map((_, i) => (
                                <Star key={i} className={`w-4 h-4 ${i < activity.rating ? 'text-[#D4AF37] fill-[#D4AF37]' : 'text-gray-600'}`} />
                              ))}
                            </div>
                          )}
                          {activity.item_price && (
                            <p className="text-sm text-[#D4AF37] mt-1">{activity.item_price.toFixed(2)} CHF</p>
                          )}
                          <p className="text-xs text-gray-500 mt-2">
                            {new Date(activity.created_at).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', hour: '2-digit', minute: '2-digit' })}
                          </p>
                        </div>
                        <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                          activity.type === 'review' ? 'bg-[#D4AF37]/20' :
                          activity.type === 'purchase' ? 'bg-green-500/20' :
                          activity.type === 'training' ? 'bg-purple-500/20' :
                          'bg-pink-500/20'
                        }`}>
                          {activity.type === 'review' && <Star className="w-5 h-5 text-[#D4AF37]" />}
                          {activity.type === 'purchase' && <ShoppingCart className="w-5 h-5 text-green-500" />}
                          {activity.type === 'training' && <GraduationCap className="w-5 h-5 text-purple-500" />}
                          {activity.type === 'wishlist' && <Heart className="w-5 h-5 text-pink-500" />}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="card-service rounded-xl p-12 text-center">
                  <Rss className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                  <p className="text-gray-400 mb-4">Aucune activité récente</p>
                  <p className="text-sm text-gray-500">Ajoutez des amis pour voir leur activité</p>
                </div>
              )}
            </div>
          )}

          {/* My Feed Tab - Mon feed personnel */}
          {activeTab === 'my_feed' && (
            <div className="space-y-6">
              <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
                Mon Feed
              </h1>
              <p className="text-gray-400">Votre historique d'activité</p>

              {myFeed.length > 0 ? (
                <div className="space-y-4">
                  {myFeed.map((activity, index) => (
                    <div key={index} className="card-service rounded-xl p-5">
                      <div className="flex items-center gap-4">
                        <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
                          activity.type === 'review' ? 'bg-[#D4AF37]/20' :
                          activity.type === 'purchase' ? 'bg-green-500/20' :
                          activity.type === 'training' ? 'bg-purple-500/20' :
                          'bg-pink-500/20'
                        }`}>
                          {activity.type === 'review' && <Star className="w-6 h-6 text-[#D4AF37]" />}
                          {activity.type === 'purchase' && <ShoppingCart className="w-6 h-6 text-green-500" />}
                          {activity.type === 'training' && <GraduationCap className="w-6 h-6 text-purple-500" />}
                          {activity.type === 'wishlist' && <Heart className="w-6 h-6 text-pink-500" />}
                        </div>
                        <div className="flex-1">
                          <p className="text-white">
                            <span className="text-gray-400">{activity.action}</span>
                            <span className="font-medium text-[#D4AF37] ml-1">{activity.target}</span>
                          </p>
                          {activity.total && <p className="text-sm text-green-500">{activity.total.toFixed(2)} CHF</p>}
                          {activity.comment && <p className="text-sm text-gray-500 italic mt-1">"{activity.comment}"</p>}
                          <p className="text-xs text-gray-500 mt-1">
                            {new Date(activity.created_at).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' })}
                          </p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="card-service rounded-xl p-12 text-center">
                  <Newspaper className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                  <p className="text-gray-400 mb-4">Aucune activité</p>
                  <p className="text-sm text-gray-500">Commencez à explorer et acheter pour voir votre historique</p>
                </div>
              )}
            </div>
          )}

          {/* Mode de vie Tab */}
          {activeTab === 'mode_vie' && (
            <div className="space-y-6">
              <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
                Mon Mode de Vie
              </h1>
              <p className="text-gray-400">Vos préférences et centres d'intérêt</p>

              {/* Preferences Stats */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="card-service rounded-xl p-5">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-full bg-pink-500/20 flex items-center justify-center">
                      <Heart className="w-6 h-6 text-pink-500" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-white">{lifestyle.wishlist?.length || 0}</p>
                      <p className="text-sm text-gray-400">Articles souhaités</p>
                    </div>
                  </div>
                </div>
                <div className="card-service rounded-xl p-5">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-full bg-[#D4AF37]/20 flex items-center justify-center">
                      <Star className="w-6 h-6 text-[#D4AF37]" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-white">{lifestyle.liked_items?.length || 0}</p>
                      <p className="text-sm text-gray-400">Avis positifs</p>
                    </div>
                  </div>
                </div>
                <div className="card-service rounded-xl p-5">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-full bg-[#0047AB]/20 flex items-center justify-center">
                      <Store className="w-6 h-6 text-[#0047AB]" />
                    </div>
                    <div>
                      <p className="text-2xl font-bold text-white">{lifestyle.personal_providers?.length || 0}</p>
                      <p className="text-sm text-gray-400">Prestataires favoris</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Top Categories */}
              {lifestyle.preferences?.top_categories?.length > 0 && (
                <div className="card-service rounded-xl p-6">
                  <h3 className="text-lg font-semibold text-white mb-4">Vos catégories préférées</h3>
                  <div className="space-y-3">
                    {lifestyle.preferences.top_categories.map((cat, index) => (
                      <div key={index} className="flex items-center justify-between">
                        <span className="text-white">{cat.name}</span>
                        <div className="flex items-center gap-2">
                          <div className="w-32 h-2 bg-white/10 rounded-full overflow-hidden">
                            <div className="h-full bg-gradient-to-r from-[#0047AB] to-[#D4AF37]" style={{ width: `${Math.min(100, cat.count * 20)}%` }} />
                          </div>
                          <span className="text-sm text-gray-400">{cat.count}</span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Top Enterprises */}
              {lifestyle.preferences?.top_enterprises?.length > 0 && (
                <div className="card-service rounded-xl p-6">
                  <h3 className="text-lg font-semibold text-white mb-4">Vos prestataires préférés</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {lifestyle.preferences.top_enterprises.map((ent, index) => (
                      <Link key={index} to={`/entreprise/${ent.id}`} className="flex items-center gap-3 p-3 bg-white/5 rounded-lg hover:bg-white/10 transition-colors">
                        <div className="w-10 h-10 rounded-full bg-[#D4AF37]/20 flex items-center justify-center overflow-hidden">
                          {ent.logo ? <img src={getImageUrl(ent.logo)} alt="" className="w-full h-full object-cover" /> : <Store className="w-5 h-5 text-[#D4AF37]" />}
                        </div>
                        <div className="flex-1">
                          <p className="text-white font-medium">{ent.name}</p>
                          <p className="text-xs text-gray-400">{ent.visits} visites</p>
                        </div>
                        <ChevronRight className="w-5 h-5 text-gray-400" />
                      </Link>
                    ))}
                  </div>
                </div>
              )}

              {/* Wishlist Preview */}
              {lifestyle.wishlist?.length > 0 && (
                <div className="card-service rounded-xl p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-white">Ma liste de souhaits</h3>
                    <button onClick={() => setActiveTab('wishlist')} className="text-sm text-[#0047AB] hover:underline">Voir tout</button>
                  </div>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    {lifestyle.wishlist.slice(0, 4).map((item, index) => (
                      <div key={index} className="bg-white/5 rounded-lg p-3 text-center">
                        <Package className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                        <p className="text-sm text-white truncate">{item.item_name}</p>
                        <p className="text-xs text-[#D4AF37]">{item.item_price?.toFixed(2)} CHF</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Invitations Tab */}
          {activeTab === 'invitations' && (
            <div className="space-y-6">
              <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
                Mes Invitations Prestataires
              </h1>
              <p className="text-gray-400">Offres exclusives des prestataires pour vous</p>

              {invitations.length > 0 ? (
                <div className="space-y-4">
                  {invitations.map((inv) => (
                    <div key={inv.id} className="card-service rounded-xl p-6 border-l-4 border-[#D4AF37]">
                      <div className="flex items-start justify-between">
                        <div className="flex gap-4">
                          <div className="w-14 h-14 rounded-xl bg-[#D4AF37]/20 flex items-center justify-center">
                            {inv.enterprise?.logo ? (
                              <img src={getImageUrl(inv.enterprise.logo)} alt="" className="w-full h-full object-cover rounded-xl" />
                            ) : (
                              <Gift className="w-7 h-7 text-[#D4AF37]" />
                            )}
                          </div>
                          <div>
                            <p className="text-sm text-[#D4AF37] font-medium">{inv.enterprise?.business_name || inv.enterprise_name}</p>
                            <h3 className="text-lg font-semibold text-white">{inv.title}</h3>
                            <p className="text-sm text-gray-400 mt-1">{inv.description}</p>
                            {inv.discount_percent && (
                              <span className="inline-block mt-2 px-3 py-1 bg-green-500/20 text-green-400 text-sm rounded-full">
                                -{inv.discount_percent}% de réduction
                              </span>
                            )}
                            {inv.valid_until && (
                              <p className="text-xs text-gray-500 mt-2">Valable jusqu'au {new Date(inv.valid_until).toLocaleDateString('fr-FR')}</p>
                            )}
                          </div>
                        </div>
                        {inv.status === 'pending' && (
                          <div className="flex gap-2">
                            <button onClick={() => handleRespondToInvitation(inv.id, true)} className="px-4 py-2 bg-[#0047AB] text-white rounded-lg hover:bg-[#2E74D6] text-sm">
                              Accepter
                            </button>
                            <button onClick={() => handleRespondToInvitation(inv.id, false)} className="px-4 py-2 bg-white/10 text-gray-400 rounded-lg hover:bg-white/20 text-sm">
                              Refuser
                            </button>
                          </div>
                        )}
                        {inv.status === 'accepted' && (
                          <span className="px-3 py-1 bg-green-500/20 text-green-400 text-sm rounded-full">Acceptée</span>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="card-service rounded-xl p-12 text-center">
                  <Gift className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                  <p className="text-gray-400 mb-4">Aucune invitation pour le moment</p>
                  <p className="text-sm text-gray-500">Les prestataires peuvent vous envoyer des offres exclusives</p>
                </div>
              )}
            </div>
          )}

          {/* Current Offers Tab */}
          {activeTab === 'offres' && (
            <div className="space-y-6">
              <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
                Mes Offres du Moment
              </h1>
              <p className="text-gray-400">Promotions et offres spéciales disponibles</p>

              {currentOffers.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {currentOffers.map((offer) => (
                    <div key={offer.id} className="card-service rounded-xl overflow-hidden group">
                      <div className="h-32 bg-gradient-to-br from-[#0047AB]/30 to-[#D4AF37]/30 relative">
                        {offer.discount_percent && (
                          <div className="absolute top-3 right-3 px-3 py-1 bg-red-500 text-white text-sm font-bold rounded-full">
                            -{offer.discount_percent}%
                          </div>
                        )}
                        <div className="absolute bottom-3 left-3">
                          <p className="text-white font-bold text-lg">{offer.title}</p>
                        </div>
                      </div>
                      <div className="p-4">
                        <div className="flex items-center gap-2 mb-2">
                          <Store className="w-4 h-4 text-[#D4AF37]" />
                          <span className="text-sm text-[#D4AF37]">{offer.enterprise?.business_name}</span>
                        </div>
                        <p className="text-sm text-gray-400 mb-3">{offer.description}</p>
                        {offer.valid_until && (
                          <p className="text-xs text-gray-500">Expire le {new Date(offer.valid_until).toLocaleDateString('fr-FR')}</p>
                        )}
                        <Link to={`/entreprise/${offer.enterprise_id}`} className="mt-3 btn-primary w-full text-center block text-sm py-2">
                          Voir l'offre
                        </Link>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="card-service rounded-xl p-12 text-center">
                  <Target className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                  <p className="text-gray-400 mb-4">Aucune offre disponible</p>
                  <p className="text-sm text-gray-500">Revenez bientôt pour découvrir de nouvelles promotions</p>
                </div>
              )}
            </div>
          )}

          {/* Guests Tab */}
          {activeTab === 'guests' && (
            <div className="space-y-6">
              <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
                Mes Guests du Moment
              </h1>
              <p className="text-gray-400">Profils que vous suivez</p>

              {favoriteGuests.length > 0 ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {favoriteGuests.map((guest) => (
                    <div key={guest.id} className="card-service rounded-xl p-5 group">
                      <div className="flex items-center gap-4">
                        <div className="w-14 h-14 rounded-full bg-gradient-to-br from-[#0047AB] to-[#D4AF37] flex items-center justify-center overflow-hidden">
                          {guest.guest_avatar || guest.current_info?.avatar ? (
                            <img src={getImageUrl(guest.guest_avatar || guest.current_info?.avatar)} alt="" className="w-full h-full object-cover" />
                          ) : (
                            <User className="w-7 h-7 text-white" />
                          )}
                        </div>
                        <div className="flex-1">
                          <p className="text-white font-semibold">{guest.guest_name || `${guest.current_info?.first_name} ${guest.current_info?.last_name}`}</p>
                          {guest.current_info?.city && (
                            <p className="text-sm text-gray-400 flex items-center gap-1">
                              <MapPin className="w-3 h-3" /> {guest.current_info.city}
                            </p>
                          )}
                        </div>
                        <button onClick={() => handleRemoveGuest(guest.id)} className="p-2 text-red-400 hover:bg-red-500/20 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity">
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                      {guest.notes && (
                        <p className="text-sm text-gray-500 mt-3 italic">"{guest.notes}"</p>
                      )}
                    </div>
                  ))}
                </div>
              ) : (
                <div className="card-service rounded-xl p-12 text-center">
                  <Star className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                  <p className="text-gray-400 mb-4">Aucun guest favori</p>
                  <p className="text-sm text-gray-500">Ajoutez des profils que vous appréciez</p>
                </div>
              )}
            </div>
          )}

          {/* Investments Tab */}
          {activeTab === 'investments' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
                  Mes Investissements
                </h1>
                <button onClick={() => setShowAddInvestment(true)} className="btn-primary flex items-center gap-2">
                  <Plus className="w-4 h-4" />
                  Ajouter
                </button>
              </div>

              {/* Stats */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <div className="card-service rounded-xl p-5">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-full bg-[#0047AB]/20 flex items-center justify-center">
                      <DollarSign className="w-6 h-6 text-[#0047AB]" />
                    </div>
                    <div>
                      <p className="text-xl font-bold text-white">{investments.statistics?.total_invested?.toFixed(0) || 0} CHF</p>
                      <p className="text-sm text-gray-400">Total investi</p>
                    </div>
                  </div>
                </div>
                <div className="card-service rounded-xl p-5">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-full bg-green-500/20 flex items-center justify-center">
                      <TrendingUp className="w-6 h-6 text-green-500" />
                    </div>
                    <div>
                      <p className="text-xl font-bold text-green-500">{investments.statistics?.total_current_value?.toFixed(0) || 0} CHF</p>
                      <p className="text-sm text-gray-400">Valeur actuelle</p>
                    </div>
                  </div>
                </div>
                <div className="card-service rounded-xl p-5">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-full bg-[#D4AF37]/20 flex items-center justify-center">
                      <PieChart className="w-6 h-6 text-[#D4AF37]" />
                    </div>
                    <div>
                      <p className={`text-xl font-bold ${investments.statistics?.total_roi >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                        {investments.statistics?.total_roi >= 0 ? '+' : ''}{investments.statistics?.total_roi?.toFixed(0) || 0} CHF
                      </p>
                      <p className="text-sm text-gray-400">ROI Total</p>
                    </div>
                  </div>
                </div>
                <div className="card-service rounded-xl p-5">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-full bg-purple-500/20 flex items-center justify-center">
                      <Home className="w-6 h-6 text-purple-500" />
                    </div>
                    <div>
                      <p className="text-xl font-bold text-white">{investments.statistics?.investment_count || 0}</p>
                      <p className="text-sm text-gray-400">Investissements</p>
                    </div>
                  </div>
                </div>
              </div>

              {/* Investments List */}
              {investments.investments?.length > 0 ? (
                <div className="space-y-4">
                  {investments.investments.map((inv) => (
                    <div key={inv.id} className="card-service rounded-xl p-5 group">
                      <div className="flex items-start justify-between">
                        <div className="flex gap-4">
                          <div className={`w-12 h-12 rounded-xl flex items-center justify-center ${
                            inv.investment_type === 'real_estate' ? 'bg-purple-500/20' :
                            inv.investment_type === 'business' ? 'bg-blue-500/20' : 'bg-gray-500/20'
                          }`}>
                            {inv.investment_type === 'real_estate' ? <Home className="w-6 h-6 text-purple-500" /> :
                             inv.investment_type === 'business' ? <Briefcase className="w-6 h-6 text-blue-500" /> :
                             <PieChart className="w-6 h-6 text-gray-500" />}
                          </div>
                          <div>
                            <h3 className="text-white font-semibold">{inv.title}</h3>
                            <p className="text-sm text-gray-400">{inv.description}</p>
                            {inv.property_address && (
                              <p className="text-sm text-gray-500 flex items-center gap-1 mt-1">
                                <MapPin className="w-3 h-3" /> {inv.property_address}
                              </p>
                            )}
                            <p className="text-xs text-gray-500 mt-2">
                              Investi le {new Date(inv.investment_date).toLocaleDateString('fr-FR')}
                            </p>
                          </div>
                        </div>
                        <div className="text-right">
                          <p className="text-white font-semibold">{inv.amount_invested?.toFixed(0)} CHF</p>
                          {inv.current_value && (
                            <p className={`text-sm ${inv.current_value >= inv.amount_invested ? 'text-green-500' : 'text-red-500'}`}>
                              → {inv.current_value.toFixed(0)} CHF
                            </p>
                          )}
                          {inv.roi_percent && (
                            <p className={`text-sm ${inv.roi_percent >= 0 ? 'text-green-500' : 'text-red-500'}`}>
                              {inv.roi_percent >= 0 ? '+' : ''}{inv.roi_percent}%
                            </p>
                          )}
                          <span className={`inline-block mt-2 px-2 py-0.5 rounded-full text-xs ${
                            inv.status === 'active' ? 'bg-green-500/20 text-green-400' :
                            inv.status === 'sold' ? 'bg-gray-500/20 text-gray-400' :
                            'bg-yellow-500/20 text-yellow-400'
                          }`}>
                            {inv.status === 'active' ? 'Actif' : inv.status === 'sold' ? 'Vendu' : 'En attente'}
                          </span>
                        </div>
                        <button onClick={() => handleDeleteInvestment(inv.id)} className="p-2 text-red-400 hover:bg-red-500/20 rounded-lg opacity-0 group-hover:opacity-100 transition-opacity ml-2">
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="card-service rounded-xl p-12 text-center">
                  <PieChart className="w-16 h-16 text-gray-600 mx-auto mb-4" />
                  <p className="text-gray-400 mb-4">Aucun investissement</p>
                  <button onClick={() => setShowAddInvestment(true)} className="btn-secondary">
                    Ajouter un investissement
                  </button>
                </div>
              )}

              {/* Add Investment Modal */}
              {showAddInvestment && (
                <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
                  <div className="card-service rounded-xl p-6 w-full max-w-lg max-h-[90vh] overflow-y-auto">
                    <h3 className="text-lg font-semibold text-white mb-6">Nouvel Investissement</h3>
                    <div className="space-y-4">
                      <div>
                        <label className="block text-sm text-gray-400 mb-2">Type *</label>
                        <select value={investmentForm.investment_type} onChange={(e) => setInvestmentForm({...investmentForm, investment_type: e.target.value})} className="input-dark w-full">
                          <option value="real_estate">Immobilier</option>
                          <option value="business">Business</option>
                          <option value="other">Autre</option>
                        </select>
                      </div>
                      <div>
                        <label className="block text-sm text-gray-400 mb-2">Titre *</label>
                        <input type="text" value={investmentForm.title} onChange={(e) => setInvestmentForm({...investmentForm, title: e.target.value})} className="input-dark w-full" placeholder="Ex: Appartement Lausanne" />
                      </div>
                      <div>
                        <label className="block text-sm text-gray-400 mb-2">Description</label>
                        <textarea value={investmentForm.description} onChange={(e) => setInvestmentForm({...investmentForm, description: e.target.value})} className="input-dark w-full h-20 resize-none" placeholder="Détails..." />
                      </div>
                      {investmentForm.investment_type === 'real_estate' && (
                        <div>
                          <label className="block text-sm text-gray-400 mb-2">Adresse du bien</label>
                          <input type="text" value={investmentForm.property_address} onChange={(e) => setInvestmentForm({...investmentForm, property_address: e.target.value})} className="input-dark w-full" placeholder="Rue, Ville" />
                        </div>
                      )}
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm text-gray-400 mb-2">Montant investi (CHF) *</label>
                          <input type="number" value={investmentForm.amount_invested} onChange={(e) => setInvestmentForm({...investmentForm, amount_invested: e.target.value})} className="input-dark w-full" placeholder="50000" />
                        </div>
                        <div>
                          <label className="block text-sm text-gray-400 mb-2">Valeur actuelle (CHF)</label>
                          <input type="number" value={investmentForm.current_value} onChange={(e) => setInvestmentForm({...investmentForm, current_value: e.target.value})} className="input-dark w-full" placeholder="55000" />
                        </div>
                      </div>
                      <div className="grid grid-cols-2 gap-4">
                        <div>
                          <label className="block text-sm text-gray-400 mb-2">Date d'investissement *</label>
                          <input type="date" value={investmentForm.investment_date} onChange={(e) => setInvestmentForm({...investmentForm, investment_date: e.target.value})} className="input-dark w-full" />
                        </div>
                        <div>
                          <label className="block text-sm text-gray-400 mb-2">ROI (%)</label>
                          <input type="number" value={investmentForm.roi_percent} onChange={(e) => setInvestmentForm({...investmentForm, roi_percent: e.target.value})} className="input-dark w-full" placeholder="10" />
                        </div>
                      </div>
                      <div>
                        <label className="block text-sm text-gray-400 mb-2">Statut</label>
                        <select value={investmentForm.status} onChange={(e) => setInvestmentForm({...investmentForm, status: e.target.value})} className="input-dark w-full">
                          <option value="active">Actif</option>
                          <option value="sold">Vendu</option>
                          <option value="pending">En attente</option>
                        </select>
                      </div>
                    </div>
                    <div className="flex gap-3 mt-6">
                      <button onClick={() => setShowAddInvestment(false)} className="btn-secondary flex-1">Annuler</button>
                      <button onClick={handleAddInvestment} className="btn-primary flex-1">Ajouter</button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Premium Tab */}
          {activeTab === 'premium' && (
            <div className="space-y-6">
              <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
                Mon Premium
              </h1>

              {/* Current Status */}
              <div className={`card-service rounded-xl p-6 border-2 ${
                premiumData.current_plan === 'vip' ? 'border-[#D4AF37]' :
                premiumData.current_plan === 'premium' ? 'border-[#0047AB]' : 'border-white/10'
              }`}>
                <div className="flex items-center gap-4">
                  <div className={`w-16 h-16 rounded-full flex items-center justify-center ${
                    premiumData.current_plan === 'vip' ? 'bg-[#D4AF37]/20' :
                    premiumData.current_plan === 'premium' ? 'bg-[#0047AB]/20' : 'bg-white/10'
                  }`}>
                    <Crown className={`w-8 h-8 ${
                      premiumData.current_plan === 'vip' ? 'text-[#D4AF37]' :
                      premiumData.current_plan === 'premium' ? 'text-[#0047AB]' : 'text-gray-500'
                    }`} />
                  </div>
                  <div>
                    <p className="text-sm text-gray-400">Votre abonnement actuel</p>
                    <p className={`text-2xl font-bold ${
                      premiumData.current_plan === 'vip' ? 'text-[#D4AF37]' :
                      premiumData.current_plan === 'premium' ? 'text-[#0047AB]' : 'text-white'
                    }`}>
                      {premiumData.current_plan === 'vip' ? 'VIP' :
                       premiumData.current_plan === 'premium' ? 'Premium' : 'Gratuit'}
                    </p>
                    <p className="text-sm text-gray-500 mt-1">{premiumData.cashback_rate}% de cashback</p>
                  </div>
                </div>
              </div>

              {/* Plans */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {/* Free */}
                <div className={`card-service rounded-xl p-6 ${premiumData.current_plan === 'free' ? 'border-2 border-white/30' : ''}`}>
                  <h3 className="text-lg font-semibold text-white mb-2">Gratuit</h3>
                  <p className="text-3xl font-bold text-white mb-4">0 <span className="text-sm font-normal text-gray-400">CHF/mois</span></p>
                  <ul className="space-y-2 text-sm text-gray-400 mb-6">
                    {premiumData.benefits?.free?.features?.map((f, i) => (
                      <li key={i} className="flex items-center gap-2">
                        <CheckCircle className="w-4 h-4 text-green-500" />
                        {f}
                      </li>
                    ))}
                  </ul>
                  {premiumData.current_plan === 'free' && (
                    <button disabled className="w-full py-2 bg-white/10 text-gray-400 rounded-lg">Plan actuel</button>
                  )}
                </div>

                {/* Premium */}
                <div className={`card-service rounded-xl p-6 border-2 ${premiumData.current_plan === 'premium' ? 'border-[#0047AB]' : 'border-[#0047AB]/30'} relative`}>
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 bg-[#0047AB] text-white text-xs rounded-full">
                    Populaire
                  </div>
                  <h3 className="text-lg font-semibold text-[#0047AB] mb-2">Premium</h3>
                  <p className="text-3xl font-bold text-white mb-4">29.99 <span className="text-sm font-normal text-gray-400">CHF/mois</span></p>
                  <ul className="space-y-2 text-sm text-gray-400 mb-6">
                    {premiumData.benefits?.premium?.features?.map((f, i) => (
                      <li key={i} className="flex items-center gap-2">
                        <CheckCircle className="w-4 h-4 text-[#0047AB]" />
                        {f}
                      </li>
                    ))}
                  </ul>
                  {premiumData.current_plan === 'premium' ? (
                    <button disabled className="w-full py-2 bg-[#0047AB]/20 text-[#0047AB] rounded-lg">Plan actuel</button>
                  ) : (
                    <button onClick={() => handleUpgradePremium('premium')} className="w-full py-2 bg-[#0047AB] text-white rounded-lg hover:bg-[#2E74D6] transition-colors">
                      Passer Premium
                    </button>
                  )}
                </div>

                {/* VIP */}
                <div className={`card-service rounded-xl p-6 border-2 ${premiumData.current_plan === 'vip' ? 'border-[#D4AF37]' : 'border-[#D4AF37]/30'} relative`}>
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 bg-[#D4AF37] text-black text-xs rounded-full font-semibold">
                    VIP
                  </div>
                  <h3 className="text-lg font-semibold text-[#D4AF37] mb-2">VIP</h3>
                  <p className="text-3xl font-bold text-white mb-4">69.99 <span className="text-sm font-normal text-gray-400">CHF/mois</span></p>
                  <ul className="space-y-2 text-sm text-gray-400 mb-6">
                    {premiumData.benefits?.vip?.features?.map((f, i) => (
                      <li key={i} className="flex items-center gap-2">
                        <CheckCircle className="w-4 h-4 text-[#D4AF37]" />
                        {f}
                      </li>
                    ))}
                  </ul>
                  {premiumData.current_plan === 'vip' ? (
                    <button disabled className="w-full py-2 bg-[#D4AF37]/20 text-[#D4AF37] rounded-lg">Plan actuel</button>
                  ) : (
                    <button onClick={() => handleUpgradePremium('vip')} className="w-full py-2 bg-[#D4AF37] text-black rounded-lg hover:bg-[#E5C048] transition-colors font-semibold">
                      Passer VIP
                    </button>
                  )}
                </div>
              </div>

              {/* Cancel subscription option for paid plans */}
              {premiumData.current_plan !== 'free' && (
                <div className="card-service rounded-xl p-6 mt-6">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-white font-semibold">Gérer l'abonnement</h3>
                      <p className="text-sm text-gray-400">
                        Prochain paiement: {premiumData.subscription?.next_billing ? 
                          new Date(premiumData.subscription.next_billing).toLocaleDateString('fr-FR') : 
                          'Non défini'}
                      </p>
                    </div>
                    <button 
                      onClick={handleCancelPremium}
                      className="px-4 py-2 bg-red-500/20 text-red-400 rounded-lg hover:bg-red-500/30 transition-colors text-sm"
                    >
                      Annuler l'abonnement
                    </button>
                  </div>
                </div>
              )}

              {/* Stripe security badge */}
              <div className="mt-6 flex items-center justify-center gap-2 text-sm text-gray-500">
                <CheckCircle className="w-4 h-4 text-green-500" />
                <span>Paiements sécurisés par Stripe</span>
              </div>
            </div>
          )}

          {/* Panier Tab */}
          {activeTab === 'panier' && (
            <div className="space-y-6">
              <div className="flex items-center justify-between">
                <h1 className="text-2xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
                  Mon Panier
                </h1>
                {cartItems.length > 0 && (
                  <span className="px-3 py-1 bg-[#0047AB]/20 text-[#0047AB] rounded-full text-sm font-medium">
                    {cartItems.length} article{cartItems.length > 1 ? 's' : ''}
                  </span>
                )}
              </div>

              {cartItems.length === 0 ? (
                <div className="card-service rounded-xl p-12 text-center">
                  <div className="w-20 h-20 bg-white/5 rounded-full flex items-center justify-center mx-auto mb-6">
                    <ShoppingCart className="w-10 h-10 text-gray-500" />
                  </div>
                  <h2 className="text-xl font-bold text-white mb-2">Votre panier est vide</h2>
                  <p className="text-gray-400 mb-6">Découvrez nos services et produits pour commencer vos achats</p>
                  <div className="flex gap-4 justify-center">
                    <Link to="/services" className="btn-primary">
                      Voir les services
                    </Link>
                    <Link to="/produits" className="btn-secondary">
                      Voir les produits
                    </Link>
                  </div>
                </div>
              ) : (
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                  {/* Items List */}
                  <div className="lg:col-span-2 space-y-4">
                    {getItemsByEnterprise().map((group) => (
                      <div key={group.enterprise_id} className="card-service rounded-xl p-6">
                        <div className="flex items-center gap-3 mb-4 pb-4 border-b border-white/10">
                          <Building2 className="w-5 h-5 text-[#D4AF37]" />
                          <span className="text-white font-medium">{group.enterprise_name}</span>
                        </div>
                        <div className="space-y-4">
                          {group.items.map((item) => (
                            <div key={item.id} className="flex items-center gap-4 p-4 bg-white/5 rounded-xl">
                              {item.image && (
                                <img 
                                  src={item.image.startsWith('http') ? item.image : `${process.env.REACT_APP_BACKEND_URL}${item.image}`}
                                  alt={item.name}
                                  className="w-20 h-20 rounded-lg object-cover"
                                />
                              )}
                              <div className="flex-1">
                                <h3 className="text-white font-medium">{item.name}</h3>
                                <p className="text-[#D4AF37] font-semibold">{item.price.toFixed(2)} CHF</p>
                              </div>
                              <div className="flex items-center gap-2">
                                <button
                                  onClick={() => updateCartQuantity(item.id, Math.max(1, item.quantity - 1))}
                                  className="p-1 bg-white/10 rounded hover:bg-white/20 transition-colors"
                                >
                                  <Minus className="w-4 h-4 text-white" />
                                </button>
                                <span className="w-8 text-center text-white">{item.quantity}</span>
                                <button
                                  onClick={() => updateCartQuantity(item.id, item.quantity + 1)}
                                  className="p-1 bg-white/10 rounded hover:bg-white/20 transition-colors"
                                >
                                  <Plus className="w-4 h-4 text-white" />
                                </button>
                              </div>
                              <button
                                onClick={() => removeCartItem(item.id)}
                                className="p-2 text-red-400 hover:bg-red-500/20 rounded-lg transition-colors"
                              >
                                <Trash2 className="w-5 h-5" />
                              </button>
                            </div>
                          ))}
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Order Summary */}
                  <div className="lg:col-span-1">
                    <div className="card-service rounded-xl p-6 sticky top-24">
                      <h3 className="text-lg font-bold text-white mb-4">Résumé</h3>
                      <div className="space-y-3 mb-6">
                        <div className="flex justify-between text-gray-400">
                          <span>Sous-total</span>
                          <span>{getCartTotal().toFixed(2)} CHF</span>
                        </div>
                        <div className="flex justify-between text-gray-400">
                          <span>Frais de livraison</span>
                          <span>À calculer</span>
                        </div>
                        <div className="border-t border-white/10 pt-3">
                          <div className="flex justify-between text-white font-bold text-lg">
                            <span>Total</span>
                            <span>{getCartTotal().toFixed(2)} CHF</span>
                          </div>
                        </div>
                      </div>
                      <Link 
                        to="/cart" 
                        className="w-full btn-primary flex items-center justify-center gap-2"
                      >
                        <CreditCard className="w-4 h-4" />
                        Passer commande
                      </Link>
                      <p className="text-xs text-gray-500 text-center mt-4">
                        Vous serez redirigé vers la page de paiement sécurisé
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}

          {/* Default placeholder for other tabs */}
          {!['overview', 'profile', 'contacts', 'cartes', 'documents', 'messages', 'particulier', 'orders', 'cashback', 'settings', 'formations', 'agenda', 'finances', 'donations', 'wishlist', 'suggestions', 'prestataires', 'demandes', 'feed', 'my_feed', 'mode_vie', 'invitations', 'offres', 'guests', 'investments', 'premium', 'panier'].includes(activeTab) && (
            <div className="card-service rounded-xl p-12 text-center">
              <div className="w-16 h-16 bg-white/5 rounded-full flex items-center justify-center mx-auto mb-4">
                <Clock className="w-8 h-8 text-gray-500" />
              </div>
              <h2 className="text-xl font-bold text-white mb-2">Section en cours de développement</h2>
              <p className="text-gray-400">Cette fonctionnalité sera bientôt disponible.</p>
            </div>
          )}
        </main>

      {/* Training Review Modal */}
      {showReviewModal && reviewingTraining && (
        <div className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
          <div className="bg-[#0F0F0F] rounded-2xl p-6 w-full max-w-md border border-white/10">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-white">Votre avis</h2>
              <button onClick={() => setShowReviewModal(false)} className="text-gray-400 hover:text-white">
                <X className="w-6 h-6" />
              </button>
            </div>
            
            <div className="mb-6">
              <p className="text-gray-400 text-sm mb-2">Formation</p>
              <p className="text-white font-medium">{reviewingTraining.training_title}</p>
              <p className="text-sm text-[#D4AF37]">{reviewingTraining.enterprise_name}</p>
            </div>
            
            {/* Star Rating */}
            <div className="mb-6">
              <p className="text-gray-400 text-sm mb-3">Note</p>
              <div className="flex gap-2">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    onClick={() => setReviewForm({...reviewForm, rating: star})}
                    className="transition-transform hover:scale-110"
                  >
                    <Star 
                      className={`w-8 h-8 ${star <= reviewForm.rating ? 'text-yellow-400 fill-yellow-400' : 'text-gray-600'}`} 
                    />
                  </button>
                ))}
              </div>
            </div>
            
            {/* Comment */}
            <div className="mb-6">
              <label className="block text-gray-400 text-sm mb-2">Commentaire (optionnel)</label>
              <textarea
                value={reviewForm.comment}
                onChange={(e) => setReviewForm({...reviewForm, comment: e.target.value})}
                placeholder="Partagez votre expérience..."
                className="input-dark w-full h-24 resize-none"
              />
            </div>
            
            <div className="flex gap-3">
              <button
                onClick={() => setShowReviewModal(false)}
                className="flex-1 py-3 border border-white/20 rounded-xl text-white hover:bg-white/5"
              >
                Annuler
              </button>
              <button
                onClick={handleSubmitReview}
                disabled={submittingReview}
                className="flex-1 py-3 bg-[#0047AB] text-white rounded-xl hover:bg-[#0047AB]/80 disabled:opacity-50 flex items-center justify-center gap-2"
              >
                {submittingReview ? (
                  <>
                    <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                    Envoi...
                  </>
                ) : (
                  <>
                    <Send className="w-4 h-4" />
                    Envoyer
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ClientDashboard;
