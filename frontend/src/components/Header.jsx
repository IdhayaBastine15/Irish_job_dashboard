import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

export default function Header() {
  const [q, setQ] = useState('')
  const navigate = useNavigate()

  return (
    <header className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
      <div className="flex items-center gap-2">
        <span className="text-2xl">🍀</span>
        <span className="font-semibold text-gray-800">Irish Job Dashboard</span>
        <span className="ml-2 text-xs bg-green-100 text-green-700 px-2 py-0.5 rounded-full">Powered by Adzuna</span>
      </div>
      <form onSubmit={(e) => { e.preventDefault(); if (q.trim()) navigate(`/jobs?q=${encodeURIComponent(q.trim())}`) }} className="flex gap-2">
        <input
          value={q}
          onChange={(e) => setQ(e.target.value)}
          placeholder="Search jobs, skills, companies..."
          className="border border-gray-300 rounded-lg px-4 py-2 text-sm w-80 focus:outline-none focus:ring-2 focus:ring-green-500"
        />
        <button type="submit" className="bg-green-600 text-white px-4 py-2 rounded-lg text-sm hover:bg-green-700">
          Search
        </button>
      </form>
    </header>
  )
}
