'use client'

import Link from 'next/link'
import { useSWRFetch } from '@/hooks/useSWRFetch'
import { Job } from '@/lib/api'
import { StatusBadge } from '@/components/StatusBadge'
import { ScoreCircle } from '@/components/ScoreBadge'

interface DashboardStats {
  total_jobs: number
  total_candidates: number
  candidates_by_status: {
    NEW: number
    PROCESSING: number
    DONE: number
    ERROR: number
  }
  candidates_by_decision: {
    pass: number
    hold: number
    reject: number
    undecided: number
  }
  recent_candidates: Array<{
    candidate_id: string
    display_name: string | null
    job_title: string
    job_id: string
    status: 'NEW' | 'PROCESSING' | 'DONE' | 'ERROR'
    total_fit_0_100: number | null
    submitted_at: string
  }>
}

export default function DashboardPage() {
  const { data: jobs } = useSWRFetch<Job[]>('/jobs')
  const { data: stats } = useSWRFetch<DashboardStats>('/dashboard/stats')

  // Fallback stats from jobs data if dashboard API is not available
  const totalJobs = stats?.total_jobs ?? jobs?.length ?? 0
  const totalCandidates = stats?.total_candidates ?? jobs?.reduce((acc, job) => acc + (job.candidate_count ?? 0), 0) ?? 0

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[var(--text-primary)]">ダッシュボード</h1>
          <p className="text-[var(--text-muted)] mt-1">採用活動の概要を確認できます</p>
        </div>
        <Link href="/jobs" className="btn-primary inline-flex items-center gap-2">
          <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="12" y1="5" x2="12" y2="19" />
            <line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          新規求人作成
        </Link>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="求人数"
          value={totalJobs}
          icon={
            <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect x="2" y="7" width="20" height="14" rx="2" ry="2"/>
              <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>
            </svg>
          }
          color="primary"
        />
        <StatCard
          title="応募者数"
          value={totalCandidates}
          icon={
            <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
              <circle cx="9" cy="7" r="4"/>
              <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
              <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
            </svg>
          }
          color="secondary"
        />
        <StatCard
          title="処理完了"
          value={stats?.candidates_by_status?.DONE ?? 0}
          icon={
            <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
              <polyline points="22 4 12 14.01 9 11.01"/>
            </svg>
          }
          color="success"
        />
        <StatCard
          title="判定待ち"
          value={stats?.candidates_by_decision?.undecided ?? 0}
          icon={
            <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10"/>
              <polyline points="12 6 12 12 16 14"/>
            </svg>
          }
          color="warning"
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Processing Status */}
        <div className="lg:col-span-1">
          <div className="card p-6 h-full">
            <h2 className="text-lg font-semibold text-[var(--text-primary)] mb-4">処理状況</h2>
            <div className="space-y-4">
              <StatusRow
                label="新規"
                count={stats?.candidates_by_status?.NEW ?? 0}
                total={totalCandidates}
                color="slate"
              />
              <StatusRow
                label="処理中"
                count={stats?.candidates_by_status?.PROCESSING ?? 0}
                total={totalCandidates}
                color="amber"
              />
              <StatusRow
                label="完了"
                count={stats?.candidates_by_status?.DONE ?? 0}
                total={totalCandidates}
                color="emerald"
              />
              <StatusRow
                label="エラー"
                count={stats?.candidates_by_status?.ERROR ?? 0}
                total={totalCandidates}
                color="red"
              />
            </div>
          </div>
        </div>

        {/* Decision Status */}
        <div className="lg:col-span-1">
          <div className="card p-6 h-full">
            <h2 className="text-lg font-semibold text-[var(--text-primary)] mb-4">判定状況</h2>
            <div className="space-y-4">
              <StatusRow
                label="通過"
                count={stats?.candidates_by_decision?.pass ?? 0}
                total={totalCandidates}
                color="emerald"
              />
              <StatusRow
                label="保留"
                count={stats?.candidates_by_decision?.hold ?? 0}
                total={totalCandidates}
                color="amber"
              />
              <StatusRow
                label="見送り"
                count={stats?.candidates_by_decision?.reject ?? 0}
                total={totalCandidates}
                color="red"
              />
              <StatusRow
                label="未判定"
                count={stats?.candidates_by_decision?.undecided ?? 0}
                total={totalCandidates}
                color="slate"
              />
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="lg:col-span-1">
          <div className="card p-6 h-full">
            <h2 className="text-lg font-semibold text-[var(--text-primary)] mb-4">クイックアクション</h2>
            <div className="space-y-3">
              <Link
                href="/jobs"
                className="flex items-center gap-3 p-3 rounded-xl bg-[var(--bg-tertiary)] hover:bg-[var(--bg-elevated)] border border-[var(--border-subtle)] hover:border-[var(--accent-primary)]/30 transition-all group"
              >
                <div className="w-10 h-10 rounded-lg bg-[var(--accent-primary)]/10 flex items-center justify-center text-[var(--accent-primary)]">
                  <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <rect x="2" y="7" width="20" height="14" rx="2" ry="2"/>
                    <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>
                  </svg>
                </div>
                <div className="flex-1">
                  <span className="text-sm font-medium text-[var(--text-primary)] group-hover:text-[var(--accent-primary)] transition-colors">求人一覧を見る</span>
                  <p className="text-xs text-[var(--text-muted)]">全ての求人を管理</p>
                </div>
                <svg className="w-5 h-5 text-[var(--text-muted)] group-hover:text-[var(--accent-primary)] transition-colors" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="9 18 15 12 9 6" />
                </svg>
              </Link>

              <Link
                href="/admin/score-config"
                className="flex items-center gap-3 p-3 rounded-xl bg-[var(--bg-tertiary)] hover:bg-[var(--bg-elevated)] border border-[var(--border-subtle)] hover:border-[var(--accent-primary)]/30 transition-all group"
              >
                <div className="w-10 h-10 rounded-lg bg-[var(--accent-secondary)]/10 flex items-center justify-center text-[var(--accent-secondary)]">
                  <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <line x1="4" y1="21" x2="4" y2="14"/>
                    <line x1="4" y1="10" x2="4" y2="3"/>
                    <line x1="12" y1="21" x2="12" y2="12"/>
                    <line x1="12" y1="8" x2="12" y2="3"/>
                    <line x1="20" y1="21" x2="20" y2="16"/>
                    <line x1="20" y1="12" x2="20" y2="3"/>
                  </svg>
                </div>
                <div className="flex-1">
                  <span className="text-sm font-medium text-[var(--text-primary)] group-hover:text-[var(--accent-primary)] transition-colors">スコア設定</span>
                  <p className="text-xs text-[var(--text-muted)]">評価パラメータを調整</p>
                </div>
                <svg className="w-5 h-5 text-[var(--text-muted)] group-hover:text-[var(--accent-primary)] transition-colors" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="9 18 15 12 9 6" />
                </svg>
              </Link>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Candidates & Jobs */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Candidates */}
        <div className="card p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-[var(--text-primary)]">最近の応募者</h2>
            <Link href="/jobs" className="text-sm text-[var(--accent-primary)] hover:underline">
              すべて見る
            </Link>
          </div>
          {stats?.recent_candidates && stats.recent_candidates.length > 0 ? (
            <div className="space-y-3">
              {stats.recent_candidates.slice(0, 5).map((candidate) => (
                <Link
                  key={candidate.candidate_id}
                  href={`/candidates/${candidate.candidate_id}`}
                  className="flex items-center gap-3 p-3 rounded-xl bg-[var(--bg-tertiary)] hover:bg-[var(--bg-elevated)] transition-colors group"
                >
                  <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-[var(--accent-primary)] to-[var(--accent-tertiary)] flex items-center justify-center text-white font-semibold">
                    {(candidate.display_name || 'A')[0].toUpperCase()}
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-[var(--text-primary)] truncate group-hover:text-[var(--accent-primary)] transition-colors">
                        {candidate.display_name || `応募者 ${candidate.candidate_id.slice(0, 8)}`}
                      </span>
                      <StatusBadge status={candidate.status} />
                    </div>
                    <p className="text-xs text-[var(--text-muted)] truncate">{candidate.job_title}</p>
                  </div>
                  <ScoreCircle score={candidate.total_fit_0_100} />
                </Link>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <div className="w-12 h-12 rounded-xl bg-[var(--bg-tertiary)] flex items-center justify-center mx-auto mb-3">
                <svg className="w-6 h-6 text-[var(--text-muted)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                  <circle cx="9" cy="7" r="4"/>
                </svg>
              </div>
              <p className="text-sm text-[var(--text-muted)]">まだ応募者がいません</p>
            </div>
          )}
        </div>

        {/* Recent Jobs */}
        <div className="card p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-[var(--text-primary)]">求人一覧</h2>
            <Link href="/jobs" className="text-sm text-[var(--accent-primary)] hover:underline">
              すべて見る
            </Link>
          </div>
          {jobs && jobs.length > 0 ? (
            <div className="space-y-3">
              {jobs.slice(0, 5).map((job) => (
                <Link
                  key={job.job_id}
                  href={`/jobs/${job.job_id}`}
                  className="flex items-center gap-3 p-3 rounded-xl bg-[var(--bg-tertiary)] hover:bg-[var(--bg-elevated)] transition-colors group"
                >
                  <div className="w-10 h-10 rounded-lg bg-[var(--accent-primary)]/10 flex items-center justify-center text-[var(--accent-primary)]">
                    <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <rect x="2" y="7" width="20" height="14" rx="2" ry="2"/>
                      <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>
                    </svg>
                  </div>
                  <div className="flex-1 min-w-0">
                    <span className="text-sm font-medium text-[var(--text-primary)] truncate block group-hover:text-[var(--accent-primary)] transition-colors">
                      {job.title}
                    </span>
                    <p className="text-xs text-[var(--text-muted)]">
                      {job.candidate_count ?? 0} 名の応募者
                    </p>
                  </div>
                  <svg className="w-5 h-5 text-[var(--text-muted)] group-hover:text-[var(--accent-primary)] transition-colors" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <polyline points="9 18 15 12 9 6" />
                  </svg>
                </Link>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <div className="w-12 h-12 rounded-xl bg-[var(--bg-tertiary)] flex items-center justify-center mx-auto mb-3">
                <svg className="w-6 h-6 text-[var(--text-muted)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="2" y="7" width="20" height="14" rx="2" ry="2"/>
                  <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>
                </svg>
              </div>
              <p className="text-sm text-[var(--text-muted)]">まだ求人がありません</p>
              <Link href="/jobs" className="btn-primary inline-flex items-center gap-2 mt-4 text-sm">
                <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="12" y1="5" x2="12" y2="19" />
                  <line x1="5" y1="12" x2="19" y2="12" />
                </svg>
                求人を作成
              </Link>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

function StatCard({
  title,
  value,
  icon,
  color,
}: {
  title: string
  value: number
  icon: React.ReactNode
  color: 'primary' | 'secondary' | 'success' | 'warning'
}) {
  const colorClasses = {
    primary: 'from-[var(--accent-primary)]/20 to-[var(--accent-primary)]/5 text-[var(--accent-primary)]',
    secondary: 'from-[var(--accent-secondary)]/20 to-[var(--accent-secondary)]/5 text-[var(--accent-secondary)]',
    success: 'from-emerald-500/20 to-emerald-500/5 text-emerald-400',
    warning: 'from-amber-500/20 to-amber-500/5 text-amber-400',
  }

  return (
    <div className="card p-5">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-[var(--text-muted)]">{title}</p>
          <p className="text-3xl font-bold text-[var(--text-primary)] mt-1">{value}</p>
        </div>
        <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${colorClasses[color]} flex items-center justify-center`}>
          {icon}
        </div>
      </div>
    </div>
  )
}

function StatusRow({
  label,
  count,
  total,
  color,
}: {
  label: string
  count: number
  total: number
  color: 'slate' | 'amber' | 'emerald' | 'red'
}) {
  const percentage = total > 0 ? Math.round((count / total) * 100) : 0

  const colorClasses = {
    slate: 'bg-slate-500',
    amber: 'bg-amber-500',
    emerald: 'bg-emerald-500',
    red: 'bg-red-500',
  }

  return (
    <div>
      <div className="flex items-center justify-between text-sm mb-2">
        <span className="text-[var(--text-secondary)]">{label}</span>
        <span className="font-medium text-[var(--text-primary)]">{count}</span>
      </div>
      <div className="h-2 rounded-full bg-[var(--bg-tertiary)] overflow-hidden">
        <div
          className={`h-full rounded-full ${colorClasses[color]} transition-all duration-500`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  )
}
