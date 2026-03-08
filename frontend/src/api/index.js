import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 15000,
})

export const jobsApi = {
  list: (params) => api.get('/jobs/', { params }),
  get: (id) => api.get(`/jobs/${id}`),
}

export const statsApi = {
  overview: () => api.get('/stats/overview'),
  byCategory: () => api.get('/stats/by-category'),
  byCounty: () => api.get('/stats/by-county'),
  topSkills: (limit = 20) => api.get('/stats/top-skills', { params: { limit } }),
  salaryDist: () => api.get('/stats/salary-distribution'),
  syncLogs: () => api.get('/stats/sync-logs'),
}

export const insightsApi = {
  market: (category) => api.get(`/insights/market/${encodeURIComponent(category)}`),
  job: (id) => api.get(`/insights/job/${id}`),
}

export default api
