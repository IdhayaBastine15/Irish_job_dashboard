import { useState, useEffect, useRef } from 'react'
import { resumeApi, applicationsApi } from '../api'
import { Upload, FileText, CheckCircle, Star, TrendingUp, Minus, Loader2, ExternalLink, BadgeEuro, MapPin, Plus } from 'lucide-react'

const fitConfig = {
  strong: { label: 'Strong Fit',   color: 'bg-emerald-100 text-emerald-700 border-emerald-200', dot: 'bg-emerald-500', icon: Star },
  good:   { label: 'Good Fit',     color: 'bg-blue-100 text-blue-700 border-blue-200',           dot: 'bg-blue-500',    icon: TrendingUp },
  less:   { label: 'Less Fit',     color: 'bg-slate-100 text-slate-500 border-slate-200',        dot: 'bg-slate-400',   icon: Minus },
}

function MatchCard({ match, onTrack }) {
  const { job, score, matched_skills, fit } = match
  const cfg = fitConfig[fit]
  const Icon = cfg.icon
  const [tracked, setTracked] = useState(false)

  const track = async () => {
    await onTrack(job)
    setTracked(true)
  }

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-5 hover:shadow-md transition-shadow">
      <div className="flex justify-between items-start gap-3 mb-2">
        <div className="min-w-0">
          <h3 className="font-semibold text-slate-800 text-[15px] leading-snug">{job.title}</h3>
          <p className="text-sm text-slate-500">{job.company}</p>
        </div>
        <div className="flex flex-col items-end gap-1.5 shrink-0">
          <span className={`text-xs px-2.5 py-1 rounded-full border font-medium flex items-center gap-1 ${cfg.color}`}>
            <Icon size={11} /> {cfg.label}
          </span>
          <span className="text-xs text-slate-400">{Math.round(score * 100)}% match</span>
        </div>
      </div>

      <div className="flex flex-wrap gap-x-3 gap-y-1 text-xs text-slate-500 mb-3">
        {job.location && <span className="flex items-center gap-1"><MapPin size={11} />{job.location}</span>}
        {(job.salary_min || job.salary_max) && (
          <span className="flex items-center gap-1 text-emerald-600 font-medium">
            <BadgeEuro size={11} />
            {job.salary_min ? `€${job.salary_min.toLocaleString()}` : ''}
            {job.salary_min && job.salary_max ? '–' : ''}
            {job.salary_max ? `€${job.salary_max.toLocaleString()}` : ''}
          </span>
        )}
      </div>

      {matched_skills.length > 0 && (
        <div className="flex flex-wrap gap-1.5 mb-3">
          {matched_skills.slice(0, 6).map(s => (
            <span key={s} className="px-2 py-0.5 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-full text-xs font-medium">{s}</span>
          ))}
          {matched_skills.length > 6 && <span className="text-xs text-slate-400 self-center">+{matched_skills.length - 6}</span>}
        </div>
      )}

      <div className="flex justify-between items-center pt-3 border-t border-slate-100">
        <div className="w-full bg-slate-100 rounded-full h-1.5 mr-3">
          <div className={`h-1.5 rounded-full ${cfg.dot}`} style={{ width: `${Math.min(score * 100, 100)}%` }} />
        </div>
        <div className="flex gap-2 shrink-0">
          {job.redirect_url && (
            <a href={job.redirect_url} target="_blank" rel="noopener noreferrer"
              className="text-xs text-slate-500 hover:text-[#169B62] flex items-center gap-1">
              View <ExternalLink size={11} />
            </a>
          )}
          <button
            onClick={track}
            disabled={tracked}
            className={`text-xs px-2.5 py-1 rounded-lg flex items-center gap-1 transition-all ${
              tracked ? 'bg-green-100 text-green-700' : 'bg-[#169B62] text-white hover:bg-green-700'
            }`}
          >
            {tracked ? <CheckCircle size={11} /> : <Plus size={11} />}
            {tracked ? 'Tracked' : 'Track'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default function Matches() {
  const [resume, setResume] = useState(null)
  const [matches, setMatches] = useState([])
  const [loading, setLoading] = useState(false)
  const [uploading, setUploading] = useState(false)
  const [filter, setFilter] = useState('all')
  const fileRef = useRef()

  useEffect(() => {
    resumeApi.get().then(({ data }) => {
      if (data) {
        setResume(data)
        loadMatches()
      }
    }).catch(() => {})
  }, [])

  const loadMatches = async () => {
    setLoading(true)
    try {
      const { data } = await resumeApi.matches()
      setMatches(data)
    } catch {
      setMatches([])
    } finally {
      setLoading(false)
    }
  }

  const handleUpload = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    setUploading(true)
    try {
      const { data } = await resumeApi.upload(file)
      setResume(data)
      await loadMatches()
    } catch (err) {
      alert('Failed to parse resume. Make sure it is a PDF, DOCX, or TXT file.')
    } finally {
      setUploading(false)
    }
  }

  const trackJob = async (job) => {
    await applicationsApi.create({
      job_id: job.id,
      job_title: job.title,
      company: job.company,
      location: job.location,
      category: job.category,
      redirect_url: job.redirect_url,
      salary_min: job.salary_min,
      salary_max: job.salary_max,
      status: 'applied',
      applied_date: new Date().toISOString().replace('Z', ''),
    })
  }

  const filtered = filter === 'all' ? matches : matches.filter(m => m.fit === filter)
  const counts = {
    all: matches.length,
    strong: matches.filter(m => m.fit === 'strong').length,
    good: matches.filter(m => m.fit === 'good').length,
    less: matches.filter(m => m.fit === 'less').length,
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-xl font-bold text-slate-800">Job Matches</h1>
        <p className="text-sm text-slate-500 mt-0.5">Upload your CV and we'll rank every Irish job listing by how well it matches your skills.</p>
      </div>

      {/* Upload card */}
      <div className={`rounded-xl border-2 border-dashed p-6 flex flex-col sm:flex-row items-center gap-4 transition-colors ${resume ? 'border-emerald-200 bg-emerald-50' : 'border-slate-200 bg-white hover:border-[#169B62]/50'}`}>
        <div className={`w-12 h-12 rounded-xl flex items-center justify-center shrink-0 ${resume ? 'bg-emerald-100' : 'bg-slate-100'}`}>
          {resume ? <CheckCircle size={22} className="text-emerald-600" /> : <FileText size={22} className="text-slate-400" />}
        </div>
        <div className="flex-1 text-center sm:text-left">
          {resume ? (
            <>
              <p className="font-semibold text-slate-800">{resume.filename}</p>
              <p className="text-sm text-slate-500">{resume.extracted_skills?.length || 0} skills extracted · {matches.length} jobs analysed</p>
            </>
          ) : (
            <>
              <p className="font-semibold text-slate-700">Upload your CV</p>
              <p className="text-sm text-slate-400">PDF, DOCX, or TXT · We extract your skills and match against all live Irish jobs</p>
            </>
          )}
        </div>
        <div>
          <input type="file" ref={fileRef} className="hidden" accept=".pdf,.docx,.txt" onChange={handleUpload} />
          <button
            onClick={() => fileRef.current.click()}
            disabled={uploading}
            className="flex items-center gap-2 bg-[#169B62] hover:bg-green-700 disabled:opacity-60 text-white px-4 py-2.5 rounded-lg text-sm font-medium transition-colors"
          >
            {uploading ? <Loader2 size={15} className="animate-spin" /> : <Upload size={15} />}
            {uploading ? 'Parsing...' : resume ? 'Replace CV' : 'Upload CV'}
          </button>
        </div>
      </div>

      {/* Skill chips from resume */}
      {resume?.extracted_skills?.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200 p-4">
          <p className="text-xs font-semibold text-slate-500 uppercase tracking-wide mb-2">Skills detected in your CV</p>
          <div className="flex flex-wrap gap-1.5">
            {resume.extracted_skills.map(s => (
              <span key={s} className="px-2.5 py-1 bg-slate-100 text-slate-700 border border-slate-200 rounded-full text-xs font-medium">{s}</span>
            ))}
          </div>
        </div>
      )}

      {/* Match results */}
      {loading ? (
        <div className="flex justify-center py-20 text-slate-400 gap-2 text-sm">
          <Loader2 size={16} className="animate-spin" /> Matching your skills against jobs...
        </div>
      ) : matches.length > 0 ? (
        <>
          {/* Fit filter tabs */}
          <div className="flex flex-wrap gap-2">
            {[
              { key: 'all',    label: `All (${counts.all})` },
              { key: 'strong', label: `⭐ Strong Fit (${counts.strong})` },
              { key: 'good',   label: `📈 Good Fit (${counts.good})` },
              { key: 'less',   label: `Less Fit (${counts.less})` },
            ].map(t => (
              <button key={t.key} onClick={() => setFilter(t.key)}
                className={`px-4 py-2 rounded-lg text-sm font-medium border transition-all ${
                  filter === t.key ? 'bg-slate-800 text-white border-transparent' : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50'
                }`}>
                {t.label}
              </button>
            ))}
          </div>

          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {filtered.map(m => (
              <MatchCard key={m.job.id} match={m} onTrack={trackJob} />
            ))}
          </div>
        </>
      ) : resume ? (
        <div className="flex flex-col items-center py-16 text-slate-400 gap-2">
          <p className="text-sm">No skill matches found. Make sure the jobs have been synced and skills extracted.</p>
        </div>
      ) : null}
    </div>
  )
}
