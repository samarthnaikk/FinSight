import React from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import FinSightLogo from '../components/FinSightLogo'

export default function DashboardPage() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = async () => {
    await logout()
    navigate('/')
  }

  return (
    <div className="app">
      <header className="dashboard-header">
        <div className="dashboard-header-left">
          <FinSightLogo width={40} height={40} />
          <h1 className="logo">FinSight AI</h1>
        </div>
        <div className="user-info">
          <span>Welcome, {user?.name || user?.username || 'User'}</span>
          <button onClick={handleLogout} className="logout-btn">Logout</button>
        </div>
      </header>

      <main className="dashboard-main">
        <h2 className="dashboard-title">Dashboard</h2>
        <p className="dashboard-subtitle">Access all FinSight AI features</p>

        <div className="features-grid">
          <Link to="/chatbot" className="feature-card">
            <div className="feature-icon">AI</div>
            <h3>Chatbot</h3>
            <p>Interact with the AI chatbot for financial insights</p>
          </Link>

          <Link to="/transcribe" className="feature-card">
            <div className="feature-icon">MIC</div>
            <h3>Audio Transcription</h3>
            <p>Transcribe audio files to text using AI</p>
          </Link>

          <Link to="/process-text" className="feature-card">
            <div className="feature-icon">TXT</div>
            <h3>Text Processing</h3>
            <p>Process and analyze transcripts with PII filtering</p>
          </Link>

          <Link to="/data-ingest" className="feature-card">
            <div className="feature-icon">DB</div>
            <h3>Data Ingestion</h3>
            <p>Ingest confidential and non-confidential data</p>
          </Link>
        </div>
      </main>
    </div>
  )
}
