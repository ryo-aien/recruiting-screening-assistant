# 統合仕様書：採用書類選考支援システム（AIスクリーニング＆ランキング）

> **関連ドキュメント：** システム設計の詳細（データモデル、非同期ジョブ、Docker構成等）は `SYSTEM_DESIGN.md` を参照

---

## 1. 概要

### 1.1 目的

採用担当者の意思決定を代替するのではなく、**書類選考における「思考の前処理」**を自動化する。

**実現する価値：**
- 1件あたりのレビュー時間削減
- 書類滞留の削減
- 判断基準の一貫性向上（説明可能な根拠の提示）
- 面談後のミスマッチ低減

### 1.2 非目的（やらないこと）

- AIが合否を自動確定する機能（最終判断は人）
- 法務・規制に抵触する属性推定（性別/年齢/国籍等）やそれに基づく自動判断

### 1.3 想定ユーザー

- 採用担当（リクルーター、HR）
- 現場面接官（書類確認）
- 採用責任者（進捗・品質の監視）

---

## 2. システム設計方針

### 2.1 スコアリング方針

| 役割 | 担当 |
|------|------|
| 構造化（抽出）・説明生成 | LLM |
| 定量スコア算出（0〜100） | アプリ側 |
| ランキング・UI表示 | アプリ側 |

**重要：LLMに0〜100のスコアを直接出させない**

### 2.2 根拠の保持

すべての抽出結果に対して、`evidence`（短い引用、20語以内）をJSONに保持する。

---

## 3. 入出力仕様

### 3.1 入力（アプリ → LLM）

| パラメータ | 説明 |
|-----------|------|
| `job_text` | 求人票の本文（テキスト） |
| `resume_text` | 履歴書＋職務経歴書の抽出テキスト |
| `score_config` | 重み・Must cap・役割距離など（固定JSON） |

### 3.2 出力（LLM → アプリ）

| フィールド | 説明 |
|-----------|------|
| `job_requirements` | Must/Nice/年数/役割期待 |
| `candidate_profile` | スキル、経験年数、役割、要約、懸念、未確認 |
| `evidence` | 各抽出の根拠（短い引用 or 位置情報） |

---

## 4. プロンプト設計

### 4.1 抽出用 System Prompt

```text
You are an information extraction engine for recruitment screening.
Return ONLY valid JSON that conforms to the provided schema.
Do not add any commentary, markdown, or extra keys.

Rules:
- Never infer or guess. If not clearly stated, set value to null and add the item to unknowns.
- Extract evidence: provide a short quote (<= 20 words) from the input text that supports each extracted item.
- Do not use sensitive attributes (age, gender, nationality, race, religion). If present, ignore them.
- Normalize skill names to common industry terms where possible (e.g., "EKS" -> "Kubernetes", "S3" -> "AWS S3").
- Experience years must be numeric if explicitly supported; otherwise null.
```

### 4.2 抽出用 User Prompt

```text
Extract job requirements and candidate profile from the following texts.

[JOB_TEXT]
{{job_text}}

[RESUME_TEXT]
{{resume_text}}

Return JSON matching the schema. Use null when unknown.
```

### 4.3 説明生成用 System Prompt

```text
You are generating an explanation for a recruitment screening score.
Use only the provided inputs and evidence. Do not invent facts.
Keep it concise and actionable for a recruiter.

Output format must be JSON with keys:
- summary (string)
- strengths (array of strings, up to 3)
- concerns (array of strings, up to 3)
- unknowns (array of strings, up to 5)
- must_gaps (array of strings)
```

### 4.4 説明生成用 User Prompt

```text
Given:
- job_requirements: {{job_requirements_json}}
- candidate_profile: {{candidate_profile_json}}
- scores: {{scores_json}}
- evidence: {{evidence_json}}

Generate the explanation JSON.
```

---

## 5. JSONスキーマ

```json
{
  "type": "object",
  "required": ["job_requirements", "candidate_profile", "evidence"],
  "properties": {
    "job_requirements": {
      "type": "object",
      "required": ["must", "nice", "role_expectation", "year_requirements"],
      "properties": {
        "must": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["id", "text", "skill_tags"],
            "properties": {
              "id": {"type": "string"},
              "text": {"type": "string"},
              "skill_tags": {"type": "array", "items": {"type": "string"}}
            }
          }
        },
        "nice": {
          "type": "array",
          "items": {
            "type": "object",
            "required": ["id", "text", "skill_tags"],
            "properties": {
              "id": {"type": "string"},
              "text": {"type": "string"},
              "skill_tags": {"type": "array", "items": {"type": "string"}}
            }
          }
        },
        "role_expectation": {"type": ["string", "null"]},
        "year_requirements": {
          "type": "object",
          "additionalProperties": {"type": ["number", "null"]}
        }
      }
    },
    "candidate_profile": {
      "type": "object",
      "required": ["skills", "roles", "experience_years", "highlights", "concerns", "unknowns"],
      "properties": {
        "skills": {"type": "array", "items": {"type": "string"}},
        "roles": {"type": "array", "items": {"type": "string"}},
        "experience_years": {
          "type": "object",
          "additionalProperties": {"type": ["number", "null"]}
        },
        "highlights": {"type": "array", "items": {"type": "string"}},
        "concerns": {"type": "array", "items": {"type": "string"}},
        "unknowns": {"type": "array", "items": {"type": "string"}}
      }
    },
    "evidence": {
      "type": "object",
      "required": ["job", "candidate"],
      "properties": {
        "job": {
          "type": "object",
          "additionalProperties": {"type": "string"}
        },
        "candidate": {
          "type": "object",
          "additionalProperties": {"type": "string"}
        }
      }
    }
  }
}
```

### 5.1 evidence キーの命名規則

| 対象 | キー形式 | 例 |
|------|---------|-----|
| Must要件 | `must:<id>` | `must:m1` |
| Nice要件 | `nice:<id>` | `nice:n1` |
| 役割期待 | `role_expectation` | - |
| 年数要件 | `year:<skill>` | `year:Python` |
| 候補者スキル | `skill:<name>` | `skill:Python` |
| 候補者年数 | `years:<skill>` | `years:Python` |
| 候補者役割 | `role:<name>` | `role:Lead` |
| ハイライト | `highlight:<n>` | `highlight:1` |

---

## 6. スコア算出ロジック（アプリ側）

### 6.1 MustScore（必須要件適合）

**判定：** 各Must要件を `satisfied / not_satisfied / unknown` で判定

**判定基準：**
- `skill_tags` のいずれかが `candidate.skills` に含まれる
- `year_requirements` がある場合は年数条件も確認
- 年数が不明なら `unknown`

**計算式：**
```
MustScore = satisfied_count / must_total
```
※ `unknown` は 0 とみなす（保守的）

### 6.2 YearScore（経験年数）

**計算式（線形クリップ）：**
```
YearScore_skill = clip(x / req, 0, 1)  // req > 0
YearScore = average(YearScore_skill for required skills)
```
※ 取得できない場合は 0

### 6.3 RoleScore（役割期待）

**距離表による算出：**

| 期待 / 実績 | IC | Lead | Manager |
|------------|-----|------|---------|
| IC | 1.0 | 0.7 | 0.3 |
| Lead | 0.7 | 1.0 | 0.7 |
| Manager | 0.3 | 0.7 | 1.0 |

※ 不明の場合は 0.5（または0）

### 6.4 NiceScore（歓迎要件適合）

**手順：**
1. 各 `nice[i].text` を embedding
2. 候補者の `skills` + `highlights` を連結してembedding
3. コサイン類似度 `sim_i` を計算
4. `NiceScore = average(topN(sim_i))`（N=3）

### 6.5 TotalFit（総合適合度）

**計算式：**
```
TotalFit01 = w_must×MustScore + w_nice×NiceScore + w_year×YearScore + w_role×RoleScore
TotalFit = round(TotalFit01 × 100)
```

**Must cap（推奨）：**
- Must未達が1つでもある場合：`TotalFit = min(TotalFit, must_cap_value)`

---

## 7. 初期設定値

```json
{
  "weights": {
    "must": 0.45,
    "nice": 0.20,
    "year": 0.20,
    "role": 0.15
  },
  "must_cap": {
    "enabled": true,
    "value": 20
  },
  "nice_agg": {
    "top_n": 3
  },
  "role_distance": {
    "IC": {"IC": 1.0, "Lead": 0.7, "Manager": 0.3},
    "Lead": {"IC": 0.7, "Lead": 1.0, "Manager": 0.7},
    "Manager": {"IC": 0.3, "Lead": 0.7, "Manager": 1.0}
  }
}
```

---

## 8. 重み設定（学習なし・手動調整）

### 8.1 設計方針

- **MVPでは機械学習による重み学習は実施しない**
- 重みは `score_config` テーブルで管理し、運用しながら手動調整
- 調整履歴は `score_config.version` で追跡可能

### 8.2 運用最適化の流れ

1. 初期重みで運用開始
2. 人の意思決定（通過/保留/見送り）をログに蓄積
3. 定期的に「上位Kに通過者がどれだけ含まれるか」を確認
4. 乖離が大きければ重みを手動調整し、新バージョンとして保存

### 8.3 将来拡張（参考）

将来的にデータが蓄積された場合、以下の拡張が可能：

| フェーズ | 手法 | 備考 |
|---------|------|------|
| Phase 2 | ロジスティック回帰 | 重みを学習、Must未達はルール優先 |
| Phase 3 | Learning to Rank | LightGBM Ranker、Precision@K最適化 |

※ 現時点では実装しない

---

## 9. API仕様（MVP）

### 9.1 求人管理

| エンドポイント | メソッド | 説明 |
|---------------|---------|------|
| `/jobs` | POST | 求人作成（title, job_text_raw, requirements_json任意） |
| `/jobs` | GET | 求人一覧 |
| `/jobs/{job_id}` | GET | 求人詳細 |

### 9.2 応募者管理

| エンドポイント | メソッド | 説明 |
|---------------|---------|------|
| `/jobs/{job_id}/candidates` | POST | 応募者作成（display_name任意） |
| `/jobs/{job_id}/candidates` | GET | 応募者一覧（total_fit、要点、ステータス） |
| `/candidates/{candidate_id}` | GET | 応募者詳細（抽出JSON、スコア内訳、根拠、説明） |
| `/candidates/{candidate_id}/documents` | POST | 書類アップロード（multipart: file, type） |
| `/candidates/{candidate_id}/decision` | POST | 意思決定登録（decision, reason任意） |

### 9.3 設定管理

| エンドポイント | メソッド | 説明 |
|---------------|---------|------|
| `/admin/score-config` | GET | 現在のスコア設定取得 |
| `/admin/score-config` | POST | スコア設定更新（重み・閾値・cap）|

### 9.4 レスポンス例（応募者一覧）

```json
{
  "candidate_id": "c-001",
  "status": "DONE",
  "total_fit_0_100": 72,
  "must_gaps_count": 1,
  "strengths_top3": ["Python 5年", "チームリード経験", "AWS構築実績"],
  "concerns_top3": ["英語力不明"],
  "decided_state": null
}
```

---

## 10. 画面仕様（MVP）

### 10.1 一覧画面

**表示項目：**
- 氏名（または匿名ID）
- 総合適合度（0〜100）
- 優先度（A/B/C）
- 強みTOP3
- 懸念TOP3
- Must未達数（例：1/8）

**操作：**
- ソート：適合度順 / 応募日時順
- フィルタ：Must未達除外、職種、スキル
- ステータス更新：未確認/レビュー中/通過/保留/見送り

### 10.2 詳細画面

**セクション：**
- サマリー（強み/懸念/未確認）
- 要件適合表（Must/Nice/年数/役割）
- 根拠リンク（抽出元の文章ハイライト）
- 採用担当メモ

---

## 11. 非機能要件

| 項目 | 要件 |
|------|------|
| 性能（バッチ） | 100件を数分以内で処理 |
| 性能（単件） | アップロード後、非同期で順次反映 |
| 可用性 | MVP：単一テナント、将来：マルチテナント |
| セキュリティ | 保存データ暗号化、アクセス制御（チーム単位） |
| 個人情報 | 表示は必要最小限、学習用途は匿名化/マスキング |

---

## 12. バイアス・コンプライアンス

- 直接属性（性別、年齢、国籍等）は特徴量に使用しない
- Proxy項目（学校名、住所等）は初期では表示のみ・学習除外
- 属性ごとの通過率/誤差を監視する監査ログ（MVPから保持）

---

## 13. 品質指標（KPI）

### 13.1 業務KPI

- 1件あたりレビュー時間（平均/中央値）
- 書類滞留日数（応募→初回判定）
- 面接後の「想定乖離」率

### 13.2 モデルKPI

- Precision@K（上位Kに通過者がどれだけ含まれるか）
- 時系列テストでの安定性
- キャリブレーション（確率の整合性）

---

## 14. リリース計画

| Phase | 内容 |
|-------|------|
| Phase 0 | 過去データでオフライン評価 |
| Phase 1（MVP） | ランキング＋強み/懸念/未確認、固定重み、ログ収集優先 |
| Phase 2 | ロジスティック回帰で重み更新、閾値調整 |
| Phase 3 | Learning to Rank、監査ビュー、ATS本格連携 |

---

## 15. リスクと対策

| リスク | 対策 |
|--------|------|
| 過去の選考癖を学習し再生産 | 「読む順番」用途に限定、監査ログ、重みの人手調整を残す |
| 情報リーク（面接後情報混入） | 特徴量生成を応募時点データに限定、パイプライン分離 |
| 説明不能なブラックボックス | サブスコア方式＋根拠ハイライトを必須要件化 |

---

## 16. システム構成（小規模実装）

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Frontend  │────▶│   Backend   │────▶│   Worker    │
│    (Web)    │     │  (FastAPI)  │     │  (Python)   │
└─────────────┘     └──────┬──────┘     └──────┬──────┘
                           │                    │
                    ┌──────▼──────┐      ┌──────▼──────┐
                    │  Database   │      │ OpenAI API  │
                    │   (MySQL)   │      │ (Responses) │
                    └─────────────┘      └─────────────┘
                           │
                    ┌──────▼──────┐
                    │   Storage   │
                    │(Local/MinIO)│
                    └─────────────┘
```

### 16.1 コンポーネント詳細

| コンポーネント | 役割 |
|---------------|------|
| Frontend (Web) | 求人作成、応募者一覧/詳細、意思決定入力 |
| Backend (FastAPI) | 認証、データCRUD、OpenAI API呼び出し（キー秘匿） |
| Worker | テキスト抽出、LLM抽出、Embedding生成、スコア算出 |
| Database (MySQL) | 求人・応募者・抽出結果・スコア・監査ログ |
| Storage | 原本ファイル、抽出テキスト、evidence JSON |

### 16.2 Worker処理フロー

1. テキスト抽出（PDF/Word → テキスト）
2. LLM抽出（Responses API → 構造化JSON）
3. Embedding生成（Embeddings API）
4. スコア算出（Pythonで計算）
5. 説明生成（Responses API）

### 16.3 キュー設計

- **最小構成：** `jobs_queue` テーブルをWorkerがポーリング
- **拡張時：** Redis + RQ/Celery

---

## 17. データモデル（RDB）

### 17.1 テーブル一覧

| テーブル | 説明 |
|---------|------|
| jobs | 求人票 |
| candidates | 応募者 |
| documents | アップロード書類 |
| extractions | LLM抽出結果 |
| embeddings | Embedding（Nice類似用） |
| scores | 算出スコア |
| explanations | 説明文 |
| decisions | 人の意思決定 |
| audit_events | 監査ログ |
| score_config | スコア設定（重み等） |
| jobs_queue | 非同期ジョブキュー |

### 17.2 主要テーブル定義

**jobs**
```
job_id (PK), title, job_text_raw, requirements_json, created_at, updated_at
```

**candidates**
```
candidate_id (PK), job_id (FK), display_name, status (NEW/PROCESSING/DONE/ERROR), submitted_at
```

**documents**
```
document_id (PK), candidate_id (FK), type (resume/cv), object_uri, text_uri, hash, created_at
```

**extractions**
```
candidate_id (PK/FK), job_requirements_json, candidate_profile_json, evidence_json, llm_model, extract_version, created_at
```

**scores**
```
candidate_id (PK/FK), must_score, nice_score, year_score, role_score, total_fit_0_100, must_gaps_json, score_config_version, computed_at
```

**explanations**
```
candidate_id (PK/FK), explanation_json (summary/strengths/concerns/unknowns/must_gaps), created_at
```

**decisions**
```
decision_id (PK), candidate_id (FK), decision (pass/hold/reject), reason, decided_by, decided_at
```

**score_config**
```
version (PK), weights_json, must_cap_enabled, must_cap_value, nice_top_n, role_distance_json, created_at
```

**jobs_queue**
```
queue_id (PK), candidate_id, job_type (TEXT_EXTRACT/LLM_EXTRACT/EMBED/SCORE/EXPLAIN), status (READY/RUNNING/DONE/FAILED), attempts, last_error, created_at, updated_at
```

---

## 18. 例外・障害時の挙動

| 状況 | 挙動 |
|------|------|
| テキスト抽出不能 | status=ERROR、原因表示（ファイル破損等） |
| LLMのJSON不正 | 再試行（最大N回）、それでも失敗ならERROR |
| Embedding失敗 | NiceScoreを0扱い＋unknownsに記録 |
| 一部unknown | unknownsに列挙、担当者に確認を促す |

---

## 19. 実装優先順位（推奨）

1. 求人・応募者・アップロード・ジョブキュー（DBポーリング）
2. テキスト抽出（まずはPDF/Wordどちらか）
3. LLM抽出（構造化JSON＋evidence）
4. スコア計算（Must/Year/Role → 次にNice Embeddings）
5. 説明生成（summary/strengths/concerns）
6. UI一覧・詳細、意思決定、監査ログ
7. score_config 管理画面（重み調整）

---
