import axios from 'axios';

// Fallback to production URL if env variable is not set
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'https://titelliv2back.onrender.com';
const API = `${BACKEND_URL}/api`;

const getAuthHeaders = () => {
  const token = localStorage.getItem('titelli_token');
  return token ? { Authorization: `Bearer ${token}` } : {};
};

// Helper function to get full image URL
export const getImageUrl = (path) => {
  if (!path) return null;
  if (path.startsWith('http')) return path;
  if (path.startsWith('/api/uploads')) return `${BACKEND_URL}${path}`;
  return path;
};

// Upload
export const uploadAPI = {
  uploadImage: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return axios.post(`${API}/upload/image`, formData, {
      headers: {
        ...getAuthHeaders(),
        'Content-Type': 'multipart/form-data',
      },
    });
  },
  uploadBase64: (imageData, filename) => axios.post(`${API}/upload/image-base64`, { image: imageData, filename }, { headers: getAuthHeaders() }),
};

// Auth
export const authAPI = {
  login: (data) => axios.post(`${API}/auth/login`, data),
  register: (data) => axios.post(`${API}/auth/register`, data),
  getMe: () => axios.get(`${API}/auth/me`, { headers: getAuthHeaders() }),
};

// Enterprises
export const enterpriseAPI = {
  list: (params) => axios.get(`${API}/enterprises`, { params: { limit: 500, ...params } }),
  get: (id) => axios.get(`${API}/enterprises/${id}`),
  getById: (id) => axios.get(`${API}/enterprises/${id}`),
  create: (data) => axios.post(`${API}/enterprises`, data, { headers: getAuthHeaders() }),
  update: (id, data) => axios.put(`${API}/enterprises/${id}`, data, { headers: getAuthHeaders() }),
};

// Services & Products
export const servicesProductsAPI = {
  list: (params) => axios.get(`${API}/services-products`, { params }),
  get: (id) => axios.get(`${API}/services-products/${id}`),
  create: (data) => axios.post(`${API}/services-products`, data, { headers: getAuthHeaders() }),
  update: (id, data) => axios.put(`${API}/services-products/${id}`, data, { headers: getAuthHeaders() }),
  delete: (id) => axios.delete(`${API}/services-products/${id}`, { headers: getAuthHeaders() }),
};


// Reviews
export const reviewAPI = {
  list: (enterpriseId) => axios.get(`${API}/reviews/${enterpriseId}`),
  create: (data) => axios.post(`${API}/reviews`, data, { headers: getAuthHeaders() }),
  getByEnterprise: (enterpriseId) => axios.get(`${API}/reviews/${enterpriseId}`),
};

// Orders
export const orderAPI = {
  list: () => axios.get(`${API}/orders`, { headers: getAuthHeaders() }),
  create: (data) => axios.post(`${API}/orders`, data, { headers: getAuthHeaders() }),
  updateStatus: (id, status) => axios.put(`${API}/orders/${id}/status`, null, { 
    params: { status }, 
    headers: getAuthHeaders() 
  }),
};

// Categories
export const categoryAPI = {
  products: () => axios.get(`${API}/categories/products`),
  services: () => axios.get(`${API}/categories/services`),
};

// Featured
export const featuredAPI = {
  tendances: () => axios.get(`${API}/featured/tendances`),
  guests: () => axios.get(`${API}/featured/guests`),
  offres: () => axios.get(`${API}/featured/offres`),
  premium: () => axios.get(`${API}/featured/premium`),
};

// Payments
export const paymentAPI = {
  createCheckout: (packageType, amount) => {
    const params = { package_type: packageType };
    if (amount) params.amount = amount;
    return axios.post(`${API}/payments/checkout`, null, { 
      params, 
      headers: getAuthHeaders() 
    });
  },
  getStatus: (sessionId) => axios.get(`${API}/payments/status/${sessionId}`),
};

// Admin
export const adminAPI = {
  stats: () => axios.get(`${API}/admin/stats`, { headers: getAuthHeaders() }),
  users: (params) => axios.get(`${API}/admin/users`, { params, headers: getAuthHeaders() }),
  verifyUser: (userId, isCertified, isLabeled) => axios.put(
    `${API}/admin/users/${userId}/verify`, 
    null,
    { params: { is_certified: isCertified, is_labeled: isLabeled }, headers: getAuthHeaders() }
  ),
  // Withdrawal management
  withdrawals: (status = null, limit = 50, skip = 0) => axios.get(`${API}/admin/withdrawals`, { 
    params: { status, limit, skip }, 
    headers: getAuthHeaders() 
  }),
  withdrawalDetail: (withdrawalId) => axios.get(`${API}/admin/withdrawals/${withdrawalId}`, { headers: getAuthHeaders() }),
  updateWithdrawalStatus: (withdrawalId, newStatus, adminNote = null) => axios.put(
    `${API}/admin/withdrawals/${withdrawalId}/status`,
    null,
    { params: { new_status: newStatus, admin_note: adminNote }, headers: getAuthHeaders() }
  ),
  exportWithdrawalsCSV: (status = null, startDate = null, endDate = null) => {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    return `${API}/admin/withdrawals/export?${params.toString()}`;
  },
  // Accounting / Comptabilité
  accountingSummary: (startDate = null, endDate = null) => axios.get(`${API}/admin/accounting/summary`, {
    params: { start_date: startDate, end_date: endDate },
    headers: getAuthHeaders()
  }),
  accountingTransactions: (type = null, startDate = null, endDate = null, limit = 100, skip = 0) => axios.get(`${API}/admin/accounting/transactions`, {
    params: { transaction_type: type, start_date: startDate, end_date: endDate, limit, skip },
    headers: getAuthHeaders()
  }),
  exportAccountingExcel: (startDate = null, endDate = null) => {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    return `${API}/admin/accounting/export/excel?${params.toString()}`;
  },
  exportAccountingPDF: (startDate = null, endDate = null) => {
    const params = new URLSearchParams();
    if (startDate) params.append('start_date', startDate);
    if (endDate) params.append('end_date', endDate);
    return `${API}/admin/accounting/export/pdf?${params.toString()}`;
  },
};

// Cashback
export const cashbackAPI = {
  balance: () => axios.get(`${API}/cashback/balance`, { headers: getAuthHeaders() }),
  history: () => axios.get(`${API}/cashback/history`, { headers: getAuthHeaders() }),
  use: (amount, orderId = null) => axios.post(`${API}/cashback/use`, null, { 
    params: { amount, order_id: orderId }, 
    headers: getAuthHeaders() 
  }),
  // Withdrawal endpoints
  withdrawalInfo: () => axios.get(`${API}/cashback/withdrawal-info`, { headers: getAuthHeaders() }),
  withdraw: (amount = null) => axios.post(`${API}/cashback/withdraw`, { amount }, { headers: getAuthHeaders() }),
  withdrawalHistory: () => axios.get(`${API}/cashback/withdrawals`, { headers: getAuthHeaders() }),
};

// ============ CLIENT DASHBOARD APIs ============

// Client Agenda
export const clientAgendaAPI = {
  list: (startDate, endDate) => axios.get(`${API}/client/agenda`, { 
    params: { start_date: startDate, end_date: endDate },
    headers: getAuthHeaders() 
  }),
  create: (data) => axios.post(`${API}/client/agenda`, data, { headers: getAuthHeaders() }),
  update: (id, data) => axios.put(`${API}/client/agenda/${id}`, data, { headers: getAuthHeaders() }),
  delete: (id) => axios.delete(`${API}/client/agenda/${id}`, { headers: getAuthHeaders() }),
};

// Client Finances
export const clientFinancesAPI = {
  getStats: () => axios.get(`${API}/client/finances`, { headers: getAuthHeaders() }),
};

// Client Donations
export const clientDonationsAPI = {
  list: () => axios.get(`${API}/client/donations`, { headers: getAuthHeaders() }),
  create: (data) => axios.post(`${API}/client/donations`, data, { headers: getAuthHeaders() }),
};

// Client Wishlist
export const wishlistAPI = {
  list: () => axios.get(`${API}/client/wishlist`, { headers: getAuthHeaders() }),
  add: (data) => axios.post(`${API}/client/wishlist`, data, { headers: getAuthHeaders() }),
  remove: (itemId) => axios.delete(`${API}/client/wishlist/${itemId}`, { headers: getAuthHeaders() }),
  check: (itemId) => axios.get(`${API}/client/wishlist/check/${itemId}`, { headers: getAuthHeaders() }),
};

// Client Suggestions from Friends
export const clientSuggestionsAPI = {
  fromFriends: () => axios.get(`${API}/client/suggestions/from-friends`, { headers: getAuthHeaders() }),
};

// Client Personal Providers
export const clientProvidersAPI = {
  list: () => axios.get(`${API}/client/providers`, { headers: getAuthHeaders() }),
  add: (data) => axios.post(`${API}/client/providers`, data, { headers: getAuthHeaders() }),
  remove: (providerId) => axios.delete(`${API}/client/providers/${providerId}`, { headers: getAuthHeaders() }),
};

// Activity Feed
export const activityFeedAPI = {
  getFeed: (limit = 50) => axios.get(`${API}/client/activity-feed`, { params: { limit }, headers: getAuthHeaders() }),
  getMyFeed: (limit = 50) => axios.get(`${API}/client/my-feed`, { params: { limit }, headers: getAuthHeaders() }),
};

// Client Lifestyle
export const lifestyleAPI = {
  get: () => axios.get(`${API}/client/lifestyle`, { headers: getAuthHeaders() }),
};

// Client Invitations
export const clientInvitationsAPI = {
  list: () => axios.get(`${API}/client/invitations`, { headers: getAuthHeaders() }),
  respond: (invitationId, accepted) => axios.put(`${API}/client/invitations/${invitationId}/respond`, null, { 
    params: { accepted }, 
    headers: getAuthHeaders() 
  }),
};

// Enterprise Invitations to Clients
export const enterpriseInvitationsAPI = {
  list: () => axios.get(`${API}/enterprise/invitations`, { headers: getAuthHeaders() }),
  create: (data) => axios.post(`${API}/enterprise/invitations`, data, { headers: getAuthHeaders() }),
  toggle: (id) => axios.put(`${API}/enterprise/invitations/${id}/toggle`, null, { headers: getAuthHeaders() }),
  delete: (id) => axios.delete(`${API}/enterprise/invitations/${id}`, { headers: getAuthHeaders() }),
};

// Current Offers/Promotions
export const currentOffersAPI = {
  list: () => axios.get(`${API}/client/current-offers`, { headers: getAuthHeaders() }),
};

// Client Promotions (Enterprise creates)
export const promotionsAPI = {
  create: (data) => axios.post(`${API}/enterprise/promotions`, null, { params: data, headers: getAuthHeaders() }),
};

// Favorite Guests
export const guestsAPI = {
  list: () => axios.get(`${API}/client/guests`, { headers: getAuthHeaders() }),
  add: (data) => axios.post(`${API}/client/guests`, data, { headers: getAuthHeaders() }),
  remove: (guestId) => axios.delete(`${API}/client/guests/${guestId}`, { headers: getAuthHeaders() }),
};

// Client Investments
export const clientInvestmentsAPI = {
  list: () => axios.get(`${API}/client/investments`, { headers: getAuthHeaders() }),
  create: (data) => axios.post(`${API}/client/investments`, data, { headers: getAuthHeaders() }),
  update: (id, data) => axios.put(`${API}/client/investments/${id}`, data, { headers: getAuthHeaders() }),
  delete: (id) => axios.delete(`${API}/client/investments/${id}`, { headers: getAuthHeaders() }),
};

// Client Premium
export const premiumAPI = {
  getStatus: () => axios.get(`${API}/client/premium`, { headers: getAuthHeaders() }),
  checkout: (plan) => axios.post(`${API}/client/premium/checkout`, null, { params: { plan }, headers: getAuthHeaders() }),
  confirm: (sessionId) => axios.post(`${API}/client/premium/confirm`, null, { params: { session_id: sessionId }, headers: getAuthHeaders() }),
  cancel: () => axios.post(`${API}/client/premium/cancel`, null, { headers: getAuthHeaders() }),
  history: () => axios.get(`${API}/client/premium/history`, { headers: getAuthHeaders() }),
};

// ============ ENTERPRISE MANAGEMENT APIs ============

// Offers/Promotions
export const offersAPI = {
  list: () => axios.get(`${API}/enterprise/offers`, { headers: getAuthHeaders() }),
  create: (data) => axios.post(`${API}/enterprise/offers`, data, { headers: getAuthHeaders() }),
  update: (id, data) => axios.put(`${API}/enterprise/offers/${id}`, data, { headers: getAuthHeaders() }),
  delete: (id) => axios.delete(`${API}/enterprise/offers/${id}`, { headers: getAuthHeaders() }),
};

// Trainings/Formations
export const trainingsAPI = {
  list: () => axios.get(`${API}/enterprise/trainings`, { headers: getAuthHeaders() }),
  listAll: (params) => axios.get(`${API}/trainings`, { params }),
  getById: (id) => axios.get(`${API}/trainings/${id}`),
  create: (data) => axios.post(`${API}/enterprise/trainings`, data, { headers: getAuthHeaders() }),
  update: (id, data) => axios.put(`${API}/enterprise/trainings/${id}`, data, { headers: getAuthHeaders() }),
  delete: (id) => axios.delete(`${API}/enterprise/trainings/${id}`, { headers: getAuthHeaders() }),
  // Client training purchases
  purchase: (trainingId) => axios.post(`${API}/trainings/${trainingId}/purchase`, null, { headers: getAuthHeaders() }),
  enroll: (trainingId, sessionId = null) => axios.post(`${API}/trainings/${trainingId}/enroll`, null, { 
    params: sessionId ? { session_id: sessionId } : {},
    headers: getAuthHeaders() 
  }),
  getMyTrainings: (status = null) => axios.get(`${API}/client/trainings`, { 
    params: status ? { status } : {},
    headers: getAuthHeaders() 
  }),
  markComplete: (enrollmentId) => axios.put(`${API}/client/trainings/${enrollmentId}/complete`, null, { headers: getAuthHeaders() }),
  // Reviews
  getReviews: (trainingId) => axios.get(`${API}/trainings/${trainingId}/reviews`),
  createReview: (trainingId, data) => axios.post(`${API}/trainings/${trainingId}/review`, data, { headers: getAuthHeaders() }),
};

// User Online Status
export const onlineStatusAPI = {
  heartbeat: () => axios.post(`${API}/user/heartbeat`, null, { headers: getAuthHeaders() }),
  setOffline: () => axios.post(`${API}/user/offline`, null, { headers: getAuthHeaders() }),
  getFriendsOnline: () => axios.get(`${API}/client/friends/online`, { headers: getAuthHeaders() }),
};

// Jobs/Emplois
export const jobsAPI = {
  list: () => axios.get(`${API}/enterprise/jobs`, { headers: getAuthHeaders() }),
  listAll: (params) => axios.get(`${API}/jobs`, { params }),
  getById: (id) => axios.get(`${API}/jobs/${id}`),
  getDetail: (jobId) => axios.get(`${API}/jobs/${jobId}`),
  create: (data) => axios.post(`${API}/enterprise/jobs`, data, { headers: getAuthHeaders() }),
  update: (id, data) => axios.put(`${API}/enterprise/jobs/${id}`, data, { headers: getAuthHeaders() }),
  toggle: (id) => axios.put(`${API}/enterprise/jobs/${id}/toggle`, null, { headers: getAuthHeaders() }),
  delete: (id) => axios.delete(`${API}/enterprise/jobs/${id}`, { headers: getAuthHeaders() }),
  getApplications: (jobId) => axios.get(`${API}/enterprise/jobs/${jobId}/applications`, { headers: getAuthHeaders() }),
  apply: (jobId, data) => axios.post(`${API}/jobs/${jobId}/apply`, data, { headers: getAuthHeaders() }),
  myApplications: () => axios.get(`${API}/client/job-applications`, { headers: getAuthHeaders() }),
};

// Real Estate/Immobilier
export const realEstateAPI = {
  list: () => axios.get(`${API}/enterprise/real-estate`, { headers: getAuthHeaders() }),
  listAll: (params) => axios.get(`${API}/real-estate`, { params }),
  create: (data) => axios.post(`${API}/enterprise/real-estate`, data, { headers: getAuthHeaders() }),
  delete: (id) => axios.delete(`${API}/enterprise/real-estate/${id}`, { headers: getAuthHeaders() }),
};

// Investments
export const investmentsAPI = {
  list: () => axios.get(`${API}/enterprise/investments`, { headers: getAuthHeaders() }),
  listAll: (params) => axios.get(`${API}/investments`, { params }),
  create: (data) => axios.post(`${API}/enterprise/investments`, data, { headers: getAuthHeaders() }),
  delete: (id) => axios.delete(`${API}/enterprise/investments/${id}`, { headers: getAuthHeaders() }),
};

// Stock Management
export const stockAPI = {
  list: () => axios.get(`${API}/enterprise/stock`, { headers: getAuthHeaders() }),
  add: (data) => axios.post(`${API}/enterprise/stock`, data, { headers: getAuthHeaders() }),
  movement: (data) => axios.post(`${API}/enterprise/stock/movement`, data, { headers: getAuthHeaders() }),
  history: () => axios.get(`${API}/enterprise/stock/history`, { headers: getAuthHeaders() }),
};

// Agenda/Calendar
export const agendaAPI = {
  list: (params) => axios.get(`${API}/enterprise/agenda`, { params, headers: getAuthHeaders() }),
  create: (data) => axios.post(`${API}/enterprise/agenda`, data, { headers: getAuthHeaders() }),
  update: (id, data) => axios.put(`${API}/enterprise/agenda/${id}`, data, { headers: getAuthHeaders() }),
  delete: (id) => axios.delete(`${API}/enterprise/agenda/${id}`, { headers: getAuthHeaders() }),
};

// Enterprise Contacts
export const enterpriseContactsAPI = {
  list: (params) => axios.get(`${API}/enterprise/contacts`, { params, headers: getAuthHeaders() }),
  get: (id) => axios.get(`${API}/enterprise/contacts/${id}`, { headers: getAuthHeaders() }),
  create: (data) => axios.post(`${API}/enterprise/contacts`, data, { headers: getAuthHeaders() }),
  update: (id, data) => axios.put(`${API}/enterprise/contacts/${id}`, data, { headers: getAuthHeaders() }),
  delete: (id) => axios.delete(`${API}/enterprise/contacts/${id}`, { headers: getAuthHeaders() }),
};

// Team/Personnel
export const teamAPI = {
  list: () => axios.get(`${API}/enterprise/team`, { headers: getAuthHeaders() }),
  add: (data) => axios.post(`${API}/enterprise/team`, data, { headers: getAuthHeaders() }),
  update: (id, data) => axios.put(`${API}/enterprise/team/${id}`, data, { headers: getAuthHeaders() }),
  delete: (id) => axios.delete(`${API}/enterprise/team/${id}`, { headers: getAuthHeaders() }),
  // Team Orders
  listOrders: () => axios.get(`${API}/enterprise/team/orders`, { headers: getAuthHeaders() }),
  createOrder: (data) => axios.post(`${API}/enterprise/team/orders`, data, { headers: getAuthHeaders() }),
  updateOrderStatus: (id, status) => axios.put(`${API}/enterprise/team/orders/${id}/status`, null, { params: { status }, headers: getAuthHeaders() }),
};

// Permanent Orders
export const permanentOrdersAPI = {
  list: () => axios.get(`${API}/enterprise/permanent-orders`, { headers: getAuthHeaders() }),
  create: (data) => axios.post(`${API}/enterprise/permanent-orders`, data, { headers: getAuthHeaders() }),
  toggle: (id) => axios.put(`${API}/enterprise/permanent-orders/${id}/toggle`, null, { headers: getAuthHeaders() }),
  delete: (id) => axios.delete(`${API}/enterprise/permanent-orders/${id}`, { headers: getAuthHeaders() }),
};

// Documents
export const documentsAPI = {
  list: (category) => axios.get(`${API}/enterprise/documents`, { params: { category }, headers: getAuthHeaders() }),
  add: (data) => axios.post(`${API}/enterprise/documents`, data, { headers: getAuthHeaders() }),
  delete: (id) => axios.delete(`${API}/enterprise/documents/${id}`, { headers: getAuthHeaders() }),
};

// Development/Formation
export const developmentAPI = {
  list: () => axios.get(`${API}/enterprise/development`, { headers: getAuthHeaders() }),
  updateProgress: (resourceId, isCompleted) => axios.post(`${API}/enterprise/development/progress`, null, { 
    params: { resource_id: resourceId, is_completed: isCompleted }, 
    headers: getAuthHeaders() 
  }),
};

// Enterprise Customers (Real targeting)
export const enterpriseCustomersAPI = {
  list: (params = {}) => axios.get(`${API}/enterprise/customers`, { params, headers: getAuthHeaders() }),
  sendQuestion: (data) => axios.post(`${API}/enterprise/send-question`, data, { headers: getAuthHeaders() }),
};

// Finances
export const financesAPI = {
  get: (params) => axios.get(`${API}/enterprise/finances`, { params, headers: getAuthHeaders() }),
  addTransaction: (data) => axios.post(`${API}/enterprise/finances/transactions`, data, { headers: getAuthHeaders() }),
  deleteTransaction: (id) => axios.delete(`${API}/enterprise/finances/transactions/${id}`, { headers: getAuthHeaders() }),
};

// Advertising
export const advertisingAPI = {
  list: () => axios.get(`${API}/enterprise/advertising`, { headers: getAuthHeaders() }),
  getPublic: (placement = null, limit = 10) => axios.get(`${API}/advertising/public`, { params: { placement, limit } }),
  trackClick: (adId) => axios.post(`${API}/advertising/${adId}/click`),
  create: (data) => axios.post(`${API}/enterprise/advertising`, data, { headers: getAuthHeaders() }),
  pay: (id) => axios.post(`${API}/enterprise/advertising/${id}/pay`, null, { headers: getAuthHeaders() }),
  activate: (id, sessionId) => axios.post(`${API}/enterprise/advertising/${id}/activate`, null, { params: { session_id: sessionId }, headers: getAuthHeaders() }),
  toggle: (id) => axios.put(`${API}/enterprise/advertising/${id}/toggle`, null, { headers: getAuthHeaders() }),
  delete: (id) => axios.delete(`${API}/enterprise/advertising/${id}`, { headers: getAuthHeaders() }),
};

// Enterprise Applications
export const enterpriseApplicationsAPI = {
  list: () => axios.get(`${API}/enterprise/applications`, { headers: getAuthHeaders() }),
  updateStatus: (applicationId, status) => axios.put(`${API}/enterprise/applications/${applicationId}/status`, null, { params: { status }, headers: getAuthHeaders() }),
};

// Notifications
export const notificationsAPI = {
  list: (unreadOnly = false) => axios.get(`${API}/notifications`, { params: { unread_only: unreadOnly }, headers: getAuthHeaders() }),
  markRead: (id) => axios.put(`${API}/notifications/${id}/read`, null, { headers: getAuthHeaders() }),
  markAllRead: () => axios.put(`${API}/notifications/read-all`, null, { headers: getAuthHeaders() }),
  delete: (id) => axios.delete(`${API}/notifications/${id}`, { headers: getAuthHeaders() }),
};

// Subscriptions / Abonnements
export const subscriptionsAPI = {
  getPlans: () => axios.get(`${API}/subscriptions/plans`),
  getCurrent: () => axios.get(`${API}/subscriptions/current`, { headers: getAuthHeaders() }),
  createCheckout: (planId, addons = []) => axios.post(`${API}/subscriptions/checkout`, null, {
    params: { plan_id: planId, addons: addons.join(',') || undefined },
    headers: getAuthHeaders()
  }),
  activate: (sessionId) => axios.post(`${API}/subscriptions/activate`, null, {
    params: { session_id: sessionId },
    headers: getAuthHeaders()
  }),
  createAddonCheckout: (addonId) => axios.post(`${API}/subscriptions/addon/checkout`, null, {
    params: { addon_id: addonId },
    headers: getAuthHeaders()
  }),
};

// IA Marketing APIs
export const iaCampaignsAPI = {
  list: () => axios.get(`${API}/enterprise/ia-campaigns`, { headers: getAuthHeaders() }),
  create: (data) => axios.post(`${API}/enterprise/ia-campaigns`, data, { headers: getAuthHeaders() }),
  toggle: (id) => axios.put(`${API}/enterprise/ia-campaigns/${id}/toggle`, null, { headers: getAuthHeaders() }),
  delete: (id) => axios.delete(`${API}/enterprise/ia-campaigns/${id}`, { headers: getAuthHeaders() }),
};

export const influencersAPI = {
  list: (category = null) => axios.get(`${API}/influencers`, { params: { category } }),
  getCollaborations: () => axios.get(`${API}/enterprise/influencer-collaborations`, { headers: getAuthHeaders() }),
  createCollaboration: (data) => axios.post(`${API}/enterprise/influencer-collaborations`, null, {
    params: { influencer_id: data.influencer_id, message: data.message, budget: data.budget },
    headers: getAuthHeaders()
  }),
  cancelCollaboration: (id) => axios.delete(`${API}/enterprise/influencer-collaborations/${id}`, { headers: getAuthHeaders() }),
  // Influencer Profile APIs
  getProfile: () => axios.get(`${API}/influencer/profile`, { headers: getAuthHeaders() }),
  updateProfile: (data) => axios.put(`${API}/influencer/profile`, data, { headers: getAuthHeaders() }),
  createProfile: (data) => axios.post(`${API}/influencer/profile`, data, { headers: getAuthHeaders() }),
  getMyCollaborations: () => axios.get(`${API}/influencer/collaborations`, { headers: getAuthHeaders() }),
  respondToCollaboration: (collabId, accept) => axios.put(`${API}/influencer/collaborations/${collabId}/respond`, null, {
    params: { accept },
    headers: getAuthHeaders()
  }),
};

export const commercialGesturesAPI = {
  list: () => axios.get(`${API}/enterprise/commercial-gestures`, { headers: getAuthHeaders() }),
  create: (data) => axios.post(`${API}/enterprise/commercial-gestures`, data, { headers: getAuthHeaders() }),
  toggle: (id) => axios.put(`${API}/enterprise/commercial-gestures/${id}/toggle`, null, { headers: getAuthHeaders() }),
  delete: (id) => axios.delete(`${API}/enterprise/commercial-gestures/${id}`, { headers: getAuthHeaders() }),
};

// ============ CLIENT APIs ============

export const clientProfileAPI = {
  get: () => axios.get(`${API}/client/profile`, { headers: getAuthHeaders() }),
  update: (data) => axios.put(`${API}/client/profile`, data, { headers: getAuthHeaders() }),
  getPublic: (userId) => axios.get(`${API}/client/profile/${userId}/public`, { headers: getAuthHeaders() }),
  getFeed: (userId) => axios.get(`${API}/client/${userId}/feed`, { headers: getAuthHeaders() }),
};

export const friendsAPI = {
  list: () => axios.get(`${API}/client/friends`, { headers: getAuthHeaders() }),
  getRequests: () => axios.get(`${API}/client/friend-requests`, { headers: getAuthHeaders() }),
  sendRequest: (friendId, message = null) => axios.post(`${API}/client/friends/request`, { friend_id: friendId, message }, { headers: getAuthHeaders() }),
  respond: (friendshipId, accept) => axios.put(`${API}/client/friends/${friendshipId}/respond`, null, { params: { accept }, headers: getAuthHeaders() }),
  remove: (friendshipId) => axios.delete(`${API}/client/friends/${friendshipId}`, { headers: getAuthHeaders() }),
  getSuggestions: () => axios.get(`${API}/client/suggested-friends`, { headers: getAuthHeaders() }),
};

export const paymentCardsAPI = {
  list: () => axios.get(`${API}/client/cards`, { headers: getAuthHeaders() }),
  add: (data) => axios.post(`${API}/client/cards`, data, { headers: getAuthHeaders() }),
  delete: (cardId) => axios.delete(`${API}/client/cards/${cardId}`, { headers: getAuthHeaders() }),
  setDefault: (cardId) => axios.put(`${API}/client/cards/${cardId}/default`, null, { headers: getAuthHeaders() }),
};

export const clientDocumentsAPI = {
  list: (category = null) => axios.get(`${API}/client/documents`, { params: { category }, headers: getAuthHeaders() }),
  add: (data) => axios.post(`${API}/client/documents`, data, { headers: getAuthHeaders() }),
  delete: (docId) => axios.delete(`${API}/client/documents/${docId}`, { headers: getAuthHeaders() }),
};

export const messagesAPI = {
  getConversations: () => axios.get(`${API}/messages/conversations`, { headers: getAuthHeaders() }),
  getMessages: (partnerId, limit = 50) => axios.get(`${API}/messages/${partnerId}`, { params: { limit }, headers: getAuthHeaders() }),
  send: (recipientId, content, messageType = 'text') => axios.post(`${API}/messages`, { recipient_id: recipientId, content, message_type: messageType }, { headers: getAuthHeaders() }),
};

// Booking / Prise de RDV
export const bookingAPI = {
  // Client books appointment with enterprise
  create: (data) => axios.post(`${API}/booking/appointment`, data, { headers: getAuthHeaders() }),
  // Get client's appointments
  myAppointments: () => axios.get(`${API}/booking/my-appointments`, { headers: getAuthHeaders() }),
  // Get enterprise availability
  getAvailability: (enterpriseId, date = null) => axios.get(`${API}/booking/enterprise/${enterpriseId}/availability`, { params: { date } }),
  // Update booking status
  updateStatus: (bookingId, status) => axios.put(`${API}/booking/${bookingId}/status`, null, { params: { status }, headers: getAuthHeaders() }),
};

export const statsAPI = {
  trackProfileView: (userId) => axios.post(`${API}/track/profile-view/${userId}`, null, { headers: getAuthHeaders() }),
  getProfileViews: () => axios.get(`${API}/stats/profile-views`, { headers: getAuthHeaders() }),
};

export default {
  auth: authAPI,
  enterprise: enterpriseAPI,
  servicesProducts: servicesProductsAPI,
  review: reviewAPI,
  order: orderAPI,
  category: categoryAPI,
  featured: featuredAPI,
  payment: paymentAPI,
  admin: adminAPI,
  cashback: cashbackAPI,
  offers: offersAPI,
  trainings: trainingsAPI,
  jobs: jobsAPI,
  realEstate: realEstateAPI,
  investments: investmentsAPI,
  stock: stockAPI,
  agenda: agendaAPI,
  team: teamAPI,
  permanentOrders: permanentOrdersAPI,
  documents: documentsAPI,
  development: developmentAPI,
  finances: financesAPI,
  advertising: advertisingAPI,
  notifications: notificationsAPI,
  subscriptions: subscriptionsAPI,
  iaCampaigns: iaCampaignsAPI,
  influencers: influencersAPI,
  clientInvitations: clientInvitationsAPI,
  commercialGestures: commercialGesturesAPI,
};
