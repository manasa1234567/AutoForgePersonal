import React from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import LoginPage from './pages/LoginPage'
import Dashboard from './pages/Dashboard'
import EmployeeListPage from './pages/EmployeeListPage'
import EmployeeDetailPage from './pages/EmployeeDetailPage'
import AIQueryPage from './pages/AIQueryPage'
import { AuthProvider } from './contexts/AuthContext'

function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path='/' element={<Dashboard />} />
          <Route path='/login' element={<LoginPage />} />
          <Route path='/employees' element={<EmployeeListPage />} />
          <Route path='/employees/:id' element={<EmployeeDetailPage />} />
          <Route path='/ai-assistant' element={<AIQueryPage />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  )
}

export default App
