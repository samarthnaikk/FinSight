import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { modelsAPI } from '../utils/api'
import CopyButton from '../components/CopyButton'
import DropAudioAnimation from '../components/DropAudioAnimation'

export default function TranscribePage() {
  const { logout } = useAuth()
  const navigate = useNavigate()
  const [selectedFile, setSelectedFile] = useState(null)
  const [transcription, setTranscription] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  const handleLogout = async () => {
    await logout()
    navigate('/')
  }

  const handleFileChange = (e) => {
    const file = e.target.files[0]
    if (file) {
      // Validate file type
      const validTypes = ['audio/wav', 'audio/mp3', 'audio/mpeg']
      if (!validTypes.includes(file.type) && !file.name.endsWith('.wav') && !file.name.endsWith('.mp3')) {
        setError('Please select a valid audio file (.wav or .mp3)')
        setSelectedFile(null)
        return
      }
      setSelectedFile(file)
      setError('')
      setTranscription(null)
    }
  }

  const handleTranscribe = async (e) => {
    e.preventDefault()
    
    if (!selectedFile) {
      setError('Please select an audio file')
      return
    }

    setIsLoading(true)
    setError('')

    try {
      const response = await modelsAPI.transcribeAudio(selectedFile)
      setTranscription(response)
    } catch (error) {
      console.error('Transcription error:', error)
      setError(error.message || 'Failed to transcribe audio')
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="dashboard-header">
        <Link to="/dashboard" className="back-link">← Back to Dashboard</Link>
        <h1 className="logo">Audio Transcription</h1>
        <button onClick={handleLogout} className="logout-btn">Logout</button>
      </header>

      <main className="feature-main">
        <div className="feature-container">
          <h2>Transcribe Audio to Text</h2>
          <p className="feature-description">
            Upload an audio file (.wav or .mp3) to transcribe it to text using AI
          </p>

          {!selectedFile && !transcription && (
            <DropAudioAnimation />
          )}

          <form onSubmit={handleTranscribe} className="feature-form">
            <div className="file-input-wrapper">
              <label htmlFor="audio-file" className="file-label">
                {selectedFile ? selectedFile.name : 'Choose audio file'}
              </label>
              <input
                type="file"
                id="audio-file"
                accept=".wav,.mp3,audio/wav,audio/mp3,audio/mpeg"
                onChange={handleFileChange}
                className="file-input"
              />
            </div>

            {error && <div className="error-message">{error}</div>}

            <button 
              type="submit" 
              className="feature-submit-btn"
              disabled={!selectedFile || isLoading}
            >
              {isLoading ? 'Transcribing...' : 'Transcribe'}
            </button>
          </form>

          {transcription && (
            <div className="result-container">
              <h3>Transcription Result</h3>
              <div className="result-box">
                <p><strong>Message:</strong> {transcription.message}</p>
                <p><strong>Transcription:</strong></p>
                <pre className="transcription-text">{transcription.transcription}</pre>
                <CopyButton 
                  textToCopy={transcription.transcription} 
                  label="Copy Transcription" 
                />
                {transcription.filename && (
                  <p><strong>Saved as:</strong> {transcription.filename}</p>
                )}
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}
