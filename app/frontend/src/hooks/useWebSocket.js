import { useState, useEffect, useCallback, useRef } from 'react';
import { useAuth } from '../context/AuthContext';
import { toast } from 'sonner';

// Détecter si on est sur Render (qui ne supporte pas bien les WebSockets)
const isRenderHost = () => {
  const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
  return backendUrl.includes('onrender.com') || backendUrl.includes('render.com');
};

/**
 * Hook pour gérer les notifications - utilise polling HTTP sur Render, WebSocket ailleurs.
 */
export const useNotificationWebSocket = () => {
  const { user, isAuthenticated } = useAuth();
  const [isConnected, setIsConnected] = useState(false);
  const [unreadCount, setUnreadCount] = useState(0);
  const [notifications, setNotifications] = useState([]);
  const wsRef = useRef(null);
  const pollingRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 3;
  const baseReconnectDelay = 5000; // 5 seconds minimum

  // Utiliser polling sur Render
  const usePolling = isRenderHost();

  // Polling HTTP pour les notifications
  const pollNotifications = useCallback(async () => {
    if (!isAuthenticated) return;
    
    const token = localStorage.getItem('titelli_token');
    if (!token) return;

    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
      const response = await fetch(`${backendUrl}/api/notifications?unread_only=false`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setNotifications(data.notifications || []);
        setUnreadCount(data.unread_count || 0);
        setIsConnected(true);
      }
    } catch (error) {
      console.error('Error polling notifications:', error);
    }
  }, [isAuthenticated]);

  // Démarrer le polling
  const startPolling = useCallback(() => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current);
    }
    
    // Poll immédiatement, puis toutes les 30 secondes
    pollNotifications();
    pollingRef.current = setInterval(pollNotifications, 30000);
    setIsConnected(true);
  }, [pollNotifications]);

  // Arrêter le polling
  const stopPolling = useCallback(() => {
    if (pollingRef.current) {
      clearInterval(pollingRef.current);
      pollingRef.current = null;
    }
    setIsConnected(false);
  }, []);

  // Construire l'URL WebSocket
  const getWebSocketUrl = useCallback(() => {
    const token = localStorage.getItem('titelli_token');
    if (!token) return null;

    const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
    const wsProtocol = backendUrl.startsWith('https') ? 'wss' : 'ws';
    const wsHost = backendUrl.replace(/^https?:\/\//, '');
    
    return `${wsProtocol}://${wsHost}/ws/notifications?token=${token}`;
  }, []);

  // Gestionnaire de messages WebSocket
  const handleMessage = useCallback((event) => {
    try {
      const data = JSON.parse(event.data);
      
      if (data.type === 'ping') {
        if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
          wsRef.current.send(JSON.stringify({ type: 'pong' }));
        }
        return;
      }
      
      if (data.type === 'notification') {
        if (data.action === 'new') {
          const notif = data.notification;
          setNotifications(prev => [notif, ...prev]);
          setUnreadCount(prev => prev + 1);
          
          toast(notif.title, {
            description: notif.message,
            duration: 5000,
            action: notif.link ? {
              label: 'Voir',
              onClick: () => window.location.href = notif.link
            } : undefined
          });
        } else if (data.action === 'count_update') {
          setUnreadCount(data.unread_count);
        } else if (data.action === 'list') {
          setNotifications(data.notifications || []);
        }
      }
    } catch (error) {
      console.error('Error parsing WebSocket message:', error);
    }
  }, []);

  // Connecter au WebSocket (seulement si pas sur Render)
  const connect = useCallback(() => {
    if (usePolling) {
      startPolling();
      return;
    }

    const url = getWebSocketUrl();
    if (!url || !isAuthenticated) return;

    if (wsRef.current) {
      wsRef.current.close();
    }

    const ws = new WebSocket(url);

    ws.onopen = () => {
      setIsConnected(true);
      reconnectAttempts.current = 0;
    };

    ws.onmessage = handleMessage;

    ws.onclose = (event) => {
      setIsConnected(false);
      
      if (event.code !== 1000 && isAuthenticated && reconnectAttempts.current < maxReconnectAttempts) {
        const delay = baseReconnectDelay * Math.pow(2, reconnectAttempts.current);
        reconnectTimeoutRef.current = setTimeout(() => {
          reconnectAttempts.current++;
          connect();
        }, delay);
      }
    };

    ws.onerror = () => {
      setIsConnected(false);
    };

    wsRef.current = ws;
  }, [getWebSocketUrl, isAuthenticated, handleMessage, usePolling, startPolling]);

  // Déconnecter
  const disconnect = useCallback(() => {
    if (usePolling) {
      stopPolling();
      return;
    }

    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (wsRef.current) {
      wsRef.current.close(1000, 'User disconnected');
      wsRef.current = null;
    }
    setIsConnected(false);
  }, [usePolling, stopPolling]);

  // Marquer une notification comme lue
  const markRead = useCallback(async (notificationId) => {
    const token = localStorage.getItem('titelli_token');
    if (!token) return;

    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
      await fetch(`${backendUrl}/api/notifications/${notificationId}/read`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      setNotifications(prev => 
        prev.map(n => n.id === notificationId ? { ...n, is_read: true } : n)
      );
      setUnreadCount(prev => Math.max(0, prev - 1));
    } catch (error) {
      console.error('Error marking notification as read:', error);
    }
  }, []);

  // Marquer toutes comme lues
  const markAllRead = useCallback(async () => {
    const token = localStorage.getItem('titelli_token');
    if (!token) return;

    try {
      const backendUrl = process.env.REACT_APP_BACKEND_URL || '';
      await fetch(`${backendUrl}/api/notifications/read-all`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      setNotifications(prev => prev.map(n => ({ ...n, is_read: true })));
      setUnreadCount(0);
    } catch (error) {
      console.error('Error marking all as read:', error);
    }
  }, []);

  // Rafraîchir les notifications
  const fetchNotifications = useCallback(() => {
    pollNotifications();
  }, [pollNotifications]);

  // Connexion automatique
  useEffect(() => {
    if (isAuthenticated && user) {
      connect();
    } else {
      disconnect();
    }

    return () => {
      disconnect();
    };
  }, [isAuthenticated, user, connect, disconnect]);

  // Nettoyage
  useEffect(() => {
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (pollingRef.current) {
        clearInterval(pollingRef.current);
      }
    };
  }, []);

  return {
    isConnected,
    unreadCount,
    notifications,
    markRead,
    markAllRead,
    fetchNotifications,
    reconnect: connect
  };
};

/**
 * Hook pour le statut de présence - désactivé sur Render.
 */
export const usePresenceWebSocket = () => {
  const [onlineFriends] = useState([]);
  const [isConnected] = useState(false);

  // Désactivé car Render ne supporte pas bien les WebSockets
  return {
    isConnected,
    onlineFriends
  };
};

export default useNotificationWebSocket;
