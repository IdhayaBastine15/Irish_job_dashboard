import { createContext, useContext } from 'react'

const SourceContext = createContext()

export function SourceProvider({ children }) {
  return (
    <SourceContext.Provider value={{ source: 'adzuna' }}>
      {children}
    </SourceContext.Provider>
  )
}

export function useSource() {
  return useContext(SourceContext)
}
