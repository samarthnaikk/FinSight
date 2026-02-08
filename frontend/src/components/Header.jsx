import React from 'react'

export default function Header({ onSignInClick, onSignUpClick }) {
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
        <button className="auth-btn sign-in-btn" onClick={onSignInClick}>
          SIGN IN
        </button>
        <button className="auth-btn sign-up-btn" onClick={onSignUpClick}>
          SIGN UP
        </button>
      </div>
    </header>
  )
}
