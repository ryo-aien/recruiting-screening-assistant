'use client'

import { useState } from 'react'

type Section = 'about' | 'dashboard' | 'jobs' | 'candidates' | 'score-config'

export default function HelpPage() {
  const [activeSection, setActiveSection] = useState<Section>('about')

  const sections = [
    { id: 'about' as Section, name: 'このシステムについて' },
    { id: 'dashboard' as Section, name: 'ダッシュボード' },
    { id: 'jobs' as Section, name: '求人管理' },
    { id: 'candidates' as Section, name: '応募者詳細' },
    { id: 'score-config' as Section, name: 'スコア設定' },
  ]

  return (
    <div className="space-y-8">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-[var(--text-primary)] mb-2">ヘルプ</h1>
        <p className="text-[var(--text-secondary)]">
          システムの使い方をご案内します
        </p>
      </div>

      <div className="flex gap-8">
        {/* Sidebar Navigation */}
        <div className="w-56 flex-shrink-0">
          <nav className="space-y-1 sticky top-8">
            {sections.map((section) => (
              <button
                key={section.id}
                onClick={() => setActiveSection(section.id)}
                className={`
                  w-full text-left px-4 py-2.5 rounded-xl text-sm font-medium transition-all
                  ${activeSection === section.id
                    ? 'bg-[var(--accent-primary)]/10 text-[var(--accent-primary)] border border-[var(--accent-primary)]/20'
                    : 'text-[var(--text-secondary)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-tertiary)]'
                  }
                `}
              >
                {section.name}
              </button>
            ))}
          </nav>
        </div>

        {/* Content */}
        <div className="flex-1 card p-8">
          {activeSection === 'about' && <AboutSection />}
          {activeSection === 'dashboard' && <DashboardSection />}
          {activeSection === 'jobs' && <JobsSection />}
          {activeSection === 'candidates' && <CandidatesSection />}
          {activeSection === 'score-config' && <ScoreConfigSection />}
        </div>
      </div>
    </div>
  )
}

function AboutSection() {
  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold text-[var(--text-primary)]">このシステムについて</h2>

      <div className="space-y-4 text-[var(--text-secondary)]">
        <p>
          <strong className="text-[var(--text-primary)]">Talent Insight</strong> は、採用書類選考を支援するAIシステムです。
        </p>

        <div className="bg-[var(--bg-tertiary)] rounded-xl p-4">
          <h3 className="font-semibold text-[var(--text-primary)] mb-2">できること</h3>
          <ul className="space-y-2 text-sm">
            <li className="flex items-start gap-2">
              <span className="text-[var(--accent-primary)] mt-0.5">●</span>
              履歴書・職務経歴書を自動で読み取り、情報を抽出
            </li>
            <li className="flex items-start gap-2">
              <span className="text-[var(--accent-primary)] mt-0.5">●</span>
              求人要件との適合度を0〜100点でスコア化
            </li>
            <li className="flex items-start gap-2">
              <span className="text-[var(--accent-primary)] mt-0.5">●</span>
              強み・懸念点・不明点を自動で抽出
            </li>
            <li className="flex items-start gap-2">
              <span className="text-[var(--accent-primary)] mt-0.5">●</span>
              応募者を適合度順にランキング表示
            </li>
          </ul>
        </div>

        <div className="bg-[var(--bg-tertiary)] rounded-xl p-4">
          <h3 className="font-semibold text-[var(--text-primary)] mb-2">AIの役割について</h3>
          <ul className="space-y-2 text-sm">
            <li className="flex items-start gap-2">
              <span className="text-emerald-400 mt-0.5">✓</span>
              AIは「読む・整理する・優先順位をつける」を担当
            </li>
            <li className="flex items-start gap-2">
              <span className="text-red-400 mt-0.5">✗</span>
              合否の最終判断はAIではなく、必ず人が行います
            </li>
            <li className="flex items-start gap-2">
              <span className="text-red-400 mt-0.5">✗</span>
              年齢・性別・国籍などによる判断は行いません
            </li>
          </ul>
        </div>
      </div>
    </div>
  )
}

function DashboardSection() {
  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold text-[var(--text-primary)]">ダッシュボード</h2>

      <div className="space-y-4 text-[var(--text-secondary)]">
        <p>
          システム全体の状況を一目で把握できる画面です。
        </p>

        <div className="space-y-4">
          <div className="bg-[var(--bg-tertiary)] rounded-xl p-4">
            <h3 className="font-semibold text-[var(--text-primary)] mb-2">統計情報</h3>
            <ul className="space-y-2 text-sm">
              <li><strong>総求人数</strong>：登録されている求人の件数</li>
              <li><strong>総応募者数</strong>：全求人への応募者の合計</li>
              <li><strong>処理待ち</strong>：まだ分析が完了していない応募者数</li>
              <li><strong>今週の応募</strong>：直近7日間の新規応募者数</li>
            </ul>
          </div>

          <div className="bg-[var(--bg-tertiary)] rounded-xl p-4">
            <h3 className="font-semibold text-[var(--text-primary)] mb-2">最近の応募者</h3>
            <p className="text-sm">
              直近で応募があった候補者が表示されます。クリックすると詳細画面に移動します。
            </p>
          </div>

          <div className="bg-[var(--bg-tertiary)] rounded-xl p-4">
            <h3 className="font-semibold text-[var(--text-primary)] mb-2">求人一覧</h3>
            <p className="text-sm">
              登録されている求人と、それぞれの応募者数が表示されます。
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

function JobsSection() {
  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold text-[var(--text-primary)]">求人管理</h2>

      <div className="space-y-4 text-[var(--text-secondary)]">
        <p>
          求人の作成・管理と、各求人への応募者一覧を確認する画面です。
        </p>

        <div className="space-y-4">
          <div className="bg-[var(--bg-tertiary)] rounded-xl p-4">
            <h3 className="font-semibold text-[var(--text-primary)] mb-2">求人の作成</h3>
            <ol className="space-y-2 text-sm list-decimal list-inside">
              <li>「新規求人作成」ボタンをクリック</li>
              <li>求人タイトルを入力</li>
              <li>求人内容（職務内容、必須要件、歓迎要件など）を入力</li>
              <li>「作成する」をクリック</li>
            </ol>
          </div>

          <div className="bg-[var(--bg-tertiary)] rounded-xl p-4">
            <h3 className="font-semibold text-[var(--text-primary)] mb-2">求人のステータス</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-[var(--accent-primary)]/10 text-[var(--accent-primary)] text-xs font-medium">
                  <span className="w-1.5 h-1.5 rounded-full bg-[var(--accent-primary)]" />
                  募集中
                </span>
                ：応募を受け付けている状態
              </li>
              <li>
                <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full bg-gray-500/10 text-gray-400 text-xs font-medium">
                  <span className="w-1.5 h-1.5 rounded-full bg-gray-400" />
                  締切
                </span>
                ：応募を締め切った状態（新規応募不可）
              </li>
            </ul>
            <p className="text-sm mt-2">
              右端の「︙」メニューからステータスを切り替えられます。
            </p>
          </div>

          <div className="bg-[var(--bg-tertiary)] rounded-xl p-4">
            <h3 className="font-semibold text-[var(--text-primary)] mb-2">応募者の追加</h3>
            <ol className="space-y-2 text-sm list-decimal list-inside">
              <li>求人をクリックして詳細画面を開く</li>
              <li>「応募者追加」ボタンをクリック</li>
              <li>氏名（任意）を入力</li>
              <li>履歴書・職務経歴書をアップロード（PDF/Word）</li>
              <li>「追加する」をクリック</li>
            </ol>
            <p className="text-sm mt-2">
              アップロード後、AIが自動で書類を分析します。
            </p>
          </div>

          <div className="bg-[var(--bg-tertiary)] rounded-xl p-4">
            <h3 className="font-semibold text-[var(--text-primary)] mb-2">応募者一覧の見方</h3>
            <ul className="space-y-2 text-sm">
              <li><strong>ランク</strong>：適合度順の順位</li>
              <li><strong>スコア</strong>：0〜100点の適合度（円グラフで表示）</li>
              <li><strong>ステータス</strong>：処理状況（NEW→処理中→完了）</li>
              <li><strong>強み</strong>：AIが抽出した強みTOP2</li>
              <li><strong>懸念</strong>：AIが抽出した懸念点TOP2</li>
              <li><strong>判定</strong>：採用担当者の判定結果</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

function CandidatesSection() {
  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold text-[var(--text-primary)]">応募者詳細</h2>

      <div className="space-y-4 text-[var(--text-secondary)]">
        <p>
          応募者の詳細情報と、AIによる分析結果を確認する画面です。
        </p>

        <div className="space-y-4">
          <div className="bg-[var(--bg-tertiary)] rounded-xl p-4">
            <h3 className="font-semibold text-[var(--text-primary)] mb-2">スコアの内訳</h3>
            <ul className="space-y-2 text-sm">
              <li><strong>必須要件（Must）</strong>：求人の必須条件をどれだけ満たしているか</li>
              <li><strong>歓迎要件（Nice）</strong>：歓迎条件との適合度</li>
              <li><strong>経験年数（Year）</strong>：求められる経験年数を満たしているか</li>
              <li><strong>役割（Role）</strong>：期待される役割との適合度</li>
            </ul>
          </div>

          <div className="bg-[var(--bg-tertiary)] rounded-xl p-4">
            <h3 className="font-semibold text-[var(--text-primary)] mb-2">AIによる分析</h3>
            <ul className="space-y-2 text-sm">
              <li><strong>サマリー</strong>：候補者の概要（1〜2文）</li>
              <li><strong>強み</strong>：評価できるポイント（最大3つ）</li>
              <li><strong>懸念</strong>：気になるポイント（最大3つ）</li>
              <li><strong>不明点</strong>：書類から読み取れなかった情報</li>
              <li><strong>未達要件</strong>：満たしていない必須要件</li>
            </ul>
          </div>

          <div className="bg-[var(--bg-tertiary)] rounded-xl p-4">
            <h3 className="font-semibold text-[var(--text-primary)] mb-2">判定の登録</h3>
            <p className="text-sm mb-2">
              画面下部から判定を登録できます。
            </p>
            <ul className="space-y-2 text-sm">
              <li>
                <span className="inline-block px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-400 text-xs font-medium">通過</span>
                ：次の選考ステップへ進める
              </li>
              <li>
                <span className="inline-block px-2 py-0.5 rounded bg-amber-500/20 text-amber-400 text-xs font-medium">保留</span>
                ：判断を保留する
              </li>
              <li>
                <span className="inline-block px-2 py-0.5 rounded bg-red-500/20 text-red-400 text-xs font-medium">見送り</span>
                ：今回は見送る
              </li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

function ScoreConfigSection() {
  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold text-[var(--text-primary)]">スコア設定</h2>

      <div className="space-y-4 text-[var(--text-secondary)]">
        <p>
          スコア計算の重み付けを調整する画面です。
        </p>

        <div className="space-y-4">
          <div className="bg-[var(--bg-tertiary)] rounded-xl p-4">
            <h3 className="font-semibold text-[var(--text-primary)] mb-2">重み設定</h3>
            <p className="text-sm mb-2">
              各スコアの重要度を調整できます。合計が100%になるよう設定してください。
            </p>
            <ul className="space-y-2 text-sm">
              <li><strong>必須要件</strong>：必須条件の重要度（初期値: 45%）</li>
              <li><strong>歓迎要件</strong>：歓迎条件の重要度（初期値: 20%）</li>
              <li><strong>経験年数</strong>：経験年数の重要度（初期値: 20%）</li>
              <li><strong>役割適合</strong>：役割適合の重要度（初期値: 15%）</li>
            </ul>
          </div>

          <div className="bg-[var(--bg-tertiary)] rounded-xl p-4">
            <h3 className="font-semibold text-[var(--text-primary)] mb-2">Mustキャップ</h3>
            <p className="text-sm">
              必須要件を満たしていない応募者のスコアに上限を設けます。
              これにより、必須要件未達の応募者が上位に表示されることを防ぎます。
            </p>
            <p className="text-sm mt-2">
              例：キャップ値20の場合、必須要件を1つでも満たしていない応募者は最大20点までしか得られません。
            </p>
          </div>

          <div className="bg-amber-500/10 border border-amber-500/20 rounded-xl p-4">
            <h3 className="font-semibold text-amber-400 mb-2">注意</h3>
            <p className="text-sm text-amber-200/80">
              設定を変更すると、既存の応募者のスコアには反映されません。
              新しく追加した応募者から新しい設定が適用されます。
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
