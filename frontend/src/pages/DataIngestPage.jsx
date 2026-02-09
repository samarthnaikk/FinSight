import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { backendAPI } from '../utils/api'

export default function DataIngestPage() {
  const { logout } = useAuth()
  const navigate = useNavigate()
  const [confidential, setConfidential] = useState('')
  const [nonConfidential, setNonConfidential] = useState('')
  const [result, setResult] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  const handleLogout = async () => {
    await logout()
    navigate('/')
  }

  const handleIngest = async (e) => {
    e.preventDefault()
    
    if (!confidential.trim() && !nonConfidential.trim()) {
      setError('Please enter at least one type of data')
      return
    }

    setIsLoading(true)
    setError('')

    try {
      const response = await backendAPI.ingestData({
        confidential: confidential || '{}',
        non_confidential: nonConfidential || '{}',
      })
      setResult(response)
      setConfidential('')
      setNonConfidential('')
    } catch (error) {
      console.error('Ingestion error:', error)
      setError(error.message || 'Failed to ingest data')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="dashboard-header">
        <Link to="/dashboard" className="back-link">← Back to Dashboard</Link>
        <h1 className="logo">Data Ingestion</h1>
        <button onClick={handleLogout} className="logout-btn">Logout</button>
      </header>

      <main className="feature-main">
        <div className="feature-container">
          <h2>Ingest AI Data</h2>
          <p className="feature-description">
            Submit confidential and non-confidential data for secure storage
          </p>

          <form onSubmit={handleIngest} className="feature-form">
            <div className="form-group">
              <label htmlFor="confidential" className="form-label">Confidential Data (JSON format)</label>
              <textarea
                id="confidential"
                value={confidential}
                onChange={(e) => setConfidential(e.target.value)}
                className="form-textarea"
                placeholder='Enter confidential data as JSON, e.g., {"account": "123", "balance": 5000}'
                rows="6"
              />
            </div>

            <div className="form-group">
              <label htmlFor="nonConfidential" className="form-label">Non-Confidential Data (JSON format)</label>
              <textarea
                id="nonConfidential"
                value={nonConfidential}
                onChange={(e) => setNonConfidential(e.target.value)}
                className="form-textarea"
                placeholder='Enter non-confidential data as JSON, e.g., {"category": "finance", "type": "analysis"}'
                rows="6"
              />
            </div>

            {error && <div className="error-message">{error}</div>}

            <button 
              type="submit" 
              className="feature-submit-btn"
              disabled={(!confidential.trim() && !nonConfidential.trim()) || isLoading}
            >
              {isLoading ? 'Ingesting...' : 'Ingest Data'}
            </button>
          </form>

          {result && (
            <div className="result-container">
              <h3>Ingestion Result</h3>
              <div className="result-box success">
                <p>{result.data?.message || 'Data ingested successfully'}</p>
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
