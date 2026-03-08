const COUNTIES = ['Dublin', 'Cork', 'Galway', 'Limerick', 'Waterford', 'Kildare', 'Wicklow', 'Meath', 'Louth', 'Clare', 'Kerry', 'Mayo', 'Donegal', 'Tipperary', 'Sligo']
const CONTRACT_TYPES = ['permanent', 'contract', 'temporary']
const CONTRACT_TIMES = ['full_time', 'part_time']

export default function FilterBar({ filters, onFilterChange }) {
  return (
    <div className="bg-white border border-gray-200 rounded-xl p-4 flex flex-wrap gap-3">
      <select value={filters.county || ''} onChange={e => onFilterChange({ county: e.target.value || undefined })}
        className="border border-gray-300 rounded-lg px-3 py-2 text-sm text-gray-600 focus:outline-none focus:ring-2 focus:ring-green-500">
        <option value="">All Counties</option>
        {COUNTIES.map(c => <option key={c}>{c}</option>)}
      </select>

      <select value={filters.contract_type || ''} onChange={e => onFilterChange({ contract_type: e.target.value || undefined })}
        className="border border-gray-300 rounded-lg px-3 py-2 text-sm text-gray-600 focus:outline-none focus:ring-2 focus:ring-green-500">
        <option value="">All Contract Types</option>
        {CONTRACT_TYPES.map(t => <option key={t} value={t}>{t.charAt(0).toUpperCase() + t.slice(1)}</option>)}
      </select>

      <select value={filters.contract_time || ''} onChange={e => onFilterChange({ contract_time: e.target.value || undefined })}
        className="border border-gray-300 rounded-lg px-3 py-2 text-sm text-gray-600 focus:outline-none focus:ring-2 focus:ring-green-500">
        <option value="">Full & Part Time</option>
        {CONTRACT_TIMES.map(t => <option key={t} value={t}>{t.replace('_', '-')}</option>)}
      </select>

      <select value={filters.sort || 'newest'} onChange={e => onFilterChange({ sort: e.target.value })}
        className="border border-gray-300 rounded-lg px-3 py-2 text-sm text-gray-600 focus:outline-none focus:ring-2 focus:ring-green-500">
        <option value="newest">Newest first</option>
        <option value="oldest">Oldest first</option>
        <option value="salary_high">Highest salary</option>
        <option value="salary_low">Lowest salary</option>
      </select>
    </div>
  )
}
