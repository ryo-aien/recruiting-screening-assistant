'use client'

interface DecisionBadgeProps {
  decision: string | null
  size?: 'sm' | 'md'
}

const decisionConfig = {
  pass: {
    label: '通過',
    bgColor: 'bg-emerald-500/20',
    textColor: 'text-emerald-300',
    borderColor: 'border-emerald-500/30',
    icon: (
      <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
        <polyline points="20 6 9 17 4 12" />
      </svg>
    ),
  },
  hold: {
    label: '保留',
    bgColor: 'bg-amber-500/20',
    textColor: 'text-amber-300',
    borderColor: 'border-amber-500/30',
    icon: (
      <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="10" />
        <line x1="8" y1="12" x2="16" y2="12" />
      </svg>
    ),
  },
  reject: {
    label: '見送り',
    bgColor: 'bg-red-500/20',
    textColor: 'text-red-300',
    borderColor: 'border-red-500/30',
    icon: (
      <svg className="w-3.5 h-3.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
        <line x1="18" y1="6" x2="6" y2="18" />
        <line x1="6" y1="6" x2="18" y2="18" />
      </svg>
    ),
  },
}

export function DecisionBadge({ decision, size = 'md' }: DecisionBadgeProps) {
  if (!decision) {
    return (
      <span
        className={`
          inline-flex items-center gap-1.5 rounded-full font-medium
          bg-[var(--bg-tertiary)] text-[var(--text-muted)] border border-[var(--border-default)]
          ${size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-3 py-1 text-xs'}
        `}
      >
        <span className="w-1.5 h-1.5 rounded-full bg-[var(--text-muted)]" />
        未決定
      </span>
    )
  }

  const config = decisionConfig[decision as keyof typeof decisionConfig]

  if (!config) {
    return null
  }

  return (
    <span
      className={`
        inline-flex items-center gap-1.5 rounded-full font-medium
        ${config.bgColor} ${config.textColor} border ${config.borderColor}
        transition-all duration-200 hover:scale-105
        ${size === 'sm' ? 'px-2 py-0.5 text-xs' : 'px-3 py-1 text-xs'}
      `}
    >
      {config.icon}
      {config.label}
    </span>
  )
}

// Large decision display for detail pages
export function DecisionDisplay({ decision }: { decision: string | null }) {
  if (!decision) {
    return (
      <div className="flex items-center gap-3 p-4 rounded-xl bg-[var(--bg-tertiary)] border border-[var(--border-default)]">
        <div className="w-10 h-10 rounded-full bg-[var(--bg-elevated)] flex items-center justify-center">
          <span className="text-[var(--text-muted)]">?</span>
        </div>
        <div>
          <div className="text-sm text-[var(--text-muted)]">判定</div>
          <div className="text-lg font-semibold text-[var(--text-secondary)]">未決定</div>
        </div>
      </div>
    )
  }

  const config = decisionConfig[decision as keyof typeof decisionConfig]

  if (!config) {
    return null
  }

  const iconBgClass = decision === 'pass'
    ? 'bg-emerald-500/30'
    : decision === 'hold'
      ? 'bg-amber-500/30'
      : 'bg-red-500/30'

  return (
    <div className={`flex items-center gap-3 p-4 rounded-xl ${config.bgColor} border ${config.borderColor}`}>
      <div className={`w-10 h-10 rounded-full ${iconBgClass} flex items-center justify-center ${config.textColor}`}>
        <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
          {decision === 'pass' && <polyline points="20 6 9 17 4 12" />}
          {decision === 'hold' && (
            <>
              <circle cx="12" cy="12" r="10" />
              <line x1="8" y1="12" x2="16" y2="12" />
            </>
          )}
          {decision === 'reject' && (
            <>
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </>
          )}
        </svg>
      </div>
      <div>
        <div className="text-sm text-[var(--text-muted)]">判定</div>
        <div className={`text-lg font-semibold ${config.textColor}`}>{config.label}</div>
      </div>
    </div>
  )
}
