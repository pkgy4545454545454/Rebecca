import React, { useState, useEffect, useCallback } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { notificationsAPI } from '../services/api';
import { Search, Menu, X, Heart, Bell, ChevronDown, User, Sparkles, Image, Video, HandCoins, Building2, UserCircle, FileText, ShoppingCart, Icon } from 'lucide-react';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '../components/ui/dropdown-menu';
import { toast } from 'sonner';
import { useNotificationWebSocket } from '../hooks/useWebSocket';

const Header = () => {
  const { user, logout, isAuthenticated, isEnterprise } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [searchQuery, setSearchQuery] = useState('');
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  // Use WebSocket for real-time notifications
  const {
    isConnected: wsConnected,
    unreadCount: wsUnreadCount,
    notifications: wsNotifications,
    markRead: wsMarkRead,
    markAllRead: wsMarkAllRead,
    fetchNotifications: wsFetchNotifications,
  } = useNotificationWebSocket();

  // State for notifications (fallback to API if WS not connected)
  const [apiNotifications, setApiNotifications] = useState([]);
  const [apiUnreadCount, setApiUnreadCount] = useState(0);

  const unreadCount = wsConnected ? wsUnreadCount : apiUnreadCount;

  // Close mobile menu on route change
  useEffect(() => {
    setMobileMenuOpen(false);
  }, [location.pathname]);

  const handleSearch = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      navigate(`/search?q=${encodeURIComponent(searchQuery)}`);
      setMobileMenuOpen(false);
    }
  };

  const navLinks = [
   
    { path: '/products', label: 'Films X', className: 'text-white-400' },
    { path: '/entreprises', label: 'Scénario X', className: 'text-white-400' },
    { path: '/dashboard/client/', label: 'Devenir V.I.P', className: 'text-pink-400 ' },
    { path: '/cart', label: 'Panier', className: 'text-pink-400'}
    
 
 
  ];

  const isActive = (path) => location.pathname === path;

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-black" data-testid="main-header">
      <div className="max-w-7xl mx-auto px-4">
        {/* Main Header Bar */}
        <div className="flex items-center justify-between h-14 lg:h-16">
          
          {/* Left: Logo + Menu + Search */}
          <div className="flex items-center gap-3 sm:gap-4">
            {/* Logo à gauche */}
            <Link to="/" className="flex-shrink-0" data-testid="logo-link">
              <img 
                src="/esclava.png" 
                alt="Titelli"
                className="w-8 h-8 sm:w-10 sm:h-10 object-contain"
              />
            </Link>

            {/* Mobile hamburger */}
            <button 
              className="lg:hidden p-1.5 text-white"
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              data-testid="mobile-menu-btn"
            >
              {mobileMenuOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
            </button>

            {/* Desktop Search Bar */}
            <form onSubmit={handleSearch} className="hidden lg:flex items-center">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Rechercher..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-64 pl-10 pr-4 py-2 bg-white/10 border border-white/10 rounded-full text-sm text-white placeholder:text-gray-400 focus:outline-none focus:border-white/30 focus:bg-white/15 transition-all"
                />
              </div>
            </form>

            {/* Desktop Navigation */}
            <nav className="hidden lg:flex items-center gap-5 ml-4">
              {navLinks.map((link) => (
                <Link
                  key={link.path}
                  to={link.path}
                  className={`text-sm font-medium transition-colors ${
                    isActive(link.path) 
                      ? 'text-white' 
                      : link.className || 'text-gray-400 hover:text-white'
                  }`}
                >
                  {link.label}
                </Link>
              ))}
              
            
            
            </nav>
          </div>

          {/* Right: Actions - Profil uniquement */}
          <div className="flex items-center gap-2 sm:gap-3">
            {/* Cashback */}
            <Link to="/cashback" className="p-2 text-amber-400 hover:text-amber-300 hidden sm:block" data-testid="cashback-link">
              <HandCoins className="w-5 h-5" />
            </Link>

            <Link to="/cart" className="p-2 text-amber-400 hover:text-amber-300 hidden sm:block" data-testid="cart-link">
              <ShoppingCart className="w-5 h-5" />
            </Link>

            {/* Profile Icon - Always visible */}
            <DropdownMenu>
              <DropdownMenuTrigger className="p-2 text-gray-400 hover:text-white outline-none" data-testid="profile-btn">
                <User className="w-5 h-5" />
              </DropdownMenuTrigger>
              <DropdownMenuContent className="bg-gray-900 border border-white/10 rounded-xl p-2 min-w-[200px]">
                {isAuthenticated ? (
                  <>
                    <div className="px-3 py-2 text-sm text-white border-b border-white/10 mb-2">
                      {user?.first_name || 'Mon compte'}
                    </div>
                    <DropdownMenuItem asChild>
                      <Link to={isEnterprise ? '/dashboard/entreprise' : '/dashboard/client'} className="cursor-pointer">
                        Dashboard
                      </Link>
                    </DropdownMenuItem>
                    <DropdownMenuItem asChild>
                      <Link to="/orders" className="cursor-pointer">
                        Mes Commandes
                      </Link>
                    </DropdownMenuItem>
                    <DropdownMenuSeparator className="bg-white/10" />
                    <DropdownMenuItem onClick={logout} className="text-red-400 cursor-pointer">
                      Déconnexion
                    </DropdownMenuItem>
                  </>
                ) : (
                  <>
                    <div className="px-3 py-2 text-sm text-gray-400 border-b border-white/10 mb-2">
                      Choisissez votre profil
                    </div>
                    <DropdownMenuItem asChild>
                      <Link to="/auth?type=client" className="flex items-center gap-2 cursor-pointer">
                        <UserCircle className="w-4 h-4 text-blue-400" />
                        <span>Client</span>
                      </Link>
                    </DropdownMenuItem>
                    <DropdownMenuItem asChild>
                      <Link to="/inscription-entreprise" className="flex items-center gap-2 cursor-pointer">
                        <Building2 className="w-4 h-4 text-amber-400" />
                        <span>Entreprise</span>
                      </Link>
                    </DropdownMenuItem>
                  </>
                )}
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </div>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div className="lg:hidden border-t border-white/10 py-4">
            {/* Search */}
            <form onSubmit={handleSearch} className="mb-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
                <input
                  type="text"
                  placeholder="Rechercher..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-2.5 bg-white/5 border border-white/10 rounded-lg text-sm text-white placeholder:text-gray-500 focus:outline-none focus:border-white/20"
                />
              </div>
            </form>

            {/* Navigation Links */}
            <nav className="space-y-1">
              {navLinks.map((link) => (
                <Link
                  key={link.path}
                  to={link.path}
                  className={`block py-3 px-4 rounded-lg text-center text-sm font-medium transition-colors ${
                    isActive(link.path) 
                      ? 'bg-white/10 text-white' 
                      : link.className || 'text-gray-300 hover:bg-white/5'
                  }`}
                  onClick={() => setMobileMenuOpen(false)}
                >
                  {link.label}
                </Link>
       

              ))}
              
              {/* Pub IA Links */}
             

              {/* Other links */}
              <div className="pt-2 border-t border-white/10 mt-2">
                 <Link to="/cart" className="p-2 text-amber-400 hover:text-amber-300 hidden sm:block" data-testid="cart-link">
                 Panier
              <ShoppingCart className="w-5 h-5" />
            </Link>

                <Link
                  to="/cashback"
                  className="block py-3 px-4 rounded-lg text-center text-sm font-medium text-amber-400 hover:bg-white/5"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Cashback
                </Link>
                <Link
                  to="/wishlist"
                  className="block py-3 px-4 rounded-lg text-center text-sm font-medium text-gray-300 hover:bg-white/5"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  Mes Favoris
                </Link>
              </div>
            </nav>
          </div>
        )}
      </div>
    </header>
  );
};

export default Header;
