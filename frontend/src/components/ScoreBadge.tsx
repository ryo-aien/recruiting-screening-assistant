'use client'

interface ScoreBadgeProps {
  score: number | null
  size?: 'sm' | 'md' | 'lg'
  showLabel?: boolean
}

export function ScoreBadge({ score, size = 'md', showLabel = true }: ScoreBadgeProps) {
  if (score === null) {
    return (
      <div className="flex items-center gap-2">
        <div
          className={`
            flex items-center justify-center rounded-xl
            bg-[var(--bg-tertiary)] border border-[var(--border-default)]
            text-[var(--text-muted)]
            ${size === 'sm' ? 'w-10 h-10 text-sm' : ''}
            ${size === 'md' ? 'w-12 h-12 text-base' : ''}
            ${size === 'lg' ? 'w-16 h-16 text-xl' : ''}
          `}
        >
          —
        </div>
        {showLabel && (
          <span className="text-sm text-[var(--text-muted)]">未算出</span>
        )}
      </div>
    )
  }

  const getScoreConfig = (score: number) => {
    if (score >= 70) {
      return {
        gradient: 'from-emerald-500 to-teal-400',
        shadow: 'shadow-emerald-500/30',
        textColor: 'text-emerald-400',
        priority: 'A',
        label: '高適合',
      }
    }
    if (score >= 40) {
      return {
        gradient: 'from-amber-500 to-yellow-400',
        shadow: 'shadow-amber-500/30',
        textColor: 'text-amber-400',
        priority: 'B',
        label: '中適合',
      }
    }
    return {
      gradient: 'from-red-500 to-orange-400',
      shadow: 'shadow-red-500/30',
      textColor: 'text-red-400',
      priority: 'C',
      label: '要確認',
    }
  }

  const config = getScoreConfig(score)

  return (
    <div className="flex items-center gap-3">
      <div
        className={`
          relative flex items-center justify-center rounded-xl font-bold text-white
          bg-gradient-to-br ${config.gradient}
          shadow-lg ${config.shadow}
          transition-all duration-300 hover:scale-105
          ${size === 'sm' ? 'w-10 h-10 text-sm' : ''}
          ${size === 'md' ? 'w-12 h-12 text-lg' : ''}
          ${size === 'lg' ? 'w-16 h-16 text-2xl' : ''}
        `}
      >
        {score}
        {/* Glow effect */}
        <div
          className={`
            absolute inset-0 rounded-xl bg-gradient-to-br ${config.gradient}
            opacity-50 blur-md -z-10
          `}
        />
      </div>
      {showLabel && (
        <div className="flex flex-col">
          <span className={`text-sm font-semibold ${config.textColor}`}>
            優先度 {config.priority}
          </span>
          <span className="text-xs text-[var(--text-muted)]">
            {config.label}
          </span>
        </div>
      )}
    </div>
  )
}

// Compact version for table cells
export function ScoreCircle({ score }: { score: number | null }) {
  if (score === null) {
    return (
      <div className="w-8 h-8 rounded-lg bg-[var(--bg-tertiary)] border border-[var(--border-default)] flex items-center justify-center text-[var(--text-muted)] text-xs">
        —
      </div>
    )
  }

  const getGradient = (score: number) => {
    if (score >= 70) return 'from-emerald-500 to-teal-400'
    if (score >= 40) return 'from-amber-500 to-yellow-400'
    return 'from-red-500 to-orange-400'
  }

  return (
    <div
      className={`
        w-8 h-8 rounded-lg font-bold text-white text-xs
        bg-gradient-to-br ${getGradient(score)}
        flex items-center justify-center
        shadow-md transition-transform hover:scale-110
      `}
    >
      {score}
    </div>
  )
}
