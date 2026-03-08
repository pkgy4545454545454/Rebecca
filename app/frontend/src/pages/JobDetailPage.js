import React, { useState, useEffect } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { 
  Briefcase, MapPin, Clock, Building2, ArrowLeft, Send, FileText, 
  Calendar, DollarSign, Users, CheckCircle, X, ChevronRight
} from 'lucide-react';
import { jobsAPI, clientDocumentsAPI } from '../services/api';
import { toast } from 'sonner';

const JobDetailPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [job, setJob] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showApplyModal, setShowApplyModal] = useState(false);
  const [userDocuments, setUserDocuments] = useState([]);
  const [applyForm, setApplyForm] = useState({
    resume_url: '',
    cover_letter: ''
  });
  const [applying, setApplying] = useState(false);

  useEffect(() => {
    fetchJob();
  }, [id]);

  const fetchJob = async () => {
    try {
      const response = await jobsAPI.getById(id);
      setJob(response.data);
    } catch (error) {
      console.error('Error fetching job:', error);
      toast.error('Offre non trouvée');
    } finally {
      setLoading(false);
    }
  };

  const handleApplyClick = async () => {
    const token = localStorage.getItem('titelli_token');
    if (!token) {
      toast.error('Connectez-vous pour postuler');
      navigate('/auth');
      return;
    }

    try {
      // Fetch all documents (not just CV category)
      const res = await clientDocumentsAPI.list();
      const allDocs = res.data?.documents || res.data || [];
      // Filter to show CV and PDF documents (useful for job applications)
      const relevantDocs = allDocs.filter(d => 
        d.category === 'cv' || d.category === 'general' || d.url?.includes('.pdf')
      );
      setUserDocuments(relevantDocs.length > 0 ? relevantDocs : allDocs);
    } catch (err) {
      console.error('Error fetching documents:', err);
      setUserDocuments([]);
    }
    setShowApplyModal(true);
  };

  const handleSubmitApplication = async () => {
    if (!applyForm.resume_url) {
      toast.error('Veuillez sélectionner un CV');
      return;
    }

    setApplying(true);
    try {
      await jobsAPI.apply(id, {
        resume_url: applyForm.resume_url,
        cover_letter: applyForm.cover_letter
      });
      toast.success('Candidature envoyée avec succès !');
      setShowApplyModal(false);
    } catch (error) {
      const msg = error.response?.data?.detail || 'Erreur lors de l\'envoi';
      toast.error(msg);
    } finally {
      setApplying(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-[#050505] pt-24 flex items-center justify-center">
        <div className="w-16 h-16 border-4 border-[#0047AB] border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (!job) {
    return (
      <div className="min-h-screen bg-[#050505] pt-24">
        <div className="max-w-4xl mx-auto px-4 py-16 text-center">
          <Briefcase className="w-16 h-16 text-gray-500 mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-white mb-2">Offre non trouvée</h1>
          <p className="text-gray-400 mb-6">Cette offre n'existe pas ou a été supprimée.</p>
          <Link to="/" className="btn-primary">Retour à l'accueil</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-[#050505] pt-24" data-testid="job-detail-page">
      {/* Hero Section with Video/Image Background */}
      <div className="relative h-[35vh] min-h-[280px] overflow-hidden">
        <div className="absolute inset-0">
          {job.cover_video ? (
            <video
              autoPlay
              muted
              loop
              playsInline
              className="w-full h-full object-cover"
            >
              <source src={job.cover_video} type="video/mp4" />
            </video>
          ) : (
            <img 
              src={job.cover_image || "https://images.unsplash.com/photo-1497366216548-37526070297c?w=1920&q=80"} 
              alt="" 
              className="w-full h-full object-cover"
            />
          )}
          <div className="absolute inset-0 bg-gradient-to-t from-[#050505] via-[#050505]/70 to-transparent" />
        </div>
        
        <div className="relative h-full flex items-end">
          <div className="max-w-4xl mx-auto px-4 md:px-8 w-full pb-8">
            <Link to="/" className="inline-flex items-center gap-2 text-gray-400 hover:text-white mb-4 transition-colors">
              <ArrowLeft className="w-4 h-4" />
              Retour aux offres
            </Link>
            <div className="flex items-center gap-3 mb-2">
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${
                job.type === 'CDI' ? 'bg-green-500/20 text-green-400' :
                job.type === 'CDD' ? 'bg-orange-500/20 text-orange-400' :
                job.type === 'Stage' ? 'bg-purple-500/20 text-purple-400' :
                job.type === 'Freelance' ? 'bg-cyan-500/20 text-cyan-400' :
                'bg-blue-500/20 text-blue-400'
              }`}>
                {job.type || 'CDI'}
              </span>
              {job.is_urgent && (
                <span className="px-3 py-1 bg-red-500/20 text-red-400 rounded-full text-sm font-medium">
                  Urgent
                </span>
              )}
            </div>
            <h1 className="text-3xl md:text-4xl font-bold text-white mb-2" style={{ fontFamily: 'Playfair Display, serif' }}>
              {job.title}
            </h1>
            <p className="text-xl text-[#D4AF37]">{job.enterprise_name}</p>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 md:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-8">
            {/* Quick Info */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="card-service rounded-xl p-4 text-center">
                <MapPin className="w-5 h-5 text-[#0047AB] mx-auto mb-2" />
                <p className="text-sm text-gray-400">Lieu</p>
                <p className="text-white font-medium">{job.location || 'Lausanne'}</p>
              </div>
              <div className="card-service rounded-xl p-4 text-center">
                <Clock className="w-5 h-5 text-[#0047AB] mx-auto mb-2" />
                <p className="text-sm text-gray-400">Type</p>
                <p className="text-white font-medium">{job.type || 'CDI'}</p>
              </div>
              <div className="card-service rounded-xl p-4 text-center">
                <DollarSign className="w-5 h-5 text-[#D4AF37] mx-auto mb-2" />
                <p className="text-sm text-gray-400">Salaire</p>
                <p className="text-white font-medium">{job.salary || 'À discuter'}</p>
              </div>
              <div className="card-service rounded-xl p-4 text-center">
                <Calendar className="w-5 h-5 text-purple-400 mx-auto mb-2" />
                <p className="text-sm text-gray-400">Début</p>
                <p className="text-white font-medium">{job.start_date || 'Dès que possible'}</p>
              </div>
            </div>

            {/* Description */}
            <div className="card-service rounded-xl p-6">
              <h2 className="text-xl font-bold text-white mb-4">Description du poste</h2>
              <div className="prose prose-invert max-w-none">
                <p className="text-gray-300 whitespace-pre-line">{job.description}</p>
              </div>
            </div>

            {/* Requirements */}
            {job.requirements && (
              <div className="card-service rounded-xl p-6">
                <h2 className="text-xl font-bold text-white mb-4">Profil recherché</h2>
                <ul className="space-y-2">
                  {(typeof job.requirements === 'string' ? job.requirements.split('\n') : job.requirements).map((req, index) => (
                    <li key={index} className="flex items-start gap-3 text-gray-300">
                      <CheckCircle className="w-5 h-5 text-green-400 mt-0.5 flex-shrink-0" />
                      <span>{req}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Benefits */}
            {job.benefits && (
              <div className="card-service rounded-xl p-6">
                <h2 className="text-xl font-bold text-white mb-4">Avantages</h2>
                <ul className="space-y-2">
                  {(typeof job.benefits === 'string' ? job.benefits.split('\n') : job.benefits).map((benefit, index) => (
                    <li key={index} className="flex items-start gap-3 text-gray-300">
                      <CheckCircle className="w-5 h-5 text-[#D4AF37] mt-0.5 flex-shrink-0" />
                      <span>{benefit}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Apply Card */}
            <div className="card-service rounded-xl p-6 sticky top-24">
              <button
                onClick={handleApplyClick}
                className="w-full btn-primary py-4 text-lg flex items-center justify-center gap-2"
                data-testid="job-apply-btn"
              >
                <Send className="w-5 h-5" />
                Postuler maintenant
              </button>
              
              <p className="text-center text-gray-500 text-sm mt-4">
                {job.applications_count ? `${job.applications_count} candidature(s)` : 'Soyez le premier à postuler !'}
              </p>

              {job.deadline && (
                <div className="mt-4 p-3 bg-orange-500/10 rounded-lg text-center">
                  <p className="text-orange-400 text-sm">
                    Date limite : {new Date(job.deadline).toLocaleDateString('fr-CH')}
                  </p>
                </div>
              )}
            </div>

            {/* Company Card */}
            <div className="card-service rounded-xl p-6">
              <div className="flex items-center gap-4 mb-4">
                <div className="w-16 h-16 rounded-xl bg-[#0047AB]/10 flex items-center justify-center">
                  {job.enterprise_logo ? (
                    <img src={job.enterprise_logo} alt="" className="w-16 h-16 rounded-xl object-cover" />
                  ) : (
                    <Building2 className="w-8 h-8 text-[#0047AB]" />
                  )}
                </div>
                <div>
                  <h3 className="text-white font-semibold">{job.enterprise_name}</h3>
                  <p className="text-gray-400 text-sm">{job.enterprise_category || 'Entreprise'}</p>
                </div>
              </div>
              
              {job.enterprise_id && (
                <Link 
                  to={`/entreprise/${job.enterprise_id}`}
                  className="w-full btn-secondary flex items-center justify-center gap-2"
                >
                  Voir l'entreprise
                  <ChevronRight className="w-4 h-4" />
                </Link>
              )}
            </div>

            {/* Share */}
            <div className="card-service rounded-xl p-4">
              <p className="text-gray-400 text-sm text-center mb-3">Partager cette offre</p>
              <div className="flex justify-center gap-3">
                <button className="p-2 bg-white/10 hover:bg-white/20 rounded-lg text-white transition-colors">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M24 4.557c-.883.392-1.832.656-2.828.775 1.017-.609 1.798-1.574 2.165-2.724-.951.564-2.005.974-3.127 1.195-.897-.957-2.178-1.555-3.594-1.555-3.179 0-5.515 2.966-4.797 6.045-4.091-.205-7.719-2.165-10.148-5.144-1.29 2.213-.669 5.108 1.523 6.574-.806-.026-1.566-.247-2.229-.616-.054 2.281 1.581 4.415 3.949 4.89-.693.188-1.452.232-2.224.084.626 1.956 2.444 3.379 4.6 3.419-2.07 1.623-4.678 2.348-7.29 2.04 2.179 1.397 4.768 2.212 7.548 2.212 9.142 0 14.307-7.721 13.995-14.646.962-.695 1.797-1.562 2.457-2.549z"/></svg>
                </button>
                <button className="p-2 bg-white/10 hover:bg-white/20 rounded-lg text-white transition-colors">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/></svg>
                </button>
                <button className="p-2 bg-white/10 hover:bg-white/20 rounded-lg text-white transition-colors">
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M.057 24l1.687-6.163c-1.041-1.804-1.588-3.849-1.587-5.946.003-6.556 5.338-11.891 11.893-11.891 3.181.001 6.167 1.24 8.413 3.488 2.245 2.248 3.481 5.236 3.48 8.414-.003 6.557-5.338 11.892-11.893 11.892-1.99-.001-3.951-.5-5.688-1.448l-6.305 1.654zm6.597-3.807c1.676.995 3.276 1.591 5.392 1.592 5.448 0 9.886-4.434 9.889-9.885.002-5.462-4.415-9.89-9.881-9.892-5.452 0-9.887 4.434-9.889 9.884-.001 2.225.651 3.891 1.746 5.634l-.999 3.648 3.742-.981zm11.387-5.464c-.074-.124-.272-.198-.57-.347-.297-.149-1.758-.868-2.031-.967-.272-.099-.47-.149-.669.149-.198.297-.768.967-.941 1.165-.173.198-.347.223-.644.074-.297-.149-1.255-.462-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.297-.347.446-.521.151-.172.2-.296.3-.495.099-.198.05-.372-.025-.521-.075-.148-.669-1.611-.916-2.206-.242-.579-.487-.501-.669-.51l-.57-.01c-.198 0-.52.074-.792.372s-1.04 1.016-1.04 2.479 1.065 2.876 1.213 3.074c.149.198 2.095 3.2 5.076 4.487.709.306 1.263.489 1.694.626.712.226 1.36.194 1.872.118.571-.085 1.758-.719 2.006-1.413.248-.695.248-1.29.173-1.414z"/></svg>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Apply Modal */}
      {showApplyModal && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 p-4" data-testid="apply-modal">
          <div className="bg-[#0A0A0A] rounded-2xl w-full max-w-lg border border-white/10 max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b border-white/10">
              <div className="flex items-center justify-between">
                <h2 className="text-xl font-bold text-white">Postuler à cette offre</h2>
                <button onClick={() => setShowApplyModal(false)} className="text-gray-400 hover:text-white">
                  <X className="w-6 h-6" />
                </button>
              </div>
            </div>
            
            <div className="p-6 space-y-6">
              {/* Job Info */}
              <div className="bg-white/5 rounded-xl p-4">
                <h3 className="text-white font-semibold">{job.title}</h3>
                <p className="text-[#D4AF37] text-sm">{job.enterprise_name}</p>
                <div className="flex items-center gap-4 text-xs text-gray-400 mt-2">
                  <span>{job.type}</span>
                  <span>{job.location || 'Lausanne'}</span>
                </div>
              </div>
              
              {/* CV Selection */}
              <div>
                <label className="block text-sm text-gray-400 mb-2">
                  <FileText className="w-4 h-4 inline mr-2" />
                  Sélectionnez votre CV *
                </label>
                {userDocuments.length > 0 ? (
                  <div className="space-y-2">
                    {userDocuments.map((doc) => (
                      <label 
                        key={doc.id} 
                        className={`flex items-center gap-3 p-3 rounded-lg cursor-pointer transition-colors ${
                          applyForm.resume_url === doc.url 
                            ? 'bg-[#0047AB]/20 border border-[#0047AB]' 
                            : 'bg-white/5 border border-white/10 hover:bg-white/10'
                        }`}
                      >
                        <input
                          type="radio"
                          name="resume"
                          value={doc.url}
                          checked={applyForm.resume_url === doc.url}
                          onChange={(e) => setApplyForm({...applyForm, resume_url: e.target.value})}
                          className="accent-[#0047AB]"
                        />
                        <FileText className="w-5 h-5 text-[#0047AB]" />
                        <div className="flex-1">
                          <span className="text-white text-sm">{doc.name}</span>
                          <span className="text-xs text-gray-500 ml-2">({doc.category})</span>
                        </div>
                      </label>
                    ))}
                  </div>
                ) : (
                  <div className="text-center p-6 bg-white/5 rounded-xl">
                    <FileText className="w-12 h-12 text-gray-500 mx-auto mb-3" />
                    <p className="text-gray-400 text-sm mb-3">Vous n'avez pas encore de CV enregistré</p>
                    <Link 
                      to={`/dashboard/client?tab=documents&returnToJob=${id}`}
                      className="text-[#0047AB] hover:underline text-sm"
                      onClick={() => setShowApplyModal(false)}
                    >
                      Ajouter un CV dans mon espace
                    </Link>
                  </div>
                )}
              </div>
              
              {/* Cover Letter */}
              <div>
                <label className="block text-sm text-gray-400 mb-2">Lettre de motivation (optionnel)</label>
                <textarea
                  value={applyForm.cover_letter}
                  onChange={(e) => setApplyForm({...applyForm, cover_letter: e.target.value})}
                  placeholder="Présentez-vous brièvement et expliquez votre motivation..."
                  className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white placeholder-gray-500 focus:border-[#0047AB] outline-none h-32 resize-none"
                />
              </div>
              
              {/* Submit */}
              <div className="flex gap-3">
                <button
                  onClick={() => setShowApplyModal(false)}
                  className="flex-1 px-4 py-3 rounded-xl bg-white/10 text-white hover:bg-white/20 transition-colors"
                >
                  Annuler
                </button>
                <button
                  onClick={handleSubmitApplication}
                  disabled={applying || !applyForm.resume_url}
                  className="flex-1 px-4 py-3 rounded-xl bg-[#0047AB] text-white hover:bg-[#0047AB]/80 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                >
                  {applying ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      Envoi...
                    </>
                  ) : (
                    <>
                      <Send className="w-4 h-4" />
                      Envoyer ma candidature
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default JobDetailPage;
