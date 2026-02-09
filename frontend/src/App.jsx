import React from 'react'
import { Routes, Route, Link } from 'react-router-dom'
import { AuthProvider } from './context/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'

import Header from './components/Header'
import SignInPage from './pages/SignInPage'
import SignUpPage from './pages/SignUpPage'
import OtpVerificationPage from './pages/OtpVerificationPage'
import DashboardPage from './pages/DashboardPage'
import ChatbotPage from './pages/ChatbotPage'
import TranscribePage from './pages/TranscribePage'
import ProcessTextPage from './pages/ProcessTextPage'
import DataIngestPage from './pages/DataIngestPage'

function LandingPage() {
  return (
    <div className="app">
      <video className="bg-video" autoPlay muted loop>
        <source src="/bg_vid.mp4" type="video/mp4" />
        Your browser does not support the video tag.
      </video>
      <Header />
      <main className="main-content">
        <div className="hero-content">
          <div className="hero-left">
            <div className="hero-buttons">
              <Link to="/signup" className="hero-btn get-started-btn">GET STARTED</Link>
              <Link to="/signin" className="hero-btn hero-sign-in-btn">SIGN IN</Link>
            </div>
          </div>
          <div className="hero-right">
            <div className="hero-right-content">
              <h1 className="hero-title larger">FinSight AI</h1>
              <div className="hero-tagline larger">
                <p>an end-to-end financial intelligence platform that transforms</p>
                <p>unstructured voice calls and complex financial documents into</p>
                <p>structured, actionable insights.</p>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default function App() {
  return (
    <AuthProvider>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/signin" element={<SignInPage />} />
        <Route path="/signup" element={<SignUpPage />} />
        <Route path="/verify-otp" element={<OtpVerificationPage />} />
        <Route 
          path="/dashboard" 
          element={
            <ProtectedRoute>
              <DashboardPage />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/chatbot" 
          element={
            <ProtectedRoute>
              <ChatbotPage />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/transcribe" 
          element={
            <ProtectedRoute>
              <TranscribePage />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/process-text" 
          element={
            <ProtectedRoute>
              <ProcessTextPage />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/data-ingest" 
          element={
            <ProtectedRoute>
              <DataIngestPage />
            </ProtectedRoute>
          } 
        />
      </Routes>
    </AuthProvider>
  )
}
