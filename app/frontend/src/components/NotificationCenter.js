import React, { useState, useEffect, useCallback } from 'react';
import { Bell, X, Check, CheckCheck, Trash2, Settings, Filter, ShoppingCart, Package, Wallet, UserPlus, Users, MessageSquare, GraduationCap, Award, Heart, Gift, Crown, TrendingUp, Briefcase, Mail, Star, AlertTriangle, CreditCard, Calendar, BarChart2, DollarSign } from 'lucide-react';
import { notificationsAPI } from '../services/api';
import { toast } from 'sonner';

// Icon mapping based on notification type
const NOTIFICATION_ICONS = {
  order_placed: ShoppingCart,
  order_status: Package,
  cashback_earned: Wallet,
  friend_request: UserPlus,
  friend_accepted: Users,
  message_received: MessageSquare,
  message: MessageSquare,
  training_enrolled: GraduationCap,
  training_enrollment: GraduationCap,
  training_completed: Award,
  wishlist_update: Heart,
  offer_special: Gift,
  premium_upgrade: Crown,
  investment_update: TrendingUp,
  job_application_status: Briefcase,
  invitation_received: Mail,
  new_order: ShoppingCart,
  order: ShoppingCart,
  order_completed: Check,
  new_review: Star,
  job_application: Briefcase,
  stock_alert: AlertTriangle,
  subscription_updated: CreditCard,
  new_follower: UserPlus,
  training_purchase: GraduationCap,
  service_booked: Calendar,
  payment_received: DollarSign,
  advertising_stats: BarChart2,
  default: Bell
};

// Color mapping based on notification type
const NOTIFICATION_COLORS = {
  order_placed: 'text-green-400 bg-green-500/20',
  order_status: 'text-blue-400 bg-blue-500/20',
  cashback_earned: 'text-yellow-400 bg-yellow-500/20',
  friend_request: 'text-purple-400 bg-purple-500/20',
  friend_accepted: 'text-green-400 bg-green-500/20',
  message_received: 'text-blue-400 bg-blue-500/20',
  message: 'text-blue-400 bg-blue-500/20',
  training_enrolled: 'text-indigo-400 bg-indigo-500/20',
  training_enrollment: 'text-indigo-400 bg-indigo-500/20',
  training_completed: 'text-yellow-400 bg-yellow-500/20',
  wishlist_update: 'text-pink-400 bg-pink-500/20',
  offer_special: 'text-orange-400 bg-orange-500/20',
  premium_upgrade: 'text-yellow-400 bg-yellow-500/20',
  investment_update: 'text-green-400 bg-green-500/20',
  job_application_status: 'text-blue-400 bg-blue-500/20',
  invitation_received: 'text-purple-400 bg-purple-500/20',
  new_order: 'text-green-400 bg-green-500/20',
  order: 'text-green-400 bg-green-500/20',
  order_completed: 'text-green-400 bg-green-500/20',
  new_review: 'text-yellow-400 bg-yellow-500/20',
  job_application: 'text-blue-400 bg-blue-500/20',
  stock_alert: 'text-red-400 bg-red-500/20',
  subscription_updated: 'text-purple-400 bg-purple-500/20',
  new_follower: 'text-blue-400 bg-blue-500/20',
  training_purchase: 'text-green-400 bg-green-500/20',
  service_booked: 'text-blue-400 bg-blue-500/20',
  payment_received: 'text-green-400 bg-green-500/20',
  advertising_stats: 'text-cyan-400 bg-cyan-500/20',
  default: 'text-gray-400 bg-gray-500/20'
};

const NotificationItem = ({ notification, onMarkRead, onDelete }) => {
  const IconComponent = NOTIFICATION_ICONS[notification.notification_type] || NOTIFICATION_ICONS.default;
  const colorClass = NOTIFICATION_COLORS[notification.notification_type] || NOTIFICATION_COLORS.default;
  
  const formatTime = (dateStr) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diff = now - date;
    
    if (diff < 60000) return 'À l\'instant';
    if (diff < 3600000) return `Il y a ${Math.floor(diff / 60000)} min`;
    if (diff < 86400000) return `Il y a ${Math.floor(diff / 3600000)} h`;
    if (diff < 604800000) return `Il y a ${Math.floor(diff / 86400000)} j`;
    return date.toLocaleDateString('fr-FR');
  };

  return (
    <div 
      className={`p-4 border-b border-white/5 hover:bg-white/5 transition-colors ${!notification.is_read ? 'bg-[#0047AB]/5' : ''}`}
      data-testid={`notification-item-${notification.id}`}
    >
      <div className="flex items-start gap-3">
        <div className={`p-2 rounded-full ${colorClass} flex-shrink-0`}>
          <IconComponent className="w-4 h-4" />
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2">
            <h4 className={`font-medium text-sm ${!notification.is_read ? 'text-white' : 'text-gray-300'}`}>
              {notification.title}
            </h4>
            <span className="text-xs text-gray-500 flex-shrink-0">
              {formatTime(notification.created_at)}
            </span>
          </div>
          <p className="text-sm text-gray-400 mt-1 line-clamp-2">
            {notification.message}
          </p>
          <div className="flex items-center gap-2 mt-2">
            {!notification.is_read && (
              <button
                onClick={() => onMarkRead(notification.id)}
                className="text-xs text-[#0047AB] hover:text-[#0056D2] flex items-center gap-1"
              >
                <Check className="w-3 h-3" />
                Marquer lu
              </button>
            )}
            <button
              onClick={() => onDelete(notification.id)}
              className="text-xs text-gray-500 hover:text-red-400 flex items-center gap-1"
            >
              <Trash2 className="w-3 h-3" />
              Supprimer
            </button>
          </div>
        </div>
        {!notification.is_read && (
          <div className="w-2 h-2 bg-[#0047AB] rounded-full flex-shrink-0 mt-1" />
        )}
      </div>
    </div>
  );
};

const NotificationCenter = ({ 
  isOpen, 
  onClose, 
  notifications = [], 
  onRefresh, 
  loading = false,
  userType = 'client',
  isRealTime = false
}) => {
  const [filter, setFilter] = useState('all');
  const [localNotifications, setLocalNotifications] = useState(notifications);

  useEffect(() => {
    setLocalNotifications(notifications);
  }, [notifications]);

  const handleMarkRead = async (notifId) => {
    try {
      await notificationsAPI.markRead(notifId);
      setLocalNotifications(prev => 
        prev.map(n => n.id === notifId ? { ...n, is_read: true } : n)
      );
    } catch (error) {
      toast.error('Erreur lors de la mise à jour');
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await notificationsAPI.markAllRead();
      setLocalNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
      toast.success('Toutes les notifications marquées comme lues');
    } catch (error) {
      toast.error('Erreur lors de la mise à jour');
    }
  };

  const handleDelete = async (notifId) => {
    try {
      await notificationsAPI.delete(notifId);
      setLocalNotifications(prev => prev.filter(n => n.id !== notifId));
      toast.success('Notification supprimée');
    } catch (error) {
      toast.error('Erreur lors de la suppression');
    }
  };

  const unreadCount = localNotifications.filter(n => !n.is_read).length;
  
  const filteredNotifications = localNotifications.filter(n => {
    if (filter === 'all') return true;
    if (filter === 'unread') return !n.is_read;
    return n.notification_type?.includes(filter);
  });

  const filterCategories = userType === 'entreprise' ? [
    { key: 'all', label: 'Tout' },
    { key: 'unread', label: 'Non lues' },
    { key: 'order', label: 'Commandes' },
    { key: 'review', label: 'Avis' },
    { key: 'job', label: 'Emplois' },
    { key: 'training', label: 'Formations' },
  ] : [
    { key: 'all', label: 'Tout' },
    { key: 'unread', label: 'Non lues' },
    { key: 'order', label: 'Commandes' },
    { key: 'cashback', label: 'Cashback' },
    { key: 'friend', label: 'Amis' },
    { key: 'message', label: 'Messages' },
  ];

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50" onClick={onClose} data-testid="notification-center">
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" />
      <div 
        className="absolute right-4 top-20 w-full max-w-md bg-[#0F0F0F] rounded-2xl border border-white/10 shadow-2xl overflow-hidden"
        onClick={e => e.stopPropagation()}
      >
        {/* Header */}
        <div className="p-4 border-b border-white/10 bg-gradient-to-r from-[#0047AB]/10 to-transparent">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Bell className="w-5 h-5 text-[#0047AB]" />
              <h2 className="text-lg font-semibold text-white">Notifications</h2>
              {unreadCount > 0 && (
                <span className="px-2 py-0.5 bg-[#0047AB] text-white text-xs rounded-full">
                  {unreadCount}
                </span>
              )}
              {/* Real-time indicator */}
              {isRealTime && (
                <span className="flex items-center gap-1 px-2 py-0.5 bg-green-500/20 text-green-400 text-xs rounded-full">
                  <span className="w-1.5 h-1.5 bg-green-400 rounded-full animate-pulse" />
                  Live
                </span>
              )}
            </div>
            <div className="flex items-center gap-2">
              {unreadCount > 0 && (
                <button 
                  onClick={handleMarkAllRead}
                  className="text-xs text-gray-400 hover:text-white flex items-center gap-1"
                >
                  <CheckCheck className="w-4 h-4" />
                  Tout lire
                </button>
              )}
              <button 
                onClick={onClose}
                className="p-1 text-gray-400 hover:text-white rounded-lg hover:bg-white/10"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Filters */}
          <div className="flex items-center gap-2 mt-3 overflow-x-auto pb-1">
            {filterCategories.map(cat => (
              <button
                key={cat.key}
                onClick={() => setFilter(cat.key)}
                className={`px-3 py-1 text-xs rounded-full whitespace-nowrap transition-colors ${
                  filter === cat.key 
                    ? 'bg-[#0047AB] text-white' 
                    : 'bg-white/5 text-gray-400 hover:bg-white/10'
                }`}
              >
                {cat.label}
              </button>
            ))}
          </div>
        </div>

        {/* Notifications List */}
        <div className="max-h-[60vh] overflow-y-auto">
          {loading ? (
            <div className="p-8 text-center">
              <div className="w-8 h-8 border-2 border-[#0047AB] border-t-transparent rounded-full animate-spin mx-auto" />
              <p className="text-gray-400 text-sm mt-2">Chargement...</p>
            </div>
          ) : filteredNotifications.length > 0 ? (
            filteredNotifications.map(notification => (
              <NotificationItem
                key={notification.id}
                notification={notification}
                onMarkRead={handleMarkRead}
                onDelete={handleDelete}
              />
            ))
          ) : (
            <div className="p-8 text-center">
              <Bell className="w-12 h-12 text-gray-600 mx-auto mb-3" />
              <p className="text-gray-400">Aucune notification</p>
              <p className="text-gray-500 text-sm mt-1">
                {filter !== 'all' ? 'Essayez un autre filtre' : 'Vous êtes à jour !'}
              </p>
            </div>
          )}
        </div>

        {/* Footer */}
        {filteredNotifications.length > 0 && (
          <div className="p-3 border-t border-white/10 bg-white/5">
            <button
              onClick={onRefresh}
              className="w-full text-center text-sm text-gray-400 hover:text-white transition-colors"
            >
              Actualiser
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

// Export a simple notification badge component
export const NotificationBadge = ({ count = 0, onClick }) => {
  if (count === 0) return null;
  
  return (
    <button
      onClick={onClick}
      className="relative p-2 text-gray-400 hover:text-white transition-colors"
      data-testid="notification-badge"
    >
      <Bell className="w-5 h-5" />
      <span className="absolute -top-1 -right-1 min-w-[18px] h-[18px] flex items-center justify-center bg-[#0047AB] text-white text-xs rounded-full px-1 animate-pulse">
        {count > 99 ? '99+' : count}
      </span>
    </button>
  );
};

// Export helper function to get icon
export const getNotificationIcon = (type) => {
  const Icon = NOTIFICATION_ICONS[type] || NOTIFICATION_ICONS.default;
  const colorClass = NOTIFICATION_COLORS[type] || NOTIFICATION_COLORS.default;
  return { Icon, colorClass };
};

export default NotificationCenter;
