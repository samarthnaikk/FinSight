import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { backendAPI } from '../utils/api'

export default function SignUpPage() {
  const navigate = useNavigate()
  const { register } = useAuth()
  const [formData, setFormData] = useState({
    name: '',
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
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

    if (!formData.name.trim()) {
      newErrors.name = 'Name is required'
    }

    if (!formData.username.trim()) {
      newErrors.username = 'Username is required'
    }

    if (!formData.email.trim()) {
      newErrors.email = 'Email is required'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      newErrors.email = 'Please enter a valid email'
    }

    if (!formData.password) {
      newErrors.password = 'Password is required'
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters'
    }

    if (!formData.confirmPassword) {
      newErrors.confirmPassword = 'Please confirm your password'
    } else if (formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match'
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
        // Register the user
        await register({
          name: formData.name,
          username: formData.username,
          email: formData.email,
          password: formData.password,
        })

        // Send OTP
        await backendAPI.sendOTP(formData.email)

        // Navigate to OTP verification page
        navigate('/verify-otp', { 
          state: { 
            email: formData.email,
            username: formData.username 
          } 
        })
      } catch (error) {
        console.error('Sign up error:', error)
        setErrors({ general: error.message || 'Registration failed. Please try again.' })
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

      <h1 className="auth-page-title">SIGN UP</h1>
      <div className="auth-title-divider"></div>

      <div className="auth-card">
        {errors.general && (
          <div style={{ color: 'red', marginBottom: '1rem', textAlign: 'center' }}>
            {errors.general}
          </div>
        )}
        <form className="auth-form" onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="name" className="auth-page-label">NAME</label>
            <input
              type="text"
              id="name"
              name="name"
              className={`auth-page-input ${errors.name ? 'error' : ''}`}
              value={formData.name}
              onChange={handleChange}
              placeholder="enter your name"
            />
            {errors.name && <span className="error-message">{errors.name}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="username" className="auth-page-label">USERNAME</label>
            <input
              type="text"
              id="username"
              name="username"
              className={`auth-page-input ${errors.username ? 'error' : ''}`}
              value={formData.username}
              onChange={handleChange}
              placeholder="enter your username"
            />
            {errors.username && <span className="error-message">{errors.username}</span>}
          </div>

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
              placeholder="minimum 6 characters"
            />
            {errors.password && <span className="error-message">{errors.password}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="confirmPassword" className="auth-page-label">CONFIRM PASSWORD</label>
            <input
              type="password"
              id="confirmPassword"
              name="confirmPassword"
              className={`auth-page-input ${errors.confirmPassword ? 'error' : ''}`}
              value={formData.confirmPassword}
              onChange={handleChange}
              placeholder="re-enter your password"
            />
            {errors.confirmPassword && <span className="error-message">{errors.confirmPassword}</span>}
          </div>

          <button type="submit" className="auth-page-submit-btn" disabled={isSubmitting}>
            {isSubmitting ? 'SIGNING UP...' : 'SIGNUP'}
          </button>
        </form>
      </div>
    </div>
  )
}
