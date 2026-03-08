import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { 
  ArrowLeft, MapPin, Users, Calendar, MessageSquare, UserPlus, 
  UserMinus, Heart, MessageCircle, Share2, Linkedin, Instagram, 
  Twitter, Globe, Clock, CheckCircle, XCircle, Loader2
} from 'lucide-react';
import { clientProfileAPI, friendsAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';
import { toast } from 'sonner';

const ClientProfilePage = () => {
  const { userId } = useParams();
  const navigate = useNavigate();
  const { user: currentUser } = useAuth();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState(false);

  useEffect(() => {
    fetchProfile();
  }, [userId]);

  const fetchProfile = async () => {
    try {
      setLoading(true);
      const res = await clientProfileAPI.getPublic(userId);
      setProfile(res.data);
    } catch (error) {
      console.error('Error fetching profile:', error);
      toast.error('Profil non trouvé');
      navigate(-1);
    } finally {
      setLoading(false);
    }
  };

  const handleSendFriendRequest = async () => {
    try {
      setActionLoading(true);
      await friendsAPI.sendRequest(userId);
      toast.success('Demande d\'ami envoyée');
      fetchProfile();
    } catch (error) {
      toast.error('Erreur lors de l\'envoi de la demande');
    } finally {
      setActionLoading(false);
    }
  };

  const handleSendMessage = () => {
    // Navigate to messages with this user
    navigate(`/dashboard/client?tab=messages&user=${userId}`);
  };

  const formatDate = (dateStr) => {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    return date.toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' });
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#050505] pt-24 flex items-center justify-center">
        <div className="w-16 h-16 border-4 border-[#0047AB] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="min-h-screen bg-[#050505] pt-24 flex items-center justify-center">
        <p className="text-gray-400">Profil non trouvé</p>
      </div>
    );
  }

  const { user, stats, is_friend, pending_request, feed_posts } = profile;

  return (
    <div className="min-h-screen bg-[#050505] pt-20" data-testid="client-profile-page">
      {/* Header with Cover Image */}
      <div className="relative">
        {/* Cover Image */}
        <div className="h-48 md:h-64 bg-gradient-to-br from-[#0047AB]/30 to-[#1a1a2e] overflow-hidden">
          {user.cover_image ? (
            <img 
              src={user.cover_image.startsWith('http') ? user.cover_image : `${process.env.REACT_APP_BACKEND_URL}${user.cover_image}`}
              alt="Cover"
              className="w-full h-full object-cover"
            />
          ) : (
            <div className="w-full h-full bg-gradient-to-br from-[#0047AB]/20 via-[#1a1a2e] to-[#050505]" />
          )}
        </div>

        {/* Back Button */}
        <button 
          onClick={() => navigate(-1)}
          className="absolute top-4 left-4 p-2 bg-black/50 backdrop-blur-sm rounded-full text-white hover:bg-black/70 transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
        </button>

        {/* Profile Info Overlay */}
        <div className="max-w-4xl mx-auto px-4 -mt-16 relative z-10">
          <div className="flex flex-col md:flex-row items-start md:items-end gap-4">
            {/* Avatar */}
            <div className="w-32 h-32 rounded-full border-4 border-[#050505] bg-[#0047AB] flex items-center justify-center text-white text-3xl font-bold overflow-hidden shadow-xl">
              {user.avatar ? (
                <img 
                  src={user.avatar.startsWith('http') ? user.avatar : `${process.env.REACT_APP_BACKEND_URL}${user.avatar}`}
                  alt={`${user.first_name} ${user.last_name}`}
                  className="w-full h-full object-cover"
                />
              ) : (
                <>{user.first_name?.[0]}{user.last_name?.[0]}</>
              )}
            </div>

            {/* Name and Actions */}
            <div className="flex-1 flex flex-col md:flex-row md:items-center md:justify-between gap-4 pb-4">
              <div>
                <h1 className="text-2xl md:text-3xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
                  {user.first_name} {user.last_name}
                </h1>
                {user.city && (
                  <p className="text-gray-400 flex items-center gap-1 mt-1">
                    <MapPin className="w-4 h-4" />
                    {user.city}
                  </p>
                )}
              </div>

              {/* Action Buttons */}
              {currentUser?.id !== userId && (
                <div className="flex gap-3">
                  {is_friend ? (
                    <>
                      <button
                        onClick={handleSendMessage}
                        className="px-6 py-2.5 bg-[#0047AB] text-white rounded-xl font-medium hover:bg-[#0047AB]/80 transition-colors flex items-center gap-2"
                      >
                        <MessageSquare className="w-4 h-4" />
                        Message
                      </button>
                      <button className="px-4 py-2.5 bg-white/10 text-white rounded-xl font-medium hover:bg-white/20 transition-colors flex items-center gap-2">
                        <CheckCircle className="w-4 h-4 text-green-400" />
                        Ami
                      </button>
                    </>
                  ) : pending_request ? (
                    <button className="px-6 py-2.5 bg-yellow-500/20 text-yellow-400 rounded-xl font-medium flex items-center gap-2" disabled>
                      <Clock className="w-4 h-4" />
                      Demande envoyée
                    </button>
                  ) : (
                    <button
                      onClick={handleSendFriendRequest}
                      disabled={actionLoading}
                      className="px-6 py-2.5 bg-[#0047AB] text-white rounded-xl font-medium hover:bg-[#0047AB]/80 transition-colors flex items-center gap-2 disabled:opacity-50"
                    >
                      {actionLoading ? (
                        <Loader2 className="w-4 h-4 animate-spin" />
                      ) : (
                        <UserPlus className="w-4 h-4" />
                      )}
                      Ajouter
                    </button>
                  )}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Left Column - Info */}
          <div className="space-y-6">
            {/* Stats Card */}
            <div className="bg-[#0F0F0F] border border-white/10 rounded-2xl p-6">
              <div className="grid grid-cols-3 gap-4 text-center">
                <div>
                  <p className="text-2xl font-bold text-white">{stats.friends_count}</p>
                  <p className="text-xs text-gray-500">Amis</p>
                </div>
                <div className="border-x border-white/10">
                  <p className="text-2xl font-bold text-white">{stats.posts_count}</p>
                  <p className="text-xs text-gray-500">Posts</p>
                </div>
                <div>
                  <p className="text-2xl font-bold text-[#0047AB]">{stats.mutual_friends}</p>
                  <p className="text-xs text-gray-500">En commun</p>
                </div>
              </div>
            </div>

            {/* Bio Card */}
            {user.bio && (
              <div className="bg-[#0F0F0F] border border-white/10 rounded-2xl p-6">
                <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">À propos</h3>
                <p className="text-white text-sm leading-relaxed">{user.bio}</p>
              </div>
            )}

            {/* Social Links */}
            {(user.linkedin || user.instagram || user.twitter || user.website) && (
              <div className="bg-[#0F0F0F] border border-white/10 rounded-2xl p-6">
                <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">Réseaux sociaux</h3>
                <div className="space-y-3">
                  {user.linkedin && (
                    <a 
                      href={user.linkedin} 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="flex items-center gap-3 text-gray-300 hover:text-[#0077b5] transition-colors group"
                    >
                      <div className="w-10 h-10 rounded-xl bg-[#0077b5]/10 flex items-center justify-center group-hover:bg-[#0077b5]/20 transition-colors">
                        <Linkedin className="w-5 h-5" />
                      </div>
                      <span className="text-sm">LinkedIn</span>
                    </a>
                  )}
                  {user.instagram && (
                    <a 
                      href={user.instagram.startsWith('http') ? user.instagram : `https://instagram.com/${user.instagram}`}
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="flex items-center gap-3 text-gray-300 hover:text-[#E4405F] transition-colors group"
                    >
                      <div className="w-10 h-10 rounded-xl bg-[#E4405F]/10 flex items-center justify-center group-hover:bg-[#E4405F]/20 transition-colors">
                        <Instagram className="w-5 h-5" />
                      </div>
                      <span className="text-sm">Instagram</span>
                    </a>
                  )}
                  {user.twitter && (
                    <a 
                      href={user.twitter.startsWith('http') ? user.twitter : `https://twitter.com/${user.twitter}`}
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="flex items-center gap-3 text-gray-300 hover:text-[#1DA1F2] transition-colors group"
                    >
                      <div className="w-10 h-10 rounded-xl bg-[#1DA1F2]/10 flex items-center justify-center group-hover:bg-[#1DA1F2]/20 transition-colors">
                        <Twitter className="w-5 h-5" />
                      </div>
                      <span className="text-sm">Twitter</span>
                    </a>
                  )}
                  {user.website && (
                    <a 
                      href={user.website}
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="flex items-center gap-3 text-gray-300 hover:text-[#0047AB] transition-colors group"
                    >
                      <div className="w-10 h-10 rounded-xl bg-[#0047AB]/10 flex items-center justify-center group-hover:bg-[#0047AB]/20 transition-colors">
                        <Globe className="w-5 h-5" />
                      </div>
                      <span className="text-sm">Site web</span>
                    </a>
                  )}
                </div>
              </div>
            )}

            {/* Member Since */}
            <div className="bg-[#0F0F0F] border border-white/10 rounded-2xl p-6">
              <div className="flex items-center gap-3 text-gray-400">
                <Calendar className="w-5 h-5" />
                <span className="text-sm">Membre depuis {formatDate(user.created_at)}</span>
              </div>
            </div>
          </div>

          {/* Right Column - Feed */}
          <div className="md:col-span-2 space-y-6">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-bold text-white" style={{ fontFamily: 'Playfair Display, serif' }}>
                Publications
              </h2>
            </div>

            {feed_posts && feed_posts.length > 0 ? (
              <div className="space-y-4">
                {feed_posts.map((post) => (
                  <div key={post.id} className="bg-[#0F0F0F] border border-white/10 rounded-2xl p-6">
                    {/* Post Header */}
                    <div className="flex items-center gap-3 mb-4">
                      <div className="w-10 h-10 rounded-full bg-[#0047AB] flex items-center justify-center text-white font-bold overflow-hidden">
                        {user.avatar ? (
                          <img 
                            src={user.avatar.startsWith('http') ? user.avatar : `${process.env.REACT_APP_BACKEND_URL}${user.avatar}`}
                            alt=""
                            className="w-full h-full object-cover"
                          />
                        ) : (
                          <>{user.first_name?.[0]}{user.last_name?.[0]}</>
                        )}
                      </div>
                      <div className="flex-1">
                        <p className="text-white font-medium">{user.first_name} {user.last_name}</p>
                        <p className="text-xs text-gray-500">{formatDate(post.created_at)}</p>
                      </div>
                    </div>

                    {/* Post Content */}
                    <p className="text-gray-300 mb-4">{post.content}</p>

                    {/* Post Image */}
                    {post.image && (
                      <div className="rounded-xl overflow-hidden mb-4">
                        <img 
                          src={post.image.startsWith('http') ? post.image : `${process.env.REACT_APP_BACKEND_URL}${post.image}`}
                          alt=""
                          className="w-full object-cover max-h-96"
                        />
                      </div>
                    )}

                    {/* Post Actions */}
                    <div className="flex items-center gap-6 pt-4 border-t border-white/10">
                      <button className="flex items-center gap-2 text-gray-400 hover:text-red-400 transition-colors">
                        <Heart className={`w-5 h-5 ${post.is_liked ? 'fill-red-400 text-red-400' : ''}`} />
                        <span className="text-sm">{post.likes_count || 0}</span>
                      </button>
                      <button className="flex items-center gap-2 text-gray-400 hover:text-[#0047AB] transition-colors">
                        <MessageCircle className="w-5 h-5" />
                        <span className="text-sm">{post.comments_count || 0}</span>
                      </button>
                      <button className="flex items-center gap-2 text-gray-400 hover:text-white transition-colors">
                        <Share2 className="w-5 h-5" />
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="bg-[#0F0F0F] border border-white/10 rounded-2xl p-12 text-center">
                <MessageCircle className="w-12 h-12 text-gray-600 mx-auto mb-4" />
                <p className="text-gray-400">Aucune publication pour le moment</p>
                {!is_friend && (
                  <p className="text-gray-500 text-sm mt-2">Devenez amis pour voir plus de contenu</p>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ClientProfilePage;
