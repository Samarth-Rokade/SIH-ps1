/**
 * Decorative infrastructure line-art for the sidebar's empty lower space.
 * Uses currentColor at low opacity so it reads as a subtle emboss on the
 * sidebar's own background in both themes (the sidebar stays a dark blue
 * panel in light mode too - see index.css sidebar-* tokens).
 */
export default function SidebarIllustration({ className = "" }) {
  return (
    <svg
      viewBox="0 0 260 260"
      fill="none"
      className={`text-white/10 ${className}`}
      preserveAspectRatio="xMidYMax slice"
      aria-hidden="true"
    >
      {/* ground line */}
      <line x1="0" y1="230" x2="260" y2="230" stroke="currentColor" strokeWidth="1.5" />

      {/* suspension bridge */}
      <path
        d="M20 230 V150 M95 230 V150"
        stroke="currentColor"
        strokeWidth="2"
        strokeLinecap="round"
      />
      <path
        d="M0 190 Q57 145 115 190"
        stroke="currentColor"
        strokeWidth="1.5"
        strokeLinecap="round"
      />
      <path d="M20 195 V150 M40 187 V150 M60 187 V150 M75 195 V150" stroke="currentColor" strokeWidth="1" />
      <line x1="0" y1="205" x2="115" y2="205" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />

      {/* skyline blocks */}
      <rect x="125" y="170" width="20" height="60" stroke="currentColor" strokeWidth="1.5" />
      <rect x="150" y="145" width="24" height="85" stroke="currentColor" strokeWidth="1.5" />
      <rect x="179" y="185" width="16" height="45" stroke="currentColor" strokeWidth="1.5" />

      {/* wind turbine (tall) */}
      <g strokeLinecap="round">
        <line x1="215" y1="230" x2="215" y2="120" stroke="currentColor" strokeWidth="2" />
        <circle cx="215" cy="120" r="2.5" fill="currentColor" stroke="none" />
        <path
          d="M215 120 L245 108 M215 120 L192 100 M215 120 L206 145"
          stroke="currentColor"
          strokeWidth="2"
        />
      </g>

      {/* wind turbine (short) */}
      <g strokeLinecap="round">
        <line x1="245" y1="230" x2="245" y2="165" stroke="currentColor" strokeWidth="1.5" />
        <circle cx="245" cy="165" r="2" fill="currentColor" stroke="none" />
        <path
          d="M245 165 L262 156 M245 165 L229 150 M245 165 L238 182"
          stroke="currentColor"
          strokeWidth="1.5"
        />
      </g>
    </svg>
  );
}
