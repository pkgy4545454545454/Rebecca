import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Briefcase, MapPin, Clock, Building2, Filter, Search, ChevronRight } from 'lucide-react';
import { jobsAPI } from '../services/api';

const JobsPage = () => {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    type: '',
    location: '',
    search: ''
  });

  useEffect(() => {
    const fetchJobs = async () => {
      try {
        const res = await jobsAPI.listAll();
        setJobs(res.data || []);
      } catch (error) {
        console.error('Error fetching jobs:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchJobs();
  }, []);

  const filteredJobs = jobs.filter(job => {
    const matchesType = !filters.type || job.job_type === filters.type;
    const matchesLocation = !filters.location || job.location?.toLowerCase().includes(filters.location.toLowerCase());
    const matchesSearch = !filters.search || 
      job.title?.toLowerCase().includes(filters.search.toLowerCase()) ||
      job.enterprise_name?.toLowerCase().includes(filters.search.toLowerCase());
    return matchesType && matchesLocation && matchesSearch;
  });

  const jobTypeLabels = {
    'full_time': 'CDI',
    'part_time': 'Temps partiel',
    'contract': 'CDD',
    'internship': 'Stage',
    'freelance': 'Freelance'
  };

  return (
    <div className="min-h-screen bg-[#050505] pt-24 pb-16">
      {/* Hero Section */}
      <div className="relative h-[300px] mb-12">
        <div 
          className="absolute inset-0 bg-cover bg-center"
          style={{ backgroundImage: 'url(https://images.unsplash.com/photo-1497366216548-37526070297c?w=1920&q=80)' }}
        >
          <div className="absolute inset-0 bg-gradient-to-b from-black/70 via-black/50 to-[#050505]" />
        </div>
        <div className="relative z-10 max-w-7xl mx-auto px-4 md:px-8 h-full flex flex-col justify-center">
          <h1 className="text-4xl md:text-5xl font-bold text-white mb-4" style={{ fontFamily: 'Playfair Display, serif' }}>
            Offres d'emploi
          </h1>
          <p className="text-lg text-gray-300 max-w-2xl">
            Découvrez les opportunités de carrière chez nos partenaires premium
          </p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 md:px-8">
        {/* Filters */}
        <div className="card-service rounded-xl p-4 mb-8">
          <div className="flex flex-wrap gap-4 items-center">
            <div className="flex-1 min-w-[200px] relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
              <input
                type="text"
                placeholder="Rechercher un poste..."
                value={filters.search}
                onChange={(e) => setFilters({...filters, search: e.target.value})}
                className="input-dark w-full pl-10"
              />
            </div>
            <select
              value={filters.type}
              onChange={(e) => setFilters({...filters, type: e.target.value})}
              className="input-dark min-w-[150px]"
            >
              <option value="">Tous les types</option>
              <option value="full_time">CDI</option>
              <option value="part_time">Temps partiel</option>
              <option value="contract">CDD</option>
              <option value="internship">Stage</option>
              <option value="freelance">Freelance</option>
            </select>
            <input
              type="text"
              placeholder="Ville..."
              value={filters.location}
              onChange={(e) => setFilters({...filters, location: e.target.value})}
              className="input-dark min-w-[150px]"
            />
          </div>
        </div>

        {/* Results */}
        <div className="mb-4 text-gray-400">
          {filteredJobs.length} offre{filteredJobs.length > 1 ? 's' : ''} trouvée{filteredJobs.length > 1 ? 's' : ''}
        </div>

        {/* Jobs Grid */}
        {loading ? (
          <div className="flex justify-center py-20">
            <div className="w-12 h-12 border-4 border-[#0047AB] border-t-transparent rounded-full animate-spin" />
          </div>
        ) : filteredJobs.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredJobs.map((job) => (
              <Link 
                key={job.id} 
                to={`/emploi/${job.id}`}
                className="card-service rounded-xl p-6 hover:scale-[1.02] transition-transform"
                data-testid={`job-card-${job.id}`}
              >
                <div className="flex items-start gap-4 mb-4">
                  <div className="w-14 h-14 rounded-xl bg-[#0047AB]/20 flex items-center justify-center overflow-hidden flex-shrink-0">
                    {job.enterprise_logo ? (
                      <img 
                        src={job.enterprise_logo.startsWith('http') ? job.enterprise_logo : `${process.env.REACT_APP_BACKEND_URL}${job.enterprise_logo}`}
                        alt={job.enterprise_name}
                        className="w-full h-full object-cover"
                      />
                    ) : (
                      <Briefcase className="w-6 h-6 text-[#0047AB]" />
                    )}
                  </div>
                  <div className="flex-1 min-w-0">
                    <h3 className="text-lg font-semibold text-white truncate">{job.title}</h3>
                    <p className="text-sm text-[#D4AF37]">{job.enterprise_name}</p>
                  </div>
                </div>

                <div className="flex flex-wrap gap-2 mb-4">
                  <span className="px-3 py-1 bg-[#0047AB]/20 text-[#0047AB] rounded-full text-xs font-medium">
                    {jobTypeLabels[job.job_type] || job.job_type}
                  </span>
                  {job.salary && (
                    <span className="px-3 py-1 bg-green-500/20 text-green-400 rounded-full text-xs font-medium">
                      {job.salary}
                    </span>
                  )}
                </div>

                <div className="flex items-center gap-4 text-sm text-gray-400">
                  <span className="flex items-center gap-1">
                    <MapPin className="w-4 h-4" />
                    {job.location || 'Lausanne'}
                  </span>
                  <span className="flex items-center gap-1">
                    <Clock className="w-4 h-4" />
                    {new Date(job.created_at).toLocaleDateString('fr-FR')}
                  </span>
                </div>

                <div className="mt-4 pt-4 border-t border-white/10 flex justify-end">
                  <span className="text-[#0047AB] text-sm font-medium flex items-center gap-1">
                    Voir l'offre
                    <ChevronRight className="w-4 h-4" />
                  </span>
                </div>
              </Link>
            ))}
          </div>
        ) : (
          <div className="card-service rounded-xl p-12 text-center">
            <Briefcase className="w-16 h-16 text-gray-600 mx-auto mb-4" />
            <h2 className="text-xl font-bold text-white mb-2">Aucune offre trouvée</h2>
            <p className="text-gray-400">Modifiez vos filtres ou revenez plus tard</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default JobsPage;
