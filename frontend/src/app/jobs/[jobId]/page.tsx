'use client'

import { useState, useRef } from 'react'
import Link from 'next/link'
import { useSWRFetch } from '@/hooks/useSWRFetch'
import { Job, CandidateListItem, createCandidate, uploadDocument } from '@/lib/api'
import { StatusBadge } from '@/components/StatusBadge'
import { ScoreCircle } from '@/components/ScoreBadge'
import { DecisionBadge } from '@/components/DecisionBadge'

export default function JobDetailPage({ params }: { params: { jobId: string } }) {
  const { jobId } = params
  const { data: job, error: jobError } = useSWRFetch<Job>(`/jobs/${jobId}`)
  const {
    data: candidates,
    error: candidatesError,
    mutate: mutateCandidates,
  } = useSWRFetch<CandidateListItem[]>(`/jobs/${jobId}/candidates?sort_by_score=true`)

  const [isAddingCandidate, setIsAddingCandidate] = useState(false)
  const [newCandidateName, setNewCandidateName] = useState('')
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [isUploading, setIsUploading] = useState(false)
  const [showJobContent, setShowJobContent] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const handleAddCandidate = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!selectedFile) {
      alert('ファイルを選択してください')
      return
    }

    setIsUploading(true)
    try {
      const candidate = await createCandidate(jobId, {
        display_name: newCandidateName || undefined,
      })

      await uploadDocument(candidate.candidate_id, selectedFile, 'resume')

      setNewCandidateName('')
      setSelectedFile(null)
      setIsAddingCandidate(false)
      mutateCandidates()
    } catch (err) {
      alert(err instanceof Error ? err.message : 'エラーが発生しました')
    } finally {
      setIsUploading(false)
    }
  }

  if (jobError || candidatesError) {
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
          <p className="text-red-400 font-medium">
            エラー: {(jobError || candidatesError)?.message}
          </p>
        </div>
      </div>
    )
  }

  if (!job) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 rounded-full border-4 border-[var(--accent-primary)]/30 border-t-[var(--accent-primary)] animate-spin" />
          <span className="text-[var(--text-secondary)]">読み込み中...</span>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Breadcrumb */}
      <nav className="flex items-center gap-2 text-sm">
        <Link
          href="/jobs"
          className="text-[var(--text-muted)] hover:text-[var(--accent-primary)] transition-colors"
        >
          求人管理
        </Link>
        <svg className="w-4 h-4 text-[var(--text-muted)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="9 18 15 12 9 6" />
        </svg>
        <span className="text-[var(--text-primary)]">{job.title}</span>
      </nav>

      {/* Job Header */}
      <div className="card p-6">
        <div className="flex items-start justify-between">
          <div className="flex items-start gap-4">
            <div className="w-14 h-14 rounded-xl bg-gradient-to-br from-[var(--accent-primary)]/20 to-[var(--accent-tertiary)]/20 flex items-center justify-center text-[var(--accent-primary)]">
              <svg className="w-7 h-7" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <rect x="2" y="7" width="20" height="14" rx="2" ry="2"/>
                <path d="M16 21V5a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v16"/>
              </svg>
            </div>
            <div>
              <h1 className="text-2xl font-bold text-[var(--text-primary)] mb-2">{job.title}</h1>
              <div className="flex items-center gap-4 text-sm text-[var(--text-muted)]">
                <span className="flex items-center gap-1.5">
                  <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                    <circle cx="9" cy="7" r="4"/>
                    <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                    <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
                  </svg>
                  {candidates?.length ?? 0} 名の応募者
                </span>
                <span className="flex items-center gap-1.5">
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
          </div>
          <button
            onClick={() => setShowJobContent(!showJobContent)}
            className="btn-secondary text-sm flex items-center gap-2"
          >
            <svg className={`w-4 h-4 transition-transform ${showJobContent ? 'rotate-180' : ''}`} viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="6 9 12 15 18 9" />
            </svg>
            求人内容
          </button>
        </div>

        {showJobContent && (
          <div className="mt-6 pt-6 border-t border-[var(--border-subtle)]">
            <pre className="whitespace-pre-wrap text-sm text-[var(--text-secondary)] bg-[var(--bg-tertiary)] p-4 rounded-xl overflow-auto max-h-64 font-sans">
              {job.job_text_raw}
            </pre>
          </div>
        )}
      </div>

      {/* Candidates Section */}
      <div className="space-y-4">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <h2 className="text-xl font-bold text-[var(--text-primary)]">
            応募者一覧
          </h2>
          <button
            onClick={() => setIsAddingCandidate(true)}
            className="btn-primary inline-flex items-center gap-2"
          >
            <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
              <circle cx="8.5" cy="7" r="4"/>
              <line x1="20" y1="8" x2="20" y2="14"/>
              <line x1="23" y1="11" x2="17" y2="11"/>
            </svg>
            応募者追加
          </button>
        </div>

        {/* Add Candidate Modal */}
        {isAddingCandidate && (
          <div className="fixed inset-0 modal-overlay flex items-center justify-center z-50 animate-fadeIn">
            <div
              className="absolute inset-0"
              onClick={() => {
                if (!isUploading) {
                  setIsAddingCandidate(false)
                  setSelectedFile(null)
                }
              }}
            />
            <div className="card p-8 w-full max-w-md mx-4 relative animate-scaleIn">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-xl font-bold text-[var(--text-primary)]">応募者追加</h2>
                <button
                  onClick={() => {
                    if (!isUploading) {
                      setIsAddingCandidate(false)
                      setSelectedFile(null)
                    }
                  }}
                  className="w-8 h-8 rounded-lg flex items-center justify-center hover:bg-[var(--bg-tertiary)] transition-colors"
                  disabled={isUploading}
                >
                  <svg className="w-5 h-5 text-[var(--text-muted)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <line x1="18" y1="6" x2="6" y2="18" />
                    <line x1="6" y1="6" x2="18" y2="18" />
                  </svg>
                </button>
              </div>
              <form onSubmit={handleAddCandidate} className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-[var(--text-secondary)] mb-2">
                    氏名（任意）
                  </label>
                  <input
                    type="text"
                    value={newCandidateName}
                    onChange={(e) => setNewCandidateName(e.target.value)}
                    className="input"
                    placeholder="匿名の場合は空欄"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-[var(--text-secondary)] mb-2">
                    書類アップロード
                  </label>
                  <div
                    className={`
                      border-2 border-dashed rounded-xl p-6 text-center cursor-pointer
                      transition-all hover:border-[var(--accent-primary)] hover:bg-[var(--accent-primary)]/5
                      ${selectedFile ? 'border-[var(--accent-primary)] bg-[var(--accent-primary)]/5' : 'border-[var(--border-default)]'}
                    `}
                    onClick={() => fileInputRef.current?.click()}
                  >
                    <input
                      type="file"
                      ref={fileInputRef}
                      accept=".pdf,.docx,.doc"
                      onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
                      className="hidden"
                      required
                    />
                    {selectedFile ? (
                      <div className="flex items-center justify-center gap-3">
                        <svg className="w-8 h-8 text-[var(--accent-primary)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                          <polyline points="14 2 14 8 20 8"/>
                          <line x1="16" y1="13" x2="8" y2="13"/>
                          <line x1="16" y1="17" x2="8" y2="17"/>
                        </svg>
                        <div className="text-left">
                          <p className="text-sm font-medium text-[var(--text-primary)]">{selectedFile.name}</p>
                          <p className="text-xs text-[var(--text-muted)]">
                            {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                          </p>
                        </div>
                      </div>
                    ) : (
                      <>
                        <svg className="w-10 h-10 text-[var(--text-muted)] mx-auto mb-3" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                          <polyline points="17 8 12 3 7 8"/>
                          <line x1="12" y1="3" x2="12" y2="15"/>
                        </svg>
                        <p className="text-sm text-[var(--text-secondary)]">
                          クリックしてファイルを選択
                        </p>
                        <p className="text-xs text-[var(--text-muted)] mt-1">
                          PDF / Word形式
                        </p>
                      </>
                    )}
                  </div>
                </div>
                <div className="flex justify-end gap-3 pt-4">
                  <button
                    type="button"
                    onClick={() => {
                      setIsAddingCandidate(false)
                      setSelectedFile(null)
                    }}
                    className="btn-secondary"
                    disabled={isUploading}
                  >
                    キャンセル
                  </button>
                  <button
                    type="submit"
                    className="btn-primary inline-flex items-center gap-2"
                    disabled={isUploading || !selectedFile}
                  >
                    {isUploading ? (
                      <>
                        <div className="w-4 h-4 rounded-full border-2 border-white/30 border-t-white animate-spin" />
                        アップロード中...
                      </>
                    ) : (
                      '追加する'
                    )}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}

        {/* Candidates Table */}
        {candidates?.length === 0 ? (
          <div className="card p-12 text-center">
            <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-[var(--accent-primary)]/20 to-[var(--accent-tertiary)]/20 flex items-center justify-center mx-auto mb-6">
              <svg className="w-10 h-10 text-[var(--accent-primary)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                <circle cx="9" cy="7" r="4"/>
                <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-[var(--text-primary)] mb-2">応募者がいません</h3>
            <p className="text-[var(--text-muted)] mb-6">
              応募書類をアップロードして選考を開始しましょう。
            </p>
            <button
              onClick={() => setIsAddingCandidate(true)}
              className="btn-primary inline-flex items-center gap-2"
            >
              <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M16 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                <circle cx="8.5" cy="7" r="4"/>
                <line x1="20" y1="8" x2="20" y2="14"/>
                <line x1="23" y1="11" x2="17" y2="11"/>
              </svg>
              応募者追加
            </button>
          </div>
        ) : (
          <div className="card overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-[var(--border-subtle)]">
                    <th className="px-6 py-4 text-left text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider">
                      ランク
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider">
                      応募者
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider">
                      ステータス
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider">
                      強み
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider">
                      懸念
                    </th>
                    <th className="px-6 py-4 text-left text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider">
                      判定
                    </th>
                    <th className="px-6 py-4"></th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-[var(--border-subtle)]">
                  {candidates?.map((candidate, index) => (
                    <tr
                      key={candidate.candidate_id}
                      className="table-row group"
                    >
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center gap-3">
                          <span className={`
                            w-8 h-8 rounded-lg flex items-center justify-center text-sm font-bold
                            ${index === 0 ? 'bg-amber-500/20 text-amber-400' : ''}
                            ${index === 1 ? 'bg-slate-400/20 text-slate-300' : ''}
                            ${index === 2 ? 'bg-orange-500/20 text-orange-400' : ''}
                            ${index > 2 ? 'bg-[var(--bg-tertiary)] text-[var(--text-muted)]' : ''}
                          `}>
                            {index + 1}
                          </span>
                          <ScoreCircle score={candidate.total_fit_0_100} />
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <Link
                          href={`/candidates/${candidate.candidate_id}`}
                          className="font-medium text-[var(--text-primary)] hover:text-[var(--accent-primary)] transition-colors"
                        >
                          {candidate.display_name || `応募者 ${candidate.candidate_id.slice(0, 8)}`}
                        </Link>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <StatusBadge status={candidate.status} />
                      </td>
                      <td className="px-6 py-4">
                        <ul className="space-y-1">
                          {candidate.strengths_top3.slice(0, 2).map((s, i) => (
                            <li key={i} className="flex items-center gap-1.5 text-sm text-emerald-400">
                              <svg className="w-3.5 h-3.5 flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                                <polyline points="20 6 9 17 4 12" />
                              </svg>
                              <span className="truncate max-w-[180px]">{s}</span>
                            </li>
                          ))}
                        </ul>
                      </td>
                      <td className="px-6 py-4">
                        <ul className="space-y-1">
                          {candidate.concerns_top3.slice(0, 2).map((c, i) => (
                            <li key={i} className="flex items-center gap-1.5 text-sm text-red-400">
                              <svg className="w-3.5 h-3.5 flex-shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                                <circle cx="12" cy="12" r="10" />
                                <line x1="12" y1="8" x2="12" y2="12" />
                                <line x1="12" y1="16" x2="12.01" y2="16" />
                              </svg>
                              <span className="truncate max-w-[180px]">{c}</span>
                            </li>
                          ))}
                        </ul>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <DecisionBadge decision={candidate.decided_state} />
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <Link
                          href={`/candidates/${candidate.candidate_id}`}
                          className="w-9 h-9 rounded-lg flex items-center justify-center bg-[var(--bg-tertiary)] group-hover:bg-[var(--accent-primary)] text-[var(--text-muted)] group-hover:text-white transition-all"
                        >
                          <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <polyline points="9 18 15 12 9 6" />
                          </svg>
                        </Link>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
