'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useSWRFetch } from '@/hooks/useSWRFetch'
import { CandidateDetail, createDecision } from '@/lib/api'
import { StatusBadge } from '@/components/StatusBadge'
import { ScoreBadge } from '@/components/ScoreBadge'
import { DecisionDisplay } from '@/components/DecisionBadge'

export default function CandidateDetailPage({
  params,
}: {
  params: { candidateId: string }
}) {
  const { candidateId } = params
  const {
    data: candidate,
    error,
    mutate,
  } = useSWRFetch<CandidateDetail>(`/candidates/${candidateId}`)

  const [isDeciding, setIsDeciding] = useState(false)
  const [decision, setDecision] = useState<'pass' | 'hold' | 'reject'>('pass')
  const [reason, setReason] = useState('')

  const handleDecision = async (e: React.FormEvent) => {
    e.preventDefault()
    try {
      await createDecision(candidateId, {
        decision,
        reason: reason || undefined,
      })
      setIsDeciding(false)
      setReason('')
      mutate()
    } catch (err) {
      alert(err instanceof Error ? err.message : 'エラーが発生しました')
    }
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

  if (!candidate) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="flex flex-col items-center gap-4">
          <div className="w-12 h-12 rounded-full border-4 border-[var(--accent-primary)]/30 border-t-[var(--accent-primary)] animate-spin" />
          <span className="text-[var(--text-secondary)]">読み込み中...</span>
        </div>
      </div>
    )
  }

  const latestDecision = candidate.decisions[0]

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
        <Link
          href={`/jobs/${candidate.job_id}`}
          className="text-[var(--text-muted)] hover:text-[var(--accent-primary)] transition-colors"
        >
          応募者一覧
        </Link>
        <svg className="w-4 h-4 text-[var(--text-muted)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
          <polyline points="9 18 15 12 9 6" />
        </svg>
        <span className="text-[var(--text-primary)]">
          {candidate.display_name || `応募者 ${candidate.candidate_id.slice(0, 8)}`}
        </span>
      </nav>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Basic Info & Scores */}
        <div className="lg:col-span-1 space-y-6">
          {/* Basic Info */}
          <div className="card p-6">
            <div className="flex items-center gap-4 mb-6">
              <div className="w-16 h-16 rounded-xl bg-gradient-to-br from-[var(--accent-primary)] to-[var(--accent-tertiary)] flex items-center justify-center text-white text-2xl font-bold">
                {(candidate.display_name || 'A')[0].toUpperCase()}
              </div>
              <div>
                <h1 className="text-xl font-bold text-[var(--text-primary)]">
                  {candidate.display_name || `応募者 ${candidate.candidate_id.slice(0, 8)}`}
                </h1>
                <div className="flex items-center gap-2 mt-1">
                  <StatusBadge status={candidate.status} />
                </div>
              </div>
            </div>

            <div className="space-y-3 text-sm">
              <div className="flex items-center justify-between py-2 border-b border-[var(--border-subtle)]">
                <span className="text-[var(--text-muted)]">応募日</span>
                <span className="text-[var(--text-primary)]">
                  {new Date(candidate.submitted_at).toLocaleDateString('ja-JP')}
                </span>
              </div>
            </div>

            {candidate.error_message && (
              <div className="mt-4 p-4 rounded-xl bg-red-500/10 border border-red-500/20">
                <div className="flex items-start gap-3">
                  <svg className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <circle cx="12" cy="12" r="10" />
                    <line x1="12" y1="8" x2="12" y2="12" />
                    <line x1="12" y1="16" x2="12.01" y2="16" />
                  </svg>
                  <p className="text-sm text-red-400">{candidate.error_message}</p>
                </div>
              </div>
            )}
          </div>

          {/* Score Summary */}
          {candidate.score && (
            <div className="card p-6">
              <h2 className="text-lg font-semibold text-[var(--text-primary)] mb-6">適合スコア</h2>
              <div className="flex justify-center mb-6">
                <ScoreBadge score={candidate.score.total_fit_0_100} size="lg" />
              </div>
              <div className="space-y-4">
                <ScoreBar label="必須要件" score={candidate.score.must_score} />
                <ScoreBar label="歓迎要件" score={candidate.score.nice_score} />
                <ScoreBar label="経験年数" score={candidate.score.year_score} />
                <ScoreBar label="役割適合" score={candidate.score.role_score} />
              </div>
              {candidate.score.must_gaps.length > 0 && (
                <div className="mt-6 p-4 rounded-xl bg-red-500/10 border border-red-500/20">
                  <h4 className="text-sm font-medium text-red-400 mb-2 flex items-center gap-2">
                    <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <circle cx="12" cy="12" r="10" />
                      <line x1="15" y1="9" x2="9" y2="15" />
                      <line x1="9" y1="9" x2="15" y2="15" />
                    </svg>
                    未達Must要件 ({candidate.score.must_gaps.length})
                  </h4>
                  <ul className="text-sm text-red-300 space-y-1">
                    {candidate.score.must_gaps.map((gap, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <span className="text-red-500 mt-1">•</span>
                        {gap}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* Decision */}
          <div className="card p-6">
            <h2 className="text-lg font-semibold text-[var(--text-primary)] mb-4">意思決定</h2>

            <DecisionDisplay decision={latestDecision?.decision || null} />

            {latestDecision && latestDecision.reason && (
              <div className="mt-4 p-3 rounded-lg bg-[var(--bg-tertiary)]">
                <p className="text-sm text-[var(--text-secondary)]">{latestDecision.reason}</p>
                <p className="text-xs text-[var(--text-muted)] mt-2">
                  {new Date(latestDecision.decided_at).toLocaleString('ja-JP')}
                </p>
              </div>
            )}

            <button
              onClick={() => setIsDeciding(true)}
              className="btn-primary w-full mt-4 flex items-center justify-center gap-2"
            >
              <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
              </svg>
              判定を登録
            </button>
          </div>
        </div>

        {/* Right Column - Explanation & Details */}
        <div className="lg:col-span-2 space-y-6">
          {/* Explanation */}
          {candidate.explanation && (
            <div className="card p-6">
              <h2 className="text-lg font-semibold text-[var(--text-primary)] mb-4 flex items-center gap-2">
                <svg className="w-5 h-5 text-[var(--accent-primary)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="10"/>
                  <line x1="12" y1="16" x2="12" y2="12"/>
                  <line x1="12" y1="8" x2="12.01" y2="8"/>
                </svg>
                AI分析サマリー
              </h2>
              {candidate.explanation.summary && (
                <p className="text-[var(--text-secondary)] mb-6 p-4 rounded-xl bg-[var(--bg-tertiary)]">
                  {candidate.explanation.summary}
                </p>
              )}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="p-4 rounded-xl bg-emerald-500/10 border border-emerald-500/20">
                  <h3 className="text-sm font-semibold text-emerald-400 mb-3 flex items-center gap-2">
                    <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                      <polyline points="20 6 9 17 4 12" />
                    </svg>
                    強み
                  </h3>
                  <ul className="text-sm text-emerald-300 space-y-2">
                    {candidate.explanation.strengths.map((s, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <span className="text-emerald-500 mt-1">+</span>
                        <span>{s}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                <div className="p-4 rounded-xl bg-red-500/10 border border-red-500/20">
                  <h3 className="text-sm font-semibold text-red-400 mb-3 flex items-center gap-2">
                    <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                      <circle cx="12" cy="12" r="10" />
                      <line x1="12" y1="8" x2="12" y2="12" />
                      <line x1="12" y1="16" x2="12.01" y2="16" />
                    </svg>
                    懸念
                  </h3>
                  <ul className="text-sm text-red-300 space-y-2">
                    {candidate.explanation.concerns.map((c, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <span className="text-red-500 mt-1">-</span>
                        <span>{c}</span>
                      </li>
                    ))}
                  </ul>
                </div>
                <div className="p-4 rounded-xl bg-amber-500/10 border border-amber-500/20">
                  <h3 className="text-sm font-semibold text-amber-400 mb-3 flex items-center gap-2">
                    <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                      <circle cx="12" cy="12" r="10" />
                      <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" />
                      <line x1="12" y1="17" x2="12.01" y2="17" />
                    </svg>
                    未確認
                  </h3>
                  <ul className="text-sm text-amber-300 space-y-2">
                    {candidate.explanation.unknowns.map((u, i) => (
                      <li key={i} className="flex items-start gap-2">
                        <span className="text-amber-500 mt-1">?</span>
                        <span>{u}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}

          {/* Extraction Details */}
          {candidate.extraction && (
            <>
              <div className="card p-6">
                <h2 className="text-lg font-semibold text-[var(--text-primary)] mb-6 flex items-center gap-2">
                  <svg className="w-5 h-5 text-[var(--accent-primary)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                    <circle cx="12" cy="7" r="4"/>
                  </svg>
                  候補者プロファイル
                </h2>
                <div className="space-y-6">
                  {candidate.extraction.candidate_profile && (
                    <>
                      <div>
                        <h3 className="text-sm font-medium text-[var(--text-muted)] mb-3">スキル</h3>
                        <div className="flex flex-wrap gap-2">
                          {(candidate.extraction.candidate_profile as any).skills?.map(
                            (skill: string, i: number) => (
                              <span
                                key={i}
                                className="px-3 py-1.5 bg-[var(--accent-primary)]/10 text-[var(--accent-primary)] text-sm rounded-lg border border-[var(--accent-primary)]/20"
                              >
                                {skill}
                              </span>
                            )
                          )}
                        </div>
                      </div>
                      <div>
                        <h3 className="text-sm font-medium text-[var(--text-muted)] mb-3">役割</h3>
                        <div className="flex flex-wrap gap-2">
                          {(candidate.extraction.candidate_profile as any).roles?.map(
                            (role: string, i: number) => (
                              <span
                                key={i}
                                className="px-3 py-1.5 bg-[var(--accent-tertiary)]/10 text-[var(--accent-tertiary)] text-sm rounded-lg border border-[var(--accent-tertiary)]/20"
                              >
                                {role}
                              </span>
                            )
                          )}
                        </div>
                      </div>
                      <div>
                        <h3 className="text-sm font-medium text-[var(--text-muted)] mb-3">
                          経験年数
                        </h3>
                        <div className="grid grid-cols-2 sm:grid-cols-3 gap-3">
                          {Object.entries(
                            (candidate.extraction.candidate_profile as any)
                              .experience_years || {}
                          ).map(([skill, years]) => (
                            <div
                              key={skill}
                              className="p-3 rounded-lg bg-[var(--bg-tertiary)] border border-[var(--border-subtle)]"
                            >
                              <div className="text-xs text-[var(--text-muted)]">{skill}</div>
                              <div className="text-lg font-semibold text-[var(--text-primary)]">
                                {years ?? '不明'}
                                <span className="text-sm font-normal text-[var(--text-muted)] ml-1">年</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                      <div>
                        <h3 className="text-sm font-medium text-[var(--text-muted)] mb-3">
                          ハイライト
                        </h3>
                        <ul className="space-y-2">
                          {(candidate.extraction.candidate_profile as any).highlights?.map(
                            (h: string, i: number) => (
                              <li
                                key={i}
                                className="flex items-start gap-3 p-3 rounded-lg bg-[var(--bg-tertiary)] text-sm text-[var(--text-secondary)]"
                              >
                                <span className="w-6 h-6 rounded-full bg-[var(--accent-primary)]/20 text-[var(--accent-primary)] flex items-center justify-center flex-shrink-0 text-xs font-medium">
                                  {i + 1}
                                </span>
                                {h}
                              </li>
                            )
                          )}
                        </ul>
                      </div>
                    </>
                  )}
                </div>
              </div>

              {/* Evidence */}
              {candidate.extraction.evidence && (
                <div className="card p-6">
                  <h2 className="text-lg font-semibold text-[var(--text-primary)] mb-4 flex items-center gap-2">
                    <svg className="w-5 h-5 text-[var(--accent-primary)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                      <polyline points="14 2 14 8 20 8"/>
                      <line x1="16" y1="13" x2="8" y2="13"/>
                      <line x1="16" y1="17" x2="8" y2="17"/>
                    </svg>
                    根拠（引用）
                  </h2>
                  <div className="space-y-3">
                    {Object.entries((candidate.extraction.evidence as any).candidate || {}).map(
                      ([key, value]) => (
                        <div key={key} className="p-4 rounded-xl bg-[var(--bg-tertiary)] border border-[var(--border-subtle)]">
                          <span className="text-xs font-medium text-[var(--accent-primary)] uppercase tracking-wider">{key}</span>
                          <p className="text-sm text-[var(--text-secondary)] mt-2 italic">
                            &ldquo;{value as string}&rdquo;
                          </p>
                        </div>
                      )
                    )}
                  </div>
                </div>
              )}
            </>
          )}

          {/* Documents */}
          {candidate.documents.length > 0 && (
            <div className="card p-6">
              <h2 className="text-lg font-semibold text-[var(--text-primary)] mb-4 flex items-center gap-2">
                <svg className="w-5 h-5 text-[var(--accent-primary)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/>
                  <polyline points="13 2 13 9 20 9"/>
                </svg>
                書類
              </h2>
              <ul className="space-y-3">
                {candidate.documents.map((doc) => (
                  <li
                    key={doc.document_id}
                    className="flex items-center justify-between p-4 rounded-xl bg-[var(--bg-tertiary)] border border-[var(--border-subtle)] hover:border-[var(--accent-primary)]/30 transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-lg bg-[var(--accent-primary)]/10 flex items-center justify-center text-[var(--accent-primary)]">
                        <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                          <polyline points="14 2 14 8 20 8"/>
                        </svg>
                      </div>
                      <div>
                        <span className="text-sm font-medium text-[var(--text-primary)]">
                          {doc.original_filename}
                        </span>
                        <div className="flex items-center gap-2 mt-0.5">
                          <span className="px-2 py-0.5 text-xs rounded-full bg-[var(--bg-elevated)] text-[var(--text-muted)]">
                            {doc.type}
                          </span>
                        </div>
                      </div>
                    </div>
                    <span className="text-xs text-[var(--text-muted)]">
                      {new Date(doc.created_at).toLocaleString('ja-JP')}
                    </span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>

      {/* Decision Modal */}
      {isDeciding && (
        <div className="fixed inset-0 modal-overlay flex items-center justify-center z-50 animate-fadeIn">
          <div
            className="absolute inset-0"
            onClick={() => setIsDeciding(false)}
          />
          <div className="card p-8 w-full max-w-md mx-4 relative animate-scaleIn">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-bold text-[var(--text-primary)]">判定を登録</h2>
              <button
                onClick={() => setIsDeciding(false)}
                className="w-8 h-8 rounded-lg flex items-center justify-center hover:bg-[var(--bg-tertiary)] transition-colors"
              >
                <svg className="w-5 h-5 text-[var(--text-muted)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="18" y1="6" x2="6" y2="18" />
                  <line x1="6" y1="6" x2="18" y2="18" />
                </svg>
              </button>
            </div>
            <form onSubmit={handleDecision} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-[var(--text-secondary)] mb-3">
                  判定
                </label>
                <div className="grid grid-cols-3 gap-3">
                  <button
                    type="button"
                    onClick={() => setDecision('pass')}
                    className={`
                      p-4 rounded-xl border-2 text-center transition-all
                      ${decision === 'pass'
                        ? 'border-emerald-500 bg-emerald-500/10 text-emerald-400'
                        : 'border-[var(--border-default)] hover:border-emerald-500/50 text-[var(--text-muted)]'
                      }
                    `}
                  >
                    <svg className="w-6 h-6 mx-auto mb-2" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                      <polyline points="20 6 9 17 4 12" />
                    </svg>
                    <span className="text-sm font-medium">通過</span>
                  </button>
                  <button
                    type="button"
                    onClick={() => setDecision('hold')}
                    className={`
                      p-4 rounded-xl border-2 text-center transition-all
                      ${decision === 'hold'
                        ? 'border-amber-500 bg-amber-500/10 text-amber-400'
                        : 'border-[var(--border-default)] hover:border-amber-500/50 text-[var(--text-muted)]'
                      }
                    `}
                  >
                    <svg className="w-6 h-6 mx-auto mb-2" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                      <circle cx="12" cy="12" r="10" />
                      <line x1="8" y1="12" x2="16" y2="12" />
                    </svg>
                    <span className="text-sm font-medium">保留</span>
                  </button>
                  <button
                    type="button"
                    onClick={() => setDecision('reject')}
                    className={`
                      p-4 rounded-xl border-2 text-center transition-all
                      ${decision === 'reject'
                        ? 'border-red-500 bg-red-500/10 text-red-400'
                        : 'border-[var(--border-default)] hover:border-red-500/50 text-[var(--text-muted)]'
                      }
                    `}
                  >
                    <svg className="w-6 h-6 mx-auto mb-2" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                      <line x1="18" y1="6" x2="6" y2="18" />
                      <line x1="6" y1="6" x2="18" y2="18" />
                    </svg>
                    <span className="text-sm font-medium">見送り</span>
                  </button>
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-[var(--text-secondary)] mb-2">
                  理由（任意）
                </label>
                <textarea
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                  className="input h-24 resize-none"
                  placeholder="判定の理由を記入..."
                />
              </div>
              <div className="flex justify-end gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setIsDeciding(false)}
                  className="btn-secondary"
                >
                  キャンセル
                </button>
                <button type="submit" className="btn-primary">
                  登録する
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  )
}

function ScoreBar({ label, score }: { label: string; score: number }) {
  const percentage = Math.round(score * 100)

  const getColor = (pct: number) => {
    if (pct >= 70) return 'from-emerald-500 to-teal-400'
    if (pct >= 40) return 'from-amber-500 to-yellow-400'
    return 'from-red-500 to-orange-400'
  }

  return (
    <div>
      <div className="flex justify-between text-sm mb-2">
        <span className="text-[var(--text-muted)]">{label}</span>
        <span className="font-semibold text-[var(--text-primary)]">{percentage}%</span>
      </div>
      <div className="progress-bar">
        <div
          className={`progress-bar-fill bg-gradient-to-r ${getColor(percentage)}`}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  )
}
