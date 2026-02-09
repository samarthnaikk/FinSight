import React from 'react'
import { Routes, Route, Link } from 'react-router-dom'

import Header from './components/Header'
import SignInPage from './pages/SignInPage'
import SignUpPage from './pages/SignUpPage'
import OtpVerificationPage from './pages/OtpVerificationPage'

function LandingPage() {
  return (
    <div className="app">
      <Header />
      <main className="main-content">
        <div className="hero-content">
          <h1 className="hero-title larger">FinSight AI</h1>
          <div className="hero-tagline larger">
            <p>an end-to-end financial intelligence platform that transforms</p>
            <p>unstructured voice calls and complex financial documents into</p>
            <p>structured, actionable insights.</p>
          </div>
          <div className="hero-buttons">
            <Link to="/signup" className="hero-btn get-started-btn">GET STARTED</Link>
            <Link to="/signin" className="hero-btn hero-sign-in-btn">SIGN IN</Link>
          </div>
        </div>
      </main>
    </div>
  )
}

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/signin" element={<SignInPage />} />
      <Route path="/signup" element={<SignUpPage />} />
      <Route path="/verify-otp" element={<OtpVerificationPage />} />
    </Routes>
  )
}
