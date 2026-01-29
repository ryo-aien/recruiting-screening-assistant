# システム設計書（全体版）：採用書類選考支援（OpenAI API／小規模Docker個人開発）

> **関連ドキュメント：** プロンプト設計・JSONスキーマ・スコアリング仕様の詳細は `UNIFIED_SPEC.md` を参照

## 1. 概要

### 1.1 目的

* 書類選考における「読む・要点抽出・要件照合・懸念抽出・優先順位付け」の前処理を自動化し、採用担当者のレビュー時間と滞留を削減する。
* AIは合否を確定しない。最終判断は人間が行う。
* 出力は説明可能であること（スコア内訳＋根拠提示）。

### 1.2 非目的

* 過去採用データを用いたモデル学習・重み学習（実施しない）。
* 属性推定（年齢・性別・国籍等）による判断。

---

## 2. 前提・制約

### 2.1 開発・運用形態

* 個人開発、単一マシン上のDocker Compose運用を想定。
* 同時利用ユーザー数は少数（1〜数名）。
* ATS連携なし（将来拡張）。

### 2.2 AI利用方針

* LLM（OpenAI Responses API）は「抽出（構造化）」と「説明文生成」に限定。
* 定量スコア（0–100）はアプリ側で計算し、LLMに直接採点させない。
* Nice要件の意味類似は Embeddings API＋コサイン類似度で定量化。

---

## 3. 全体アーキテクチャ

### 3.1 コンポーネント一覧

1. **Web UI**

* 求人作成／応募者登録
* 応募者一覧（順位・適合度・強み/懸念・Must未達）
* 応募者詳細（内訳・根拠・原文・意思決定）

2. **Backend API（アプリケーション層）**

* 認証・認可（簡易）
* データCRUD
* ジョブ登録・結果参照
* OpenAI API呼び出し（キー秘匿・レート制御・監査）

3. **Worker（非同期処理）**

* 文書テキスト抽出（PDF/Word）
* LLM抽出（Responses API）
* Embedding生成（Embeddings API）
* スコア算出、説明生成

4. **RDB（MySQL）**

* 求人・応募者・文書・抽出結果・スコア・意思決定・監査ログ

5. **Object Storage（小規模ならローカルボリュームでも可）**

* 原本ファイル
* 抽出テキスト
* 根拠（evidence）JSON

6. **Queue（簡易構成）**

* 最小：DBのjobsテーブルをWorkerがポーリング

---

## 4. データフロー

### 4.1 求人登録

1. UI→Backend：求人票本文を登録
2. Backend：求人票本文を保存
3. （オプション）Worker：求人票からMust/Nice等をLLMで抽出し `requirements_json` を自動生成

   * 初期は「手入力」でも可（MVP簡略）

### 4.2 応募書類アップロード〜スコア反映

1. UI→Backend：応募者作成＋書類アップロード
2. Backend：原本を保存し、`jobs_queue` に処理ジョブを登録
3. Worker：

   * 文書テキスト抽出 → `documents.text_uri` 保存
   * LLMで「求人要件＋候補者プロファイル」を構造化JSON抽出（根拠付き）
   * Embeddings生成（Nice類似用）
   * スコア計算（アプリ側ロジック）
   * 説明生成（LLM、入力は抽出JSON＋計算済みスコア）
4. UI：一覧・詳細で表示

### 4.3 人の意思決定（通過/保留/見送り）

1. UI→Backend：意思決定を登録（理由任意）
2. Backend：`decisions`、`audit_events` に保存
3. （将来）このログで運用改善（重み設定の調整等）

---

## 5. 機能要件

### 5.1 求人管理

* 求人作成・更新・一覧
* 必須要件／歓迎要件の編集（手動 or LLM抽出結果の修正）

### 5.2 応募者管理

* 応募者作成・一覧
* 書類アップロード（PDF/Word）
* ステータス（未処理/処理中/処理完了/エラー）

### 5.3 スコアリング・ランキング

* MustScore / NiceScore / YearScore / RoleScore（0〜1）
* TotalFit（0〜100）
* Must未達の場合のcap（上限）適用
* ランキング（求人ごとにTotalFit降順）

### 5.4 説明可能性（必須）

* Must未達・未確認の表示
* 強みTOP3、懸念TOP3、未確認（unknowns）
* 根拠（短い引用）を併記

### 5.5 監査ログ

* 誰がいつ何をしたか（最低限：意思決定、設定変更、候補者閲覧）

---

## 6. 非機能要件

### 6.1 性能

* 1件の書類処理（抽出＋Embedding＋スコア＋説明）を実用的な時間で完了（小規模のため厳密SLAは置かない）
* 同時処理は1〜数件を想定（Workerは単一でも可）

### 6.2 可用性

* 単一ホストで再起動に耐える（データは永続化ボリューム）

### 6.3 セキュリティ／プライバシー

* OpenAI APIキーはサーバ側環境変数で保持（クライアント非公開）
* PIIを扱うためアクセス制御（簡易ログイン、またはローカル運用前提）
* 個人情報（住所・電話等）は抽出対象にしない方針（プロンプトで除外）

---

## 7. データモデル（RDB）

### 7.1 テーブル定義（論理）

**jobs**

* job_id (PK)
* title
* job_text_raw
* requirements_json（Must/Nice/年数/役割期待。手入力 or 自動抽出）
* created_at, updated_at

**candidates**

* candidate_id (PK)
* job_id (FK)
* display_name（匿名化したいならID表示に切替）
* status（NEW/PROCESSING/DONE/ERROR）
* submitted_at

**documents**

* document_id (PK)
* candidate_id (FK)
* type（resume/cv）
* object_uri（原本）
* text_uri（抽出テキスト）
* hash（冪等性）
* created_at

**extractions**

* candidate_id (PK/FK)
* job_requirements_json（LLM抽出。job側のrequirements_jsonと差分が出てもよい）
* candidate_profile_json
* evidence_json
* llm_model
* extract_version
* created_at

**embeddings**

* embedding_id (PK)
* candidate_id (FK)
* kind（candidate_summary / nice_req）
* ref_id（nice_req_id等）
* vector（DBに保存するか、ファイル化するか、もしくは省略して都度生成）
* created_at

**scores**

* candidate_id (PK/FK)
* must_score, nice_score, year_score, role_score（0〜1）
* total_fit_0_100
* must_gaps_json（未達Mustの一覧）
* score_config_version
* computed_at

**explanations**

* candidate_id (PK/FK)
* explanation_json（summary/strengths/concerns/unknowns/must_gaps）
* created_at

**decisions**

* decision_id (PK)
* candidate_id (FK)
* decision（pass/hold/reject）
* reason（任意）
* decided_by
* decided_at

**audit_events**

* event_id (PK)
* actor_id
* action
* entity_type
* entity_id
* payload_json
* created_at

### 7.2 設定（score_config）

**score_config**

* version (PK)
* weights_json（must/nice/year/role）
* must_cap_enabled, must_cap_value
* nice_top_n
* role_distance_json
* created_at

---

## 8. 非同期ジョブ設計

### 8.1 ジョブ種類（DBポーリング想定）

**jobs_queue**

* queue_id (PK)
* candidate_id
* job_type（TEXT_EXTRACT / LLM_EXTRACT / EMBED / SCORE / EXPLAIN）
* status（READY/RUNNING/DONE/FAILED）
* attempts
* last_error
* created_at, updated_at

### 8.2 冪等性

* documents.hash と extract_version、score_config_version をキーに再計算を制御
* 例：同じ文書hashで既にDONEならスキップ

### 8.3 リトライ

* OpenAI呼び出し失敗時は attempts++ し、指数バックオフ（簡易なら一定間隔）
* 最終FAILEDでUIにエラー表示

---

## 9. スコアリング仕様（確定版：学習なし）

### 9.1 サブスコア（0〜1）

1. **MustScore（ルールベース）**

* Must要件ごとに `satisfied / not_satisfied / unknown` を決定
* unknownは保守的に 0 扱い（設定で変更可）
* MustScore = satisfied_count / must_total

2. **YearScore（連続値）**

* 要求年数 req（例：Python 3年）と実績 x が取得できる場合のみ算出
* 小規模運用では線形クリップを推奨：

  * YearScore_skill = clip(x / req, 0, 1)
* YearScore = required_skills平均（または最小。設定で選択可）

3. **RoleScore（距離表）**

* role_expectation（IC/Lead/Manager 等）と candidate.roles を距離表で評価
* 一致=1.0、隣接=0.7、乖離=0.3、不明=0.5（初期）

4. **NiceScore（Embeddings類似度）**

* nice要件ごとにembeddingを作成し、候補者summary embeddingとのコサイン類似度を計算
* NiceScore = topN平均（N=3等）

### 9.2 合成スコア（0〜100）

* TotalFit01 = w_must*MustScore + w_nice*NiceScore + w_year*YearScore + w_role*RoleScore
* TotalFit = round(TotalFit01 * 100)

### 9.3 Must cap（推奨）

* Must未達が1つでもあれば、TotalFitに上限を付与：

  * TotalFit = min(TotalFit, must_cap_value)（例：20）
* 目的：Must未達が上位に来る事故を防ぐ（説明容易）

---

## 10. OpenAIプロンプト設計（スコアリング用：抽出＋説明）

※ 詳細なプロンプト設計・JSONスキーマは `UNIFIED_SPEC.md` セクション4〜5を参照

### 10.1 抽出（構造化JSON）— Responses API

**System Prompt要点：**
- 情報抽出エンジンとして動作
- 推測・推論禁止（不明はnull + unknownsに追加）
- evidence（20語以内の引用）を必ず付与
- センシティブ属性（年齢・性別・国籍等）は無視
- スキル名は業界標準に正規化

**出力JSON Schema：**
- `job_requirements`：must/nice/role_expectation/year_requirements
- `candidate_profile`：skills/roles/experience_years/highlights/concerns/unknowns
- `evidence`：job側・candidate側の根拠引用

---

### 10.2 NiceScore用 Embeddings（定量）

* 入力テキスト
  * nice要件：`nice[i].text`
  * 候補者：`candidate_summary_text = join(skills + highlights)`（アプリ生成）
* アプリ側でembeddingを取得しコサイン類似度計算
* NiceScoreは topN平均（デフォルトN=3）

---

### 10.3 説明生成（スコア説明）— Responses API

**System Prompt要点：**
- 提供された入力とevidenceのみ使用（事実の捏造禁止）
- リクルーター向けに簡潔・実用的に

**出力JSON：**
- summary (string)
- strengths (array, up to 3)
- concerns (array, up to 3)
- unknowns (array, up to 5)
- must_gaps (array)

---

## 11. API設計（Backend）

### 11.1 エンドポイント（MVP）

* `POST /jobs`

  * body: title, job_text_raw（＋任意でrequirements_json）

* `GET /jobs`

* `GET /jobs/{job_id}`

* `POST /jobs/{job_id}/candidates`

  * body: display_name（任意）

* `POST /candidates/{candidate_id}/documents`

  * multipart: file, type（resume/cv）

* `GET /jobs/{job_id}/candidates`

  * 一覧：total_fit、要点、ステータス

* `GET /candidates/{candidate_id}`

  * 詳細：抽出JSON、スコア内訳、根拠、説明

* `POST /candidates/{candidate_id}/decision`

  * body: decision(pass/hold/reject), reason(optional)

* `GET /admin/score-config`

* `POST /admin/score-config`

  * 重み・閾値・capを更新（学習なしの運用最適化）

### 11.2 レスポンス設計（一覧に必要な最小項目）

* candidate_id
* status
* total_fit_0_100
* must_gaps_count
* strengths_top3
* concerns_top3
* decided_state（あれば）

---

## 12. UI設計（MVP）

### 12.1 応募者一覧

* ソート：TotalFit降順（デフォルト）
* 表示：TotalFit、優先度（A/B/Cは閾値で付与）、強みTOP3、懸念TOP3、Must未達数
* フィルタ：Must未達除外、ステータス、手動ピン留め（任意）

### 12.2 応募者詳細

* スコア内訳（Must/Nice/Year/Role）
* Must未達／未確認
* 根拠引用（短文）
* 原文参照（抽出テキスト）
* 意思決定入力（通過/保留/見送り、理由）

---

## 13. Docker構成（docker-compose）

### 13.1 サービス例

* `web`（UI、必要なら）
* `api`（Backend）
* `worker`（非同期）
* `db`（MySQL）
* `storage`（ローカルvolume、またはminio）
* （任意）`redis`（キュー導入時）

### 13.2 永続化ボリューム

* MySQL data
* storage data（raw/text/evidence）

---

## 14. 運用・監視（小規模）

### 14.1 監視項目（最低限）

* jobs_queue のFAILED件数
* OpenAI呼び出し失敗回数（レート、タイムアウト）
* 1件あたり処理時間（目視でも可）

### 14.2 ログ

* candidate_id単位で「いつ、どのジョブが、どのバージョンで」動いたか
* score_config_version を必ず記録（後から説明可能にする）

---

## 15. セキュリティ設計（小規模の実務ライン）

* OpenAI APIキーは `api` / `worker` の環境変数にのみ設定
* UIから直接OpenAIを叩かない（キー漏洩防止）
* PIIの保存最小化（表示名を匿名化できる設計）
* 監査ログにアクセス者・意思決定者を残す

---

## 16. 例外・障害時の挙動

* テキスト抽出不能：status=ERROR、原因表示（ファイル破損等）
* LLMのJSON不正：再試行（最大N回）、それでも失敗ならERROR
* Embedding失敗：NiceScoreを0扱い＋unknownに記録（運用上の選択）
* 一部unknown：unknownsに列挙し、担当者に確認を促す（断定しない）

---

## 17. 将来拡張（今回の設計を崩さずに追加可能）

* ATS連携（応募取り込み／ステータス書き戻し）
* 面接議事録要約（ただしスコア入力と混ぜず、リーク防止で別パイプライン）
* 会社独自ルーブリックのファイル化と参照（file_search相当の導入）
* 多求人・多チームのテナント化（RBAC強化）

---

## 18. 実装優先順位（推奨）

1. 求人・応募者・アップロード・ジョブキュー（DBポーリング）
2. テキスト抽出（まずはPDF/Wordどちらか）
3. LLM抽出（構造化JSON＋evidence）
4. スコア計算（Must/Year/Role → 次にNice Embeddings）
5. 説明生成（summary/strengths/concerns）
6. UI一覧・詳細、意思決定、監査ログ
7. score_config 管理画面（重み調整）

---

