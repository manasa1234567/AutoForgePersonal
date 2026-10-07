import React, { useState, useEffect } from 'react'
import { useParams, useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'
import axios from 'axios'

interface Employee {
  employee_id: number
  name: string
  email: string
  phone?: string
  department?: string
  designation?: string
  joining_date?: string
  manager?: string
  location?: string
  is_active: boolean
}

export default function EmployeeDetailPage() {
  const { id } = useParams()
  const { token, logout } = useAuth()
  const navigate = useNavigate()
  const [employee, setEmployee] = useState<Employee | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!token) {
      navigate('/login')
      return
    }
    setLoading(true)
    axios
      .get<Employee>(`/employees/${id}`, { headers: { Authorization: `Bearer ${token}` } })
      .then((res) => {
        setEmployee(res.data)
        setError(null)
      })
      .catch(() => {
        setError('Failed to load employee data or access denied.')
        setEmployee(null)
      })
      .finally(() => setLoading(false))
  }, [id, token, navigate])

  if (!employee && loading) return <p>Loading...</p>
  if (error) return <p role="alert" className="text-red-600">{error}</p>
  if (!employee) return <p>No employee data found.</p>

  return (
    <div className="min-h-screen p-6 bg-gray-50">
      <header className="flex justify-between items-center mb-6">
        <h1 className="text-3xl font-bold">Employee Detail - {employee.name}</h1>
        <Link to="/employees" className="text-blue-600 hover:underline">
          Back to List
        </Link>
      </header>
      <section>
        <div className="bg-white rounded shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Personal Information</h2>
          <dl className="grid grid-cols-2 gap-4">
            <dt className="font-semibold">Employee ID:</dt>
            <dd>{employee.employee_id}</dd>
            <dt className="font-semibold">Email:</dt>
            <dd>{employee.email}</dd>
            <dt className="font-semibold">Phone:</dt>
            <dd>{employee.phone || '-'}</dd>
            <dt className="font-semibold">Department:</dt>
            <dd>{employee.department || '-'}</dd>
            <dt className="font-semibold">Designation:</dt>
            <dd>{employee.designation || '-'}</dd>
            <dt className="font-semibold">Joining Date:</dt>
            <dd>{employee.joining_date || '-'}</dd>
            <dt className="font-semibold">Manager:</dt>
            <dd>{employee.manager || '-'}</dd>
            <dt className="font-semibold">Location:</dt>
            <dd>{employee.location || '-'}</dd>
            <dt className="font-semibold">Active:</dt>
            <dd>{employee.is_active ? 'Yes' : 'No'}</dd>
          </dl>
        </div>
      </section>
    </div>
  )
}
