// ============================================
// TITELLI - API JavaScript
// ============================================

const API_URL = 'http://localhost:8001';

// Get token from localStorage
function getToken() {
    return localStorage.getItem('titelli_token');
}

// Get headers with auth
function getHeaders() {
    const headers = { 'Content-Type': 'application/json' };
    const token = getToken();
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    return headers;
}

// API Functions
const API = {
    // Auth
    async register(data) {
        const res = await fetch(`${API_URL}/api/auth/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        return res.json();
    },

    async login(email, password) {
        const res = await fetch(`${API_URL}/api/auth/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        return res.json();
    },

    async getMe() {
        const res = await fetch(`${API_URL}/api/auth/me`, {
            headers: getHeaders()
        });
        return res.json();
    },

    // Enterprises
    async getEnterprises(params = {}) {
        const query = new URLSearchParams(params).toString();
        const res = await fetch(`${API_URL}/api/enterprises?${query}`);
        return res.json();
    },

    async getEnterprise(id) {
        const res = await fetch(`${API_URL}/api/enterprises/${id}`);
        return res.json();
    },

    async createEnterprise(data) {
        const res = await fetch(`${API_URL}/api/enterprises`, {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify(data)
        });
        return res.json();
    },

    async updateEnterprise(id, data) {
        const res = await fetch(`${API_URL}/api/enterprises/${id}`, {
            method: 'PUT',
            headers: getHeaders(),
            body: JSON.stringify(data)
        });
        return res.json();
    },

    // Services & Products
    async getServicesProducts(params = {}) {
        const query = new URLSearchParams(params).toString();
        const res = await fetch(`${API_URL}/api/services-products?${query}`);
        return res.json();
    },

    async createServiceProduct(data) {
        const res = await fetch(`${API_URL}/api/services-products`, {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify(data)
        });
        return res.json();
    },

    async deleteServiceProduct(id) {
        const res = await fetch(`${API_URL}/api/services-products/${id}`, {
            method: 'DELETE',
            headers: getHeaders()
        });
        return res.json();
    },

    // Reviews
    async getReviews(enterpriseId) {
        const res = await fetch(`${API_URL}/api/reviews/${enterpriseId}`);
        return res.json();
    },

    async createReview(data) {
        const res = await fetch(`${API_URL}/api/reviews`, {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify(data)
        });
        return res.json();
    },

    // Orders
    async getOrders() {
        const res = await fetch(`${API_URL}/api/orders`, {
            headers: getHeaders()
        });
        return res.json();
    },

    async createOrder(data) {
        const res = await fetch(`${API_URL}/api/orders`, {
            method: 'POST',
            headers: getHeaders(),
            body: JSON.stringify(data)
        });
        return res.json();
    },

    // Categories
    async getProductCategories() {
        const res = await fetch(`${API_URL}/api/categories/products`);
        return res.json();
    },

    async getServiceCategories() {
        const res = await fetch(`${API_URL}/api/categories/services`);
        return res.json();
    },

    // Featured
    async getTendances() {
        const res = await fetch(`${API_URL}/api/featured/tendances`);
        return res.json();
    },

    async getGuests() {
        const res = await fetch(`${API_URL}/api/featured/guests`);
        return res.json();
    },

    async getOffres() {
        const res = await fetch(`${API_URL}/api/featured/offres`);
        return res.json();
    },

    async getPremium() {
        const res = await fetch(`${API_URL}/api/featured/premium`);
        return res.json();
    },

    // Payments
    async createCheckout(packageType, amount = null) {
        let url = `${API_URL}/api/payments/checkout?package_type=${packageType}`;
        if (amount) url += `&amount=${amount}`;
        const res = await fetch(url, {
            method: 'POST',
            headers: getHeaders()
        });
        return res.json();
    },

    async getPaymentStatus(sessionId) {
        const res = await fetch(`${API_URL}/api/payments/status/${sessionId}`);
        return res.json();
    },

    // Admin
    async getAdminStats() {
        const res = await fetch(`${API_URL}/api/admin/stats`, {
            headers: getHeaders()
        });
        return res.json();
    },

    async getAdminUsers() {
        const res = await fetch(`${API_URL}/api/admin/users`, {
            headers: getHeaders()
        });
        return res.json();
    },

    async verifyUser(userId, isCertified, isLabeled) {
        const res = await fetch(`${API_URL}/api/admin/users/${userId}/verify?is_certified=${isCertified}&is_labeled=${isLabeled}`, {
            method: 'PUT',
            headers: getHeaders()
        });
        return res.json();
    },

    // Cashback
    async getCashbackBalance() {
        const res = await fetch(`${API_URL}/api/cashback/balance`, {
            headers: getHeaders()
        });
        return res.json();
    }
};
