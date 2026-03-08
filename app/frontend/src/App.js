import React, { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { Toaster } from 'sonner';
import { AuthProvider, useAuth } from './context/AuthContext';
import { CartProvider } from './context/CartContext';

// Layout
import Header from './components/Header';
import Footer from './components/Footer';
import SplashScreen from './components/SplashScreen';

// Pages
import HomePage from './pages/HomePage';
import AuthPage from './pages/AuthPage';
import ServicesPage from './pages/ServicesPage';
import ProductsPage from './pages/ProductsPage';
import ServiceProductDetailPage from './pages/ServiceProductDetailPage';
import EnterprisesPage from './pages/EnterprisesPage';
import EnterprisePage from './pages/EnterprisePage';
import EnterpriseDashboard from './pages/EnterpriseDashboard';
import ClientDashboard from './pages/ClientDashboard';
import InfluencerDashboard from './pages/InfluencerDashboard';
import AdminDashboard from './pages/AdminDashboard';
import CartPage from './pages/CartPage';
import OrdersPage from './pages/OrdersPage';
import JobDetailPage from './pages/JobDetailPage';
import JobsPage from './pages/JobsPage';
import ClientProfilePage from './pages/ClientProfilePage';
import EnterpriseRegistrationPage from './pages/EnterpriseRegistrationPage';
import { PaymentSuccessPage, PaymentCancelPage } from './pages/PaymentPages';
import RdvTitelliPage from './pages/RdvTitelliPage';
import RdvChatPage from './pages/RdvChatPage';
import SpecialistsPage from './pages/SpecialistsPage';
import TitelliProPage from './pages/TitelliProPage';
import SportsPage from './pages/SportsPage';
import MediaPubPage from './pages/MediaPubPage';
import VideoPubPage from './pages/VideoPubPage';
import AboutPage from './pages/AboutPage';
import CGVPage from './pages/CGVPage';
import MentionsLegalesPage from './pages/MentionsLegalesPage';
import FAQPage from './pages/FAQPage';
import StatusPage from './pages/StatusPage';
import CashbackPage from './pages/CashbackPage';
import WelcomePopup from './components/WelcomePopup';

import './index.css';

// Protected Route Component
const ProtectedRoute = ({ children, allowedTypes = [] }) => {
  const { isAuthenticated, user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-[#050505] flex items-center justify-center">
        <div className="w-16 h-16 border-4 border-[#0047AB] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/auth" replace />;
  }

  if (allowedTypes.length > 0 && !allowedTypes.includes(user?.user_type)) {
    return <Navigate to="/" replace />;
  }

  return children;
};

// Layout wrapper
const MainLayout = ({ children, showFooter = true }) => {
  return (
    <>
      <Header />
      <main className="min-h-screen pt-20">
        {children}
      </main>
      {showFooter && <Footer />}
    </>
  );
};

// Dashboard Layout (no footer)
const DashboardLayout = ({ children }) => {
  return (
    <>
      <Header />
      {children}
    </>
  );
};

function AppRoutes() {
  return (
    <Routes>
      {/* Public Routes */}
      <Route path="/" element={<MainLayout><HomePage /></MainLayout>} />
      <Route path="/auth" element={<AuthPage />} />
      <Route path="/inscription-entreprise" element={<MainLayout showFooter={false}><EnterpriseRegistrationPage /></MainLayout>} />
      <Route path="/services" element={<MainLayout><ServicesPage /></MainLayout>} />
      <Route path="/products" element={<MainLayout><ProductsPage /></MainLayout>} />
      <Route path="/produits" element={<MainLayout><ProductsPage /></MainLayout>} />
      <Route path="/service/:id" element={<MainLayout><ServiceProductDetailPage /></MainLayout>} />
      <Route path="/product/:id" element={<MainLayout><ServiceProductDetailPage /></MainLayout>} />
      <Route path="/item/:id" element={<MainLayout><ServiceProductDetailPage /></MainLayout>} />
      <Route path="/entreprises" element={<MainLayout><EnterprisesPage /></MainLayout>} />
      <Route path="/entreprise/:id" element={<MainLayout><EnterprisePage /></MainLayout>} />
      
      {/* Client Profile Route */}
      <Route path="/profil/:userId" element={<MainLayout><ClientProfilePage /></MainLayout>} />
      
      {/* Jobs/Emplois Routes */}
      <Route path="/emplois" element={<MainLayout><JobsPage /></MainLayout>} />
      <Route path="/emploi/:id" element={<MainLayout><JobDetailPage /></MainLayout>} />
      
      {/* Filtered pages - reuse EnterprisesPage with filter */}
      <Route path="/certifies" element={<MainLayout><EnterprisesPage /></MainLayout>} />
      <Route path="/labellises" element={<MainLayout><EnterprisesPage /></MainLayout>} />
      <Route path="/premium" element={<MainLayout><EnterprisesPage /></MainLayout>} />
      <Route path="/guests" element={<MainLayout><EnterprisesPage /></MainLayout>} />

      {/* Cart & Orders Routes */}
      <Route path="/cart" element={<MainLayout><CartPage /></MainLayout>} />
      <Route path="/orders" element={<MainLayout><OrdersPage /></MainLayout>} />

      {/* Payment Routes */}
      <Route path="/payment/success" element={<MainLayout><PaymentSuccessPage /></MainLayout>} />
      <Route path="/payment/cancel" element={<MainLayout><PaymentCancelPage /></MainLayout>} />

      {/* RDV Titelli Routes - Social Booking */}
      <Route path="/rdv" element={<RdvTitelliPage />} />
      <Route path="/rdv/chat/:roomId" element={<RdvChatPage />} />

      {/* Specialists Routes */}
      <Route path="/specialists" element={<SpecialistsPage />} />

      {/* Sports & Competitions Routes */}
      <Route path="/sports" element={<SportsPage />} />

      {/* Media Pub - Création de publicités */}
      <Route path="/media-pub" element={<MainLayout><MediaPubPage /></MainLayout>} />
      <Route path="/media-pub/success" element={<MainLayout><MediaPubPage /></MainLayout>} />
      
      {/* Video Pub - Création de vidéos publicitaires IA */}
      <Route path="/video-pub" element={<MainLayout><VideoPubPage /></MainLayout>} />
      <Route path="/video-pub/success" element={<MainLayout><VideoPubPage /></MainLayout>} />

      {/* Titelli Pro++ Route (Enterprise only) */}
      <Route path="/enterprise/pro" element={<TitelliProPage />} />
      <Route path="/titelli-pro" element={<TitelliProPage />} />
      <Route path="/pro" element={<TitelliProPage />} />

      {/* Protected Enterprise Routes */}
      <Route 
        path="/dashboard/entreprise/*" 
        element={
          <ProtectedRoute allowedTypes={['entreprise']}>
            <DashboardLayout><EnterpriseDashboard /></DashboardLayout>
          </ProtectedRoute>
        } 
      />

      {/* Protected Client Routes */}
      <Route 
        path="/dashboard/client/*" 
        element={
          <ProtectedRoute allowedTypes={['client']}>
            <DashboardLayout><ClientDashboard /></DashboardLayout>
          </ProtectedRoute>
        } 
      />

      {/* Protected Influencer Routes */}
      <Route 
        path="/dashboard/influencer/*" 
        element={
          <ProtectedRoute allowedTypes={['influencer']}>
            <DashboardLayout><InfluencerDashboard /></DashboardLayout>
          </ProtectedRoute>
        } 
      />

      {/* Admin Route */}
      <Route 
        path="/admin/*" 
        element={
          <ProtectedRoute>
            <DashboardLayout><AdminDashboard /></DashboardLayout>
          </ProtectedRoute>
        } 
      />

      {/* Static Pages */}
      <Route path="/about" element={<MainLayout><AboutPage /></MainLayout>} />
      <Route path="/cashback" element={<MainLayout><CashbackPage /></MainLayout>} />
      <Route path="/cgv" element={<MainLayout><CGVPage /></MainLayout>} />
      <Route path="/mentions-legales" element={<MainLayout><MentionsLegalesPage /></MainLayout>} />
      <Route path="/faq" element={<MainLayout><FAQPage /></MainLayout>} />
      <Route path="/status" element={<MainLayout><StatusPage /></MainLayout>} />
      <Route path="/partenaires" element={<MainLayout><PartenairesPage /></MainLayout>} />
      <Route path="/service-client" element={<MainLayout><ServiceClientPage /></MainLayout>} />

      {/* 404 */}
      <Route path="*" element={<MainLayout><NotFoundPage /></MainLayout>} />
    </Routes>
  );
}

// Simple Static Pages (keep only PartenairesPage, ServiceClientPage, NotFoundPage)
const PartenairesPage = () => (
  <div className="min-h-screen bg-[#050505] pt-24 px-4">
    <div className="max-w-4xl mx-auto py-16">
      <h1 className="text-4xl font-bold text-white mb-8" style={{ fontFamily: 'Playfair Display, serif' }}>
        Nos Partenaires
      </h1>
      <p className="text-gray-400 text-lg mb-8">
        Titelli collabore avec les meilleurs acteurs de la région pour vous offrir une expérience exceptionnelle.
      </p>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
        {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
          <div key={i} className="card-service rounded-xl p-8 flex items-center justify-center">
            <div className="w-16 h-16 bg-white/10 rounded-full" />
          </div>
        ))}
      </div>
    </div>
  </div>
);

const ServiceClientPage = () => (
  <div className="min-h-screen bg-[#050505] pt-24 px-4">
    <div className="max-w-4xl mx-auto py-16">
      <h1 className="text-4xl font-bold text-white mb-8" style={{ fontFamily: 'Playfair Display, serif' }}>
        Service Client
      </h1>
      <div className="card-service rounded-xl p-8 mb-8">
        <h2 className="text-xl font-bold text-white mb-4">Contactez-nous</h2>
        <p className="text-gray-400 mb-6">Notre équipe est disponible pour répondre à toutes vos questions.</p>
        <div className="space-y-4">
          <p className="text-gray-400">📧 Email: contact@titelli.com</p>
          <p className="text-gray-400">📞 Téléphone: +41 XX XXX XX XX</p>
          <p className="text-gray-400">📍 Adresse: Lausanne, Suisse</p>
        </div>
      </div>
      <div className="card-service rounded-xl p-8">
        <h2 className="text-xl font-bold text-white mb-4">FAQ</h2>
        <div className="space-y-4">
          <div>
            <h3 className="text-white font-medium mb-2">Comment créer un compte entreprise ?</h3>
            <p className="text-gray-400 text-sm">Cliquez sur "Connexion" puis sélectionnez "Entreprise" lors de l'inscription.</p>
          </div>
          <div>
            <h3 className="text-white font-medium mb-2">Comment devenir certifié ?</h3>
            <p className="text-gray-400 text-sm">Contactez notre équipe pour passer la certification (200 CHF).</p>
          </div>
        </div>
      </div>
    </div>
  </div>
);

const NotFoundPage = () => (
  <div className="min-h-screen bg-[#050505] pt-24 flex items-center justify-center">
    <div className="text-center">
      <h1 className="text-6xl font-bold text-white mb-4" style={{ fontFamily: 'Playfair Display, serif' }}>404</h1>
      <p className="text-gray-400 mb-8">Page non trouvée</p>
      <a href="/" className="btn-primary">Retour à l'accueil</a>
    </div>
  </div>
);

function App() {
  const [showSplash, setShowSplash] = useState(true);
  const [splashShown, setSplashShown] = useState(false);

  useEffect(() => {
    // Check if splash was already shown in this session
    const hasSeenSplash = sessionStorage.getItem('titelli_splash_shown');
    if (hasSeenSplash) {
      setShowSplash(false);
      setSplashShown(true);
    }
  }, []);

  const handleSplashComplete = () => {
    setShowSplash(false);
    setSplashShown(true);
    sessionStorage.setItem('titelli_splash_shown', 'true');
  };

  return (
    <BrowserRouter>
      <AuthProvider>
        <CartProvider>
          {showSplash && !splashShown && (
            <SplashScreen onComplete={handleSplashComplete} />
          )}
          <Toaster 
            position="top-right"
            toastOptions={{
              style: {
                background: '#0F0F0F',
                color: '#E5E5E5',
                border: '1px solid rgba(255,255,255,0.1)'
              }
            }}
          />
          <WelcomePopup />
          <AppRoutes />
        </CartProvider>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
