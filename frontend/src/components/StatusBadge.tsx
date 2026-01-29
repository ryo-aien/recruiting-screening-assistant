'use client'

interface StatusBadgeProps {
  status: 'NEW' | 'PROCESSING' | 'DONE' | 'ERROR'
}

const statusConfig = {
  NEW: {
    label: '新規',
    bgColor: 'bg-slate-500/20',
    textColor: 'text-slate-300',
    borderColor: 'border-slate-500/30',
    dotColor: 'bg-slate-400',
  },
  PROCESSING: {
    label: '処理中',
    bgColor: 'bg-amber-500/20',
    textColor: 'text-amber-300',
    borderColor: 'border-amber-500/30',
    dotColor: 'bg-amber-400',
    animate: true,
  },
  DONE: {
    label: '完了',
    bgColor: 'bg-emerald-500/20',
    textColor: 'text-emerald-300',
    borderColor: 'border-emerald-500/30',
    dotColor: 'bg-emerald-400',
  },
  ERROR: {
    label: 'エラー',
    bgColor: 'bg-red-500/20',
    textColor: 'text-red-300',
    borderColor: 'border-red-500/30',
    dotColor: 'bg-red-400',
  },
}

export function StatusBadge({ status }: StatusBadgeProps) {
  const config = statusConfig[status]

  return (
    <span
      className={`
        inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium
        ${config.bgColor} ${config.textColor} border ${config.borderColor}
        transition-all duration-200
      `}
    >
      <span
        className={`
          w-1.5 h-1.5 rounded-full ${config.dotColor}
          ${config.animate ? 'animate-pulse' : ''}
        `}
      />
      {config.label}
    </span>
  )
}
