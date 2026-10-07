import React, { createContext, useContext, useState, ReactNode, useEffect } from 'react'
import axios from 'axios'

interface User {
  username: string
  email: string
  roles: string[]
}

interface AuthContextType {
  user: User | null
  token: string | null
  login: (username: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null)
  const [token, setToken] = useState<string | null>(null)

  useEffect(() => {
    // load token & user from storage if any
    const storedToken = localStorage.getItem('token')
    if (storedToken) {
      setToken(storedToken)
      // fetch user info
      axios
        .get('/auth/me', { headers: { Authorization: `Bearer ${storedToken}` } })
        .then((res) => setUser(res.data))
        .catch(() => {
          logout()
        })
    }
  }, [])

  const login = async (username: string, password: string) => {
    // For demo, derived from username
    let demoToken = null
    if (username === 'hr') demoToken = 'hr_token'
    else if (username === 'manager') demoToken = 'manager_token'
    else if (username === 'itadmin') demoToken = 'it_token'
    else if (username === 'employee') demoToken = 'employee_token'
    else throw new Error('Invalid credentials')

    localStorage.setItem('token', demoToken)
    setToken(demoToken)

    // Fetch user info
    const res = await axios.get('/auth/me', {
      headers: { Authorization: `Bearer ${demoToken}` },
    })
    setUser(res.data)
  }

  const logout = () => {
    setUser(null)
    setToken(null)
    localStorage.removeItem('token')
  }

  return <AuthContext.Provider value={{ user, token, login, logout }}>{children}</AuthContext.Provider>
}

export const useAuth = () => {
  const ctx = useContext(AuthContext)
  if (ctx === undefined) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return ctx
}
