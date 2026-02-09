import React, { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { backendAPI } from '../utils/api'

export default function OtpVerificationPage() {
  const location = useLocation()
  const navigate = useNavigate()
  const email = location.state?.email || ''
  const username = location.state?.username || ''
  const [otp, setOtp] = useState('')
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  const maskedEmail = email
    ? email.replace(/^(.{2})(.*)(@.*)$/, (_, start, middle, end) =>
        start + '*'.repeat(middle.length) + end
      )
    : '***************@gmail.com'

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (!otp.trim()) {
      setError('OTP is required')
      return
    }

    setError('')
    setIsSubmitting(true)

    try {
      await backendAPI.verifyOTP({
        email: email,
        otp: otp,
      })

      alert('OTP verified successfully! Please sign in.')
      navigate('/signin')
    } catch (error) {
      console.error('OTP verification error:', error)
      setError(error.message || 'OTP verification failed. Please try again.')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleResend = async () => {
    try {
      await backendAPI.sendOTP(email)
      alert('OTP resent successfully!')
    } catch (error) {
      console.error('Resend OTP error:', error)
      alert('Failed to resend OTP. Please try again.')
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-page-nav">
        <Link to="/" className="back-to-home-btn">
          <span className="back-arrow">←</span> BACK TO HOME
        </Link>
      </div>

      <h1 className="auth-page-title">OTP VERIFICATION</h1>
      <div className="auth-title-divider"></div>

      <div className="auth-card">
        <div className="otp-info-text">
          <p>You will receive OTP on your registered email id</p>
          <p>Registered email: {maskedEmail}</p>
        </div>

        <form className="auth-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <input
              type="text"
              id="otp"
              name="otp"
              className={`auth-page-input ${error ? 'error' : ''}`}
              value={otp}
              onChange={(e) => {
                setOtp(e.target.value)
                if (error) setError('')
              }}
              placeholder="enter your received otp"
            />
            {error && <span className="error-message">{error}</span>}
          </div>

          <p className="auth-switch-text">
            You didn't receive OTP ? <button type="button" className="auth-switch-link resend-btn" onClick={handleResend}>RESEND CODE</button>
          </p>

          <button type="submit" className="auth-page-submit-btn" disabled={isSubmitting}>
            {isSubmitting ? 'VERIFYING...' : 'VERIFIED'}
          </button>
        </form>
      </div>
    </div>
  )
}
