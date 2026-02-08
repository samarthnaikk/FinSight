import React from 'react'
import Header from './components/Header'
import Dashboard from './components/Dashboard'

export default function App() {
  return (
    <div className="app">
      <Header />
      <main className="container">
        <Dashboard />
      </main>
    </div>
  )
}
