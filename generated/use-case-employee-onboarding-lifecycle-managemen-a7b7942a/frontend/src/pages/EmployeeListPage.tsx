import React, { useEffect, useState, useMemo } from 'react'
import { useAuth } from '../contexts/AuthContext'
import axios from 'axios'
import { AgGridReact } from 'ag-grid-react'
import { useNavigate } from 'react-router-dom'
import 'ag-grid-community/styles/ag-grid.css'
import 'ag-grid-community/styles/ag-theme-alpine.css'

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

export default function EmployeeListPage() {
  const { user, token, logout } = useAuth()
  const navigate = useNavigate()
  const [rowData, setRowData] = useState<Employee[]>([])
  const [loading, setLoading] = useState(true)

  const columnDefs = useMemo(() => [
    { headerName: 'ID', field: 'employee_id', sortable: true, filter: 'agNumberColumnFilter', width: 80 },
    { headerName: 'Name', field: 'name', sortable: true, filter: true, flex: 1 },
    { headerName: 'Email', field: 'email', sortable: true, filter: true, flex: 1 },
    { headerName: 'Department', field: 'department', sortable: true, filter: true, flex: 1 },
    { headerName: 'Designation', field: 'designation', sortable: true, filter: true, flex: 1 },
    { headerName: 'Joining Date', field: 'joining_date', sortable: true, filter: 'agDateColumnFilter', flex: 1 },
    { headerName: 'Manager', field: 'manager', sortable: true, filter: true, flex: 1 },
    { headerName: 'Location', field: 'location', sortable: true, filter: true, flex: 1 },
    { headerName: 'Active', field: 'is_active', sortable: true, filter: true, width: 100 },
  ], [])

  useEffect(() => {
    if (!token) {
      navigate('/login')
      return
    }

    setLoading(true)
    axios
      .get<Employee[]>('/employees', { headers: { Authorization: `Bearer ${token}` } })
      .then((res) => setRowData(res.data))
      .catch(() => logout())
      .finally(() => setLoading(false))
  }, [token, logout, navigate])

  const onRowClicked = (event: any) => {
    navigate(`/employees/${event.data.employee_id}`)
  }

  return (
    <div className="min-h-screen p-4 bg-gray-50">
      <h1 className="text-2xl font-bold mb-4">Employee List</h1>
      {loading ? (
        <p>Loading employees...</p>
      ) : (
        <div className="ag-theme-alpine" style={{ height: 600, width: '100%' }}>
          <AgGridReact
            rowData={rowData}
            columnDefs={columnDefs}
            pagination
            paginationPageSize={20}
            onRowClicked={onRowClicked}
            defaultColDef={{ resizable: true, filter: true }}
            suppressRowClickSelection
          />
        </div>
      )}
    </div>
  )
}
