#!/usr/bin/env python3
"""
サンプルデータ作成スクリプト（コンテナ内実行用）
動作確認用の求人・応募者データを投入します

大規模版:
- 求人: 50件
- 応募者: 500-700名
- より多様なステータス・品質分布
"""

import asyncio
import json
import random
import uuid
from datetime import datetime, timedelta

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal


# ==================================================
# サンプル求人データ（50件）
# ==================================================
SAMPLE_JOBS = [
    # ---- 既存の求人（15件） ----
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
    {
        "title": "データエンジニア",
        "job_text_raw": """【募集職種】
データエンジニア

【業務内容】
- データパイプラインの設計・構築
- データウェアハウスの運用・最適化
- ETL処理の開発・保守
- データ品質管理

【必須要件】
- SQL 3年以上の実務経験
- Python/Scalaでのデータ処理経験
- BigQuery/Redshift/Snowflakeいずれかの経験
- Apache Spark/Airflowの経験

【歓迎要件】
- dbt経験
- Kafka/Pub Sub等のストリーミング処理
- 機械学習パイプライン構築経験

【求める役割】
データ基盤チームのコアメンバー

【年収】
700万円〜1000万円
""",
    },
    {
        "title": "機械学習エンジニア",
        "job_text_raw": """【募集職種】
機械学習エンジニア

【業務内容】
- 機械学習モデルの開発・運用
- 特徴量エンジニアリング
- MLOpsの構築・改善
- A/Bテストの設計・分析

【必須要件】
- Python 3年以上の実務経験
- 機械学習モデルの本番運用経験
- TensorFlow/PyTorchの経験
- 統計・数学の基礎知識

【歓迎要件】
- 自然言語処理の経験
- 推薦システムの開発経験
- Kubeflow/MLflow等のMLOps経験
- 論文執筆・学会発表経験

【求める役割】
ML領域のテックリード

【年収】
800万円〜1300万円
""",
    },
    {
        "title": "iOSエンジニア",
        "job_text_raw": """【募集職種】
iOSエンジニア

【業務内容】
- iOSアプリの設計・開発
- UIKitおよびSwiftUIでの実装
- パフォーマンス最適化
- コードレビュー

【必須要件】
- iOS開発 3年以上の実務経験
- Swift経験
- UIKit/SwiftUIの知識
- App Store申請経験

【歓迎要件】
- Objective-C経験
- CI/CD構築経験
- ユニットテスト/UIテスト経験

【求める役割】
iOSチームのシニアメンバー

【年収】
600万円〜900万円
""",
    },
    {
        "title": "Androidエンジニア",
        "job_text_raw": """【募集職種】
Androidエンジニア

【業務内容】
- Androidアプリの設計・開発
- Kotlin/Jetpack Composeでの実装
- パフォーマンス最適化
- コードレビュー

【必須要件】
- Android開発 3年以上の実務経験
- Kotlin経験
- Jetpack Compose経験
- Google Play申請経験

【歓迎要件】
- Java経験
- Flutter経験
- CI/CD構築経験

【求める役割】
Androidチームのシニアメンバー

【年収】
600万円〜900万円
""",
    },
    {
        "title": "QAエンジニア",
        "job_text_raw": """【募集職種】
QAエンジニア

【業務内容】
- テスト計画・設計
- 自動テストの構築・運用
- 品質分析・改善提案
- テストプロセスの標準化

【必須要件】
- QA 3年以上の実務経験
- テスト設計スキル
- 自動テスト（Selenium/Cypress等）経験
- アジャイル開発の経験

【歓迎要件】
- JSTQB認定資格
- API/パフォーマンステスト経験
- セキュリティテスト経験

【求める役割】
QAリード候補

【年収】
500万円〜800万円
""",
    },
    {
        "title": "セキュリティエンジニア",
        "job_text_raw": """【募集職種】
セキュリティエンジニア

【業務内容】
- 脆弱性診断・ペネトレーションテスト
- セキュリティ監視体制の構築
- インシデント対応
- セキュリティポリシー策定

【必須要件】
- セキュリティ 3年以上の実務経験
- 脆弱性診断経験
- ネットワーク/OS/Webの基礎知識
- セキュリティツール（Burp Suite等）の使用経験

【歓迎要件】
- CISSP/CEH等の資格
- SOC運用経験
- クラウドセキュリティ経験
- バグバウンティ実績

【求める役割】
セキュリティチームのリーダー候補

【年収】
700万円〜1100万円
""",
    },
    {
        "title": "プロダクトマネージャー",
        "job_text_raw": """【募集職種】
プロダクトマネージャー

【業務内容】
- プロダクト戦略の立案
- ロードマップ策定・管理
- 要件定義・優先順位付け
- ステークホルダーとの調整

【必須要件】
- PM 3年以上の実務経験
- BtoB SaaSのプロダクト経験
- データ分析に基づく意思決定経験
- アジャイル開発の経験

【歓迎要件】
- エンジニア出身
- UXデザインの知識
- 英語でのコミュニケーション

【求める役割】
プロダクトリード

【年収】
800万円〜1200万円
""",
    },
    {
        "title": "テックリード（バックエンド）",
        "job_text_raw": """【募集職種】
テックリード（バックエンド）

【業務内容】
- 技術戦略の策定
- アーキテクチャ設計
- チームの技術指導
- コードレビュー・品質管理

【必須要件】
- バックエンド開発 7年以上
- 複数言語での開発経験
- マイクロサービス設計経験
- チームリード経験

【歓迎要件】
- CTO/VP of Engineering経験
- スタートアップでの立ち上げ経験
- OSS貢献実績

【求める役割】
バックエンドチームの技術責任者

【年収】
1000万円〜1500万円
""",
    },
    {
        "title": "DevOpsエンジニア",
        "job_text_raw": """【募集職種】
DevOpsエンジニア

【業務内容】
- CI/CDパイプラインの構築・運用
- インフラの自動化
- 開発環境の整備
- 本番デプロイの管理

【必須要件】
- DevOps 3年以上の実務経験
- GitHub Actions/Jenkins等のCI/CD経験
- Docker/Kubernetes経験
- IaC（Terraform/Ansible）経験

【歓迎要件】
- ArgoCD/Flux等のGitOps経験
- セキュリティスキャン導入経験
- 監視・ログ基盤構築経験

【求める役割】
DevOpsチームのコアメンバー

【年収】
600万円〜950万円
""",
    },
    {
        "title": "Goエンジニア",
        "job_text_raw": """【募集職種】
Goエンジニア

【業務内容】
- Go言語でのバックエンド開発
- マイクロサービスの設計・実装
- APIの設計・開発
- パフォーマンス最適化

【必須要件】
- Go 2年以上の実務経験
- REST API設計・実装経験
- RDBMSの経験
- Gitでのチーム開発経験

【歓迎要件】
- gRPC経験
- Kubernetes運用経験
- 他言語からのキャリアチェンジ歓迎

【求める役割】
バックエンドチームのメンバー

【年収】
600万円〜900万円
""",
    },
    {
        "title": "UI/UXデザイナー",
        "job_text_raw": """【募集職種】
UI/UXデザイナー

【業務内容】
- ユーザーリサーチ・分析
- ワイヤーフレーム・プロトタイプ作成
- UIデザイン
- デザインシステムの構築

【必須要件】
- UI/UXデザイン 3年以上の実務経験
- Figma/Sketch等のツール経験
- プロトタイピング経験
- ユーザーリサーチ経験

【歓迎要件】
- フロントエンド実装スキル
- ユーザビリティテスト経験
- デザインシステム構築経験

【求める役割】
デザインチームのリード候補

【年収】
500万円〜800万円
""",
    },
    {
        "title": "フルスタックエンジニア",
        "job_text_raw": """【募集職種】
フルスタックエンジニア

【業務内容】
- フロントエンドからバックエンドまでの開発
- 機能の設計・実装
- インフラ構築・運用
- 技術選定

【必須要件】
- Web開発 5年以上の実務経験
- フロントエンド（React/Vue等）経験
- バックエンド（Python/Go/Node.js等）経験
- RDBMSの経験

【歓迎要件】
- スタートアップでの経験
- リーダー経験
- モバイルアプリ開発経験

【求める役割】
プロダクト開発のキーメンバー

【年収】
700万円〜1100万円
""",
    },
    # ---- 新卒・ジュニア向け（5件） ----
    {
        "title": "新卒Webエンジニア（2025年卒）",
        "job_text_raw": """【募集職種】
新卒Webエンジニア（2025年卒）

【業務内容】
- Webアプリケーションの開発
- 先輩エンジニアのサポートのもとでの機能実装
- コードレビューへの参加
- 技術調査・学習

【必須要件】
- 2025年3月卒業見込み
- プログラミング経験（言語不問）
- 基本的なGit操作
- 学習意欲の高さ

【歓迎要件】
- 個人開発やチーム開発の経験
- インターンシップ経験
- 競技プログラミング経験
- CS学部・情報系専攻

【求める役割】
次世代を担うエンジニア候補

【年収】
400万円〜500万円
""",
    },
    {
        "title": "ジュニアフロントエンドエンジニア",
        "job_text_raw": """【募集職種】
ジュニアフロントエンドエンジニア

【業務内容】
- React/TypeScriptを用いたUI開発
- 既存コンポーネントの改修・保守
- デザイナーとの連携
- ユニットテストの作成

【必須要件】
- フロントエンド開発経験1年以上
- HTML/CSS/JavaScriptの基礎知識
- React or Vueの基礎知識
- Git操作経験

【歓迎要件】
- TypeScript経験
- ポートフォリオサイトの運営
- UI/UXへの関心

【求める役割】
フロントエンドチームのメンバー

【年収】
400万円〜550万円
""",
    },
    {
        "title": "新卒データアナリスト（2025年卒）",
        "job_text_raw": """【募集職種】
新卒データアナリスト（2025年卒）

【業務内容】
- データ分析・可視化
- SQLを用いたデータ抽出
- BIツールでのダッシュボード作成
- 分析レポートの作成

【必須要件】
- 2025年3月卒業見込み
- SQLの基礎知識
- 統計学の基礎知識
- ExcelまたはGoogle Sheetsの操作

【歓迎要件】
- Pythonでのデータ分析経験
- Tableauなどのツール経験
- 理系学部出身
- データサイエンスの授業履修

【求める役割】
データ分析チームのメンバー

【年収】
400万円〜500万円
""",
    },
    {
        "title": "ジュニアQAエンジニア",
        "job_text_raw": """【募集職種】
ジュニアQAエンジニア

【業務内容】
- テストケースの作成・実行
- バグの報告・管理
- 自動テストスクリプトの作成補助
- 品質改善への提案

【必須要件】
- ソフトウェアテスト経験1年以上
- テスト設計の基礎知識
- Webアプリケーションの理解
- Jira等の課題管理ツール経験

【歓迎要件】
- 自動テスト（Selenium等）経験
- プログラミングスキル
- JSTQBなどの資格

【求める役割】
QAチームのメンバー

【年収】
350万円〜500万円
""",
    },
    {
        "title": "エンジニアインターン（長期）",
        "job_text_raw": """【募集職種】
エンジニアインターン（長期・有給）

【業務内容】
- プロダクト開発のサポート
- 簡単な機能実装
- テスト・ドキュメント作成
- 技術調査

【必須要件】
- 大学または大学院在学中
- プログラミング経験（言語不問）
- 週3日以上勤務可能
- 6ヶ月以上の勤務を想定

【歓迎要件】
- Web開発の経験
- 個人開発の実績
- 情報系学部在籍

【求める役割】
チームの一員としての開発参加

【時給】
1,500円〜2,500円
""",
    },
    # ---- リモートワーク特化（5件） ----
    {
        "title": "フルリモートバックエンドエンジニア",
        "job_text_raw": """【募集職種】
フルリモートバックエンドエンジニア

【業務内容】
- バックエンドAPIの設計・開発
- データベース設計・最適化
- 非同期コミュニケーションでのチーム開発
- ドキュメントの整備

【必須要件】
- バックエンド開発3年以上
- Python/Go/Ruby/Node.jsいずれかの経験
- リモートワーク経験1年以上
- 自走力・セルフマネジメント能力

【歓迎要件】
- フルリモート企業での勤務経験
- 複数タイムゾーンでの協業経験
- 英語でのコミュニケーション

【勤務条件】
完全フルリモート（国内在住）、フレックス制

【年収】
600万円〜900万円
""",
    },
    {
        "title": "リモートワークSREエンジニア",
        "job_text_raw": """【募集職種】
リモートワークSREエンジニア

【業務内容】
- クラウドインフラの設計・運用
- 監視・アラート体制の整備
- インシデント対応（オンコール輪番制）
- Infrastructure as Codeの推進

【必須要件】
- SRE/インフラ経験3年以上
- AWS/GCP/Azureいずれかの実務経験
- Terraform/CloudFormation経験
- リモートでのオンコール対応経験

【歓迎要件】
- 24/7対応の経験
- グローバルチームでの経験
- SLO/SLIの設計経験

【勤務条件】
フルリモート可、オンコール手当あり

【年収】
700万円〜1100万円
""",
    },
    {
        "title": "フルリモートフルスタックエンジニア",
        "job_text_raw": """【募集職種】
フルリモートフルスタックエンジニア

【業務内容】
- フロントエンド・バックエンド両方の開発
- 小規模チームでの機能開発
- 技術選定・アーキテクチャ設計
- コードレビュー

【必須要件】
- フルスタック開発経験4年以上
- React/Vue + Node.js/Python経験
- 自律的に業務を進める能力
- ビデオ会議でのコミュニケーション

【歓迎要件】
- スタートアップでのフルリモート経験
- 複数プロジェクトの並行対応経験

【勤務条件】
完全フルリモート、コアタイムなし

【年収】
650万円〜1000万円
""",
    },
    {
        "title": "海外在住可フロントエンドエンジニア",
        "job_text_raw": """【募集職種】
海外在住可フロントエンドエンジニア

【業務内容】
- React/TypeScriptでのSPA開発
- グローバルチームとの協業
- 多言語対応（i18n）の実装
- パフォーマンス最適化

【必須要件】
- フロントエンド開発3年以上
- React + TypeScript経験
- 英語でのコミュニケーション（読み書き）
- 非同期コミュニケーション能力

【歓迎要件】
- 海外勤務・在住経験
- 英語でのビデオ会議経験
- 複数タイムゾーンでの勤務経験

【勤務条件】
海外在住可（日本時間でのミーティング参加必須）

【年収】
600万円〜950万円（海外在住の場合は現地通貨対応）
""",
    },
    {
        "title": "ワーケーション可能インフラエンジニア",
        "job_text_raw": """【募集職種】
ワーケーション可能インフラエンジニア

【業務内容】
- クラウドインフラの構築・運用
- CI/CDパイプラインの整備
- セキュリティ対策の実装
- コスト最適化

【必須要件】
- インフラエンジニア経験3年以上
- AWS認定資格（SAA以上）
- 安定したインターネット環境の確保
- 自己管理能力

【歓迎要件】
- ワーケーション経験
- デジタルノマド経験
- 複数拠点での勤務経験

【勤務条件】
月1回程度の出社あり、それ以外は場所自由

【年収】
600万円〜900万円
""",
    },
    # ---- マネージャー・ディレクター職（5件） ----
    {
        "title": "エンジニアリングマネージャー",
        "job_text_raw": """【募集職種】
エンジニアリングマネージャー（EM）

【業務内容】
- エンジニアチーム（5-10名）のマネジメント
- 1on1・評価・キャリア支援
- 採用活動（面接・オファー）
- プロジェクト管理・リソース調整

【必須要件】
- エンジニア経験5年以上
- ピープルマネジメント経験2年以上
- 採用面接の経験
- アジャイル開発の経験

【歓迎要件】
- 10名以上のチームマネジメント経験
- 複数チームの統括経験
- エンジニア組織の立ち上げ経験

【求める役割】
エンジニアチームの成長と成果に責任を持つ

【年収】
900万円〜1400万円
""",
    },
    {
        "title": "VPoE（Vice President of Engineering）",
        "job_text_raw": """【募集職種】
VPoE（Vice President of Engineering）

【業務内容】
- エンジニア組織全体（30-50名）の統括
- 技術戦略の策定・実行
- 採用・育成計画の立案
- 経営層との連携

【必須要件】
- エンジニア経験10年以上
- EM経験3年以上または複数チーム統括経験
- 組織拡大フェーズでの経験
- 予算策定・管理経験

【歓迎要件】
- CTO/VPoE経験
- 50名以上の組織マネジメント経験
- IPO準備フェーズでの経験

【求める役割】
エンジニア組織の最高責任者

【年収】
1200万円〜2000万円
""",
    },
    {
        "title": "プロダクト開発部長",
        "job_text_raw": """【募集職種】
プロダクト開発部長

【業務内容】
- プロダクト開発部門の統括
- 開発ロードマップの策定
- エンジニア・PM・デザイナーの連携推進
- 開発プロセスの改善

【必須要件】
- エンジニア経験7年以上
- 部門長またはディレクター経験3年以上
- 複数職種のマネジメント経験
- プロダクト戦略への関与経験

【歓迎要件】
- 新規事業の立ち上げ経験
- M&A後のPMI経験
- グローバル展開経験

【求める役割】
プロダクト開発の全体責任者

【年収】
1000万円〜1600万円
""",
    },
    {
        "title": "CTOアシスタント / CTO室",
        "job_text_raw": """【募集職種】
CTOアシスタント / CTO室メンバー

【業務内容】
- CTOの業務サポート
- 技術戦略の調査・資料作成
- 社内横断プロジェクトの推進
- 技術広報・ブランディング

【必須要件】
- エンジニア経験5年以上
- 複数領域の技術知識
- 資料作成・プレゼンスキル
- プロジェクトマネジメント経験

【歓迎要件】
- テックリード経験
- 技術広報・アドボカシー経験
- 経営企画に関する知識

【求める役割】
CTOの右腕として技術戦略を支援

【年収】
800万円〜1200万円
""",
    },
    {
        "title": "テックリード（アーキテクト）",
        "job_text_raw": """【募集職種】
テックリード / ソフトウェアアーキテクト

【業務内容】
- システムアーキテクチャの設計
- 技術的意思決定のリード
- 技術負債の解消計画
- チームの技術力向上支援

【必須要件】
- エンジニア経験8年以上
- 大規模システムの設計経験
- マイクロサービス/分散システムの知識
- チームへの技術指導経験

【歓迎要件】
- OSS貢献実績
- 技術カンファレンス登壇経験
- 特許・論文執筆経験

【求める役割】
技術面での最高責任者（CTO補佐）

【年収】
1000万円〜1500万円
""",
    },
    # ---- スタートアップ向け（5件） ----
    {
        "title": "スタートアップCTO候補",
        "job_text_raw": """【募集職種】
スタートアップCTO候補

【業務内容】
- 技術戦略の立案・実行
- プロダクト開発のリード
- エンジニアチームの採用・組織構築
- 創業メンバーとしての経営参画

【必須要件】
- エンジニア経験7年以上
- 0→1のプロダクト開発経験
- チームビルディング経験
- 事業成長への強いコミットメント

【歓迎要件】
- スタートアップでのCTO/VPoE経験
- 資金調達に関与した経験
- ストックオプションの理解

【勤務条件】
ストックオプション付与あり

【年収】
800万円〜1500万円 + SO
""",
    },
    {
        "title": "創業期エンジニア（ジェネラリスト）",
        "job_text_raw": """【募集職種】
創業期エンジニア（1号/2号エンジニア）

【業務内容】
- フロントエンド〜バックエンド〜インフラまで全般
- プロダクトの高速開発
- 技術選定への参画
- 将来のチームリード候補

【必須要件】
- Web開発経験3年以上
- フルスタックでの開発経験
- 不確実性を楽しめるマインド
- スタートアップへの理解と興味

【歓迎要件】
- 創業期スタートアップでの経験
- 個人開発でのリリース経験
- 起業経験または起業志向

【勤務条件】
ストックオプション付与あり

【年収】
600万円〜900万円 + SO
""",
    },
    {
        "title": "シードステージPM",
        "job_text_raw": """【募集職種】
シードステージプロダクトマネージャー

【業務内容】
- プロダクト戦略の立案
- ユーザーインタビュー・仮説検証
- 開発優先順位の決定
- 事業計画への貢献

【必須要件】
- PM経験2年以上またはエンジニア経験3年以上
- 0→1フェーズでの経験
- ユーザーリサーチ経験
- 仮説思考・実験マインド

【歓迎要件】
- 起業経験
- 新規事業立ち上げ経験
- ドメインエキスパート

【勤務条件】
ストックオプション付与あり

【年収】
600万円〜1000万円 + SO
""",
    },
    {
        "title": "成長期テックリード",
        "job_text_raw": """【募集職種】
成長期テックリード（シリーズA〜B）

【業務内容】
- 急成長するプロダクトの技術リード
- スケーラビリティの確保
- 技術負債のコントロール
- チーム拡大への対応

【必須要件】
- エンジニア経験5年以上
- 高トラフィックサービスの経験
- 急成長フェーズでの開発経験
- チームリード経験

【歓迎要件】
- スタートアップでのシリーズA〜C経験
- 10倍成長への対応経験
- 採用面接経験

【年収】
800万円〜1200万円
""",
    },
    {
        "title": "スタートアップSRE",
        "job_text_raw": """【募集職種】
スタートアップSRE / インフラエンジニア

【業務内容】
- AWS/GCPでのインフラ構築
- CI/CDパイプラインの整備
- 監視・アラート体制の構築
- コスト最適化

【必須要件】
- インフラ/SRE経験2年以上
- AWS/GCPの実務経験
- コンテナ技術（Docker/Kubernetes）
- スタートアップへの興味

【歓迎要件】
- スタートアップでのSRE経験
- 少人数チームでの経験
- フルスタック志向

【年収】
550万円〜850万円
""",
    },
    # ---- 外資系企業向け（5件） ----
    {
        "title": "Senior Software Engineer (Global)",
        "job_text_raw": """【Position】
Senior Software Engineer (Global Team)

【Responsibilities】
- Design and develop scalable backend services
- Collaborate with global teams across multiple time zones
- Participate in code reviews and architecture discussions
- Mentor junior engineers

【Requirements】
- 5+ years of software engineering experience
- Proficiency in Java, Go, or Python
- Experience with microservices architecture
- Business-level English (speaking and writing)

【Nice to Have】
- Experience working in global companies
- Open source contribution
- AWS/GCP certification

【Expected Role】
Senior IC or Tech Lead

【Salary】
12M - 18M JPY
""",
    },
    {
        "title": "Site Reliability Engineer (English Required)",
        "job_text_raw": """【Position】
Site Reliability Engineer (English Required)

【Responsibilities】
- Manage and improve global infrastructure
- Participate in 24/7 on-call rotation with global team
- Develop automation and monitoring tools
- Incident response and post-mortem

【Requirements】
- 3+ years of SRE/DevOps experience
- Strong AWS/GCP experience
- Fluent English (daily communication)
- Experience with Kubernetes and Terraform

【Nice to Have】
- Experience with follow-the-sun support model
- SRE experience at global companies
- Japanese language skills

【Work Style】
Remote-friendly, flexible hours

【Salary】
10M - 16M JPY
""",
    },
    {
        "title": "Staff Engineer (Silicon Valley Style)",
        "job_text_raw": """【Position】
Staff Engineer

【Responsibilities】
- Drive technical direction across multiple teams
- Lead complex cross-functional projects
- Influence engineering culture and practices
- Mentor senior engineers

【Requirements】
- 10+ years of software engineering experience
- Track record of technical leadership
- Experience with large-scale distributed systems
- Strong communication skills (English/Japanese)

【Nice to Have】
- Experience at FAANG or similar companies
- Published papers or patents
- Conference speaking experience

【Expected Role】
Staff+ IC track

【Salary】
18M - 30M JPY
""",
    },
    {
        "title": "Engineering Manager (Bilingual)",
        "job_text_raw": """【Position】
Engineering Manager (Bilingual)

【Responsibilities】
- Manage engineering team (8-15 engineers)
- Work with US/EU headquarters
- Hiring and performance management
- Bridge between Japan office and global teams

【Requirements】
- 5+ years of engineering experience
- 2+ years of people management experience
- Fluent English and Japanese (native or near-native)
- Experience in multinational environment

【Nice to Have】
- Experience at global tech companies
- MBA or equivalent
- Experience building teams from scratch

【Salary】
14M - 22M JPY
""",
    },
    {
        "title": "Principal Engineer (Tech Leadership)",
        "job_text_raw": """【Position】
Principal Engineer

【Responsibilities】
- Define technical strategy for the organization
- Solve the most complex technical challenges
- Represent engineering externally
- Guide architecture decisions company-wide

【Requirements】
- 12+ years of engineering experience
- Recognized expertise in one or more domains
- Experience influencing without authority
- Strong written and verbal communication

【Nice to Have】
- Industry recognition (talks, publications)
- Experience at Principal+ level
- Open source leadership

【Expected Role】
Principal IC (equivalent to Director)

【Salary】
20M - 35M JPY
""",
    },
    # ---- 業界特化（10件） ----
    {
        "title": "フィンテックエンジニア",
        "job_text_raw": """【募集職種】
フィンテックエンジニア

【業務内容】
- 金融システムのバックエンド開発
- 決済・送金機能の実装
- セキュリティ対策の実装
- 規制対応（金融庁ガイドライン等）

【必須要件】
- バックエンド開発経験3年以上
- 金融業界での開発経験
- セキュリティに関する知識
- 高可用性システムの経験

【歓迎要件】
- 決済システムの開発経験
- PCI DSS対応経験
- ブロックチェーン技術の知識
- 資金決済法の知識

【求める役割】
金融システム開発のコアメンバー

【年収】
700万円〜1100万円
""",
    },
    {
        "title": "ヘルスケアITエンジニア",
        "job_text_raw": """【募集職種】
ヘルスケアITエンジニア

【業務内容】
- 医療・ヘルスケアシステムの開発
- HL7 FHIR準拠のAPI開発
- 個人情報保護対策の実装
- 医療機関との連携機能開発

【必須要件】
- バックエンド開発経験3年以上
- 医療・ヘルスケア業界への関心
- セキュリティ・プライバシー意識
- REST API設計経験

【歓迎要件】
- 医療情報システムの開発経験
- HL7 FHIR/医療データ標準の知識
- 医療情報技師資格
- PHR/EHRシステムの経験

【求める役割】
ヘルスケアプラットフォーム開発メンバー

【年収】
600万円〜950万円
""",
    },
    {
        "title": "ゲームエンジニア（Unity）",
        "job_text_raw": """【募集職種】
ゲームエンジニア（Unity）

【業務内容】
- Unityを使用したゲーム開発
- ゲームロジックの実装
- パフォーマンス最適化
- マルチプラットフォーム対応

【必須要件】
- Unity開発経験3年以上
- C#プログラミング経験
- 3Dゲームまたは2Dゲームのリリース経験
- Git等のバージョン管理

【歓迎要件】
- コンシューマーゲーム開発経験
- シェーダープログラミング経験
- ネットワークゲームの開発経験
- 個人でのゲームリリース経験

【求める役割】
ゲーム開発チームのエンジニア

【年収】
500万円〜850万円
""",
    },
    {
        "title": "ゲームエンジニア（Unreal Engine）",
        "job_text_raw": """【募集職種】
ゲームエンジニア（Unreal Engine）

【業務内容】
- Unreal Engineを使用したゲーム開発
- C++でのゲームプレイ実装
- グラフィックス最適化
- AAA品質のゲーム開発

【必須要件】
- Unreal Engine開発経験2年以上
- C++プログラミング経験
- 3Dゲームの開発経験
- パフォーマンス最適化経験

【歓迎要件】
- コンシューマーゲームの出荷経験
- Blueprint活用経験
- レンダリングパイプラインの知識
- VR/AR開発経験

【求める役割】
大規模ゲーム開発のエンジニア

【年収】
600万円〜1000万円
""",
    },
    {
        "title": "AI/MLエンジニア（LLM特化）",
        "job_text_raw": """【募集職種】
AI/MLエンジニア（LLM特化）

【業務内容】
- 大規模言語モデル（LLM）の活用・チューニング
- RAG（Retrieval-Augmented Generation）システムの構築
- プロンプトエンジニアリング
- LLMアプリケーションの開発

【必須要件】
- Python開発経験3年以上
- LLM（GPT/Claude等）の活用経験
- LangChain/LlamaIndex等のフレームワーク経験
- ベクトルDB（Pinecone/Weaviate等）の経験

【歓迎要件】
- LLMのファインチューニング経験
- 自社LLMの開発・運用経験
- NLP/深層学習の専門知識
- 論文読解・実装能力

【求める役割】
LLMプロダクトの技術リード

【年収】
800万円〜1400万円
""",
    },
    {
        "title": "ブロックチェーンエンジニア",
        "job_text_raw": """【募集職種】
ブロックチェーンエンジニア

【業務内容】
- スマートコントラクトの開発
- DAppsのバックエンド開発
- ブロックチェーンインフラの構築
- セキュリティ監査対応

【必須要件】
- プログラミング経験3年以上
- Ethereum/Solidityの開発経験
- Web3.js/ethers.jsの経験
- 暗号技術の基礎知識

【歓迎要件】
- DeFi/NFTプロジェクトの経験
- セキュリティ監査の経験
- 複数チェーン（Polygon/Solana等）の経験
- スマートコントラクトの脆弱性診断経験

【求める役割】
Web3プロダクトの開発リード

【年収】
700万円〜1300万円
""",
    },
    {
        "title": "AR/VRエンジニア",
        "job_text_raw": """【募集職種】
AR/VRエンジニア

【業務内容】
- AR/VRアプリケーションの開発
- 3Dコンテンツの実装
- デバイス対応（Quest/Vision Pro等）
- UXの最適化

【必須要件】
- Unity or Unreal Engine経験2年以上
- AR/VR開発経験1年以上
- 3D数学（線形代数等）の理解
- C#またはC++経験

【歓迎要件】
- ARKit/ARCore経験
- Meta Quest開発経験
- Apple Vision Pro開発経験
- 空間コンピューティングへの関心

【求める役割】
XR開発チームのエンジニア

【年収】
600万円〜1000万円
""",
    },
    {
        "title": "自動運転エンジニア",
        "job_text_raw": """【募集職種】
自動運転エンジニア

【業務内容】
- 自動運転ソフトウェアの開発
- センサーフュージョン・認識処理
- 経路計画アルゴリズムの実装
- シミュレーション環境の構築

【必須要件】
- C++/Python開発経験3年以上
- 画像処理・点群処理の経験
- ROS/ROS2の経験
- 機械学習・深層学習の知識

【歓迎要件】
- 自動車業界での開発経験
- 自動運転プロジェクトの経験
- AUTOSAR/車載OS経験
- 機能安全（ISO 26262）の知識

【求める役割】
自動運転開発チームのエンジニア

【年収】
700万円〜1200万円
""",
    },
    {
        "title": "ロボティクスエンジニア",
        "job_text_raw": """【募集職種】
ロボティクスエンジニア

【業務内容】
- ロボットソフトウェアの開発
- モーションプランニングの実装
- センサー統合・制御システム開発
- ROS2ベースのシステム構築

【必須要件】
- C++/Python開発経験3年以上
- ROS/ROS2の実務経験
- ロボット工学の基礎知識
- Linux環境での開発経験

【歓迎要件】
- 産業用ロボットの開発経験
- 移動ロボット・マニピュレータの経験
- SLAM・Navigation経験
- 制御工学の専門知識

【求める役割】
ロボット開発チームのエンジニア

【年収】
600万円〜1000万円
""",
    },
    {
        "title": "宇宙開発エンジニア",
        "job_text_raw": """【募集職種】
宇宙開発エンジニア（ソフトウェア）

【業務内容】
- 人工衛星・探査機のソフトウェア開発
- 地上管制システムの開発
- ミッション計画ソフトウェア開発
- 高信頼性ソフトウェアの設計

【必須要件】
- C/C++開発経験3年以上
- 組み込みシステム開発経験
- 高信頼性システムの開発経験
- 宇宙開発への強い関心

【歓迎要件】
- 宇宙産業での開発経験
- RTOS経験
- 航空宇宙工学の知識
- ECSS/CCSDS標準の知識

【求める役割】
宇宙機ソフトウェア開発エンジニア

【年収】
600万円〜1100万円
""",
    },
]


# ==================================================
# 名前パターン（拡充版：100種類以上）
# ==================================================

# 日本人名（苗字）
JAPANESE_LAST_NAMES = [
    "田中", "鈴木", "佐藤", "山田", "高橋", "伊藤", "渡辺", "中村", "小林", "加藤",
    "吉田", "山口", "松本", "井上", "木村", "林", "斎藤", "清水", "山崎", "森",
    "池田", "橋本", "阿部", "石川", "前田", "藤田", "小川", "岡田", "後藤", "長谷川",
    "石井", "村上", "近藤", "坂本", "遠藤", "青木", "藤井", "西村", "福田", "太田",
    "三浦", "藤原", "岡本", "松田", "中川", "中野", "原田", "小野", "田村", "竹内",
    "金子", "和田", "中山", "石田", "上田", "森田", "原", "柴田", "酒井", "工藤",
    "横山", "宮崎", "宮本", "内田", "高木", "安藤", "島田", "谷口", "大野", "丸山",
    "今井", "河野", "藤本", "村田", "武田", "上野", "杉山", "増田", "小山", "大塚",
    "平野", "菅原", "久保", "松井", "野口", "千葉", "岩崎", "桜井", "木下", "野村",
]

# 日本人名（名前：男性）
JAPANESE_FIRST_NAMES_MALE = [
    "太郎", "次郎", "健一", "雄大", "直樹", "翔太", "大輔", "一郎", "誠", "隆",
    "拓也", "和也", "浩二", "雅人", "亮", "康介", "俊介", "大地", "祐介", "慎也",
    "翔", "颯太", "蓮", "大翔", "陽翔", "悠真", "湊", "樹", "悠斗", "朝陽",
    "健太", "龍一", "真一", "浩", "学", "剛", "修", "徹", "聡", "豊",
    "哲也", "達也", "賢一", "正樹", "秀樹", "光男", "博之", "英樹", "雄一", "勝",
]

# 日本人名（名前：女性）
JAPANESE_FIRST_NAMES_FEMALE = [
    "花子", "美咲", "愛", "恵", "智子", "由美", "真理子", "さくら", "優子", "陽子",
    "彩", "里奈", "菜々子", "沙織", "真由美", "裕子", "麻衣", "美穂", "葵", "結衣",
    "凛", "陽菜", "芽依", "紬", "咲良", "莉子", "結月", "美月", "心春", "杏",
    "恵美", "真美", "久美子", "洋子", "京子", "良子", "和子", "美和", "理恵", "香織",
    "明美", "幸子", "典子", "尚子", "文子", "雅子", "純子", "絵里", "奈美", "瞳",
]

# 外国人名（英語圏）
ENGLISH_FIRST_NAMES = [
    "James", "John", "Robert", "Michael", "David", "William", "Richard", "Joseph", "Thomas", "Christopher",
    "Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", "Jessica", "Sarah", "Karen",
    "Daniel", "Matthew", "Anthony", "Mark", "Donald", "Steven", "Paul", "Andrew", "Joshua", "Kenneth",
    "Emily", "Emma", "Olivia", "Ava", "Isabella", "Sophia", "Charlotte", "Mia", "Amelia", "Harper",
]

ENGLISH_LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez",
    "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
    "Lee", "Thompson", "White", "Harris", "Clark", "Lewis", "Robinson", "Walker", "Hall", "Allen",
]

# 外国人名（中国語圏）
CHINESE_NAMES = [
    "王偉", "李娜", "張強", "劉洋", "陳靜", "楊敏", "趙軍", "黄芳", "周杰", "吴秀英",
    "徐明", "孫麗", "胡勇", "朱艶", "高峰", "林琳", "何健", "郭雪", "馬超", "羅蘭",
]

# 外国人名（韓国語圏）
KOREAN_NAMES = [
    "김민준", "이서연", "박지훈", "최유진", "정현우", "강수빈", "조민서", "윤서현", "장준혁", "임하은",
    "한승민", "오지아", "서동현", "신예은", "권태호", "황미래", "안성훈", "송지원", "전민호", "홍서윤",
]


# ==================================================
# スキルセット定義（拡充版）
# ==================================================
SKILL_SETS = {
    "python_backend": {
        "skills": ["Python", "FastAPI", "Django", "Flask", "MySQL", "PostgreSQL", "Redis", "Docker", "Git", "AWS", "GCP"],
        "must_skills": ["Python", "Git"],
        "roles": ["IC", "Lead"],
    },
    "react_frontend": {
        "skills": ["React", "TypeScript", "JavaScript", "HTML", "CSS", "Next.js", "GraphQL", "REST API", "Figma", "Jest"],
        "must_skills": ["React", "TypeScript", "JavaScript"],
        "roles": ["IC", "Lead"],
    },
    "sre": {
        "skills": ["AWS", "GCP", "Azure", "Linux", "Terraform", "Kubernetes", "Docker", "Prometheus", "Grafana", "Ansible"],
        "must_skills": ["AWS", "Linux", "Docker"],
        "roles": ["IC", "Lead"],
    },
    "data_engineer": {
        "skills": ["Python", "SQL", "BigQuery", "Redshift", "Snowflake", "Spark", "Airflow", "dbt", "Kafka", "AWS"],
        "must_skills": ["SQL", "Python"],
        "roles": ["IC", "Lead"],
    },
    "ml_engineer": {
        "skills": ["Python", "TensorFlow", "PyTorch", "scikit-learn", "Pandas", "NumPy", "Kubeflow", "MLflow", "SQL", "AWS"],
        "must_skills": ["Python", "TensorFlow", "PyTorch"],
        "roles": ["IC", "Lead"],
    },
    "ios": {
        "skills": ["Swift", "UIKit", "SwiftUI", "Objective-C", "Xcode", "Combine", "RxSwift", "Core Data", "Git"],
        "must_skills": ["Swift", "UIKit"],
        "roles": ["IC", "Lead"],
    },
    "android": {
        "skills": ["Kotlin", "Java", "Jetpack Compose", "Android SDK", "Room", "Coroutines", "Dagger", "Git"],
        "must_skills": ["Kotlin", "Android SDK"],
        "roles": ["IC", "Lead"],
    },
    "qa": {
        "skills": ["Selenium", "Cypress", "Jest", "JUnit", "Postman", "JMeter", "SQL", "Python", "Git"],
        "must_skills": ["Selenium", "Cypress"],
        "roles": ["IC", "Lead"],
    },
    "security": {
        "skills": ["Burp Suite", "OWASP", "Nmap", "Wireshark", "Python", "Linux", "AWS", "Docker", "Git"],
        "must_skills": ["Burp Suite", "Linux"],
        "roles": ["IC", "Lead"],
    },
    "devops": {
        "skills": ["Docker", "Kubernetes", "GitHub Actions", "Jenkins", "Terraform", "Ansible", "AWS", "Linux", "Python", "Git"],
        "must_skills": ["Docker", "Kubernetes", "Git"],
        "roles": ["IC", "Lead"],
    },
    "go_backend": {
        "skills": ["Go", "gRPC", "REST API", "MySQL", "PostgreSQL", "Redis", "Docker", "Kubernetes", "Git", "AWS"],
        "must_skills": ["Go", "Git"],
        "roles": ["IC", "Lead"],
    },
    "fullstack": {
        "skills": ["React", "TypeScript", "Node.js", "Python", "Go", "PostgreSQL", "Redis", "Docker", "AWS", "Git"],
        "must_skills": ["React", "TypeScript", "Git"],
        "roles": ["IC", "Lead"],
    },
    # 新規追加スキルセット
    "junior_web": {
        "skills": ["JavaScript", "HTML", "CSS", "React", "Git", "REST API"],
        "must_skills": ["JavaScript", "HTML", "CSS"],
        "roles": ["IC"],
    },
    "junior_qa": {
        "skills": ["Selenium", "Postman", "Jira", "SQL", "Python"],
        "must_skills": ["Selenium", "Postman"],
        "roles": ["IC"],
    },
    "data_analyst": {
        "skills": ["SQL", "Python", "Excel", "Tableau", "BigQuery", "Pandas"],
        "must_skills": ["SQL", "Excel"],
        "roles": ["IC"],
    },
    "management": {
        "skills": ["Scrum", "Agile", "JIRA", "Confluence", "1on1", "OKR", "採用面接", "評価制度"],
        "must_skills": ["Scrum", "Agile"],
        "roles": ["Lead", "Manager"],
    },
    "vp_engineering": {
        "skills": ["組織設計", "予算管理", "採用戦略", "技術戦略", "経営会議", "OKR", "評価制度", "1on1"],
        "must_skills": ["組織設計", "採用戦略"],
        "roles": ["Manager", "Executive"],
    },
    "architect": {
        "skills": ["システム設計", "マイクロサービス", "DDD", "AWS", "GCP", "Kubernetes", "API設計", "技術負債解消"],
        "must_skills": ["システム設計", "マイクロサービス"],
        "roles": ["Lead", "Architect"],
    },
    "startup_generalist": {
        "skills": ["React", "Node.js", "Python", "AWS", "Docker", "PostgreSQL", "Git", "Agile"],
        "must_skills": ["React", "Node.js", "Git"],
        "roles": ["IC", "Lead"],
    },
    "unity": {
        "skills": ["Unity", "C#", "3D数学", "シェーダー", "Git", "iOS", "Android"],
        "must_skills": ["Unity", "C#"],
        "roles": ["IC", "Lead"],
    },
    "unreal": {
        "skills": ["Unreal Engine", "C++", "Blueprint", "3D数学", "シェーダー", "Git"],
        "must_skills": ["Unreal Engine", "C++"],
        "roles": ["IC", "Lead"],
    },
    "llm_engineer": {
        "skills": ["Python", "LangChain", "LlamaIndex", "OpenAI API", "Claude API", "Pinecone", "Weaviate", "RAG", "プロンプトエンジニアリング"],
        "must_skills": ["Python", "LangChain", "RAG"],
        "roles": ["IC", "Lead"],
    },
    "blockchain": {
        "skills": ["Solidity", "Ethereum", "Web3.js", "ethers.js", "Hardhat", "Smart Contract", "DeFi", "NFT"],
        "must_skills": ["Solidity", "Ethereum"],
        "roles": ["IC", "Lead"],
    },
    "ar_vr": {
        "skills": ["Unity", "Unreal Engine", "ARKit", "ARCore", "OpenXR", "C#", "C++", "3D数学"],
        "must_skills": ["Unity", "ARKit"],
        "roles": ["IC", "Lead"],
    },
    "autonomous_driving": {
        "skills": ["C++", "Python", "ROS", "ROS2", "センサーフュージョン", "SLAM", "深層学習", "画像処理"],
        "must_skills": ["C++", "ROS", "Python"],
        "roles": ["IC", "Lead"],
    },
    "robotics": {
        "skills": ["C++", "Python", "ROS", "ROS2", "制御工学", "SLAM", "モーションプランニング", "Linux"],
        "must_skills": ["C++", "ROS", "Python"],
        "roles": ["IC", "Lead"],
    },
    "space": {
        "skills": ["C", "C++", "RTOS", "組み込み", "高信頼性設計", "ECSS", "CCSDS", "Python"],
        "must_skills": ["C", "C++", "RTOS"],
        "roles": ["IC", "Lead"],
    },
    "fintech": {
        "skills": ["Java", "Python", "Go", "PostgreSQL", "Redis", "セキュリティ", "決済システム", "AWS"],
        "must_skills": ["Java", "PostgreSQL", "セキュリティ"],
        "roles": ["IC", "Lead"],
    },
    "healthcare": {
        "skills": ["Python", "Java", "HL7 FHIR", "REST API", "セキュリティ", "AWS", "PostgreSQL"],
        "must_skills": ["Python", "REST API"],
        "roles": ["IC", "Lead"],
    },
    "global_engineer": {
        "skills": ["Java", "Go", "Python", "AWS", "Kubernetes", "Microservices", "English", "Git"],
        "must_skills": ["Java", "Go", "English"],
        "roles": ["IC", "Lead"],
    },
    "bilingual_em": {
        "skills": ["English", "Japanese", "Scrum", "Agile", "1on1", "採用面接", "評価制度", "プロジェクト管理"],
        "must_skills": ["English", "Japanese", "Scrum"],
        "roles": ["Lead", "Manager"],
    },
}

# ==================================================
# ジョブとスキルセットのマッピング（50件）
# ==================================================
JOB_SKILL_MAPPING = {
    # 既存（0-14）
    0: "python_backend",    # シニアPythonエンジニア
    1: "react_frontend",    # フロントエンドエンジニア（React）
    2: "sre",               # インフラエンジニア（SRE）
    3: "data_engineer",     # データエンジニア
    4: "ml_engineer",       # 機械学習エンジニア
    5: "ios",               # iOSエンジニア
    6: "android",           # Androidエンジニア
    7: "qa",                # QAエンジニア
    8: "security",          # セキュリティエンジニア
    9: "python_backend",    # プロダクトマネージャー
    10: "python_backend",   # テックリード（バックエンド）
    11: "devops",           # DevOpsエンジニア
    12: "go_backend",       # Goエンジニア
    13: "react_frontend",   # UI/UXデザイナー
    14: "fullstack",        # フルスタックエンジニア
    # 新卒・ジュニア向け（15-19）
    15: "junior_web",       # 新卒Webエンジニア
    16: "react_frontend",   # ジュニアフロントエンドエンジニア
    17: "data_analyst",     # 新卒データアナリスト
    18: "junior_qa",        # ジュニアQAエンジニア
    19: "junior_web",       # エンジニアインターン
    # リモートワーク特化（20-24）
    20: "python_backend",   # フルリモートバックエンドエンジニア
    21: "sre",              # リモートワークSREエンジニア
    22: "fullstack",        # フルリモートフルスタックエンジニア
    23: "react_frontend",   # 海外在住可フロントエンドエンジニア
    24: "sre",              # ワーケーション可能インフラエンジニア
    # マネージャー・ディレクター職（25-29）
    25: "management",       # エンジニアリングマネージャー
    26: "vp_engineering",   # VPoE
    27: "management",       # プロダクト開発部長
    28: "architect",        # CTOアシスタント
    29: "architect",        # テックリード（アーキテクト）
    # スタートアップ向け（30-34）
    30: "architect",        # スタートアップCTO候補
    31: "startup_generalist",  # 創業期エンジニア
    32: "management",       # シードステージPM
    33: "fullstack",        # 成長期テックリード
    34: "sre",              # スタートアップSRE
    # 外資系企業向け（35-39）
    35: "global_engineer",  # Senior Software Engineer (Global)
    36: "sre",              # Site Reliability Engineer (English Required)
    37: "architect",        # Staff Engineer (Silicon Valley Style)
    38: "bilingual_em",     # Engineering Manager (Bilingual)
    39: "architect",        # Principal Engineer
    # 業界特化（40-49）
    40: "fintech",          # フィンテックエンジニア
    41: "healthcare",       # ヘルスケアITエンジニア
    42: "unity",            # ゲームエンジニア（Unity）
    43: "unreal",           # ゲームエンジニア（Unreal Engine）
    44: "llm_engineer",     # AI/MLエンジニア（LLM特化）
    45: "blockchain",       # ブロックチェーンエンジニア
    46: "ar_vr",            # AR/VRエンジニア
    47: "autonomous_driving",  # 自動運転エンジニア
    48: "robotics",         # ロボティクスエンジニア
    49: "space",            # 宇宙開発エンジニア
}


# ==================================================
# キャリアパターン定義
# ==================================================
CAREER_PATTERNS = [
    {
        "type": "standard",
        "name": "正社員一筋",
        "description": "一社または少数の会社で正社員として勤務",
        "weight": 30,
    },
    {
        "type": "job_hopper",
        "name": "転職経験複数",
        "description": "2-5社での転職経験あり",
        "weight": 25,
    },
    {
        "type": "freelance",
        "name": "フリーランス経験",
        "description": "フリーランスまたは業務委託での勤務経験",
        "weight": 15,
    },
    {
        "type": "side_job",
        "name": "副業経験者",
        "description": "本業と並行して副業経験あり",
        "weight": 10,
    },
    {
        "type": "gap",
        "name": "ブランクあり",
        "description": "育児・介護・留学などでブランク期間あり",
        "weight": 8,
    },
    {
        "type": "career_change",
        "name": "未経験からの転向",
        "description": "異業種・異職種からの転向",
        "weight": 7,
    },
    {
        "type": "overseas",
        "name": "海外経験あり",
        "description": "海外での就業または留学経験",
        "weight": 5,
    },
]

# ==================================================
# 学歴パターン定義
# ==================================================
EDUCATION_PATTERNS = [
    {
        "type": "cs_major",
        "name": "情報系学部卒",
        "universities": ["東京大学", "京都大学", "東京工業大学", "大阪大学", "筑波大学", "早稲田大学", "慶應義塾大学", "電気通信大学"],
        "weight": 30,
    },
    {
        "type": "non_cs",
        "name": "非情報系学部卒",
        "universities": ["東京大学", "京都大学", "一橋大学", "慶應義塾大学", "早稲田大学", "上智大学", "明治大学", "青山学院大学"],
        "weight": 25,
    },
    {
        "type": "graduate",
        "name": "大学院卒",
        "universities": ["東京大学大学院", "京都大学大学院", "東京工業大学大学院", "NAIST", "JAIST"],
        "weight": 15,
    },
    {
        "type": "kosen",
        "name": "高専卒",
        "universities": ["東京高専", "大阪高専", "沼津高専", "鈴鹿高専", "明石高専"],
        "weight": 10,
    },
    {
        "type": "vocational",
        "name": "専門学校卒",
        "universities": ["HAL東京", "デジタルハリウッド", "バンタン", "ECCコンピュータ"],
        "weight": 10,
    },
    {
        "type": "self_taught",
        "name": "独学・ブートキャンプ",
        "universities": ["独学", "Codecamp", "テックキャンプ", "DMM WEBCAMP", "RUNTEQ"],
        "weight": 10,
    },
]


def get_random_name(include_foreign: bool = True) -> tuple:
    """ランダムな名前を生成。(display_name, name_type)を返す"""
    if include_foreign and random.random() < 0.15:  # 15%の確率で外国人名
        name_type = random.choice(["english", "chinese", "korean"])
        if name_type == "english":
            first = random.choice(ENGLISH_FIRST_NAMES)
            last = random.choice(ENGLISH_LAST_NAMES)
            return f"{first} {last}", "english"
        elif name_type == "chinese":
            return random.choice(CHINESE_NAMES), "chinese"
        else:  # korean
            return random.choice(KOREAN_NAMES), "korean"
    else:
        last = random.choice(JAPANESE_LAST_NAMES)
        if random.random() < 0.5:
            first = random.choice(JAPANESE_FIRST_NAMES_MALE)
        else:
            first = random.choice(JAPANESE_FIRST_NAMES_FEMALE)
        return f"{last} {first}", "japanese"


def get_random_career() -> dict:
    """ランダムなキャリアパターンを選択"""
    weights = [p["weight"] for p in CAREER_PATTERNS]
    return random.choices(CAREER_PATTERNS, weights=weights)[0]


def get_random_education() -> dict:
    """ランダムな学歴パターンを選択"""
    weights = [p["weight"] for p in EDUCATION_PATTERNS]
    pattern = random.choices(EDUCATION_PATTERNS, weights=weights)[0]
    return {
        **pattern,
        "university": random.choice(pattern["universities"]),
    }


def generate_candidate(job_index: int, quality: str) -> dict:
    """
    候補者データを生成する

    quality:
    - "excellent": 優秀な候補者（スコア85-100）
    - "good": 良い候補者（スコア60-84）
    - "average": 平均的な候補者（スコア40-59）
    - "poor": 不適合な候補者（スコア15-39）
    """
    skill_type = JOB_SKILL_MAPPING.get(job_index, "python_backend")
    skill_set = SKILL_SETS[skill_type]

    # 名前生成
    display_name, name_type = get_random_name(include_foreign=True)

    # キャリア・学歴パターン
    career = get_random_career()
    education = get_random_education()

    # 経験年数のレンジ（品質と求人タイプに応じて調整）
    is_junior_position = job_index in [15, 16, 17, 18, 19]  # 新卒・ジュニア求人

    if is_junior_position:
        # 新卒・ジュニア向け求人の場合
        if quality == "excellent":
            experience_base = random.randint(0, 2)
        elif quality == "good":
            experience_base = random.randint(0, 1)
        elif quality == "average":
            experience_base = random.randint(0, 1)
        else:
            experience_base = 0
    else:
        # 通常の求人
        if quality == "excellent":
            # シニア・マネージャー求人かどうかで調整
            is_senior = job_index in [0, 2, 4, 8, 10, 25, 26, 27, 28, 29, 30, 35, 37, 38, 39]
            if is_senior:
                experience_base = random.randint(8, 15)
            else:
                experience_base = random.randint(5, 10)
        elif quality == "good":
            experience_base = random.randint(3, 7)
        elif quality == "average":
            experience_base = random.randint(2, 4)
        else:  # poor
            experience_base = random.randint(0, 2)

    # スキルと経験年数を品質に応じて生成
    if quality == "excellent":
        num_skills = random.randint(7, 10)
        must_score = random.uniform(0.95, 1.0)
        nice_score = random.uniform(0.75, 0.95)
        role_match = True
        total_score = random.randint(85, 100)
        concerns = []
        must_gaps = []
    elif quality == "good":
        num_skills = random.randint(5, 8)
        must_score = random.uniform(0.8, 0.95)
        nice_score = random.uniform(0.5, 0.75)
        role_match = random.choice([True, True, False])
        total_score = random.randint(60, 84)
        concerns = random.sample(["経験年数が若干不足", "マネジメント経験なし", "特定領域の経験が浅い"], k=random.randint(0, 1))
        must_gaps = []
    elif quality == "average":
        num_skills = random.randint(4, 6)
        must_score = random.uniform(0.6, 0.8)
        nice_score = random.uniform(0.3, 0.5)
        role_match = random.choice([True, False])
        total_score = random.randint(40, 59)
        concerns = random.sample(["経験年数不足", "必須スキル一部不足", "異なる領域からの転向", "チーム開発経験が少ない"], k=random.randint(1, 2))
        must_gaps = random.sample(["必須要件の一部が不足"], k=random.randint(0, 1))
    else:  # poor
        num_skills = random.randint(2, 4)
        must_score = random.uniform(0.3, 0.6)
        nice_score = random.uniform(0.1, 0.3)
        role_match = False
        total_score = random.randint(15, 39)
        concerns = ["経験年数が大幅に不足", "必須スキル不足", "求める役割とのミスマッチ"]
        must_gaps = ["必須要件を満たしていない"]

    # スキル選択
    available_skills = skill_set["skills"]
    must_skills = skill_set["must_skills"]

    if quality in ["excellent", "good"]:
        skills = must_skills.copy()
        remaining = [s for s in available_skills if s not in skills]
        skills.extend(random.sample(remaining, min(num_skills - len(skills), len(remaining))))
    else:
        # 不適合な候補者は必須スキルの一部しか持っていない
        skills = random.sample(must_skills, min(len(must_skills) - 1, max(1, random.randint(1, 2))))
        remaining = [s for s in available_skills if s not in skills]
        skills.extend(random.sample(remaining, min(num_skills - len(skills), len(remaining))))

    # 役割
    available_roles = skill_set["roles"]
    if quality == "excellent":
        roles = available_roles.copy()
        if "Manager" not in roles and random.random() > 0.5:
            roles.append("Manager")
    elif quality == "good":
        roles = ["Lead", "IC"] if "Lead" in available_roles and role_match else ["IC"]
    else:
        roles = ["IC"]

    # 経験年数
    primary_skill = skills[0] if skills else "Python"
    experience_years = {primary_skill: experience_base}
    if len(skills) > 1:
        experience_years[skills[1]] = max(1, experience_base - random.randint(1, 3))

    # キャリアパターンに応じた追加情報
    career_highlights = []
    if career["type"] == "freelance":
        career_highlights.append("フリーランス経験あり（複数プロジェクト参画）")
    elif career["type"] == "overseas":
        career_highlights.append("海外での就業経験あり")
    elif career["type"] == "side_job":
        career_highlights.append("副業で複数のプロジェクトに参画")
    elif career["type"] == "career_change":
        career_highlights.append("異業種からのキャリアチェンジ")
        if quality not in ["excellent", "good"]:
            concerns.append("前職とのギャップ")

    # ハイライト生成
    highlights = []
    if quality == "excellent":
        highlights = [
            f"{primary_skill} {experience_base}年以上の豊富な経験",
            "大規模プロジェクトでのリード経験",
            "チーム管理・育成経験あり",
        ]
        if education["type"] in ["cs_major", "graduate"]:
            highlights.append(f"{education['university']}卒の専門知識")
    elif quality == "good":
        highlights = [
            f"{primary_skill} {experience_base}年の実務経験",
            "複数プロジェクトでの開発経験",
        ]
    elif quality == "average":
        highlights = [
            f"{primary_skill}の基礎的な経験",
            "学習意欲が高い",
        ]
    else:
        highlights = [
            "新しい分野への挑戦意欲",
        ]

    highlights.extend(career_highlights)

    # サマリ生成
    if quality == "excellent":
        summary = f"{primary_skill}を中心に{experience_base}年以上の豊富な経験を持つ優秀な候補者。{education['university']}出身。必須要件をすべて満たしており、即戦力として期待できます。"
    elif quality == "good":
        summary = f"{primary_skill}の経験が{experience_base}年あり、基本的な要件を満たしている候補者。{career['name']}。さらなる成長が期待できます。"
    elif quality == "average":
        summary = f"{primary_skill}の経験はあるものの、要件との適合度は中程度。{education['name']}。ポテンシャル採用として検討の余地あり。"
    else:
        summary = f"必須要件との適合度が低く、現時点では求める人材像とのギャップがある候補者。"

    # 強み
    strengths = [f"{primary_skill}の実務経験"] + highlights[:2]

    return {
        "job_index": job_index,
        "display_name": display_name,
        "name_type": name_type,
        "career_type": career["type"],
        "education_type": education["type"],
        "extraction": {
            "job_requirements": {
                "must": [
                    {"id": f"m{i+1}", "text": f"必須要件{i+1}", "skill_tags": must_skills[:i+1]}
                    for i in range(min(4, len(must_skills)))
                ],
                "nice": [
                    {"id": f"n{i+1}", "text": f"歓迎要件{i+1}", "skill_tags": [available_skills[i] if i < len(available_skills) else "その他"]}
                    for i in range(3)
                ],
                "role_expectation": "Lead" if job_index in [0, 2, 4, 8, 10, 25, 26, 27, 28, 29, 30] else "IC",
                "year_requirements": {primary_skill: 3 if not is_junior_position else 0},
            },
            "candidate_profile": {
                "skills": skills,
                "roles": roles,
                "experience_years": experience_years,
                "highlights": highlights,
                "concerns": concerns,
                "unknowns": [] if quality in ["excellent", "good"] else ["詳細な経験"],
                "education": education["university"],
                "career_pattern": career["name"],
            },
            "evidence": {
                "job": {"must:m1": "必須要件1"},
                "candidate": {"skill:" + primary_skill: f"{primary_skill}歴{experience_base}年"},
            },
        },
        "score": {
            "must_score": round(must_score, 2),
            "nice_score": round(nice_score, 2),
            "year_score": round(min(1.0, experience_base / 5) if not is_junior_position else 1.0, 2),
            "role_score": 1.0 if role_match else 0.7,
            "total_fit_0_100": total_score,
            "must_gaps": must_gaps,
        },
        "explanation": {
            "summary": summary,
            "strengths": strengths,
            "concerns": concerns,
            "unknowns": [] if quality in ["excellent", "good"] else ["詳細不明な点あり"],
            "must_gaps": must_gaps,
        },
    }


def generate_all_candidates() -> list:
    """全候補者データを生成（500-700名）"""
    candidates = []

    # 品質分布（計画に従う）
    # excellent: 10%, good: 30%, average: 40%, poor: 20%

    # 各求人に対して候補者を生成（各求人10-15名）
    for job_index in range(len(SAMPLE_JOBS)):
        # 各求人の候補者数（10-15名）
        total_per_job = random.randint(10, 15)

        # 品質分布に従って各品質の候補者数を計算
        num_excellent = max(1, int(total_per_job * 0.10))  # 10%
        num_good = int(total_per_job * 0.30)               # 30%
        num_poor = int(total_per_job * 0.20)               # 20%
        num_average = total_per_job - num_excellent - num_good - num_poor  # 残り（約40%）

        for _ in range(num_excellent):
            candidates.append(generate_candidate(job_index, "excellent"))
        for _ in range(num_good):
            candidates.append(generate_candidate(job_index, "good"))
        for _ in range(num_average):
            candidates.append(generate_candidate(job_index, "average"))
        for _ in range(num_poor):
            candidates.append(generate_candidate(job_index, "poor"))

    return candidates


# ==================================================
# ステータス分布（計画に従う）
# DONE: 60%, PROCESSING: 20%, NEW: 15%, ERROR: 5%
# ==================================================
def get_random_status() -> str:
    """計画に従ったステータス分布でステータスを返す"""
    return random.choices(
        ["DONE", "PROCESSING", "NEW", "ERROR"],
        weights=[60, 20, 15, 5]
    )[0]


async def seed_data():
    """サンプルデータを作成"""
    async with AsyncSessionLocal() as session:
        # スコア設定の確認・作成
        print("\n=== スコア設定確認 ===")
        result = await session.execute(text("SELECT version FROM score_config ORDER BY version DESC LIMIT 1"))
        row = result.fetchone()
        if row:
            score_config_version = row[0]
            print(f"  既存のスコア設定を使用: version {score_config_version}")
        else:
            # デフォルトのスコア設定を作成
            default_weights = {"must": 0.45, "nice": 0.20, "year": 0.20, "role": 0.15}
            default_role_distance = {
                "IC": {"IC": 1.0, "Lead": 0.7, "Manager": 0.5},
                "Lead": {"IC": 0.7, "Lead": 1.0, "Manager": 0.8},
                "Manager": {"IC": 0.5, "Lead": 0.8, "Manager": 1.0},
            }
            await session.execute(
                text("""
                    INSERT INTO score_config (version, weights_json, must_cap_enabled, must_cap_value, nice_top_n, role_distance_json, created_at)
                    VALUES (1, :weights_json, TRUE, 20, 3, :role_distance_json, NOW())
                """),
                {
                    "weights_json": json.dumps(default_weights),
                    "role_distance_json": json.dumps(default_role_distance),
                },
            )
            score_config_version = 1
            print("  デフォルトのスコア設定を作成: version 1")

        # 既存データの確認
        result = await session.execute(text("SELECT COUNT(*) as cnt FROM jobs"))
        row = result.fetchone()
        if row and row[0] > 0:
            print(f"\n既存のデータがあります（{row[0]}件の求人）。追加します...")

        job_ids = []

        # 求人データ作成
        print("\n=== 求人データ作成 ===")
        for job_data in SAMPLE_JOBS:
            job_id = str(uuid.uuid4())
            job_ids.append(job_id)

            await session.execute(
                text("""
                    INSERT INTO jobs (job_id, title, job_text_raw, created_at, updated_at)
                    VALUES (:job_id, :title, :job_text_raw, NOW(), NOW())
                """),
                {"job_id": job_id, "title": job_data["title"], "job_text_raw": job_data["job_text_raw"]},
            )
            print(f"  作成: {job_data['title']} (ID: {job_id[:8]}...)")

        print(f"\n  合計 {len(SAMPLE_JOBS)} 件の求人を作成")

        # 応募者データ生成
        print("\n=== 応募者データ生成中 ===")
        all_candidates = generate_all_candidates()
        print(f"  {len(all_candidates)}名の応募者データを生成")

        # 応募者データ作成
        print("\n=== 応募者データ作成 ===")
        decisions_made = []

        # ステータスごとのカウント
        status_counts_generated = {"DONE": 0, "PROCESSING": 0, "NEW": 0, "ERROR": 0}

        for i, candidate_data in enumerate(all_candidates):
            job_id = job_ids[candidate_data["job_index"]]
            candidate_id = str(uuid.uuid4())

            # ステータスをランダムに設定（新しい分布に従う）
            status = get_random_status()
            status_counts_generated[status] += 1

            # 提出日時をランダムに設定（過去60日以内）
            days_ago = random.randint(0, 60)
            submitted_at = datetime.now() - timedelta(days=days_ago, hours=random.randint(0, 23))

            # 応募者
            await session.execute(
                text("""
                    INSERT INTO candidates (candidate_id, job_id, display_name, status, submitted_at)
                    VALUES (:candidate_id, :job_id, :display_name, :status, :submitted_at)
                """),
                {
                    "candidate_id": candidate_id,
                    "job_id": job_id,
                    "display_name": candidate_data["display_name"],
                    "status": status,
                    "submitted_at": submitted_at,
                },
            )

            # DONE ステータスの場合のみ、詳細データを追加
            if status == "DONE":
                # 抽出結果
                extraction = candidate_data["extraction"]
                await session.execute(
                    text("""
                        INSERT INTO extractions (candidate_id, job_requirements_json, candidate_profile_json, evidence_json, llm_model, extract_version, created_at)
                        VALUES (:candidate_id, :job_requirements_json, :candidate_profile_json, :evidence_json, 'sample', 'v1', NOW())
                    """),
                    {
                        "candidate_id": candidate_id,
                        "job_requirements_json": json.dumps(extraction["job_requirements"], ensure_ascii=False),
                        "candidate_profile_json": json.dumps(extraction["candidate_profile"], ensure_ascii=False),
                        "evidence_json": json.dumps(extraction["evidence"], ensure_ascii=False),
                    },
                )

                # スコア
                score = candidate_data["score"]
                await session.execute(
                    text("""
                        INSERT INTO scores (candidate_id, must_score, nice_score, year_score, role_score, total_fit_0_100, must_gaps_json, score_config_version, computed_at)
                        VALUES (:candidate_id, :must_score, :nice_score, :year_score, :role_score, :total_fit_0_100, :must_gaps_json, :score_config_version, NOW())
                    """),
                    {
                        "candidate_id": candidate_id,
                        "must_score": score["must_score"],
                        "nice_score": score["nice_score"],
                        "year_score": score["year_score"],
                        "role_score": score["role_score"],
                        "total_fit_0_100": score["total_fit_0_100"],
                        "must_gaps_json": json.dumps(score["must_gaps"], ensure_ascii=False),
                        "score_config_version": score_config_version,
                    },
                )

                # 説明
                explanation = candidate_data["explanation"]
                await session.execute(
                    text("""
                        INSERT INTO explanations (candidate_id, explanation_json, created_at)
                        VALUES (:candidate_id, :explanation_json, NOW())
                    """),
                    {
                        "candidate_id": candidate_id,
                        "explanation_json": json.dumps(explanation, ensure_ascii=False),
                    },
                )

                # 意思決定パターン（計画に従って約50%は未判定）
                # 判定済みの50%の中での分布
                if random.random() < 0.5:  # 50%は判定済み
                    total_score = score["total_fit_0_100"]
                    if total_score >= 80:
                        # 優秀候補は即pass傾向
                        decision = random.choices(["pass", "hold"], weights=[0.75, 0.25])[0]
                    elif total_score >= 60:
                        # 良い候補は検討後
                        decision = random.choices(["pass", "hold", "reject"], weights=[0.4, 0.4, 0.2])[0]
                    elif total_score >= 40:
                        # 平均的な候補
                        decision = random.choices(["pass", "hold", "reject"], weights=[0.2, 0.4, 0.4])[0]
                    else:
                        # 低スコアはreject傾向
                        decision = random.choices(["hold", "reject"], weights=[0.2, 0.8])[0]

                    decisions_made.append({
                        "candidate_id": candidate_id,
                        "decision": decision,
                    })

            if (i + 1) % 50 == 0:
                print(f"  {i + 1}/{len(all_candidates)} 名作成完了...")

        # 意思決定データ作成
        print(f"\n=== 意思決定データ作成 ({len(decisions_made)}件) ===")
        for decision_data in decisions_made:
            decision_id = str(uuid.uuid4())
            decided_at = datetime.now() - timedelta(days=random.randint(0, 14), hours=random.randint(0, 23))

            # 理由のバリエーション
            if decision_data["decision"] == "pass":
                reasons = [
                    "要件を満たしており、面談希望",
                    "スキルセットが合致、次のステップへ",
                    "経験豊富で即戦力として期待",
                    "技術力が高く、チームへの貢献が期待できる",
                ]
            elif decision_data["decision"] == "hold":
                reasons = [
                    "追加情報を確認後に判断",
                    "他候補者との比較検討中",
                    "スキルは良いが経験年数が若干不足",
                    "ポテンシャルはあるが慎重に検討",
                ]
            else:  # reject
                reasons = [
                    "要件との適合度が低い",
                    "必須スキルが不足",
                    "求める経験レベルに達していない",
                    "他の候補者を優先",
                ]

            await session.execute(
                text("""
                    INSERT INTO decisions (decision_id, candidate_id, decision, reason, decided_by, decided_at)
                    VALUES (:decision_id, :candidate_id, :decision, :reason, :decided_by, :decided_at)
                """),
                {
                    "decision_id": decision_id,
                    "candidate_id": decision_data["candidate_id"],
                    "decision": decision_data["decision"],
                    "reason": random.choice(reasons),
                    "decided_by": random.choice(["recruiter_a", "recruiter_b", "hiring_manager", "tech_lead"]),
                    "decided_at": decided_at,
                },
            )

        await session.commit()

        # 統計情報の表示
        result = await session.execute(text("SELECT COUNT(*) FROM candidates"))
        total_candidates = result.scalar()

        result = await session.execute(text("SELECT status, COUNT(*) FROM candidates GROUP BY status"))
        status_counts = {row[0]: row[1] for row in result.fetchall()}

        result = await session.execute(text("SELECT COUNT(*) FROM decisions"))
        total_decisions = result.scalar()

        result = await session.execute(text("SELECT decision, COUNT(*) FROM decisions GROUP BY decision"))
        decision_counts = {row[0]: row[1] for row in result.fetchall()}

        print("\n" + "=" * 50)
        print("=== 完了 ===")
        print("=" * 50)
        print(f"\n【求人】 {len(SAMPLE_JOBS)}件")
        print(f"\n【応募者】 {total_candidates}名")
        print(f"  - DONE: {status_counts.get('DONE', 0)}名 ({status_counts.get('DONE', 0) / total_candidates * 100:.1f}%)")
        print(f"  - PROCESSING: {status_counts.get('PROCESSING', 0)}名 ({status_counts.get('PROCESSING', 0) / total_candidates * 100:.1f}%)")
        print(f"  - NEW: {status_counts.get('NEW', 0)}名 ({status_counts.get('NEW', 0) / total_candidates * 100:.1f}%)")
        print(f"  - ERROR: {status_counts.get('ERROR', 0)}名 ({status_counts.get('ERROR', 0) / total_candidates * 100:.1f}%)")
        print(f"\n【意思決定】 {total_decisions}件")
        print(f"  - pass: {decision_counts.get('pass', 0)}件")
        print(f"  - hold: {decision_counts.get('hold', 0)}件")
        print(f"  - reject: {decision_counts.get('reject', 0)}件")
        print(f"\n【未判定】 {status_counts.get('DONE', 0) - total_decisions}名")
        print("\n" + "=" * 50)
        print("フロントエンドで確認: http://localhost:3000")
        print("=" * 50)


def main():
    asyncio.run(seed_data())


if __name__ == "__main__":
    main()
