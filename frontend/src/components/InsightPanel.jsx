import { useState } from 'react'
import { insightsApi } from '../api'

export default function InsightPanel({ category }) {
  const [insight, setInsight] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const load = async () => {
    setLoading(true)
    setError(null)
    try {
      const { data } = await insightsApi.market(category)
      setInsight(data)
    } catch (e) {
      setError('Claude API unavailable — check your ANTHROPIC_API_KEY')
    } finally {
      setLoading(false)
    }
  }

  if (!insight && !loading) {
    return (
      <div className="bg-gradient-to-br from-green-50 to-blue-50 rounded-xl border border-green-200 p-5">
        <div className="flex items-center justify-between mb-2">
          <h3 className="font-semibold text-gray-700 flex items-center gap-2">
            <span>✨</span> AI Market Insight
          </h3>
          <button
            onClick={load}
            className="text-sm bg-green-600 text-white px-3 py-1.5 rounded-lg hover:bg-green-700"
          >
            Generate for "{category}"
          </button>
        </div>
        <p className="text-sm text-gray-400">Click to generate a Claude-powered market analysis for this category.</p>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="bg-gradient-to-br from-green-50 to-blue-50 rounded-xl border border-green-200 p-5 animate-pulse">
        <p className="text-sm text-gray-400">Asking Claude about the {category} market...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-red-50 rounded-xl border border-red-200 p-4 text-sm text-red-600">{error}</div>
    )
  }

  return (
    <div className="bg-gradient-to-br from-green-50 to-blue-50 rounded-xl border border-green-200 p-5">
      <h3 className="font-semibold text-gray-700 flex items-center gap-2 mb-4">
        <span>✨</span> AI Market Insight — {category}
      </h3>
      <p className="text-sm text-gray-700 mb-4">{insight.summary}</p>
      <div className="grid grid-cols-2 gap-4">
        <div>
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Top Skills in Demand</p>
          <div className="flex flex-wrap gap-1.5">
            {insight.top_skills?.map(s => (
              <span key={s} className="px-2 py-0.5 bg-green-100 text-green-700 rounded-full text-xs">{s}</span>
            ))}
          </div>
        </div>
        <div>
          <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Emerging Skills</p>
          <div className="flex flex-wrap gap-1.5">
            {insight.skill_gaps?.map(s => (
              <span key={s} className="px-2 py-0.5 bg-orange-100 text-orange-700 rounded-full text-xs">{s}</span>
            ))}
          </div>
        </div>
      </div>
      {insight.market_note && (
        <p className="text-xs text-gray-500 mt-4 italic border-t border-green-200 pt-3">{insight.market_note}</p>
      )}
    </div>
  )
}
