'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'

const navigation = [
  {
    name: 'ダッシュボード',
    href: '/',
    icon: (
      <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <rect x="3" y="3" width="7" height="7"/>
        <rect x="14" y="3" width="7" height="7"/>
        <rect x="14" y="14" width="7" height="7"/>
        <rect x="3" y="14" width="7" height="7"/>
      </svg>
    ),
  },
  {
    name: '求人管理',
    href: '/jobs',
    icon: (
      <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <rect x="2" y="7" width="20" height="14" rx="2" ry="2"/>
        <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>
      </svg>
    ),
  },
]

const settingsNavigation = [
  {
    name: 'スコア設定',
    href: '/admin/score-config',
    icon: (
      <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <line x1="4" y1="21" x2="4" y2="14"/>
        <line x1="4" y1="10" x2="4" y2="3"/>
        <line x1="12" y1="21" x2="12" y2="12"/>
        <line x1="12" y1="8" x2="12" y2="3"/>
        <line x1="20" y1="21" x2="20" y2="16"/>
        <line x1="20" y1="12" x2="20" y2="3"/>
        <line x1="1" y1="14" x2="7" y2="14"/>
        <line x1="9" y1="8" x2="15" y2="8"/>
        <line x1="17" y1="16" x2="23" y2="16"/>
      </svg>
    ),
  },
  {
    name: 'ヘルプ',
    href: '/help',
    icon: (
      <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
        <circle cx="12" cy="12" r="10"/>
        <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/>
        <line x1="12" y1="17" x2="12.01" y2="17"/>
      </svg>
    ),
  },
]

export function Sidebar() {
  const pathname = usePathname()

  return (
    <aside className="fixed inset-y-0 left-0 z-50 w-64 bg-[var(--bg-primary)] border-r border-[var(--border-subtle)]">
      <div className="flex flex-col h-full">
        {/* Logo */}
        <div className="h-16 flex items-center gap-3 px-6 border-b border-[var(--border-subtle)]">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[var(--accent-primary)] via-[var(--accent-secondary)] to-[var(--accent-tertiary)] flex items-center justify-center shadow-lg">
            <svg className="w-5 h-5 text-white" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 2L2 7l10 5 10-5-10-5z"/>
              <path d="M2 17l10 5 10-5"/>
              <path d="M2 12l10 5 10-5"/>
            </svg>
          </div>
          <div className="flex flex-col">
            <span className="text-base font-semibold tracking-tight text-[var(--text-primary)]">
              Talent Insight
            </span>
            <span className="text-xs text-[var(--text-muted)] -mt-0.5">
              AI Screening Platform
            </span>
          </div>
        </div>

        {/* Navigation */}
        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
          <div className="mb-2">
            <span className="px-3 text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider">
              メイン
            </span>
          </div>
          {navigation.map((item) => {
            const isActive = pathname === item.href || (item.href !== '/' && pathname.startsWith(item.href))
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`
                  flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200
                  ${isActive
                    ? 'bg-[var(--accent-primary)]/10 text-[var(--accent-primary)] border border-[var(--accent-primary)]/20'
                    : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-tertiary)]'
                  }
                `}
              >
                <span className={isActive ? 'text-[var(--accent-primary)]' : 'text-[var(--text-muted)]'}>
                  {item.icon}
                </span>
                {item.name}
              </Link>
            )
          })}

          <div className="pt-6 mb-2">
            <span className="px-3 text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider">
              設定
            </span>
          </div>
          {settingsNavigation.map((item) => {
            const isActive = pathname === item.href
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`
                  flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-200
                  ${isActive
                    ? 'bg-[var(--accent-primary)]/10 text-[var(--accent-primary)] border border-[var(--accent-primary)]/20'
                    : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-tertiary)]'
                  }
                `}
              >
                <span className={isActive ? 'text-[var(--accent-primary)]' : 'text-[var(--text-muted)]'}>
                  {item.icon}
                </span>
                {item.name}
              </Link>
            )
          })}
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-[var(--border-subtle)]">
          <div className="flex items-center gap-3 px-3 py-2">
            <span className="flex items-center gap-1.5 text-xs text-[var(--text-muted)]">
              <span className="w-2 h-2 rounded-full bg-[var(--score-excellent)] animate-pulse"/>
              システム稼働中
            </span>
          </div>
          <div className="px-3 mt-1">
            <span className="text-xs text-[var(--text-muted)]">v1.0.0</span>
          </div>
        </div>
      </div>
    </aside>
  )
}
