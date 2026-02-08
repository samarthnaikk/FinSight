import React, { useState } from 'react'
import Modal from './Modal'

export default function SignInDialog({ isOpen, onClose }) {
  const [formData, setFormData] = useState({
    usernameOrEmail: '',
    password: ''
  })
  
  const [errors, setErrors] = useState({})

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
    // Clear error for this field when user starts typing
    if (errors[name]) {
      setErrors(prev => ({
        ...prev,
        [name]: ''
      }))
    }
  }

  const validateForm = () => {
    const newErrors = {}
    
    if (!formData.usernameOrEmail.trim()) {
      newErrors.usernameOrEmail = 'Username or email is required'
    }
    
    if (!formData.password) {
      newErrors.password = 'Password is required'
    }
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = (e) => {
    e.preventDefault()
    
    if (validateForm()) {
      // Form is valid - in a real app, this would call an API
      console.log('Sign in form submitted:', formData)
      alert('Sign in successful! (Frontend only - no backend integration)')
      handleClose()
    }
  }

  const handleClose = () => {
    setFormData({
      usernameOrEmail: '',
      password: ''
    })
    setErrors({})
    onClose()
  }

  return (
    <Modal isOpen={isOpen} onClose={handleClose} title="Welcome Back">
      <form className="auth-form" onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="usernameOrEmail" className="form-label">Username or Email</label>
          <input
            type="text"
            id="usernameOrEmail"
            name="usernameOrEmail"
            className={`form-input ${errors.usernameOrEmail ? 'error' : ''}`}
            value={formData.usernameOrEmail}
            onChange={handleChange}
            placeholder="Enter your username or email"
          />
          {errors.usernameOrEmail && <span className="error-message">{errors.usernameOrEmail}</span>}
        </div>

        <div className="form-group">
          <label htmlFor="password" className="form-label">Password</label>
          <input
            type="password"
            id="password"
            name="password"
            className={`form-input ${errors.password ? 'error' : ''}`}
            value={formData.password}
            onChange={handleChange}
            placeholder="Enter your password"
          />
          {errors.password && <span className="error-message">{errors.password}</span>}
        </div>

        <button type="submit" className="auth-submit-btn">
          Sign In
        </button>
      </form>
    </Modal>
  )
}
