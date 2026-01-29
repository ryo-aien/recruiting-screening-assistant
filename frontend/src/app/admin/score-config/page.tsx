'use client'

import { useState, useEffect } from 'react'
import { useSWRFetch } from '@/hooks/useSWRFetch'
import { ScoreConfig, updateScoreConfig } from '@/lib/api'

export default function ScoreConfigPage() {
  const { data: config, error, mutate } = useSWRFetch<ScoreConfig>('/admin/score-config')

  const [weights, setWeights] = useState({
    must: 0.45,
    nice: 0.20,
    year: 0.20,
    role: 0.15,
  })
  const [mustCapEnabled, setMustCapEnabled] = useState(true)
  const [mustCapValue, setMustCapValue] = useState(20)
  const [niceTopN, setNiceTopN] = useState(3)
  const [isSaving, setIsSaving] = useState(false)
  const [saveSuccess, setSaveSuccess] = useState(false)

  useEffect(() => {
    if (config) {
      setWeights(config.weights_json as any)
      setMustCapEnabled(config.must_cap_enabled)
      setMustCapValue(config.must_cap_value)
      setNiceTopN(config.nice_top_n)
    }
  }, [config])

  const totalWeight = Object.values(weights).reduce((a, b) => a + b, 0)
  const isValidTotal = Math.abs(totalWeight - 1.0) < 0.01

  const handleSave = async () => {
    if (!isValidTotal) {
      alert('重みの合計が1.0になるように調整してください')
      return
    }

    setIsSaving(true)
    setSaveSuccess(false)
    try {
      await updateScoreConfig({
        weights,
        must_cap_enabled: mustCapEnabled,
        must_cap_value: mustCapValue,
        nice_top_n: niceTopN,
      })
      mutate()
      setSaveSuccess(true)
      setTimeout(() => setSaveSuccess(false), 3000)
    } catch (err) {
      alert(err instanceof Error ? err.message : 'エラーが発生しました')
    } finally {
      setIsSaving(false)
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

  if (!config) {
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
    <div className="max-w-3xl mx-auto space-y-8">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-[var(--text-primary)] mb-2">スコア設定</h1>
          <p className="text-[var(--text-secondary)]">
            スコアリングアルゴリズムのパラメータを調整します
          </p>
        </div>
        <div className="flex items-center gap-2 px-4 py-2 rounded-xl bg-[var(--accent-primary)]/10 border border-[var(--accent-primary)]/20">
          <svg className="w-4 h-4 text-[var(--accent-primary)]" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 20v-6M6 20V10M18 20V4"/>
          </svg>
          <span className="text-sm font-medium text-[var(--accent-primary)]">v{config.version}</span>
        </div>
      </div>

      {/* Save Success Toast */}
      {saveSuccess && (
        <div className="fixed top-4 right-4 z-50 animate-fadeIn">
          <div className="flex items-center gap-3 px-4 py-3 rounded-xl bg-emerald-500/20 border border-emerald-500/30 text-emerald-400">
            <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <polyline points="20 6 9 17 4 12" />
            </svg>
            <span className="font-medium">設定を保存しました</span>
          </div>
        </div>
      )}

      {/* Weight Settings */}
      <div className="card p-6">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-[var(--accent-primary)]/20 to-[var(--accent-tertiary)]/20 flex items-center justify-center text-[var(--accent-primary)]">
            <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 20v-6M6 20V10M18 20V4"/>
            </svg>
          </div>
          <div>
            <h2 className="text-lg font-semibold text-[var(--text-primary)]">スコア重み</h2>
            <p className="text-sm text-[var(--text-muted)]">
              各スコアの重みを設定します。合計が1.0になる必要があります。
            </p>
          </div>
        </div>

        <div className="space-y-5">
          <WeightSlider
            label="必須要件 (Must)"
            description="Must要件の充足度"
            value={weights.must}
            onChange={(v) => setWeights({ ...weights, must: v })}
            color="emerald"
          />
          <WeightSlider
            label="歓迎要件 (Nice)"
            description="Nice要件との類似度"
            value={weights.nice}
            onChange={(v) => setWeights({ ...weights, nice: v })}
            color="amber"
          />
          <WeightSlider
            label="経験年数 (Year)"
            description="求める経験年数との適合"
            value={weights.year}
            onChange={(v) => setWeights({ ...weights, year: v })}
            color="violet"
          />
          <WeightSlider
            label="役割適合 (Role)"
            description="期待役割との適合度"
            value={weights.role}
            onChange={(v) => setWeights({ ...weights, role: v })}
            color="blue"
          />
        </div>

        <div className={`
          mt-6 p-4 rounded-xl border
          ${isValidTotal
            ? 'bg-emerald-500/10 border-emerald-500/20'
            : 'bg-red-500/10 border-red-500/20'
          }
        `}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              {isValidTotal ? (
                <svg className="w-5 h-5 text-emerald-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="20 6 9 17 4 12" />
                </svg>
              ) : (
                <svg className="w-5 h-5 text-red-400" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="10" />
                  <line x1="12" y1="8" x2="12" y2="12" />
                  <line x1="12" y1="16" x2="12.01" y2="16" />
                </svg>
              )}
              <span className={isValidTotal ? 'text-emerald-400' : 'text-red-400'}>
                重みの合計
              </span>
            </div>
            <span className={`text-2xl font-bold ${isValidTotal ? 'text-emerald-400' : 'text-red-400'}`}>
              {totalWeight.toFixed(2)}
            </span>
          </div>
          {!isValidTotal && (
            <p className="text-sm text-red-300 mt-2">
              合計が1.0になるように調整してください
            </p>
          )}
        </div>
      </div>

      {/* Must Cap Settings */}
      <div className="card p-6">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-red-500/20 to-orange-500/20 flex items-center justify-center text-red-400">
            <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            </svg>
          </div>
          <div>
            <h2 className="text-lg font-semibold text-[var(--text-primary)]">Must Cap設定</h2>
            <p className="text-sm text-[var(--text-muted)]">
              必須要件を満たさない候補者のスコアに上限を設定します
            </p>
          </div>
        </div>

        <div className="space-y-5">
          <label className="flex items-center gap-3 p-4 rounded-xl bg-[var(--bg-tertiary)] border border-[var(--border-subtle)] cursor-pointer hover:border-[var(--accent-primary)]/30 transition-colors">
            <input
              type="checkbox"
              checked={mustCapEnabled}
              onChange={(e) => setMustCapEnabled(e.target.checked)}
              className="w-5 h-5"
            />
            <div>
              <span className="font-medium text-[var(--text-primary)]">Must Cap を有効にする</span>
              <p className="text-sm text-[var(--text-muted)]">
                必須要件未達の場合、スコアに上限を適用
              </p>
            </div>
          </label>

          {mustCapEnabled && (
            <div className="p-4 rounded-xl bg-[var(--bg-tertiary)] border border-[var(--border-subtle)]">
              <div className="flex items-center justify-between mb-3">
                <span className="text-sm text-[var(--text-secondary)]">上限値</span>
                <span className="text-2xl font-bold text-[var(--text-primary)]">{mustCapValue}</span>
              </div>
              <input
                type="range"
                min="0"
                max="50"
                value={mustCapValue}
                onChange={(e) => setMustCapValue(Number(e.target.value))}
                className="w-full"
              />
              <p className="text-xs text-[var(--text-muted)] mt-3">
                必須要件未達の候補者のスコアは最大{mustCapValue}点に制限されます
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Nice Score Settings */}
      <div className="card p-6">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-amber-500/20 to-yellow-500/20 flex items-center justify-center text-amber-400">
            <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
            </svg>
          </div>
          <div>
            <h2 className="text-lg font-semibold text-[var(--text-primary)]">Nice Score設定</h2>
            <p className="text-sm text-[var(--text-muted)]">
              歓迎要件のスコア計算に使用する上位N件を設定します
            </p>
          </div>
        </div>

        <div className="p-4 rounded-xl bg-[var(--bg-tertiary)] border border-[var(--border-subtle)]">
          <div className="flex items-center justify-between mb-3">
            <span className="text-sm text-[var(--text-secondary)]">Top N</span>
            <span className="text-2xl font-bold text-[var(--text-primary)]">{niceTopN}</span>
          </div>
          <input
            type="range"
            min="1"
            max="10"
            value={niceTopN}
            onChange={(e) => setNiceTopN(Number(e.target.value))}
            className="w-full"
          />
          <p className="text-xs text-[var(--text-muted)] mt-3">
            類似度の高い上位{niceTopN}件の歓迎要件でスコアを計算します
          </p>
        </div>
      </div>

      {/* Role Distance Matrix */}
      <div className="card p-6">
        <div className="flex items-center gap-3 mb-6">
          <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-500/20 to-cyan-500/20 flex items-center justify-center text-blue-400">
            <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
              <line x1="3" y1="9" x2="21" y2="9"/>
              <line x1="9" y1="21" x2="9" y2="9"/>
            </svg>
          </div>
          <div>
            <h2 className="text-lg font-semibold text-[var(--text-primary)]">役割距離マトリクス</h2>
            <p className="text-sm text-[var(--text-muted)]">
              期待役割と実績役割の距離（類似度）を定義します
            </p>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-[var(--border-subtle)]">
                <th className="px-4 py-3 text-left text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider">
                  期待 / 実績
                </th>
                {['IC', 'Lead', 'Manager'].map((role) => (
                  <th key={role} className="px-4 py-3 text-center text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider">
                    {role}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--border-subtle)]">
              {Object.entries(config.role_distance_json).map(([expected, actual]) => (
                <tr key={expected} className="hover:bg-[var(--bg-elevated)] transition-colors">
                  <td className="px-4 py-3 text-sm font-medium text-[var(--text-primary)]">
                    {expected}
                  </td>
                  {['IC', 'Lead', 'Manager'].map((role) => {
                    const value = (actual as Record<string, number>)[role]
                    const isHighMatch = value >= 0.9
                    const isMedMatch = value >= 0.5 && value < 0.9
                    return (
                      <td key={role} className="px-4 py-3 text-center">
                        <span className={`
                          inline-flex items-center justify-center w-12 h-8 rounded-lg text-sm font-medium
                          ${isHighMatch ? 'bg-emerald-500/20 text-emerald-400' : ''}
                          ${isMedMatch ? 'bg-amber-500/20 text-amber-400' : ''}
                          ${!isHighMatch && !isMedMatch ? 'bg-[var(--bg-tertiary)] text-[var(--text-muted)]' : ''}
                        `}>
                          {value?.toFixed(1) ?? '-'}
                        </span>
                      </td>
                    )
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="text-xs text-[var(--text-muted)] mt-4 flex items-center gap-2">
          <svg className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <circle cx="12" cy="12" r="10"/>
            <line x1="12" y1="16" x2="12" y2="12"/>
            <line x1="12" y1="8" x2="12.01" y2="8"/>
          </svg>
          役割距離マトリクスは現在読み取り専用です
        </p>
      </div>

      {/* Save Button */}
      <div className="flex justify-end pb-8">
        <button
          onClick={handleSave}
          disabled={isSaving || !isValidTotal}
          className="btn-primary inline-flex items-center gap-2 px-8 disabled:opacity-50"
        >
          {isSaving ? (
            <>
              <div className="w-4 h-4 rounded-full border-2 border-white/30 border-t-white animate-spin" />
              保存中...
            </>
          ) : (
            <>
              <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
                <polyline points="17 21 17 13 7 13 7 21"/>
                <polyline points="7 3 7 8 15 8"/>
              </svg>
              設定を保存
            </>
          )}
        </button>
      </div>
    </div>
  )
}

function WeightSlider({
  label,
  description,
  value,
  onChange,
  color,
}: {
  label: string
  description: string
  value: number
  onChange: (value: number) => void
  color: 'emerald' | 'amber' | 'violet' | 'blue'
}) {
  const percentage = (value * 100).toFixed(0)

  const colorClasses = {
    emerald: 'from-emerald-500 to-teal-400',
    amber: 'from-amber-500 to-yellow-400',
    violet: 'from-violet-500 to-purple-400',
    blue: 'from-blue-500 to-cyan-400',
  }

  return (
    <div className="p-4 rounded-xl bg-[var(--bg-tertiary)] border border-[var(--border-subtle)]">
      <div className="flex items-center justify-between mb-3">
        <div>
          <span className="font-medium text-[var(--text-primary)]">{label}</span>
          <p className="text-xs text-[var(--text-muted)]">{description}</p>
        </div>
        <span className="text-2xl font-bold text-[var(--text-primary)]">{percentage}%</span>
      </div>
      <div className="relative">
        <div className="absolute inset-0 h-2 mt-2 rounded-full bg-[var(--bg-elevated)]" />
        <div
          className={`absolute h-2 mt-2 rounded-full bg-gradient-to-r ${colorClasses[color]}`}
          style={{ width: `${percentage}%` }}
        />
        <input
          type="range"
          min="0"
          max="100"
          value={value * 100}
          onChange={(e) => onChange(Number(e.target.value) / 100)}
          className="relative w-full"
        />
      </div>
    </div>
  )
}
