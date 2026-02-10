import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { modelsAPI } from '../utils/api'
import CopyButton from '../components/CopyButton'
import JsonViewer from '../components/JsonViewer'

export default function ProcessTextPage() {
  const { logout } = useAuth()
  const navigate = useNavigate()
  const [text, setText] = useState('')
  const [filename, setFilename] = useState('transcript')
  const [result, setResult] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  const handleLogout = async () => {
    await logout()
    navigate('/')
  }

  const handleProcess = async (e) => {
    e.preventDefault()
    
    if (!text.trim()) {
      setError('Please enter text to process')
      return
    }

    setIsLoading(true)
    setError('')

    try {
      const response = await modelsAPI.processTranscript(text, filename)
      setResult(response)
    } catch (error) {
      console.error('Processing error:', error)
      setError(error.message || 'Failed to process text')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="dashboard-header">
        <Link to="/dashboard" className="back-link">← Back to Dashboard</Link>
        <h1 className="logo">Text Processing</h1>
        <button onClick={handleLogout} className="logout-btn">Logout</button>
      </header>

      <main className="feature-main">
        <div className="feature-container">
          <h2>Process Transcript Text</h2>
          <p className="feature-description">
            Process text through the pipeline for PII removal and structured output generation
          </p>

          <form onSubmit={handleProcess} className="feature-form">
            <div className="form-group">
              <label htmlFor="filename" className="form-label">Filename (optional)</label>
              <input
                type="text"
                id="filename"
                value={filename}
                onChange={(e) => setFilename(e.target.value)}
                className="form-input"
                placeholder="Enter filename"
              />
            </div>

            <div className="form-group">
              <label htmlFor="text" className="form-label">Text to Process</label>
              <textarea
                id="text"
                value={text}
                onChange={(e) => setText(e.target.value)}
                className="form-textarea"
                placeholder="Enter or paste text to process"
                rows="10"
              />
            </div>

            {error && <div className="error-message">{error}</div>}

            <button 
              type="submit" 
              className="feature-submit-btn"
              disabled={!text.trim() || isLoading}
            >
              {isLoading ? 'Processing...' : 'Process Text'}
            </button>
          </form>

          {result && (
            <div className="result-container">
              <h3>Processing Result</h3>
              <div className="result-box">
                <p><strong>Message:</strong> {result.message}</p>
                
                {result.files && (
                  <div>
                    <p><strong>Generated Files:</strong></p>
                    <ul>
                      {result.files.pii_cleaned && <li>PII Cleaned: {result.files.pii_cleaned}</li>}
                      {result.files.structured_output && <li>Structured Output: {result.files.structured_output}</li>}
                    </ul>
                  </div>
                )}
                
                {result.data && (
                  <div>
                    <p><strong>Structured Data:</strong></p>
                    <JsonViewer data={result.data} />
                    <CopyButton 
                      textToCopy={JSON.stringify(result.data, null, 2)} 
                      label="Copy Data" 
                    />
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
