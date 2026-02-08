import React from 'react'

export default function Header() {
  return (
    <header className="header minimal">
      <div className="left">
        <div className="logo" aria-hidden>🔷</div>
        <div className="project-name">FinSight</div>
      </div>

      <div className="right">
        <a href="#" className="link">Sign In</a>
        <a href="#" className="cta">Sign Up</a>
        <a href="#" className="link">Help</a>
      </div>
    </header>
  )
}
