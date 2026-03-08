// ============================================
// TITELLI - Main JavaScript
// ============================================

// Toast notifications
function showToast(message, type = 'success') {
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 3000);
}

// Auth state management
function isLoggedIn() {
    return !!localStorage.getItem('titelli_token');
}

function getUser() {
    const user = localStorage.getItem('titelli_user');
    return user ? JSON.parse(user) : null;
}

function setAuth(token, user) {
    localStorage.setItem('titelli_token', token);
    localStorage.setItem('titelli_user', JSON.stringify(user));
}

function logout() {
    localStorage.removeItem('titelli_token');
    localStorage.removeItem('titelli_user');
    window.location.href = 'index.html';
}

// Update header based on auth state
function updateHeader() {
    const authButtons = document.querySelector('.header-actions');
    if (!authButtons) return;

    const user = getUser();

    if (user) {
        const dashboardUrl = user.user_type === 'entreprise' 
            ? 'dashboard-entreprise.html' 
            : 'dashboard-client.html';
        
        authButtons.innerHTML = `
            <a href="${dashboardUrl}" class="btn btn-secondary btn-small">
                ${user.first_name} ${user.last_name}
            </a>
            <button onclick="logout()" class="btn btn-small" style="background: transparent; color: var(--text-secondary);">
                Déconnexion
            </button>
        `;
    } else {
        authButtons.innerHTML = `
            <a href="auth.html" class="btn btn-primary">Connexion</a>
        `;
    }
}

// Create enterprise card HTML
function createEnterpriseCard(enterprise) {
    const badges = [];
    if (enterprise.is_certified) badges.push('<span class="badge badge-certified">✓ Certifié</span>');
    if (enterprise.is_labeled) badges.push('<span class="badge badge-labeled">★ Labellisé</span>');
    if (enterprise.is_premium) badges.push('<span class="badge badge-premium">♛ Premium</span>');

    return `
        <a href="entreprise.html?id=${enterprise.id}" class="card">
            <div class="card-image" style="background: linear-gradient(135deg, #0047AB 0%, #001a3f 100%); display: flex; align-items: center; justify-content: center; font-size: 48px; color: white;">
                ${enterprise.business_name.charAt(0)}
            </div>
            <div class="card-body">
                ${badges.length > 0 ? `<div class="badges">${badges.join('')}</div>` : ''}
                <h3 class="card-title">${enterprise.business_name}</h3>
                ${enterprise.slogan ? `<p class="card-slogan">${enterprise.slogan}</p>` : ''}
                <p class="card-description">${enterprise.description || ''}</p>
                <div class="card-footer">
                    <span class="card-category">${enterprise.category || 'Service'}</span>
                    ${enterprise.rating > 0 ? `<span class="card-rating">⭐ ${enterprise.rating.toFixed(1)}</span>` : ''}
                </div>
            </div>
        </a>
    `;
}

// Create service/product card HTML
function createServiceCard(item) {
    return `
        <div class="card">
            <div class="card-image" style="background: linear-gradient(135deg, ${item.type === 'service' ? '#0047AB' : '#D4AF37'} 0%, #001a3f 100%); display: flex; align-items: center; justify-content: center;">
                <span style="background: ${item.type === 'service' ? 'var(--primary)' : 'var(--secondary)'}; color: ${item.type === 'service' ? 'white' : 'black'}; padding: 4px 12px; border-radius: 999px; font-size: 12px;">
                    ${item.type === 'service' ? 'Service' : 'Produit'}
                </span>
            </div>
            <div class="card-body">
                <h3 class="card-title">${item.name}</h3>
                <p class="card-description">${item.description}</p>
                <div class="card-footer">
                    <span class="card-category">${item.category}</span>
                    <span style="font-weight: 700; font-size: 18px;">${item.price.toFixed(2)} CHF</span>
                </div>
            </div>
        </div>
    `;
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric'
    });
}

// Init on page load
document.addEventListener('DOMContentLoaded', () => {
    updateHeader();
});
