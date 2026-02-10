import React from 'react'

export default function DropAudioAnimation() {
  return (
    <div className="drop-audio-animation">
      <svg 
        width="200" 
        height="200" 
        viewBox="0 0 200 200" 
        fill="none" 
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* Microphone body */}
        <g className="microphone-group">
          {/* Mic stand */}
          <line x1="100" y1="140" x2="100" y2="165" stroke="#C0C0C0" strokeWidth="3" strokeLinecap="round"/>
          <path d="M 85 165 L 115 165" stroke="#C0C0C0" strokeWidth="3" strokeLinecap="round"/>
          
          {/* Mic body */}
          <rect x="85" y="60" width="30" height="60" rx="15" fill="url(#micGradient)" stroke="#C9A961" strokeWidth="2"/>
          
          {/* Mic grid lines */}
          <line x1="90" y1="75" x2="110" y2="75" stroke="#1a1a1a" strokeWidth="1.5" opacity="0.3"/>
          <line x1="90" y1="85" x2="110" y2="85" stroke="#1a1a1a" strokeWidth="1.5" opacity="0.3"/>
          <line x1="90" y1="95" x2="110" y2="95" stroke="#1a1a1a" strokeWidth="1.5" opacity="0.3"/>
          <line x1="90" y1="105" x2="110" y2="105" stroke="#1a1a1a" strokeWidth="1.5" opacity="0.3"/>
          
          {/* Mic connector */}
          <path d="M 100 120 Q 100 130 100 140" stroke="#C0C0C0" strokeWidth="2" fill="none"/>
          
          {/* Sound waves (animated) */}
          <g className="sound-wave-1">
            <path d="M 125 70 Q 135 80 125 90" stroke="#C9A961" strokeWidth="2" fill="none" opacity="0.6"/>
          </g>
          <g className="sound-wave-2">
            <path d="M 140 70 Q 155 80 140 90" stroke="#C0C0C0" strokeWidth="2" fill="none" opacity="0.4"/>
          </g>
          <g className="sound-wave-1">
            <path d="M 75 70 Q 65 80 75 90" stroke="#C9A961" strokeWidth="2" fill="none" opacity="0.6"/>
          </g>
          <g className="sound-wave-2">
            <path d="M 60 70 Q 45 80 60 90" stroke="#C0C0C0" strokeWidth="2" fill="none" opacity="0.4"/>
          </g>
        </g>
        
        {/* Drop/Upload arrow (animated) */}
        <g className="drop-arrow">
          <path 
            d="M 100 20 L 100 50" 
            stroke="#D4B76C" 
            strokeWidth="3" 
            strokeLinecap="round"
            markerEnd="url(#arrowhead)"
          />
          <polygon 
            points="100,50 95,40 105,40" 
            fill="#D4B76C"
          />
        </g>
        
        {/* Text */}
        <text 
          x="100" 
          y="190" 
          fontFamily="Inter, sans-serif" 
          fontSize="14" 
          fontWeight="600" 
          fill="#C0C0C0" 
          textAnchor="middle"
          letterSpacing="1"
        >
          DROP YOUR AUDIO
        </text>
        
        <defs>
          <linearGradient id="micGradient" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" stopColor="#C9A961" stopOpacity="0.8" />
            <stop offset="100%" stopColor="#A88B4A" stopOpacity="0.6" />
          </linearGradient>
        </defs>
      </svg>
    </div>
  )
}
