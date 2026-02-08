import React from 'react'

export default function Header() {
  return (
    <header className="header">
      <div className="brand">FinSight <span className="badge">AI</span></div>
      <nav className="nav">
        <a href="#">Dashboard</a>
        <a href="#">Calls</a>
        <a href="#">Documents</a>
        <a href="#">Integrations</a>
      </nav>
    </header>
  )
}
