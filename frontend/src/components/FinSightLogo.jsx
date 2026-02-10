import React from 'react'

export default function FinSightLogo({ width = 40, height = 40 }) {
  return (
    <svg 
      width={width} 
      height={height} 
      viewBox="0 0 100 100" 
      fill="none" 
      xmlns="http://www.w3.org/2000/svg"
      className="finsight-logo"
    >
      {/* Background circle */}
      <circle cx="50" cy="50" r="48" fill="url(#logoGradient)" opacity="0.1"/>
      
      {/* Finance chart line */}
      <path 
        d="M 15 70 L 30 55 L 45 60 L 60 40 L 75 45 L 85 25" 
        stroke="url(#lineGradient)" 
        strokeWidth="3" 
        strokeLinecap="round" 
        strokeLinejoin="round"
        fill="none"
      />
      
      {/* Data points */}
      <circle cx="30" cy="55" r="4" fill="#C9A961" />
      <circle cx="45" cy="60" r="4" fill="#C9A961" />
      <circle cx="60" cy="40" r="5" fill="#D4B76C" />
      <circle cx="75" cy="45" r="4" fill="#C9A961" />
      
      {/* Dollar sign overlay */}
      <text 
        x="50" 
        y="75" 
        fontFamily="Arial, sans-serif" 
        fontSize="32" 
        fontWeight="bold" 
        fill="#C0C0C0" 
        textAnchor="middle"
        opacity="0.7"
      >
        $
      </text>
      
      {/* Gradients */}
      <defs>
        <linearGradient id="logoGradient" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#C9A961" stopOpacity="1" />
          <stop offset="100%" stopColor="#C0C0C0" stopOpacity="1" />
        </linearGradient>
        <linearGradient id="lineGradient" x1="0%" y1="0%" x2="100%" y2="0%">
          <stop offset="0%" stopColor="#C0C0C0" />
          <stop offset="50%" stopColor="#D4B76C" />
          <stop offset="100%" stopColor="#C9A961" />
        </linearGradient>
      </defs>
    </svg>
  )
}


//just a comment