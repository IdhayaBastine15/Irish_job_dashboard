import { useState, useEffect } from 'react'
import { applicationsApi } from '../api'
import { Briefcase, Clock, Trophy, XCircle, Trash2, ExternalLink, BadgeEuro, MapPin, Plus, Loader2 } from 'lucide-react'

const STATUSES = [
  { key: 'all',       label: 'All',        icon: Briefcase,  color: 'slate'  },
  { key: 'applied',   label: 'Applied',    icon: Clock,      color: 'blue'   },
  { key: 'interview', label: 'Interview',  icon: Briefcase,  color: 'amber'  },
  { key: 'offer',     label: 'Offer',      icon: Trophy,     color: 'green'  },
  { key: 'rejected',  label: 'Rejected',   icon: XCircle,    color: 'red'    },
]

const statusStyles = {
  applied:   'bg-blue-100 text-blue-700 border-blue-200',
  interview: 'bg-amber-100 text-amber-700 border-amber-200',
  offer:     'bg-emerald-100 text-emerald-700 border-emerald-200',
  rejected:  'bg-red-100 text-red-600 border-red-200',
}

const tabActive = {
  slate: 'bg-slate-800 text-white',
  blue:  'bg-blue-500 text-white',
  amber: 'bg-amber-500 text-white',
  green: 'bg-emerald-500 text-white',
  red:   'bg-red-500 text-white',
}

export default function Process() {
  const [applications, setApplications] = useState([])
  const [loading, setLoading] = useState(true)
  const [activeTab, setActiveTab] = useState('all')
  const [updating, setUpdating] = useState(null)

  const load = async (status) => {
    setLoading(true)
    try {
      const { data } = await applicationsApi.list(status === 'all' ? null : status)
      setApplications(data)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load(activeTab) }, [activeTab])

  const changeStatus = async (id, status) => {
    setUpdating(id)
    try {
      const { data } = await applicationsApi.update(id, { status })
      setApplications(prev => prev.map(a => a.id === id ? data : a))
    } finally {
      setUpdating(null)
    }
  }

  const remove = async (id) => {
    await applicationsApi.delete(id)
    setApplications(prev => prev.filter(a => a.id !== id))
  }

  const counts = STATUSES.reduce((acc, s) => {
    acc[s.key] = s.key === 'all' ? applications.length : applications.filter(a => a.status === s.key).length
    return acc
  }, {})

  return (
    <div className="space-y-5">
      <div>
        <h1 className="text-xl font-bold text-slate-800">Applications Tracker</h1>
        <p className="text-sm text-slate-500 mt-0.5">Track every job you've applied to — add jobs from the Browse Jobs page.</p>
      </div>

      {/* Status tabs */}
      <div className="flex flex-wrap gap-2">
        {STATUSES.map(s => {
          const Icon = s.icon
          const isActive = activeTab === s.key
          return (
            <button
              key={s.key}
              onClick={() => setActiveTab(s.key)}
              className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-medium border transition-all ${
                isActive ? tabActive[s.color] + ' border-transparent shadow-sm' : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50'
              }`}
            >
              <Icon size={14} />
              {s.label}
              <span className={`ml-1 px-1.5 py-0.5 rounded-full text-xs ${isActive ? 'bg-white/20' : 'bg-slate-100 text-slate-500'}`}>
                {activeTab === 'all' ? (s.key === 'all' ? applications.length : applications.filter(a => a.status === s.key).length) : (s.key === activeTab ? applications.length : '')}
              </span>
            </button>
          )
        })}
      </div>

      {/* List */}
      {loading ? (
        <div className="flex justify-center py-20 text-slate-400 gap-2 text-sm">
          <Loader2 size={16} className="animate-spin" /> Loading...
        </div>
      ) : applications.length === 0 ? (
        <div className="flex flex-col items-center py-20 text-slate-400 gap-3">
          <Briefcase size={36} strokeWidth={1.5} />
          <p className="text-sm">No applications yet. Go to <strong>Browse Jobs</strong> and click "Track Application" on any job.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {applications.map(app => (
            <div key={app.id} className="bg-white rounded-xl border border-slate-200 p-4 flex flex-col sm:flex-row sm:items-center gap-4 hover:shadow-sm transition-shadow">
              {/* Job info */}
              <div className="flex-1 min-w-0">
                <div className="flex items-start gap-2 flex-wrap">
                  <h3 className="font-semibold text-slate-800 text-[15px] leading-snug">{app.job_title}</h3>
                  <span className={`text-xs px-2 py-0.5 rounded-full border font-medium ${statusStyles[app.status]}`}>
                    {app.status.charAt(0).toUpperCase() + app.status.slice(1)}
                  </span>
                </div>
                <div className="flex flex-wrap gap-x-3 gap-y-1 text-xs text-slate-500 mt-1">
                  {app.company && <span>{app.company}</span>}
                  {app.location && <span className="flex items-center gap-1"><MapPin size={11} />{app.location}</span>}
                  {(app.salary_min || app.salary_max) && (
                    <span className="flex items-center gap-1 text-emerald-600 font-medium">
                      <BadgeEuro size={11} />
                      {app.salary_min ? `€${app.salary_min.toLocaleString()}` : ''}
                      {app.salary_min && app.salary_max ? '–' : ''}
                      {app.salary_max ? `€${app.salary_max.toLocaleString()}` : ''}
                    </span>
                  )}
                  {app.applied_date && <span>Applied {new Date(app.applied_date).toLocaleDateString('en-IE')}</span>}
                </div>
                {app.notes && <p className="text-xs text-slate-400 mt-1 italic">{app.notes}</p>}
              </div>

              {/* Actions */}
              <div className="flex items-center gap-2 shrink-0">
                <select
                  value={app.status}
                  onChange={e => changeStatus(app.id, e.target.value)}
                  disabled={updating === app.id}
                  className="text-xs border border-slate-200 rounded-lg px-2 py-1.5 bg-white focus:outline-none focus:ring-2 focus:ring-[#169B62]/30 disabled:opacity-50"
                >
                  <option value="applied">Applied</option>
                  <option value="interview">Interview</option>
                  <option value="offer">Offer</option>
                  <option value="rejected">Rejected</option>
                </select>

                {app.redirect_url && (
                  <a href={app.redirect_url} target="_blank" rel="noopener noreferrer"
                    className="p-1.5 rounded-lg text-slate-400 hover:text-[#169B62] hover:bg-green-50 transition-colors">
                    <ExternalLink size={15} />
                  </a>
                )}
                <button onClick={() => remove(app.id)}
                  className="p-1.5 rounded-lg text-slate-400 hover:text-red-500 hover:bg-red-50 transition-colors">
                  <Trash2 size={15} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
