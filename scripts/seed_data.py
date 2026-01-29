#!/usr/bin/env python3
"""
サンプルデータ作成スクリプト
動作確認用の求人・応募者データを投入します
"""

import asyncio
import uuid
from datetime import datetime

import asyncmy
from asyncmy.cursors import DictCursor


# サンプル求人データ
SAMPLE_JOBS = [
    {
        "title": "シニアPythonエンジニア",
        "job_text_raw": """【募集職種】
シニアPythonエンジニア

【業務内容】
- バックエンドAPIの設計・開発
- データパイプラインの構築
- コードレビュー・技術指導

【必須要件】
- Python 5年以上の実務経験
- Webフレームワーク（FastAPI/Django/Flask）の経験
- RDBMSの設計・運用経験
- Gitを用いたチーム開発経験

【歓迎要件】
- AWS/GCPでのインフラ構築経験
- Kubernetes/Docker経験
- 機械学習・データ分析経験
- テックリード経験

【求める役割】
テックリード候補として、設計からコードレビューまで担当

【年収】
800万円〜1200万円
""",
    },
    {
        "title": "フロントエンドエンジニア（React）",
        "job_text_raw": """【募集職種】
フロントエンドエンジニア

【業務内容】
- React/TypeScriptを用いたWebアプリケーション開発
- UIコンポーネントの設計・実装
- パフォーマンス最適化

【必須要件】
- React 3年以上の実務経験
- TypeScript経験
- HTML/CSS/JavaScriptの基礎知識
- REST API連携の経験

【歓迎要件】
- Next.js経験
- GraphQL経験
- デザインシステム構築経験
- Figma等のデザインツール経験

【求める役割】
フロントエンド開発のコアメンバー

【年収】
600万円〜900万円
""",
    },
    {
        "title": "インフラエンジニア（SRE）",
        "job_text_raw": """【募集職種】
インフラエンジニア / SRE

【業務内容】
- クラウドインフラの設計・構築・運用
- CI/CDパイプラインの整備
- 監視・アラート体制の構築
- インシデント対応・ポストモーテム

【必須要件】
- AWS 3年以上の実務経験
- Linux管理経験
- Infrastructure as Code（Terraform/CloudFormation）
- コンテナ技術（Docker/Kubernetes）

【歓迎要件】
- GCP/Azure経験
- セキュリティ関連の知識・経験
- 大規模トラフィック対応経験
- SLO/SLI設計経験

【求める役割】
SREチームのリーダー候補

【年収】
700万円〜1100万円
""",
    },
]

# サンプル応募者データ（抽出済み状態）
SAMPLE_CANDIDATES = [
    # Job 1 (Python) の応募者
    {
        "job_index": 0,
        "display_name": "田中 太郎",
        "extraction": {
            "job_requirements": {
                "must": [
                    {"id": "m1", "text": "Python 5年以上の実務経験", "skill_tags": ["Python"]},
                    {"id": "m2", "text": "Webフレームワーク経験", "skill_tags": ["FastAPI", "Django", "Flask"]},
                    {"id": "m3", "text": "RDBMS設計・運用経験", "skill_tags": ["MySQL", "PostgreSQL"]},
                    {"id": "m4", "text": "Git経験", "skill_tags": ["Git"]},
                ],
                "nice": [
                    {"id": "n1", "text": "AWS/GCPでのインフラ構築経験", "skill_tags": ["AWS", "GCP"]},
                    {"id": "n2", "text": "Kubernetes/Docker経験", "skill_tags": ["Kubernetes", "Docker"]},
                    {"id": "n3", "text": "機械学習・データ分析経験", "skill_tags": ["ML", "データ分析"]},
                ],
                "role_expectation": "Lead",
                "year_requirements": {"Python": 5},
            },
            "candidate_profile": {
                "skills": ["Python", "FastAPI", "Django", "MySQL", "PostgreSQL", "AWS", "Docker", "Git"],
                "roles": ["Lead", "IC"],
                "experience_years": {"Python": 7, "AWS": 3},
                "highlights": ["Python 7年の経験", "チームリーダーとして5名のチームを管理", "AWS認定ソリューションアーキテクト取得"],
                "concerns": [],
                "unknowns": ["Kubernetes経験の詳細"],
            },
            "evidence": {
                "job": {"must:m1": "Python 5年以上の実務経験"},
                "candidate": {"skill:Python": "Python歴7年、FastAPI/Djangoでの開発経験豊富"},
            },
        },
        "score": {
            "must_score": 1.0,
            "nice_score": 0.75,
            "year_score": 1.0,
            "role_score": 1.0,
            "total_fit_0_100": 95,
            "must_gaps": [],
        },
        "explanation": {
            "summary": "Python 7年の豊富な経験とチームリーダー経験を持つ優秀な候補者。必須要件をすべて満たしており、即戦力として期待できます。",
            "strengths": ["Python 7年の実務経験", "FastAPI/Djangoの両方の経験", "AWSの実務経験3年"],
            "concerns": [],
            "unknowns": ["Kubernetes経験の詳細が不明"],
            "must_gaps": [],
        },
    },
    {
        "job_index": 0,
        "display_name": "鈴木 花子",
        "extraction": {
            "job_requirements": {
                "must": [
                    {"id": "m1", "text": "Python 5年以上の実務経験", "skill_tags": ["Python"]},
                    {"id": "m2", "text": "Webフレームワーク経験", "skill_tags": ["FastAPI", "Django", "Flask"]},
                    {"id": "m3", "text": "RDBMS設計・運用経験", "skill_tags": ["MySQL", "PostgreSQL"]},
                    {"id": "m4", "text": "Git経験", "skill_tags": ["Git"]},
                ],
                "nice": [
                    {"id": "n1", "text": "AWS/GCPでのインフラ構築経験", "skill_tags": ["AWS", "GCP"]},
                    {"id": "n2", "text": "Kubernetes/Docker経験", "skill_tags": ["Kubernetes", "Docker"]},
                ],
                "role_expectation": "Lead",
                "year_requirements": {"Python": 5},
            },
            "candidate_profile": {
                "skills": ["Python", "Flask", "PostgreSQL", "Git", "Docker"],
                "roles": ["IC"],
                "experience_years": {"Python": 4},
                "highlights": ["機械学習プロジェクトでのPython活用", "データパイプライン構築経験"],
                "concerns": ["Python経験が要件より1年不足"],
                "unknowns": ["マネジメント経験"],
            },
            "evidence": {
                "job": {"must:m1": "Python 5年以上の実務経験"},
                "candidate": {"skill:Python": "Python歴4年、主にデータ分析・ML領域"},
            },
        },
        "score": {
            "must_score": 0.75,
            "nice_score": 0.5,
            "year_score": 0.8,
            "role_score": 0.7,
            "total_fit_0_100": 20,  # Must capが適用
            "must_gaps": ["Python 5年以上の実務経験（現在4年）"],
        },
        "explanation": {
            "summary": "データ分析・ML領域でのPython経験がある候補者。経験年数が1年不足しており、リーダー経験もないため、要件との適合度は低め。",
            "strengths": ["機械学習プロジェクト経験", "データパイプライン構築スキル"],
            "concerns": ["Python経験が要件より1年不足", "リーダー経験なし"],
            "unknowns": ["Webフレームワークの詳細経験"],
            "must_gaps": ["Python 5年以上の実務経験（現在4年）"],
        },
    },
    {
        "job_index": 0,
        "display_name": "佐藤 次郎",
        "extraction": {
            "job_requirements": {
                "must": [
                    {"id": "m1", "text": "Python 5年以上の実務経験", "skill_tags": ["Python"]},
                    {"id": "m2", "text": "Webフレームワーク経験", "skill_tags": ["FastAPI", "Django", "Flask"]},
                    {"id": "m3", "text": "RDBMS設計・運用経験", "skill_tags": ["MySQL", "PostgreSQL"]},
                    {"id": "m4", "text": "Git経験", "skill_tags": ["Git"]},
                ],
                "nice": [
                    {"id": "n1", "text": "AWS/GCPでのインフラ構築経験", "skill_tags": ["AWS", "GCP"]},
                    {"id": "n2", "text": "Kubernetes/Docker経験", "skill_tags": ["Kubernetes", "Docker"]},
                ],
                "role_expectation": "Lead",
                "year_requirements": {"Python": 5},
            },
            "candidate_profile": {
                "skills": ["Python", "Django", "MySQL", "AWS", "Kubernetes", "Docker", "Git", "Terraform"],
                "roles": ["Lead", "Manager"],
                "experience_years": {"Python": 6, "AWS": 5},
                "highlights": ["エンジニアリングマネージャー経験3年", "AWS上での大規模システム構築", "Kubernetes本番運用経験"],
                "concerns": [],
                "unknowns": [],
            },
            "evidence": {
                "job": {"must:m1": "Python 5年以上の実務経験"},
                "candidate": {"skill:Python": "Python歴6年、Django中心に開発"},
            },
        },
        "score": {
            "must_score": 1.0,
            "nice_score": 0.9,
            "year_score": 1.0,
            "role_score": 0.7,
            "total_fit_0_100": 92,
            "must_gaps": [],
        },
        "explanation": {
            "summary": "マネージャー経験もある非常に優秀な候補者。技術力・マネジメント力ともに高く、即戦力として期待できます。ただし、求める役割がリードであり、マネージャー志向の方には物足りない可能性あり。",
            "strengths": ["Python 6年＋AWS 5年の豊富な経験", "エンジニアリングマネージャー経験", "Kubernetes本番運用経験"],
            "concerns": ["オーバースペックの可能性"],
            "unknowns": [],
            "must_gaps": [],
        },
    },
    # Job 2 (React) の応募者
    {
        "job_index": 1,
        "display_name": "山田 美咲",
        "extraction": {
            "job_requirements": {
                "must": [
                    {"id": "m1", "text": "React 3年以上の実務経験", "skill_tags": ["React"]},
                    {"id": "m2", "text": "TypeScript経験", "skill_tags": ["TypeScript"]},
                    {"id": "m3", "text": "HTML/CSS/JavaScript", "skill_tags": ["HTML", "CSS", "JavaScript"]},
                    {"id": "m4", "text": "REST API連携", "skill_tags": ["REST API"]},
                ],
                "nice": [
                    {"id": "n1", "text": "Next.js経験", "skill_tags": ["Next.js"]},
                    {"id": "n2", "text": "GraphQL経験", "skill_tags": ["GraphQL"]},
                ],
                "role_expectation": "IC",
                "year_requirements": {"React": 3},
            },
            "candidate_profile": {
                "skills": ["React", "TypeScript", "Next.js", "HTML", "CSS", "JavaScript", "GraphQL"],
                "roles": ["IC"],
                "experience_years": {"React": 4, "TypeScript": 3},
                "highlights": ["Next.jsでの大規模サービス開発", "デザインシステム構築経験", "パフォーマンス最適化実績"],
                "concerns": [],
                "unknowns": [],
            },
            "evidence": {
                "job": {"must:m1": "React 3年以上の実務経験"},
                "candidate": {"skill:React": "React歴4年、TypeScriptとの組み合わせで開発"},
            },
        },
        "score": {
            "must_score": 1.0,
            "nice_score": 0.85,
            "year_score": 1.0,
            "role_score": 1.0,
            "total_fit_0_100": 97,
            "must_gaps": [],
        },
        "explanation": {
            "summary": "React/TypeScriptの経験が豊富で、Next.jsやGraphQLなど歓迎要件も満たす優秀な候補者。即戦力として期待できます。",
            "strengths": ["React 4年の実務経験", "Next.js大規模開発経験", "デザインシステム構築経験"],
            "concerns": [],
            "unknowns": [],
            "must_gaps": [],
        },
    },
    {
        "job_index": 1,
        "display_name": "高橋 健一",
        "extraction": {
            "job_requirements": {
                "must": [
                    {"id": "m1", "text": "React 3年以上の実務経験", "skill_tags": ["React"]},
                    {"id": "m2", "text": "TypeScript経験", "skill_tags": ["TypeScript"]},
                    {"id": "m3", "text": "HTML/CSS/JavaScript", "skill_tags": ["HTML", "CSS", "JavaScript"]},
                    {"id": "m4", "text": "REST API連携", "skill_tags": ["REST API"]},
                ],
                "nice": [
                    {"id": "n1", "text": "Next.js経験", "skill_tags": ["Next.js"]},
                ],
                "role_expectation": "IC",
                "year_requirements": {"React": 3},
            },
            "candidate_profile": {
                "skills": ["Vue.js", "JavaScript", "HTML", "CSS"],
                "roles": ["IC"],
                "experience_years": {"Vue.js": 3, "React": 1},
                "highlights": ["Vue.js 3年の経験", "フロントエンド全般の知識"],
                "concerns": ["Reactの経験が不足"],
                "unknowns": ["TypeScript経験"],
            },
            "evidence": {
                "job": {"must:m1": "React 3年以上の実務経験"},
                "candidate": {"skill:React": "React歴1年、主にVue.jsで開発"},
            },
        },
        "score": {
            "must_score": 0.5,
            "nice_score": 0.3,
            "year_score": 0.33,
            "role_score": 1.0,
            "total_fit_0_100": 20,  # Must cap適用
            "must_gaps": ["React 3年以上の実務経験（現在1年）", "TypeScript経験"],
        },
        "explanation": {
            "summary": "Vue.jsの経験は豊富だが、Reactの経験が不足。TypeScript経験も不明で、必須要件を満たしていない。",
            "strengths": ["フロントエンド全般の知識", "Vue.js 3年の経験"],
            "concerns": ["React経験が1年のみ", "TypeScript経験不明"],
            "unknowns": ["TypeScript習得意欲"],
            "must_gaps": ["React 3年以上の実務経験（現在1年）", "TypeScript経験"],
        },
    },
    # Job 3 (SRE) の応募者
    {
        "job_index": 2,
        "display_name": "伊藤 雄大",
        "extraction": {
            "job_requirements": {
                "must": [
                    {"id": "m1", "text": "AWS 3年以上の実務経験", "skill_tags": ["AWS"]},
                    {"id": "m2", "text": "Linux管理経験", "skill_tags": ["Linux"]},
                    {"id": "m3", "text": "IaC経験", "skill_tags": ["Terraform", "CloudFormation"]},
                    {"id": "m4", "text": "コンテナ技術", "skill_tags": ["Docker", "Kubernetes"]},
                ],
                "nice": [
                    {"id": "n1", "text": "GCP/Azure経験", "skill_tags": ["GCP", "Azure"]},
                    {"id": "n2", "text": "セキュリティ関連", "skill_tags": ["Security"]},
                ],
                "role_expectation": "Lead",
                "year_requirements": {"AWS": 3},
            },
            "candidate_profile": {
                "skills": ["AWS", "GCP", "Linux", "Terraform", "Kubernetes", "Docker", "Prometheus", "Grafana"],
                "roles": ["Lead"],
                "experience_years": {"AWS": 5, "Kubernetes": 3},
                "highlights": ["SREチームリーダー経験", "99.99%可用性の達成", "大規模Kubernetes運用"],
                "concerns": [],
                "unknowns": [],
            },
            "evidence": {
                "job": {"must:m1": "AWS 3年以上の実務経験"},
                "candidate": {"skill:AWS": "AWS歴5年、大規模インフラ構築・運用"},
            },
        },
        "score": {
            "must_score": 1.0,
            "nice_score": 0.8,
            "year_score": 1.0,
            "role_score": 1.0,
            "total_fit_0_100": 96,
            "must_gaps": [],
        },
        "explanation": {
            "summary": "SREとして豊富な経験を持つ優秀な候補者。リーダー経験もあり、即戦力として期待できます。",
            "strengths": ["AWS 5年の豊富な経験", "SREチームリーダー経験", "99.99%可用性達成実績"],
            "concerns": [],
            "unknowns": [],
            "must_gaps": [],
        },
    },
]


async def create_sample_data():
    """サンプルデータを作成"""

    # データベース接続
    conn = await asyncmy.connect(
        host="localhost",
        port=3306,
        user="screening_user",
        password="screening_pass",
        db="screening",
    )

    try:
        async with conn.cursor(DictCursor) as cursor:
            # 既存データの確認
            await cursor.execute("SELECT COUNT(*) as cnt FROM jobs")
            result = await cursor.fetchone()
            if result["cnt"] > 0:
                print("既存のデータがあります。追加しますか？ (y/n): ", end="")
                response = input()
                if response.lower() != "y":
                    print("キャンセルしました")
                    return

            job_ids = []

            # 求人データ作成
            print("\n=== 求人データ作成 ===")
            for job_data in SAMPLE_JOBS:
                job_id = str(uuid.uuid4())
                job_ids.append(job_id)

                await cursor.execute(
                    """
                    INSERT INTO jobs (job_id, title, job_text_raw, created_at, updated_at)
                    VALUES (%s, %s, %s, NOW(), NOW())
                    """,
                    (job_id, job_data["title"], job_data["job_text_raw"]),
                )
                print(f"  作成: {job_data['title']} (ID: {job_id[:8]}...)")

            # スコア設定の確認
            await cursor.execute("SELECT version FROM score_config ORDER BY version DESC LIMIT 1")
            config = await cursor.fetchone()
            score_config_version = config["version"] if config else 1

            # 応募者データ作成
            print("\n=== 応募者データ作成 ===")
            for candidate_data in SAMPLE_CANDIDATES:
                job_id = job_ids[candidate_data["job_index"]]
                candidate_id = str(uuid.uuid4())

                # 応募者
                await cursor.execute(
                    """
                    INSERT INTO candidates (candidate_id, job_id, display_name, status, submitted_at)
                    VALUES (%s, %s, %s, 'DONE', NOW())
                    """,
                    (candidate_id, job_id, candidate_data["display_name"]),
                )

                # 抽出結果
                import json
                extraction = candidate_data["extraction"]
                await cursor.execute(
                    """
                    INSERT INTO extractions (candidate_id, job_requirements_json, candidate_profile_json, evidence_json, llm_model, extract_version, created_at)
                    VALUES (%s, %s, %s, %s, 'sample', 'v1', NOW())
                    """,
                    (
                        candidate_id,
                        json.dumps(extraction["job_requirements"], ensure_ascii=False),
                        json.dumps(extraction["candidate_profile"], ensure_ascii=False),
                        json.dumps(extraction["evidence"], ensure_ascii=False),
                    ),
                )

                # スコア
                score = candidate_data["score"]
                await cursor.execute(
                    """
                    INSERT INTO scores (candidate_id, must_score, nice_score, year_score, role_score, total_fit_0_100, must_gaps_json, score_config_version, computed_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
                    """,
                    (
                        candidate_id,
                        score["must_score"],
                        score["nice_score"],
                        score["year_score"],
                        score["role_score"],
                        score["total_fit_0_100"],
                        json.dumps(score["must_gaps"], ensure_ascii=False),
                        score_config_version,
                    ),
                )

                # 説明
                explanation = candidate_data["explanation"]
                await cursor.execute(
                    """
                    INSERT INTO explanations (candidate_id, explanation_json, created_at)
                    VALUES (%s, %s, NOW())
                    """,
                    (
                        candidate_id,
                        json.dumps(explanation, ensure_ascii=False),
                    ),
                )

                print(f"  作成: {candidate_data['display_name']} (スコア: {score['total_fit_0_100']})")

            await conn.commit()

            print("\n=== 完了 ===")
            print(f"求人: {len(SAMPLE_JOBS)}件")
            print(f"応募者: {len(SAMPLE_CANDIDATES)}名")
            print("\nフロントエンドで確認: http://localhost:3000/jobs")

    finally:
        await conn.ensure_closed()


if __name__ == "__main__":
    asyncio.run(create_sample_data())
