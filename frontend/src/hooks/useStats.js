import { useState, useEffect } from 'react'
import { statsApi } from '../api'

export function useStats() {
  const [data, setData] = useState({
    overview: null,
    byCategory: [],
    byCounty: [],
    topSkills: [],
    salaryDist: [],
  })
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const load = async () => {
      setLoading(true)
      try {
        const [ov, cat, county, skills, salary] = await Promise.all([
          statsApi.overview(),
          statsApi.byCategory(),
          statsApi.byCounty(),
          statsApi.topSkills(20),
          statsApi.salaryDist(),
        ])
        setData({
          overview: ov.data,
          byCategory: cat.data,
          byCounty: county.data,
          topSkills: skills.data,
          salaryDist: salary.data,
        })
      } catch (e) {
        setError(e.message)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  return { ...data, loading, error }
}
