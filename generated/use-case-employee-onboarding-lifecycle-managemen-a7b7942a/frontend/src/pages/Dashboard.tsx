import React, { useEffect, useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import axios from 'axios'
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell, Legend } from 'recharts'
import { Link, useNavigate } from 'react-router-dom'

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#a83279']

export default function Dashboard() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [kpis, setKpis] = useState({
    totalEmployees: 0,
    activeEmployees: 0,
    newJoiners: 0,
    remoteEmployees: 0,
    pendingOnboarding: 0,
  })
  const [departmentDistribution, setDepartmentDistribution] = useState<any[]>([])
  const [monthlyHiringTrend, setMonthlyHiringTrend] = useState<any[]>([])
  const [locationDistribution, setLocationDistribution] = useState<any[]>([])

  useEffect(() => {
    if (!user) {
      navigate('/login')
      return
    }
    // For demo, set static data
    setKpis({
      totalEmployees: 120,
      activeEmployees: 110,
      newJoiners: 10,
      remoteEmployees: 35,
      pendingOnboarding: 5,
    })
    setDepartmentDistribution([
      { name: 'Engineering', value: 50 },
      { name: 'HR', value: 20 },
      { name: 'Sales', value: 25 },
      { name: 'Support', value: 15 },
    ])
    setMonthlyHiringTrend([
      { month: 'Jan', count: 2 },
      { month: 'Feb', count: 5 },
      { month: 'Mar', count: 3 },
      { month: 'Apr', count: 4 },
    ])
    setLocationDistribution([
      { name: 'New York', value: 40 },
      { name: 'San Francisco', value: 35 },
      { name: 'Remote', value: 25 },
    ])
  }, [user, navigate])

  if (!user) return null

  return (
    <div className="min-h-screen p-6 bg-gray-50">
      <header className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <div>
          <button
            onClick={logout}
            className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700"
            aria-label="Logout"
          >
            Logout
          </button>
        </div>
      </header>
      <section className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
        <div className="bg-white rounded p-4 shadow">
          <h2 className="text-xl font-semibold mb-2">Total Employees</h2>
          <p className="text-3xl">{kpis.totalEmployees}</p>
        </div>
        <div className="bg-white rounded p-4 shadow">
          <h2 className="text-xl font-semibold mb-2">Active Employees</h2>
          <p className="text-3xl">{kpis.activeEmployees}</p>
        </div>
        <div className="bg-white rounded p-4 shadow">
          <h2 className="text-xl font-semibold mb-2">New Joiners</h2>
          <p className="text-3xl">{kpis.newJoiners}</p>
        </div>
        <div className="bg-white rounded p-4 shadow">
          <h2 className="text-xl font-semibold mb-2">Remote Employees</h2>
          <p className="text-3xl">{kpis.remoteEmployees}</p>
        </div>
        <div className="bg-white rounded p-4 shadow">
          <h2 className="text-xl font-semibold mb-2">Pending Onboarding</h2>
          <p className="text-3xl">{kpis.pendingOnboarding}</p>
        </div>
      </section>
      <section className="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="bg-white rounded p-4 shadow">
          <h3 className="text-xl font-semibold mb-4">Department Distribution</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={departmentDistribution}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={80}
                fill="#8884d8"
                label
              >
                {departmentDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Legend verticalAlign="bottom" height={36} />
            </PieChart>
          </ResponsiveContainer>
        </div>
        <div className="bg-white rounded p-4 shadow">
          <h3 className="text-xl font-semibold mb-4">Monthly Hiring Trend</h3>
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={monthlyHiringTrend}>
              <XAxis dataKey="month" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#82ca9d" />
            </BarChart>
          </ResponsiveContainer>
        </div>
        <div className="bg-white rounded p-4 shadow">
          <h3 className="text-xl font-semibold mb-4">Employee Location Distribution</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={locationDistribution}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={80}
                fill="#8884d8"
                label
              >
                {locationDistribution.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Legend verticalAlign="bottom" height={36} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </section>
      <footer className="mt-12">
        <Link to="/employees" className="text-blue-600 hover:underline">
          Manage Employees
        </Link>
      </footer>
    </div>
  )
}
