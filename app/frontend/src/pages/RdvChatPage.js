/**
 * RDV Chat Page - Real-time messaging for Rdv chez Titelli
 */
import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, useParams } from 'react-router-dom';
import Header from '../components/Header';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Card } from '../components/ui/card';
import { toast } from 'sonner';
import { 
  Send, ArrowLeft, User, Clock, Heart, Users, 
  MessageCircle, MoreVertical
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL || '';
const WS_URL = API_URL ? API_URL.replace('https://', 'wss://').replace('http://', 'ws://') : '';

export default function RdvChatPage() {
  const { user, token } = useAuth();
  const { roomId } = useParams();
  const navigate = useNavigate();
  
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [room, setRoom] = useState(null);
  const [loading, setLoading] = useState(true);
  const [connected, setConnected] = useState(false);
  const [otherParticipant, setOtherParticipant] = useState(null);
  const [isTyping, setIsTyping] = useState(false);
  
  const messagesEndRef = useRef(null);
  const wsRef = useRef(null);
  const typingTimeoutRef = useRef(null);

  // Scroll to bottom
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Fetch room info and messages
  const fetchRoomData = useCallback(async () => {
    if (!token || !roomId) return;
    
    try {
      setLoading(true);
      
      // Fetch rooms to get room info
      const roomsRes = await fetch(`${API_URL}/api/rdv/chat/rooms`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (roomsRes.ok) {
        const data = await roomsRes.json();
        const currentRoom = data.rooms?.find(r => r.id === roomId);
        if (currentRoom) {
          setRoom(currentRoom);
          setOtherParticipant(currentRoom.other_participant);
        }
      }
      
      // Fetch messages
      const messagesRes = await fetch(`${API_URL}/api/rdv/chat/rooms/${roomId}/messages?limit=100`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (messagesRes.ok) {
        const data = await messagesRes.json();
        setMessages(data.messages || []);
      }
      
    } catch (error) {
      console.error('Error fetching room data:', error);
      toast.error('Erreur de chargement');
    } finally {
      setLoading(false);
    }
  }, [token, roomId]);

  // Connect WebSocket
  const connectWebSocket = useCallback(() => {
    if (!token || !roomId) return;
    
    try {
      const wsUrl = `${WS_URL}/api/rdv/chat/ws/${roomId}?token=${token}`;
      const ws = new WebSocket(wsUrl);
      
      ws.onopen = () => {
        console.log('Chat WebSocket connected');
        setConnected(true);
      };
      
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.type === 'new_message') {
          setMessages(prev => [...prev, data.message]);
        } else if (data.type === 'typing') {
          if (data.user_id !== user?.id) {
            setIsTyping(true);
            if (typingTimeoutRef.current) {
              clearTimeout(typingTimeoutRef.current);
            }
            typingTimeoutRef.current = setTimeout(() => setIsTyping(false), 2000);
          }
        }
      };
      
      ws.onclose = () => {
        console.log('Chat WebSocket disconnected');
        setConnected(false);
        // Try to reconnect after 3 seconds
        setTimeout(connectWebSocket, 3000);
      };
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
      
      wsRef.current = ws;
      
    } catch (error) {
      console.error('WebSocket connection error:', error);
    }
  }, [token, roomId, user?.id]);

  useEffect(() => {
    if (!user) {
      navigate('/auth');
      return;
    }
    
    fetchRoomData();
    connectWebSocket();
    
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
      if (typingTimeoutRef.current) {
        clearTimeout(typingTimeoutRef.current);
      }
    };
  }, [user, navigate, fetchRoomData, connectWebSocket]);

  // Send message via WebSocket
  const sendMessage = async () => {
    if (!newMessage.trim()) return;
    
    const messageContent = newMessage.trim();
    setNewMessage('');
    
    // Try WebSocket first
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({
        type: 'message',
        content: messageContent
      }));
    } else {
      // Fallback to HTTP
      try {
        const res = await fetch(`${API_URL}/api/rdv/chat/rooms/${roomId}/messages`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`
          },
          body: JSON.stringify({ content: messageContent })
        });
        
        if (res.ok) {
          const data = await res.json();
          setMessages(prev => [...prev, data.message]);
        }
      } catch (error) {
        toast.error('Erreur d\'envoi');
      }
    }
  };

  // Send typing indicator
  const handleTyping = () => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'typing' }));
    }
  };

  // Handle Enter key
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  if (!user) return null;

  return (
    <div className="min-h-screen bg-gradient-to-b from-zinc-950 via-zinc-900 to-zinc-950 flex flex-col">
      <Header />
      
      <main className="flex-1 pt-20 pb-4 px-4 flex flex-col max-w-4xl mx-auto w-full">
        {/* Chat Header */}
        <Card className="bg-zinc-800/50 border-zinc-700 p-4 mb-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button 
                variant="ghost" 
                size="icon"
                onClick={() => navigate('/rdv')}
              >
                <ArrowLeft className="w-5 h-5" />
              </Button>
              
              {otherParticipant ? (
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-zinc-700 overflow-hidden">
                    {otherParticipant.image ? (
                      <img src={otherParticipant.image} alt="" className="w-full h-full object-cover" />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center">
                        <User className="w-5 h-5 text-zinc-400" />
                      </div>
                    )}
                  </div>
                  <div>
                    <h2 className="text-white font-semibold">{otherParticipant.name}</h2>
                    <div className="flex items-center gap-2 text-xs text-zinc-400">
                      {room?.offer?.offer_type === 'romantic' ? (
                        <Heart className="w-3 h-3 text-pink-400" />
                      ) : (
                        <Users className="w-3 h-3 text-emerald-400" />
                      )}
                      <span>{room?.offer?.title || 'Chat'}</span>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-zinc-700 flex items-center justify-center">
                    <MessageCircle className="w-5 h-5 text-zinc-400" />
                  </div>
                  <h2 className="text-white font-semibold">Chat</h2>
                </div>
              )}
            </div>
            
            <div className="flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${connected ? 'bg-emerald-400' : 'bg-red-400'}`} />
              <span className="text-xs text-zinc-400">
                {connected ? 'Connecté' : 'Déconnecté'}
              </span>
            </div>
          </div>
        </Card>

        {/* Messages Container */}
        <Card className="bg-zinc-800/30 border-zinc-700 flex-1 overflow-hidden flex flex-col">
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {loading ? (
              <div className="text-center py-8 text-zinc-400">
                Chargement des messages...
              </div>
            ) : messages.length === 0 ? (
              <div className="text-center py-8 text-zinc-400">
                <MessageCircle className="w-12 h-12 mx-auto mb-4 opacity-50" />
                <p>Aucun message pour le moment</p>
                <p className="text-sm">Commencez la conversation !</p>
              </div>
            ) : (
              <>
                {messages.map((msg, index) => {
                  const isOwnMessage = msg.sender_id === user.id;
                  const showAvatar = index === 0 || messages[index - 1]?.sender_id !== msg.sender_id;
                  
                  return (
                    <div 
                      key={msg.id || index}
                      className={`flex ${isOwnMessage ? 'justify-end' : 'justify-start'}`}
                    >
                      <div className={`flex items-end gap-2 max-w-[75%] ${isOwnMessage ? 'flex-row-reverse' : ''}`}>
                        {!isOwnMessage && showAvatar && (
                          <div className="w-8 h-8 rounded-full bg-zinc-700 overflow-hidden flex-shrink-0">
                            {msg.sender_image ? (
                              <img src={msg.sender_image} alt="" className="w-full h-full object-cover" />
                            ) : (
                              <div className="w-full h-full flex items-center justify-center text-xs text-zinc-400">
                                {msg.sender_name?.charAt(0) || '?'}
                              </div>
                            )}
                          </div>
                        )}
                        {!isOwnMessage && !showAvatar && <div className="w-8" />}
                        
                        <div className={`rounded-2xl px-4 py-2 ${
                          isOwnMessage 
                            ? 'bg-amber-600 text-white' 
                            : 'bg-zinc-700 text-white'
                        }`}>
                          {!isOwnMessage && showAvatar && (
                            <div className="text-xs text-zinc-300 mb-1 font-medium">
                              {msg.sender_name}
                            </div>
                          )}
                          <p className="break-words">{msg.content}</p>
                          <div className={`text-xs mt-1 ${isOwnMessage ? 'text-amber-200' : 'text-zinc-400'}`}>
                            {msg.created_at && new Date(msg.created_at).toLocaleTimeString('fr-FR', {
                              hour: '2-digit',
                              minute: '2-digit'
                            })}
                          </div>
                        </div>
                      </div>
                    </div>
                  );
                })}
                
                {isTyping && (
                  <div className="flex items-center gap-2 text-zinc-400 text-sm">
                    <div className="flex gap-1">
                      <span className="w-2 h-2 bg-zinc-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                      <span className="w-2 h-2 bg-zinc-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                      <span className="w-2 h-2 bg-zinc-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                    </div>
                    <span>écrit...</span>
                  </div>
                )}
                
                <div ref={messagesEndRef} />
              </>
            )}
          </div>

          {/* Message Input */}
          <div className="p-4 border-t border-zinc-700">
            <div className="flex gap-2">
              <Input
                value={newMessage}
                onChange={(e) => {
                  setNewMessage(e.target.value);
                  handleTyping();
                }}
                onKeyPress={handleKeyPress}
                placeholder="Écrivez un message..."
                className="bg-zinc-800 border-zinc-600 text-white placeholder:text-zinc-500"
                disabled={!connected}
              />
              <Button 
                onClick={sendMessage}
                disabled={!newMessage.trim() || !connected}
                className="bg-amber-600 hover:bg-amber-700"
              >
                <Send className="w-5 h-5" />
              </Button>
            </div>
          </div>
        </Card>
      </main>
    </div>
  );
}
