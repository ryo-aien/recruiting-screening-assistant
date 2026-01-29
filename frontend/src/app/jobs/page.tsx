'use client'

import { useState, useRef, useEffect } from 'react'
import Link from 'next/link'
import { useSWRFetch } from '@/hooks/useSWRFetch'
import { Job, JobStatus, createJob, updateJobStatus } from '@/lib/api'

interface ConfirmModalState {
  isOpen: boolean
  job: Job | null
  newStatus: JobStatus | null
}

export default function JobsPage() {
  const { data: jobs, error, isLoading, mutate } = useSWRFetch<Job[]>('/jobs')
  const [isCreating, setIsCreating] = useState(false)
  const [newJob, setNewJob] = useState({ title: '', job_text_raw: '' })
  const [updatingJobId, setUpdatingJobId] = useState<string | null>(null)
  const [openMenuId, setOpenMenuId] = useState<string | null>(null)
  const [confirmModal, setConfirmModal] = useState<ConfirmModalState>({
    isOpen: false,
    job: null,
    newStatus: null,
  })
  const menuRef = useRef<HTMLDivElement>(null)

  // メニュー外クリックで閉じる
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        setOpenMenuId(null)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await createJob(newJob)
      setNewJob({ title: '', job_text_raw: '' })
      setIsCreating(false)
      mutate()
    } catch (err) {
      alert(err instanceof Error ? err.message : 'エラーが発生しました')
    }
  }

  const handleChangeStatus = (job: Job, newStatus: JobStatus) => {
    if (job.status === newStatus) {
      setOpenMenuId(null)
      return
    }

    setOpenMenuId(null)
    setConfirmModal({
      isOpen: true,
      job,
      newStatus,
    })
  }

  const handleConfirmStatusChange = async () => {
    if (!confirmModal.job || !confirmModal.newStatus) return

    const { job, newStatus } = confirmModal
    setConfirmModal({ isOpen: false, job: null, newStatus: null })
    setUpdatingJobId(job.job_id)

    try {
      await updateJobStatus(job.job_id, newStatus)
      mutate()
    } catch (err) {
      alert(err instanceof Error ? err.message : 'エラーが発生しました')
    } finally {
      setUpdatingJobId(null)
    }
  }

  const handleCancelStatusChange = () => {
    setConfirmModal({ isOpen: false, job: null, newStatus: null })
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 rounded-full border-4 border-[var(--accent-primary)]/30 border-t-[var(--accent-primary)] animate-spin" />
          <span className="text-[var(--text-secondary)]">読み込み中...</span>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="card p-8 text-center">
          <div className="w-16 h-16 rounded-full bg-red-500/20 flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-red-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
          </div>
          <p className="text-red-400 font-medium">エラー: {error.message}</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-[var(--text-primary)] mb-2">求人管理</h1>
          <p className="text-[var(--text-secondary)]">
            {jobs?.length || 0} 件の求人を管理中
          </p>
        </div>
        <button
          onClick={() => setIsCreating(true)}
          className="btn-primary inline-flex items-center gap-2"
        >
          <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <line x1="12" y1="5" x2="12" y2="19" />
            <line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          新規求人作成
        </button>
      </div>

      {/* Status Change Confirm Modal */}
      {confirmModal.isOpen && confirmModal.job && confirmModal.newStatus && (
        <div className="fixed inset-0 modal-overlay flex items-center justify-center z-50 animate-fadeIn">
          <div
            className="absolute inset-0"
            onClick={handleCancelStatusChange}
          />
          <div className="card p-6 w-full max-w-md mx-4 relative animate-scaleIn">
            {/* Icon */}
            <div className="flex justify-center mb-5">
              {confirmModal.newStatus === 'CLOSED' ? (
                <div className="w-14 h-14 rounded-full bg-amber-500/20 flex items-center justify-center">
                  <svg className="w-7 h-7 text-amber-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <circle cx="12" cy="12" r="10" />
                    <line x1="12" y1="8" x2="12" y2="12" />
                    <line x1="12" y1="16" x2="12.01" y2="16" />
                  </svg>
                </div>
              ) : (
                <div className="w-14 h-14 rounded-full bg-emerald-500/20 flex items-center justify-center">
                  <svg className="w-7 h-7 text-emerald-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" />
                    <polyline points="22 4 12 14.01 9 11.01" />
                  </svg>
                </div>
              )}
            </div>

            {/* Title */}
            <h3 className="text-lg font-bold text-[var(--text-primary)] text-center mb-2">
              {confirmModal.newStatus === 'CLOSED' ? '求人を締め切りますか？' : '求人を再開しますか？'}
            </h3>

            {/* Description */}
            <p className="text-sm text-[var(--text-secondary)] text-center mb-6">
              {confirmModal.newStatus === 'CLOSED' ? (
                <>
                  <span className="font-medium text-[var(--text-primary)]">{confirmModal.job.title}</span>
                  <br />
                  締め切り後は新規応募を受け付けられません。
                </>
              ) : (
                <>
                  <span className="font-medium text-[var(--text-primary)]">{confirmModal.job.title}</span>
                  <br />
                  再開すると応募の受付が可能になります。
                </>
              )}
            </p>

            {/* Buttons */}
            <div className="flex gap-3">
              <button
                onClick={handleCancelStatusChange}
                className="flex-1 btn-secondary"
              >
                キャンセル
              </button>
              <button
                onClick={handleConfirmStatusChange}
                className={`flex-1 px-4 py-2.5 rounded-xl font-medium transition-all ${
                  confirmModal.newStatus === 'CLOSED'
                    ? 'bg-amber-500 hover:bg-amber-600 text-white'
                    : 'bg-emerald-500 hover:bg-emerald-600 text-white'
                }`}
              >
                {confirmModal.newStatus === 'CLOSED' ? '締め切る' : '再開する'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Create Job Modal */}
      {isCreating && (
        <div className="fixed inset-0 modal-overlay flex items-center justify-center z-50 animate-fadeIn">
          <div
            className="absolute inset-0"
            onClick={() => setIsCreating(false)}
          />
          <div className="card p-8 w-full max-w-2xl mx-4 relative animate-scaleIn">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-[var(--text-primary)]">新規求人作成</h2>
              <button
                onClick={() => setIsCreating(false)}
                className="w-8 h-8 rounded-lg flex items-center justify-center hover:bg-[var(--bg-tertiary)] transition-colors"
              >
                <svg className="w-5 h-5 text-[var(--text-muted)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="18" y1="6" x2="6" y2="18" />
                  <line x1="6" y1="6" x2="18" y2="18" />
                </svg>
              </button>
            </div>
            <form onSubmit={handleCreate} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-[var(--text-secondary)] mb-2">
                  求人タイトル
                </label>
                <input
                  type="text"
                  value={newJob.title}
                  onChange={(e) => setNewJob({ ...newJob, title: e.target.value })}
                  className="input"
                  placeholder="例: シニアフロントエンドエンジニア"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-[var(--text-secondary)] mb-2">
                  求人内容
                </label>
                <textarea
                  value={newJob.job_text_raw}
                  onChange={(e) => setNewJob({ ...newJob, job_text_raw: e.target.value })}
                  className="input h-64 resize-none"
                  placeholder="職務内容、必須要件、歓迎要件などを記載..."
                  required
                />
              </div>
              <div className="flex justify-end gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setIsCreating(false)}
                  className="btn-secondary"
                >
                  キャンセル
                </button>
                <button type="submit" className="btn-primary">
                  作成する
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Jobs Grid */}
      {jobs?.length === 0 ? (
        <div className="card p-12 text-center">
          <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-[var(--accent-primary)]/20 to-[var(--accent-tertiary)]/20 flex items-center justify-center mx-auto mb-6">
            <svg className="w-10 h-10 text-[var(--accent-primary)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect x="2" y="7" width="20" height="14" rx="2" ry="2"/>
              <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>
            </svg>
          </div>
          <h3 className="text-xl font-semibold text-[var(--text-primary)] mb-2">求人がありません</h3>
          <p className="text-[var(--text-muted)] mb-6">
            最初の求人を作成して、採用活動を開始しましょう。
          </p>
          <button
            onClick={() => setIsCreating(true)}
            className="btn-primary inline-flex items-center gap-2"
          >
            <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <line x1="12" y1="5" x2="12" y2="19" />
              <line x1="5" y1="12" x2="19" y2="12" />
            </svg>
            新規求人作成
          </button>
        </div>
      ) : (
        <div className="grid gap-4">
          {jobs?.map((job, index) => (
            <div
              key={job.job_id}
              className={`card p-6 hover:border-[var(--accent-primary)]/30 group animate-fadeIn ${job.status === 'CLOSED' ? 'opacity-60' : ''} ${openMenuId === job.job_id ? 'relative z-40' : ''}`}
              style={{ animationDelay: `${index * 0.05}s`, opacity: 0 }}
            >
              <div className="flex items-center justify-between">
                <Link href={`/jobs/${job.job_id}`} className="flex items-center gap-4 flex-1">
                  <div className={`w-12 h-12 rounded-xl flex items-center justify-center group-hover:scale-110 transition-transform ${
                    job.status === 'CLOSED'
                      ? 'bg-gray-500/20 text-gray-400'
                      : 'bg-gradient-to-br from-[var(--accent-primary)]/20 to-[var(--accent-tertiary)]/20 text-[var(--accent-primary)]'
                  }`}>
                    <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <rect x="2" y="7" width="20" height="14" rx="2" ry="2"/>
                      <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>
                    </svg>
                  </div>
                  <div>
                    <h3 className={`text-lg font-semibold transition-colors ${
                      job.status === 'CLOSED'
                        ? 'text-[var(--text-muted)]'
                        : 'text-[var(--text-primary)] group-hover:text-[var(--accent-primary)]'
                    }`}>
                      {job.title}
                    </h3>
                    <div className="flex items-center gap-4 mt-1">
                      <span className="flex items-center gap-1.5 text-sm text-[var(--text-muted)]">
                        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                          <circle cx="9" cy="7" r="4"/>
                          <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                          <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                        </svg>
                        {job.candidate_count ?? 0} 名の応募者
                      </span>
                      <span className="flex items-center gap-1.5 text-sm text-[var(--text-muted)]">
                        <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                          <line x1="16" y1="2" x2="16" y2="6"/>
                          <line x1="8" y1="2" x2="8" y2="6"/>
                          <line x1="3" y1="10" x2="21" y2="10"/>
                        </svg>
                        {new Date(job.created_at).toLocaleDateString('ja-JP')}
                      </span>
                    </div>
                  </div>
                </Link>
                <div className="flex items-center gap-3">
                  {/* Status Badge */}
                  {job.status === 'OPEN' ? (
                    <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-[var(--accent-primary)]/10 text-[var(--accent-primary)] text-sm font-medium">
                      <span className="w-2 h-2 rounded-full bg-[var(--accent-primary)] animate-pulse" />
                      募集中
                    </div>
                  ) : (
                    <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-gray-500/10 text-gray-400 text-sm font-medium">
                      <span className="w-2 h-2 rounded-full bg-gray-400" />
                      締切
                    </div>
                  )}

                  {/* Detail Link */}
                  <Link
                    href={`/jobs/${job.job_id}`}
                    className="w-10 h-10 rounded-lg flex items-center justify-center bg-[var(--bg-tertiary)] hover:bg-[var(--accent-primary)] text-[var(--text-muted)] hover:text-white transition-all"
                  >
                    <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <polyline points="9 18 15 12 9 6" />
                    </svg>
                  </Link>

                  {/* Three Dots Menu */}
                  <div className="relative" ref={openMenuId === job.job_id ? menuRef : null}>
                    <button
                      onClick={(e) => {
                        e.preventDefault()
                        e.stopPropagation()
                        setOpenMenuId(openMenuId === job.job_id ? null : job.job_id)
                      }}
                      disabled={updatingJobId === job.job_id}
                      className="w-10 h-10 rounded-lg flex items-center justify-center hover:bg-[var(--bg-tertiary)] text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-all disabled:opacity-50"
                    >
                      {updatingJobId === job.job_id ? (
                        <div className="w-4 h-4 rounded-full border-2 border-current/30 border-t-current animate-spin" />
                      ) : (
                        <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                          <circle cx="12" cy="6" r="2" />
                          <circle cx="12" cy="12" r="2" />
                          <circle cx="12" cy="18" r="2" />
                        </svg>
                      )}
                    </button>

                    {/* Dropdown Menu */}
                    {openMenuId === job.job_id && (
                      <div className="absolute right-0 top-full mt-1 w-40 bg-[var(--bg-secondary)] border border-[var(--border-default)] rounded-lg shadow-lg overflow-hidden z-50 animate-fadeIn">
                        <div className="py-1">
                          <button
                            onClick={(e) => {
                              e.preventDefault()
                              e.stopPropagation()
                              handleChangeStatus(job, 'OPEN')
                            }}
                            className={`w-full px-4 py-2.5 text-left text-sm flex items-center gap-3 transition-colors ${
                              job.status === 'OPEN'
                                ? 'bg-[var(--accent-primary)]/10 text-[var(--accent-primary)]'
                                : 'text-[var(--text-secondary)] hover:bg-[var(--bg-tertiary)]'
                            }`}
                          >
                            <span className={`w-2 h-2 rounded-full ${
                              job.status === 'OPEN' ? 'bg-[var(--accent-primary)]' : 'bg-gray-400'
                            }`} />
                            募集中
                            {job.status === 'OPEN' && (
                              <svg className="w-4 h-4 ml-auto" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                                <polyline points="20 6 9 17 4 12" />
                              </svg>
                            )}
                          </button>
                          <button
                            onClick={(e) => {
                              e.preventDefault()
                              e.stopPropagation()
                              handleChangeStatus(job, 'CLOSED')
                            }}
                            className={`w-full px-4 py-2.5 text-left text-sm flex items-center gap-3 transition-colors ${
                              job.status === 'CLOSED'
                                ? 'bg-gray-500/10 text-gray-400'
                                : 'text-[var(--text-secondary)] hover:bg-[var(--bg-tertiary)]'
                            }`}
                          >
                            <span className={`w-2 h-2 rounded-full ${
                              job.status === 'CLOSED' ? 'bg-gray-400' : 'bg-gray-500'
                            }`} />
                            締切
                            {job.status === 'CLOSED' && (
                              <svg className="w-4 h-4 ml-auto" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                                <polyline points="20 6 9 17 4 12" />
                              </svg>
                            )}
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
