import React, { useState } from 'react'

import Header from './components/Header'
import SignInDialog from './components/SignInDialog'
import SignUpDialog from './components/SignUpDialog'

export default function App() {
  const [isSignInOpen, setIsSignInOpen] = useState(false)
  const [isSignUpOpen, setIsSignUpOpen] = useState(false)

  return (
    <div className="app">
      <Header 
        onSignInClick={() => setIsSignInOpen(true)}
        onSignUpClick={() => setIsSignUpOpen(true)}
      />
      <main className="main-content">
        <div className="hero-content">
          <h1 className="hero-title larger">FinSight AI</h1>
          <div className="hero-tagline larger">
            <p>An end-to-end financial intelligence platform that transforms</p>
            <p>unstructured voice calls and complex financial documents into</p>
            <p>structured, actionable insights.</p>
          </div>
        </div>
      </main>
      
      <SignInDialog 
        isOpen={isSignInOpen} 
        onClose={() => setIsSignInOpen(false)} 
      />
      <SignUpDialog 
        isOpen={isSignUpOpen} 
        onClose={() => setIsSignUpOpen(false)} 
      />
    </div>
  )
}
