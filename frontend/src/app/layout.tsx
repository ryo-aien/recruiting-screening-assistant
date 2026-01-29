import type { Metadata } from 'next'
import './globals.css'
import { Sidebar } from '@/components/Sidebar'

export const metadata: Metadata = {
  title: 'Talent Insight | AI採用スクリーニング',
  description: 'AIによる書類選考の前処理を自動化し、採用担当者の意思決定を支援',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="ja">
      <body className="noise-overlay">
        <div className="min-h-screen flex">
          {/* Sidebar */}
          <Sidebar />

          {/* Main Content */}
          <div className="flex-1 flex flex-col ml-64">
            {/* Top Header */}
            <header className="sticky top-0 z-40 h-16 border-b border-[var(--border-subtle)] bg-[var(--bg-primary)]/80 backdrop-blur-xl">
              <div className="h-full px-6 flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <h1 className="text-lg font-semibold text-[var(--text-primary)]" id="page-title">
                    ダッシュボード
                  </h1>
                </div>
                <div className="flex items-center gap-4">
                  <button className="w-10 h-10 rounded-xl flex items-center justify-center hover:bg-[var(--bg-tertiary)] transition-colors text-[var(--text-muted)]">
                    <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
                      <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
                    </svg>
                  </button>
                  <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-[var(--accent-primary)] to-[var(--accent-tertiary)] flex items-center justify-center text-white font-semibold">
                    A
                  </div>
                </div>
              </div>
            </header>

            {/* Page Content */}
            <main className="flex-1 bg-[var(--bg-secondary)]">
              <div className="p-6">
                {children}
              </div>
            </main>
          </div>
        </div>
      </body>
    </html>
  )
}
