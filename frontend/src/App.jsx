import React from 'react'

import Header from './components/Header'

export default function App() {
  return (
    <div className="app">
      <Header />
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
    </div>
  )
}
