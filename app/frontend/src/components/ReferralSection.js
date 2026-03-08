/**
 * Referral/Parrainage Component for Titelli
 * Allows users to share their referral code and track referrals
 */
import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Input } from './ui/input';
import { toast } from 'sonner';
import { 
  Gift, Copy, Share2, Users, Trophy, Star, 
  CheckCircle, ArrowRight, Sparkles, Crown
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

export default function ReferralSection() {
  const { token } = useAuth();
  const [referralData, setReferralData] = useState(null);
  const [stats, setStats] = useState(null);
  const [leaderboard, setLeaderboard] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showLeaderboard, setShowLeaderboard] = useState(false);

  const fetchReferralData = useCallback(async () => {
    if (!token) return;
    
    try {
      setLoading(true);
      
      // Get referral code
      const codeRes = await fetch(`${API_URL}/api/gamification/referral/my-code`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (codeRes.ok) {
        const data = await codeRes.json();
        setReferralData(data);
      }
      
      // Get detailed stats
      const statsRes = await fetch(`${API_URL}/api/gamification/referral/stats`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (statsRes.ok) {
        const data = await statsRes.json();
        setStats(data);
      }
      
    } catch (error) {
      console.error('Error fetching referral data:', error);
    } finally {
      setLoading(false);
    }
  }, [token]);

  const fetchLeaderboard = async () => {
    try {
      const res = await fetch(`${API_URL}/api/gamification/referral/leaderboard?limit=10`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (res.ok) {
        const data = await res.json();
        setLeaderboard(data.leaderboard || []);
      }
    } catch (error) {
      console.error('Error fetching leaderboard:', error);
    }
  };

  useEffect(() => {
    fetchReferralData();
  }, [fetchReferralData]);

  useEffect(() => {
    if (showLeaderboard) {
      fetchLeaderboard();
    }
  }, [showLeaderboard, token]);

  const copyCode = () => {
    if (referralData?.code) {
      navigator.clipboard.writeText(referralData.code);
      toast.success('Code copié !');
    }
  };

  const copyLink = () => {
    if (referralData?.share_url) {
      navigator.clipboard.writeText(referralData.share_url);
      toast.success('Lien copié !');
    }
  };

  const shareReferral = async () => {
    if (navigator.share && referralData) {
      try {
        await navigator.share({
          title: 'Rejoins Titelli !',
          text: referralData.share_message,
          url: referralData.share_url
        });
      } catch (err) {
        // User cancelled or error
        copyLink();
      }
    } else {
      copyLink();
    }
  };

  if (loading) {
    return (
      <Card className="bg-zinc-800/50 border-zinc-700">
        <CardContent className="p-6 text-center">
          <div className="animate-pulse">Chargement...</div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {/* Main Referral Card */}
      <Card className="bg-gradient-to-br from-purple-900/40 to-zinc-900 border-purple-600/50">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Gift className="w-5 h-5 text-purple-400" />
              <CardTitle className="text-white">Parrainage</CardTitle>
            </div>
            <Badge className="bg-purple-600">
              <Sparkles className="w-3 h-3 mr-1" />
              +50 pts/parrainage
            </Badge>
          </div>
          <CardDescription className="text-zinc-400">
            Invitez vos amis et gagnez des points ensemble !
          </CardDescription>
        </CardHeader>
        
        <CardContent className="space-y-4">
          {/* Referral Code */}
          <div className="bg-zinc-800/50 rounded-lg p-4">
            <label className="text-xs text-zinc-400 block mb-2">Votre code de parrainage</label>
            <div className="flex items-center gap-2">
              <Input 
                value={referralData?.code || ''}
                readOnly
                className="bg-zinc-900 border-zinc-700 text-xl font-mono text-center tracking-widest text-purple-400"
              />
              <Button 
                variant="outline" 
                size="icon"
                onClick={copyCode}
                className="shrink-0"
              >
                <Copy className="w-4 h-4" />
              </Button>
            </div>
          </div>
          
          {/* Share Buttons */}
          <div className="grid grid-cols-2 gap-2">
            <Button 
              onClick={copyLink}
              variant="outline"
              className="bg-zinc-800/50"
            >
              <Copy className="w-4 h-4 mr-2" />
              Copier le lien
            </Button>
            <Button 
              onClick={shareReferral}
              className="bg-purple-600 hover:bg-purple-700"
            >
              <Share2 className="w-4 h-4 mr-2" />
              Partager
            </Button>
          </div>
          
          {/* Stats */}
          <div className="grid grid-cols-2 gap-4 pt-4 border-t border-zinc-700">
            <div className="text-center">
              <div className="text-2xl font-bold text-white">
                {stats?.referrals_count || 0}
              </div>
              <div className="text-xs text-zinc-400">Amis parrainés</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-400">
                +{stats?.total_points_earned || 0}
              </div>
              <div className="text-xs text-zinc-400">Points gagnés</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Rewards Card */}
      <Card className="bg-zinc-800/50 border-zinc-700">
        <CardHeader className="pb-2">
          <CardTitle className="text-white text-lg flex items-center gap-2">
            <Trophy className="w-5 h-5 text-amber-400" />
            Récompenses
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {/* Each referral */}
            <div className="flex items-center justify-between p-2 rounded bg-zinc-900/50">
              <div className="flex items-center gap-2">
                <Users className="w-4 h-4 text-zinc-400" />
                <span className="text-sm text-zinc-300">Chaque parrainage</span>
              </div>
              <Badge className="bg-purple-600/20 text-purple-400">+50 pts</Badge>
            </div>
            
            {/* 5 referrals bonus */}
            <div className={`flex items-center justify-between p-2 rounded ${
              stats?.bonuses_achieved?.['5_referrals'] ? 'bg-emerald-900/30 border border-emerald-600/50' : 'bg-zinc-900/50'
            }`}>
              <div className="flex items-center gap-2">
                {stats?.bonuses_achieved?.['5_referrals'] ? (
                  <CheckCircle className="w-4 h-4 text-emerald-400" />
                ) : (
                  <Star className="w-4 h-4 text-zinc-400" />
                )}
                <span className="text-sm text-zinc-300">5 parrainages</span>
              </div>
              <Badge className={stats?.bonuses_achieved?.['5_referrals'] 
                ? 'bg-emerald-600' 
                : 'bg-amber-600/20 text-amber-400'
              }>
                +100 pts bonus
              </Badge>
            </div>
            
            {/* 10 referrals bonus */}
            <div className={`flex items-center justify-between p-2 rounded ${
              stats?.bonuses_achieved?.['10_referrals'] ? 'bg-emerald-900/30 border border-emerald-600/50' : 'bg-zinc-900/50'
            }`}>
              <div className="flex items-center gap-2">
                {stats?.bonuses_achieved?.['10_referrals'] ? (
                  <CheckCircle className="w-4 h-4 text-emerald-400" />
                ) : (
                  <Star className="w-4 h-4 text-zinc-400" />
                )}
                <span className="text-sm text-zinc-300">10 parrainages</span>
              </div>
              <Badge className={stats?.bonuses_achieved?.['10_referrals'] 
                ? 'bg-emerald-600' 
                : 'bg-amber-600/20 text-amber-400'
              }>
                +250 pts bonus
              </Badge>
            </div>
            
            {/* 25 referrals bonus */}
            <div className={`flex items-center justify-between p-2 rounded ${
              stats?.bonuses_achieved?.['25_referrals'] ? 'bg-emerald-900/30 border border-emerald-600/50' : 'bg-zinc-900/50'
            }`}>
              <div className="flex items-center gap-2">
                {stats?.bonuses_achieved?.['25_referrals'] ? (
                  <CheckCircle className="w-4 h-4 text-emerald-400" />
                ) : (
                  <Crown className="w-4 h-4 text-amber-400" />
                )}
                <span className="text-sm text-zinc-300">25 parrainages</span>
              </div>
              <Badge className={stats?.bonuses_achieved?.['25_referrals'] 
                ? 'bg-emerald-600' 
                : 'bg-amber-600/20 text-amber-400'
              }>
                +500 pts bonus
              </Badge>
            </div>
          </div>
          
          {/* Next bonus progress */}
          {stats?.next_bonus && (
            <div className="mt-4 p-3 bg-zinc-900/50 rounded-lg">
              <div className="flex items-center justify-between text-sm">
                <span className="text-zinc-400">Prochain bonus</span>
                <span className="text-purple-400 font-medium">
                  {stats.referrals_count}/{stats.next_bonus.count} parrainages
                </span>
              </div>
              <div className="mt-2 h-2 bg-zinc-700 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-purple-600 transition-all"
                  style={{ 
                    width: `${Math.min(100, (stats.referrals_count / stats.next_bonus.count) * 100)}%` 
                  }}
                />
              </div>
              <div className="mt-1 text-xs text-zinc-500 text-right">
                Encore {stats.next_bonus.remaining} pour +{stats.next_bonus.points} pts
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Recent Referrals */}
      {stats?.referrals?.length > 0 && (
        <Card className="bg-zinc-800/50 border-zinc-700">
          <CardHeader className="pb-2">
            <CardTitle className="text-white text-lg">Parrainages récents</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {stats.referrals.map((ref, i) => (
                <div key={i} className="flex items-center justify-between p-2 bg-zinc-900/50 rounded">
                  <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-full bg-purple-600/20 flex items-center justify-center">
                      <Users className="w-4 h-4 text-purple-400" />
                    </div>
                    <div>
                      <div className="text-sm text-white">{ref.name}</div>
                      <div className="text-xs text-zinc-500">
                        {new Date(ref.joined_at).toLocaleDateString('fr-FR')}
                      </div>
                    </div>
                  </div>
                  <Badge className="bg-emerald-600/20 text-emerald-400">
                    +{ref.points_earned} pts
                  </Badge>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Leaderboard Toggle */}
      <Button 
        variant="outline" 
        className="w-full"
        onClick={() => setShowLeaderboard(!showLeaderboard)}
      >
        <Trophy className="w-4 h-4 mr-2" />
        {showLeaderboard ? 'Masquer' : 'Voir'} le classement des parrains
        <ArrowRight className={`w-4 h-4 ml-2 transition-transform ${showLeaderboard ? 'rotate-90' : ''}`} />
      </Button>

      {/* Leaderboard */}
      {showLeaderboard && leaderboard.length > 0 && (
        <Card className="bg-zinc-800/50 border-zinc-700">
          <CardHeader className="pb-2">
            <CardTitle className="text-white text-lg flex items-center gap-2">
              <Trophy className="w-5 h-5 text-amber-400" />
              Top Parrains
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              {leaderboard.map((user, i) => (
                <div 
                  key={i} 
                  className={`flex items-center justify-between p-2 rounded ${
                    i === 0 ? 'bg-amber-900/30 border border-amber-600/50' :
                    i === 1 ? 'bg-zinc-700/50 border border-zinc-600/50' :
                    i === 2 ? 'bg-amber-800/20 border border-amber-700/30' :
                    'bg-zinc-900/50'
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${
                      i === 0 ? 'bg-amber-500 text-black' :
                      i === 1 ? 'bg-zinc-400 text-black' :
                      i === 2 ? 'bg-amber-700 text-white' :
                      'bg-zinc-700 text-zinc-300'
                    }`}>
                      {user.rank}
                    </div>
                    <span className="text-white">{user.name}</span>
                  </div>
                  <div className="text-right">
                    <div className="text-sm text-white font-medium">{user.referrals_count} parrainages</div>
                    <div className="text-xs text-purple-400">+{user.total_points} pts</div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Share Message */}
      <div className="text-center text-xs text-zinc-500 px-4">
        Partagez votre code avec vos amis. Quand ils s'inscrivent, vous gagnez tous les deux des points !
      </div>
    </div>
  );
}
