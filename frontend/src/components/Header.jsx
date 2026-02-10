import React from 'react'

export default function Header() {
  return (
    <header className="header-ref">
      <div className="header-left">
        <div className="logo-text">LOGO</div>
        <div className="brand-text">FINSIGHT</div>
      </div>

      <div className="header-right">
        <button className="capsule-btn">ABOUT US</button>
        <button className="capsule-btn">SERVICES</button>
        <button className="capsule-btn">HELP</button>
      </div>
    </header>
  )
}
