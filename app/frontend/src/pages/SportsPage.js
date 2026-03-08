/**
 * Sports & Competitions Page
 * - Find opponents
 * - Create/join matches
 * - Teams management
 * - Tournaments
 */
import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate } from 'react-router-dom';
import Header from '../components/Header';
import Footer from '../components/Footer';
import { Button } from '../components/ui/button';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '../components/ui/card';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '../components/ui/dialog';
import { Input } from '../components/ui/input';
import { Textarea } from '../components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { toast } from 'sonner';
import { 
  Users, Trophy, Calendar, MapPin, Clock, Plus, 
  UserPlus, Swords, Target, Medal, Flag
} from 'lucide-react';

const API_URL = process.env.REACT_APP_BACKEND_URL;

// Sport emoji mapping
const sportEmojis = {
  football: '⚽',
  tennis: '🎾',
  basketball: '🏀',
  volleyball: '🏐',
  badminton: '🏸',
  padel: '🎾',
  running: '🏃',
  swimming: '🏊',
  cycling: '🚴',
  fitness: '💪',
  other: '🏆'
};

export default function SportsPage() {
  const { user, token } = useAuth();
  const navigate = useNavigate();
  
  // State
  const [activeTab, setActiveTab] = useState('matches');
  const [matches, setMatches] = useState([]);
  const [myMatches, setMyMatches] = useState([]);
  const [teams, setTeams] = useState([]);
  const [competitions, setCompetitions] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedSport, setSelectedSport] = useState('all');
  
  // Modal states
  const [showMatchModal, setShowMatchModal] = useState(false);
  const [showTeamModal, setShowTeamModal] = useState(false);
  const [showCompetitionModal, setShowCompetitionModal] = useState(false);
  
  // Form states
  const [newMatch, setNewMatch] = useState({
    sport: 'football',
    title: '',
    match_type: 'friendly',
    location: '',
    date_time: '',
    max_players: 2,
    team_size: 1,
    description: '',
    looking_for: 'opponent'
  });
  
  const [newTeam, setNewTeam] = useState({
    name: '',
    sport: 'football',
    description: ''
  });
  
  const [newCompetition, setNewCompetition] = useState({
    name: '',
    sport: 'football',
    competition_type: 'knockout',
    max_teams: 8,
    entry_fee: 0,
    prize: '',
    description: ''
  });

  // Fetch data
  const fetchData = useCallback(async () => {
    try {
      setLoading(true);
      
      const headers = token ? { Authorization: `Bearer ${token}` } : {};
      
      const [matchesRes, teamsRes, compsRes, catsRes] = await Promise.all([
        fetch(`${API_URL}/api/sports/matches${selectedSport !== 'all' ? `?sport=${selectedSport}` : ''}`, { headers }),
        fetch(`${API_URL}/api/sports/teams${selectedSport !== 'all' ? `?sport=${selectedSport}` : ''}`),
        fetch(`${API_URL}/api/sports/competitions${selectedSport !== 'all' ? `?sport=${selectedSport}` : ''}`),
        fetch(`${API_URL}/api/sports/categories`)
      ]);
      
      if (matchesRes.ok) {
        const data = await matchesRes.json();
        setMatches(data.matches || []);
      }
      
      if (teamsRes.ok) {
        const data = await teamsRes.json();
        setTeams(data.teams || []);
      }
      
      if (compsRes.ok) {
        const data = await compsRes.json();
        setCompetitions(data.competitions || []);
      }
      
      if (catsRes.ok) {
        const data = await catsRes.json();
        setCategories(data.categories || []);
      }
      
      // Fetch my matches if logged in
      if (token) {
        const myMatchesRes = await fetch(`${API_URL}/api/sports/matches/my`, { headers });
        if (myMatchesRes.ok) {
          const data = await myMatchesRes.json();
          setMyMatches(data.matches || []);
        }
      }
      
    } catch (error) {
      console.error('Error fetching data:', error);
    } finally {
      setLoading(false);
    }
  }, [token, selectedSport]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  // Create match
  const handleCreateMatch = async () => {
    if (!user) {
      navigate('/auth');
      return;
    }
    
    if (!newMatch.title) {
      toast.error('Veuillez donner un titre à votre match');
      return;
    }
    
    try {
      const res = await fetch(`${API_URL}/api/sports/matches`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(newMatch)
      });
      
      if (res.ok) {
        toast.success('Match créé ! 🎉');
        setShowMatchModal(false);
        setNewMatch({
          sport: 'football',
          title: '',
          match_type: 'friendly',
          location: '',
          date_time: '',
          max_players: 2,
          team_size: 1,
          description: '',
          looking_for: 'opponent'
        });
        fetchData();
      } else {
        const data = await res.json();
        toast.error(data.detail || 'Erreur');
      }
    } catch (error) {
      toast.error('Erreur de connexion');
    }
  };

  // Join match
  const handleJoinMatch = async (matchId) => {
    if (!user) {
      navigate('/auth');
      return;
    }
    
    try {
      const res = await fetch(`${API_URL}/api/sports/matches/${matchId}/join`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (res.ok) {
        toast.success('Vous avez rejoint le match ! 🏆');
        fetchData();
      } else {
        const data = await res.json();
        toast.error(data.detail || 'Erreur');
      }
    } catch (error) {
      toast.error('Erreur de connexion');
    }
  };

  // Create team
  const handleCreateTeam = async () => {
    if (!user) {
      navigate('/auth');
      return;
    }
    
    if (!newTeam.name) {
      toast.error('Veuillez donner un nom à votre équipe');
      return;
    }
    
    try {
      const res = await fetch(`${API_URL}/api/sports/teams`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`
        },
        body: JSON.stringify(newTeam)
      });
      
      if (res.ok) {
        toast.success('Équipe créée ! 🏆');
        setShowTeamModal(false);
        setNewTeam({ name: '', sport: 'football', description: '' });
        fetchData();
      } else {
        const data = await res.json();
        toast.error(data.detail || 'Erreur');
      }
    } catch (error) {
      toast.error('Erreur de connexion');
    }
  };

  // Join team
  const handleJoinTeam = async (teamId) => {
    if (!user) {
      navigate('/auth');
      return;
    }
    
    try {
      const res = await fetch(`${API_URL}/api/sports/teams/${teamId}/join`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (res.ok) {
        toast.success('Vous avez rejoint l\'équipe !');
        fetchData();
      } else {
        const data = await res.json();
        toast.error(data.detail || 'Erreur');
      }
    } catch (error) {
      toast.error('Erreur de connexion');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-zinc-950 via-zinc-900 to-zinc-950">
      <Header />
      
      <main className="pt-24 pb-16 px-4 md:px-8">
        <div className="max-w-7xl mx-auto">
          
          {/* Hero */}
          <div className="text-center mb-12">
            <h1 className="text-4xl md:text-5xl font-bold text-white mb-4">
              Sports & <span className="text-amber-400">Compétitions</span>
            </h1>
            <p className="text-zinc-400 text-lg max-w-2xl mx-auto">
              Trouve un adversaire, rejoins un match ou crée ta propre compétition !
            </p>
          </div>

          {/* Sport Filter */}
          <div className="flex flex-wrap justify-center gap-2 mb-8">
            <Button
              variant={selectedSport === 'all' ? 'default' : 'outline'}
              size="sm"
              onClick={() => setSelectedSport('all')}
              className={selectedSport === 'all' ? 'bg-amber-600' : ''}
            >
              Tous
            </Button>
            {categories.slice(0, 8).map(cat => (
              <Button
                key={cat.id}
                variant={selectedSport === cat.id ? 'default' : 'outline'}
                size="sm"
                onClick={() => setSelectedSport(cat.id)}
                className={selectedSport === cat.id ? 'bg-amber-600' : ''}
              >
                {cat.icon} {cat.name}
              </Button>
            ))}
          </div>

          {/* Main Tabs */}
          <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
            <TabsList className="bg-zinc-800/50 border border-zinc-700">
              <TabsTrigger value="matches" className="data-[state=active]:bg-amber-600">
                <Swords className="w-4 h-4 mr-2" /> Matchs
              </TabsTrigger>
              <TabsTrigger value="teams" className="data-[state=active]:bg-amber-600">
                <Users className="w-4 h-4 mr-2" /> Équipes
              </TabsTrigger>
              <TabsTrigger value="competitions" className="data-[state=active]:bg-amber-600">
                <Trophy className="w-4 h-4 mr-2" /> Compétitions
              </TabsTrigger>
              {user && (
                <TabsTrigger value="my-matches" className="data-[state=active]:bg-amber-600">
                  <Target className="w-4 h-4 mr-2" /> Mes Matchs
                </TabsTrigger>
              )}
            </TabsList>

            {/* Matches Tab */}
            <TabsContent value="matches" className="space-y-6">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-semibold text-white">Matchs Disponibles</h2>
                <Button onClick={() => setShowMatchModal(true)} className="bg-amber-600 hover:bg-amber-700">
                  <Plus className="w-4 h-4 mr-2" />
                  Créer un match
                </Button>
              </div>
              
              {loading ? (
                <div className="text-center py-12 text-zinc-400">Chargement...</div>
              ) : matches.length === 0 ? (
                <Card className="bg-zinc-800/50 border-zinc-700">
                  <CardContent className="p-12 text-center">
                    <Swords className="w-12 h-12 text-zinc-500 mx-auto mb-4" />
                    <p className="text-zinc-400">Aucun match disponible pour le moment</p>
                    <Button 
                      onClick={() => setShowMatchModal(true)} 
                      className="mt-4 bg-amber-600 hover:bg-amber-700"
                    >
                      Créer le premier match
                    </Button>
                  </CardContent>
                </Card>
              ) : (
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {matches.map(match => (
                    <Card key={match.id} className="bg-zinc-800/50 border-zinc-700 hover:border-amber-600/50 transition-all">
                      <CardHeader className="pb-2">
                        <div className="flex items-start justify-between">
                          <div className="flex items-center gap-3">
                            <span className="text-3xl">{sportEmojis[match.sport] || '🏆'}</span>
                            <div>
                              <CardTitle className="text-white">{match.title}</CardTitle>
                              <CardDescription>par {match.creator_name}</CardDescription>
                            </div>
                          </div>
                          <Badge className={
                            match.looking_for === 'opponent' ? 'bg-red-600' :
                            match.looking_for === 'players' ? 'bg-amber-600' : 'bg-purple-600'
                          }>
                            {match.looking_for === 'opponent' ? 'Cherche adversaire' :
                             match.looking_for === 'players' ? 'Cherche joueurs' : 'Cherche équipe'}
                          </Badge>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <div className="flex flex-wrap gap-2 text-sm text-zinc-400 mb-3">
                          {match.location && (
                            <span className="flex items-center gap-1">
                              <MapPin className="w-3 h-3" /> {match.location}
                            </span>
                          )}
                          {match.date_time && (
                            <span className="flex items-center gap-1">
                              <Calendar className="w-3 h-3" /> 
                              {new Date(match.date_time).toLocaleDateString('fr-FR')}
                            </span>
                          )}
                          <span className="flex items-center gap-1">
                            <Users className="w-3 h-3" /> 
                            {match.participants?.length || 1}/{match.max_players}
                          </span>
                        </div>
                        {match.description && (
                          <p className="text-zinc-300 text-sm">{match.description}</p>
                        )}
                      </CardContent>
                      <CardFooter>
                        <Button 
                          className="w-full bg-emerald-600 hover:bg-emerald-700"
                          onClick={() => handleJoinMatch(match.id)}
                        >
                          <UserPlus className="w-4 h-4 mr-2" />
                          Rejoindre
                        </Button>
                      </CardFooter>
                    </Card>
                  ))}
                </div>
              )}
            </TabsContent>

            {/* Teams Tab */}
            <TabsContent value="teams" className="space-y-6">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-semibold text-white">Équipes</h2>
                <Button onClick={() => setShowTeamModal(true)} className="bg-amber-600 hover:bg-amber-700">
                  <Plus className="w-4 h-4 mr-2" />
                  Créer une équipe
                </Button>
              </div>
              
              {teams.length === 0 ? (
                <Card className="bg-zinc-800/50 border-zinc-700">
                  <CardContent className="p-12 text-center">
                    <Users className="w-12 h-12 text-zinc-500 mx-auto mb-4" />
                    <p className="text-zinc-400">Aucune équipe pour le moment</p>
                  </CardContent>
                </Card>
              ) : (
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {teams.map(team => (
                    <Card key={team.id} className="bg-zinc-800/50 border-zinc-700">
                      <CardHeader>
                        <div className="flex items-center gap-3">
                          <span className="text-3xl">{sportEmojis[team.sport] || '🏆'}</span>
                          <div>
                            <CardTitle className="text-white">{team.name}</CardTitle>
                            <CardDescription>{team.members?.length || 1} membre(s)</CardDescription>
                          </div>
                        </div>
                      </CardHeader>
                      <CardContent>
                        {team.description && (
                          <p className="text-zinc-300 text-sm mb-3">{team.description}</p>
                        )}
                        <div className="flex gap-4 text-sm">
                          <span className="text-emerald-400">✓ {team.wins || 0} V</span>
                          <span className="text-zinc-400">{team.draws || 0} N</span>
                          <span className="text-red-400">✗ {team.losses || 0} D</span>
                        </div>
                      </CardContent>
                      <CardFooter>
                        <Button 
                          className="w-full"
                          variant="outline"
                          onClick={() => handleJoinTeam(team.id)}
                        >
                          Rejoindre l'équipe
                        </Button>
                      </CardFooter>
                    </Card>
                  ))}
                </div>
              )}
            </TabsContent>

            {/* Competitions Tab */}
            <TabsContent value="competitions" className="space-y-6">
              <div className="flex justify-between items-center">
                <h2 className="text-xl font-semibold text-white">Compétitions & Tournois</h2>
                <Button onClick={() => setShowCompetitionModal(true)} className="bg-amber-600 hover:bg-amber-700">
                  <Plus className="w-4 h-4 mr-2" />
                  Organiser un tournoi
                </Button>
              </div>
              
              {competitions.length === 0 ? (
                <Card className="bg-zinc-800/50 border-zinc-700">
                  <CardContent className="p-12 text-center">
                    <Trophy className="w-12 h-12 text-zinc-500 mx-auto mb-4" />
                    <p className="text-zinc-400">Aucune compétition pour le moment</p>
                  </CardContent>
                </Card>
              ) : (
                <div className="grid md:grid-cols-2 gap-6">
                  {competitions.map(comp => (
                    <Card key={comp.id} className="bg-zinc-800/50 border-zinc-700">
                      <CardHeader>
                        <div className="flex items-start justify-between">
                          <div className="flex items-center gap-3">
                            <Trophy className="w-8 h-8 text-amber-400" />
                            <div>
                              <CardTitle className="text-white">{comp.name}</CardTitle>
                              <CardDescription>{sportEmojis[comp.sport]} {comp.sport}</CardDescription>
                            </div>
                          </div>
                          <Badge className={
                            comp.status === 'registration_open' ? 'bg-emerald-600' :
                            comp.status === 'in_progress' ? 'bg-amber-600' : 'bg-zinc-600'
                          }>
                            {comp.status === 'registration_open' ? 'Inscriptions ouvertes' :
                             comp.status === 'in_progress' ? 'En cours' : comp.status}
                          </Badge>
                        </div>
                      </CardHeader>
                      <CardContent>
                        <div className="grid grid-cols-2 gap-4 text-sm mb-3">
                          <div className="text-zinc-400">
                            <Users className="w-3 h-3 inline mr-1" />
                            {comp.registered_teams?.length || 0}/{comp.max_teams} équipes
                          </div>
                          {comp.entry_fee > 0 && (
                            <div className="text-amber-400">
                              {comp.entry_fee} CHF / équipe
                            </div>
                          )}
                          {comp.prize && (
                            <div className="text-emerald-400 col-span-2">
                              <Medal className="w-3 h-3 inline mr-1" />
                              Prix: {comp.prize}
                            </div>
                          )}
                        </div>
                        {comp.description && (
                          <p className="text-zinc-300 text-sm">{comp.description}</p>
                        )}
                      </CardContent>
                      <CardFooter>
                        <Button className="w-full bg-amber-600 hover:bg-amber-700">
                          <Flag className="w-4 h-4 mr-2" />
                          Inscrire mon équipe
                        </Button>
                      </CardFooter>
                    </Card>
                  ))}
                </div>
              )}
            </TabsContent>

            {/* My Matches Tab */}
            {user && (
              <TabsContent value="my-matches" className="space-y-6">
                <h2 className="text-xl font-semibold text-white">Mes Matchs</h2>
                
                {myMatches.length === 0 ? (
                  <Card className="bg-zinc-800/50 border-zinc-700">
                    <CardContent className="p-12 text-center">
                      <Target className="w-12 h-12 text-zinc-500 mx-auto mb-4" />
                      <p className="text-zinc-400">Vous n'avez pas encore de match</p>
                    </CardContent>
                  </Card>
                ) : (
                  <div className="space-y-4">
                    {myMatches.map(match => (
                      <Card key={match.id} className="bg-zinc-800/50 border-zinc-700">
                        <CardContent className="p-4">
                          <div className="flex items-center justify-between">
                            <div className="flex items-center gap-4">
                              <span className="text-3xl">{sportEmojis[match.sport] || '🏆'}</span>
                              <div>
                                <h3 className="text-white font-semibold">{match.title}</h3>
                                <p className="text-zinc-400 text-sm">
                                  {match.participants?.length || 1}/{match.max_players} joueurs
                                </p>
                              </div>
                            </div>
                            <Badge className={
                              match.status === 'confirmed' ? 'bg-emerald-600' :
                              match.status === 'open' ? 'bg-amber-600' : 'bg-zinc-600'
                            }>
                              {match.status === 'confirmed' ? 'Confirmé' :
                               match.status === 'open' ? 'En attente' : match.status}
                            </Badge>
                          </div>
                        </CardContent>
                      </Card>
                    ))}
                  </div>
                )}
              </TabsContent>
            )}
          </Tabs>
        </div>
      </main>

      {/* Create Match Modal */}
      <Dialog open={showMatchModal} onOpenChange={setShowMatchModal}>
        <DialogContent className="bg-zinc-900 border-zinc-700 text-white max-w-lg">
          <DialogHeader>
            <DialogTitle>Créer un match</DialogTitle>
            <DialogDescription className="text-zinc-400">
              Trouve un adversaire ou des joueurs
            </DialogDescription>
          </DialogHeader>
          
          <div className="space-y-4 py-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm text-zinc-400 mb-1 block">Sport</label>
                <Select
                  value={newMatch.sport}
                  onValueChange={(value) => setNewMatch({...newMatch, sport: value})}
                >
                  <SelectTrigger className="bg-zinc-800 border-zinc-700">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {categories.map(cat => (
                      <SelectItem key={cat.id} value={cat.id}>
                        {cat.icon} {cat.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
              <div>
                <label className="text-sm text-zinc-400 mb-1 block">Je cherche</label>
                <Select
                  value={newMatch.looking_for}
                  onValueChange={(value) => setNewMatch({...newMatch, looking_for: value})}
                >
                  <SelectTrigger className="bg-zinc-800 border-zinc-700">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="opponent">Un adversaire</SelectItem>
                    <SelectItem value="players">Des joueurs</SelectItem>
                    <SelectItem value="team">Une équipe</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            
            <div>
              <label className="text-sm text-zinc-400 mb-1 block">Titre du match *</label>
              <Input
                value={newMatch.title}
                onChange={(e) => setNewMatch({...newMatch, title: e.target.value})}
                placeholder="Ex: Match de foot 5v5 ce samedi"
                className="bg-zinc-800 border-zinc-700"
              />
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm text-zinc-400 mb-1 block">Lieu</label>
                <Input
                  value={newMatch.location}
                  onChange={(e) => setNewMatch({...newMatch, location: e.target.value})}
                  placeholder="Ex: Stade de la Pontaise"
                  className="bg-zinc-800 border-zinc-700"
                />
              </div>
              <div>
                <label className="text-sm text-zinc-400 mb-1 block">Date & Heure</label>
                <Input
                  type="datetime-local"
                  value={newMatch.date_time}
                  onChange={(e) => setNewMatch({...newMatch, date_time: e.target.value})}
                  className="bg-zinc-800 border-zinc-700"
                />
              </div>
            </div>
            
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="text-sm text-zinc-400 mb-1 block">Nombre de joueurs</label>
                <Input
                  type="number"
                  value={newMatch.max_players}
                  onChange={(e) => setNewMatch({...newMatch, max_players: parseInt(e.target.value) || 2})}
                  className="bg-zinc-800 border-zinc-700"
                />
              </div>
              <div>
                <label className="text-sm text-zinc-400 mb-1 block">Type</label>
                <Select
                  value={newMatch.match_type}
                  onValueChange={(value) => setNewMatch({...newMatch, match_type: value})}
                >
                  <SelectTrigger className="bg-zinc-800 border-zinc-700">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="friendly">Amical</SelectItem>
                    <SelectItem value="competition">Compétition</SelectItem>
                    <SelectItem value="tournament">Tournoi</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </div>
            
            <div>
              <label className="text-sm text-zinc-400 mb-1 block">Description</label>
              <Textarea
                value={newMatch.description}
                onChange={(e) => setNewMatch({...newMatch, description: e.target.value})}
                placeholder="Détails supplémentaires..."
                className="bg-zinc-800 border-zinc-700"
              />
            </div>
          </div>
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowMatchModal(false)}>
              Annuler
            </Button>
            <Button onClick={handleCreateMatch} className="bg-amber-600 hover:bg-amber-700">
              Créer le match
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Create Team Modal */}
      <Dialog open={showTeamModal} onOpenChange={setShowTeamModal}>
        <DialogContent className="bg-zinc-900 border-zinc-700 text-white max-w-md">
          <DialogHeader>
            <DialogTitle>Créer une équipe</DialogTitle>
          </DialogHeader>
          
          <div className="space-y-4 py-4">
            <div>
              <label className="text-sm text-zinc-400 mb-1 block">Nom de l'équipe *</label>
              <Input
                value={newTeam.name}
                onChange={(e) => setNewTeam({...newTeam, name: e.target.value})}
                placeholder="Ex: FC Lausanne Legends"
                className="bg-zinc-800 border-zinc-700"
              />
            </div>
            
            <div>
              <label className="text-sm text-zinc-400 mb-1 block">Sport</label>
              <Select
                value={newTeam.sport}
                onValueChange={(value) => setNewTeam({...newTeam, sport: value})}
              >
                <SelectTrigger className="bg-zinc-800 border-zinc-700">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {categories.map(cat => (
                    <SelectItem key={cat.id} value={cat.id}>
                      {cat.icon} {cat.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div>
              <label className="text-sm text-zinc-400 mb-1 block">Description</label>
              <Textarea
                value={newTeam.description}
                onChange={(e) => setNewTeam({...newTeam, description: e.target.value})}
                placeholder="Présentez votre équipe..."
                className="bg-zinc-800 border-zinc-700"
              />
            </div>
          </div>
          
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowTeamModal(false)}>
              Annuler
            </Button>
            <Button onClick={handleCreateTeam} className="bg-amber-600 hover:bg-amber-700">
              Créer l'équipe
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Footer />
    </div>
  );
}
