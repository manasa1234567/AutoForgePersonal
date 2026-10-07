import React, { useState } from 'react'
import { useAuth } from '../contexts/AuthContext'
import axios from 'axios'

export default function AIQueryPage() {
  const { token } = useAuth()
  const [query, setQuery] = useState('')
  const [response, setResponse] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError(null)
    setResponse(null)

    try {
      const res = await axios.post(
        '/ai/query',
        { query },
        { headers: { Authorization: `Bearer ${token}` } }
      )
      setResponse(res.data.response)
    } catch (err) {
      setError('Failed to get response from AI assistant.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen p-6 bg-gray-50 flex flex-col items-center">
      <h1 className="text-3xl font-bold mb-8">AI Assistant</h1>
      <form onSubmit={handleSubmit} className="w-full max-w-xl">
        <textarea
          className="w-full p-3 border rounded mb-4"
          placeholder="Enter your query or command..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          rows={4}
          required
          aria-label="AI assistant query input"
        />
        <button
          type="submit"
          disabled={loading}
          className="px-6 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? 'Processing...' : 'Send'}
        </button>
      </form>
      {response && (
        <div className="mt-6 p-4 bg-white rounded shadow max-w-xl w-full whitespace-pre-wrap" aria-live="polite">
          <strong>Response:</strong>
          <p>{response}</p>
        </div>
      )}
      {error && <div className="mt-6 text-red-600" role="alert">{error}</div>}
    </div>
  )
}
