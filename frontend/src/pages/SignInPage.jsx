import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function SignInPage() {
  const navigate = useNavigate()
  const { login } = useAuth()
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  })

  const [errors, setErrors] = useState({})
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }))
    }
  }

  const validateForm = () => {
    const newErrors = {}

    if (!formData.email.trim()) {
      newErrors.email = 'Email address is required'
    }

    if (!formData.password) {
      newErrors.password = 'Password is required'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (validateForm()) {
      setIsSubmitting(true)
      setErrors({})

      try {
        await login({
          email: formData.email,
          password: formData.password,
        })

        // Navigate to dashboard on successful login
        navigate('/dashboard')
      } catch (error) {
        console.error('Sign in error:', error)
        setErrors({ general: error.message || 'Login failed. Please check your credentials.' })
      } finally {
        setIsSubmitting(false)
      }
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-page-nav">
        <Link to="/" className="back-to-home-btn">
          <span className="back-arrow">←</span> BACK TO HOME
        </Link>
      </div>

      <h1 className="auth-page-title">SIGN IN</h1>
      <div className="auth-title-divider"></div>

      <div className="auth-card">
        {errors.general && (
          <div style={{ color: 'red', marginBottom: '1rem', textAlign: 'center' }}>
            {errors.general}
          </div>
        )}
        <form className="auth-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="email" className="auth-page-label">EMAIL ADDRESS</label>
            <input
              type="text"
              id="email"
              name="email"
              className={`auth-page-input ${errors.email ? 'error' : ''}`}
              value={formData.email}
              onChange={handleChange}
              placeholder="enter your email address"
            />
            {errors.email && <span className="error-message">{errors.email}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="password" className="auth-page-label">PASSWORD</label>
            <input
              type="password"
              id="password"
              name="password"
              className={`auth-page-input ${errors.password ? 'error' : ''}`}
              value={formData.password}
              onChange={handleChange}
              placeholder="enter your password"
            />
            {errors.password && <span className="error-message">{errors.password}</span>}
          </div>

          <button type="submit" className="auth-page-submit-btn" disabled={isSubmitting}>
            {isSubmitting ? 'SIGNING IN...' : 'SIGN IN'}
          </button>
        </form>

        <p className="auth-switch-text">
          You don't have an account ? <Link to="/signup" className="auth-switch-link">SIGN UP</Link>
        </p>
      </div>
    </div>
  )
}
