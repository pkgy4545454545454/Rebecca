/**
 * Notifications Component
 * - Real-time notifications via WebSocket
 * - Notification dropdown
 * - Mark as read functionality
 */
import React, { useState, useEffect, useCallback, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Bell, Check, Trash2, X, ExternalLink } from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;
const WS_URL = API_URL.replace('https://', 'wss://').replace('http://', 'ws://');

export default function NotificationsDropdown() {
  const { user, token } = useAuth();
  const navigate = useNavigate();
  
  const [isOpen, setIsOpen] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(false);
  
  const dropdownRef = useRef(null);
  const wsRef = useRef(null);

  // Fetch notifications
  const fetchNotifications = useCallback(async () => {
    if (!token) return;
    
    try {
      setLoading(true);
      const res = await fetch(`${API_URL}/api/notifications?limit=20`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (res.ok) {
        const data = await res.json();
        setNotifications(data.notifications || []);
        setUnreadCount(data.unread_count || 0);
      }
    } catch (error) {
      console.error('Error fetching notifications:', error);
    } finally {
      setLoading(false);
    }
  }, [token]);

  // Connect WebSocket for real-time notifications
  useEffect(() => {
    if (!token || !user) return;
    
    const connectWS = () => {
      try {
        // Use the main WebSocket connection from the app
        // Notifications come through the existing ws_manager
        // This is handled by the main app WebSocket
      } catch (error) {
        console.error('WebSocket error:', error);
      }
    };
    
    connectWS();
    fetchNotifications();
    
    // Poll for notifications every 30 seconds
    const interval = setInterval(fetchNotifications, 30000);
    
    return () => {
      clearInterval(interval);
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [token, user, fetchNotifications]);

  // Handle click outside to close dropdown
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };
    
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Mark as read
  const handleMarkAsRead = async (notificationId) => {
    try {
      await fetch(`${API_URL}/api/notifications/${notificationId}/read`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setNotifications(prev => 
        prev.map(n => n.id === notificationId ? {...n, is_read: true} : n)
      );
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (error) {
      console.error('Error marking as read:', error);
    }
  };

  // Mark all as read
  const handleMarkAllAsRead = async () => {
    try {
      await fetch(`${API_URL}/api/notifications/read-all`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setNotifications(prev => prev.map(n => ({...n, is_read: true})));
      setUnreadCount(0);
    } catch (error) {
      console.error('Error marking all as read:', error);
    }
  };

  // Delete notification
  const handleDelete = async (notificationId) => {
    try {
      await fetch(`${API_URL}/api/notifications/${notificationId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` }
      });
      
      setNotifications(prev => prev.filter(n => n.id !== notificationId));
    } catch (error) {
      console.error('Error deleting notification:', error);
    }
  };

  // Handle notification click
  const handleNotificationClick = (notification) => {
    if (!notification.is_read) {
      handleMarkAsRead(notification.id);
    }
    
    if (notification.action_url) {
      navigate(notification.action_url);
      setIsOpen(false);
    }
  };

  // Format time
  const formatTime = (dateStr) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diff = now - date;
    
    if (diff < 60000) return 'À l\'instant';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}min`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h`;
    return date.toLocaleDateString('fr-FR');
  };

  if (!user) return null;

  return (
    <div className="relative" ref={dropdownRef}>
      {/* Bell Button */}
      <Button
        variant="ghost"
        size="icon"
        onClick={() => {
          setIsOpen(!isOpen);
          if (!isOpen) fetchNotifications();
        }}
        className="relative"
        data-testid="notifications-bell"
      >
        <Bell className="w-5 h-5 text-zinc-400 hover:text-white" />
        {unreadCount > 0 && (
          <Badge 
            className="absolute -top-1 -right-1 h-5 w-5 flex items-center justify-center p-0 bg-red-600 text-white text-xs"
          >
            {unreadCount > 9 ? '9+' : unreadCount}
          </Badge>
        )}
      </Button>

      {/* Dropdown */}
      {isOpen && (
        <div className="absolute right-0 mt-2 w-80 md:w-96 bg-zinc-900 border border-zinc-700 rounded-xl shadow-2xl z-50 overflow-hidden">
          {/* Header */}
          <div className="flex items-center justify-between px-4 py-3 border-b border-zinc-700">
            <h3 className="text-white font-semibold">Notifications</h3>
            {unreadCount > 0 && (
              <Button 
                variant="ghost" 
                size="sm" 
                onClick={handleMarkAllAsRead}
                className="text-xs text-zinc-400 hover:text-white"
              >
                <Check className="w-3 h-3 mr-1" />
                Tout lire
              </Button>
            )}
          </div>

          {/* Notifications List */}
          <div className="max-h-96 overflow-y-auto">
            {loading ? (
              <div className="p-8 text-center text-zinc-500">
                Chargement...
              </div>
            ) : notifications.length === 0 ? (
              <div className="p-8 text-center text-zinc-500">
                <Bell className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p>Aucune notification</p>
              </div>
            ) : (
              notifications.map(notification => (
                <div 
                  key={notification.id}
                  className={`flex items-start gap-3 px-4 py-3 border-b border-zinc-800 hover:bg-zinc-800/50 cursor-pointer transition-colors ${
                    !notification.is_read ? 'bg-zinc-800/30' : ''
                  }`}
                  onClick={() => handleNotificationClick(notification)}
                >
                  {/* Icon */}
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0 ${
                    notification.color === 'pink' ? 'bg-pink-600/20' :
                    notification.color === 'green' ? 'bg-emerald-600/20' :
                    notification.color === 'blue' ? 'bg-blue-600/20' :
                    notification.color === 'amber' ? 'bg-amber-600/20' :
                    notification.color === 'red' ? 'bg-red-600/20' :
                    notification.color === 'purple' ? 'bg-purple-600/20' :
                    'bg-zinc-700'
                  }`}>
                    <span className="text-lg">{notification.icon}</span>
                  </div>
                  
                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2">
                      <p className={`text-sm font-medium ${notification.is_read ? 'text-zinc-400' : 'text-white'}`}>
                        {notification.title}
                      </p>
                      {!notification.is_read && (
                        <div className="w-2 h-2 rounded-full bg-amber-500 flex-shrink-0 mt-1.5" />
                      )}
                    </div>
                    <p className="text-xs text-zinc-500 mt-0.5 line-clamp-2">{notification.message}</p>
                    <p className="text-xs text-zinc-600 mt-1">{formatTime(notification.created_at)}</p>
                  </div>
                  
                  {/* Actions */}
                  <div className="flex-shrink-0">
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-6 w-6 text-zinc-500 hover:text-red-400"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDelete(notification.id);
                      }}
                    >
                      <X className="w-3 h-3" />
                    </Button>
                  </div>
                </div>
              ))
            )}
          </div>

          {/* Footer */}
          {notifications.length > 0 && (
            <div className="px-4 py-2 border-t border-zinc-700">
              <Button 
                variant="ghost" 
                size="sm" 
                className="w-full text-xs text-zinc-400 hover:text-white"
                onClick={() => {
                  navigate('/notifications');
                  setIsOpen(false);
                }}
              >
                Voir toutes les notifications
                <ExternalLink className="w-3 h-3 ml-1" />
              </Button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
