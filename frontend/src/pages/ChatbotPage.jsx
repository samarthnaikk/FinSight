import React, { useState, useEffect, useRef } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { backendAPI } from '../utils/api'

export default function ChatbotPage() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isTyping, setIsTyping] = useState(false)
  const [isLoadingHistory, setIsLoadingHistory] = useState(true)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages, isTyping])

  // Load conversation history on mount
  useEffect(() => {
    const loadHistory = async () => {
      setIsLoadingHistory(true)
      try {
        const response = await backendAPI.getChatHistory()
        if (response.success && response.data?.messages) {
          setMessages(response.data.messages)
        }
      } catch (error) {
        console.error('Failed to load chat history:', error)
      } finally {
        setIsLoadingHistory(false)
      }
    }
    loadHistory()
  }, [])

  const handleLogout = async () => {
    await logout()
    navigate('/')
  }

  const handleSendMessage = async (e) => {
    e.preventDefault()
    
    if (!inputMessage.trim()) return

    const userMessage = inputMessage.trim()
    
    // Add user message to chat
    const newUserMessage = { role: 'user', content: userMessage }
    setMessages(prev => [...prev, newUserMessage])
    setInputMessage('')
    setIsLoading(true)
    setIsTyping(true)

    try {
      const response = await backendAPI.sendChatMessage(userMessage)
      
      // Add bot response
      if (response.success && response.data?.message) {
        setMessages(prev => [...prev, { 
          role: 'assistant', 
          content: response.data.message 
        }])
      } else {
        throw new Error(response.error || 'Failed to get response')
      }
    } catch (error) {
      console.error('Chat error:', error)
      setMessages(prev => [...prev, { 
        role: 'error', 
        content: error.message || 'Failed to send message' 
      }])
    } finally {
      setIsLoading(false)
      setIsTyping(false)
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
            {isLoadingHistory ? (
              <div className="welcome-message">
                <p>Loading conversation history...</p>
              </div>
            ) : messages.length === 0 ? (
              <div className="welcome-message">
                <h3>Welcome to FinSight AI Chatbot</h3>
                <p>Start a conversation to get financial insights</p>
              </div>
            ) : null}
            
            {messages.map((msg, idx) => (
              <div key={idx} className={`message message-${msg.role} message-fade-in`}>
                <div className="message-content">{msg.content}</div>
              </div>
            ))}
            
            {isTyping && (
              <div className="message message-assistant message-fade-in">
                <div className="message-content typing-indicator">
                  <span className="typing-dot"></span>
                  <span className="typing-dot"></span>
                  <span className="typing-dot"></span>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
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
