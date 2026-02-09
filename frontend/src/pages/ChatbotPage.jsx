import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { backendAPI } from '../utils/api'

export default function ChatbotPage() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)

  const handleLogout = async () => {
    await logout()
    navigate('/')
  }

  const handleSendMessage = async (e) => {
    e.preventDefault()
    
    if (!inputMessage.trim()) return

    const userMessage = inputMessage.trim()
    
    // Add user message to chat
    setMessages(prev => [...prev, { role: 'user', content: userMessage }])
    setInputMessage('')
    setIsLoading(true)

    try {
      const response = await backendAPI.sendChatMessage(userMessage)
      
      // Add bot response
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: response.data?.message || 'Message stored successfully' 
      }])
    } catch (error) {
      console.error('Chat error:', error)
      setMessages(prev => [...prev, { 
        role: 'error', 
        content: error.message || 'Failed to send message' 
      }])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="app">
      <header className="dashboard-header">
        <Link to="/dashboard" className="back-link">← Back to Dashboard</Link>
        <h1 className="logo">FinSight AI Chatbot</h1>
        <button onClick={handleLogout} className="logout-btn">Logout</button>
      </header>

      <main className="chatbot-main">
        <div className="chat-container">
          <div className="chat-messages">
            {messages.length === 0 && (
              <div className="welcome-message">
                <h3>Welcome to FinSight AI Chatbot</h3>
                <p>Start a conversation to get financial insights</p>
              </div>
            )}
            
            {messages.map((msg, idx) => (
              <div key={idx} className={`message message-${msg.role}`}>
                <div className="message-content">{msg.content}</div>
              </div>
            ))}
            
            {isLoading && (
              <div className="message message-assistant">
                <div className="message-content">Thinking...</div>
              </div>
            )}
          </div>

          <form onSubmit={handleSendMessage} className="chat-input-form">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder="Type your message..."
              className="chat-input"
              disabled={isLoading}
            />
            <button type="submit" className="send-btn" disabled={isLoading || !inputMessage.trim()}>
              Send
            </button>
          </form>
        </div>
      </main>
    </div>
  )
}
