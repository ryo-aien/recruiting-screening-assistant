# Cloud Run デプロイガイド

## 構成図

```
                    ┌─────────────────────────────────────────┐
                    │              Google Cloud               │
                    │                                         │
┌──────────┐        │  ┌─────────────┐    ┌─────────────┐    │
│  ユーザー │───────▶│  │  Cloud Run  │    │  Cloud Run  │    │
└──────────┘        │  │  (Frontend) │    │   (API)     │    │
                    │  └──────┬──────┘    └──────┬──────┘    │
                    │         │                   │           │
                    │         │            ┌──────▼──────┐    │
                    │         │            │  Cloud Run  │    │
                    │         │            │  (Worker)   │    │
                    │         │            └──────┬──────┘    │
                    │         │                   │           │
                    │  ┌──────▼───────────────────▼──────┐    │
                    │  │           Cloud SQL             │    │
                    │  │           (MySQL 8.0)           │    │
                    │  └─────────────────────────────────┘    │
                    │                   │                     │
                    │  ┌────────────────▼────────────────┐    │
                    │  │        Cloud Storage            │    │
                    │  │        (ファイル保存)            │    │
                    │  └─────────────────────────────────┘    │
                    │                                         │
                    └─────────────────────────────────────────┘
```

## 前提条件

- Google Cloud アカウント
- gcloud CLI インストール済み
- プロジェクト作成済み

## 1. 初期セットアップ

```bash
# プロジェクトID設定
export PROJECT_ID=your-project-id
export REGION=asia-northeast1

# gcloud 認証・設定
gcloud auth login
gcloud config set project $PROJECT_ID
gcloud config set run/region $REGION

# 必要なAPIを有効化
gcloud services enable \
  run.googleapis.com \
  sqladmin.googleapis.com \
  storage.googleapis.com \
  cloudbuild.googleapis.com \
  secretmanager.googleapis.com
```

## 2. Cloud SQL (MySQL) セットアップ

```bash
# Cloud SQL インスタンス作成
gcloud sql instances create screening-db \
  --database-version=MYSQL_8_0 \
  --tier=db-f1-micro \
  --region=$REGION \
  --root-password=YOUR_ROOT_PASSWORD

# データベース作成
gcloud sql databases create screening --instance=screening-db

# ユーザー作成
gcloud sql users create screening_user \
  --instance=screening-db \
  --password=YOUR_DB_PASSWORD
```

## 3. Cloud Storage セットアップ

```bash
# バケット作成
gcloud storage buckets create gs://${PROJECT_ID}-screening-storage \
  --location=$REGION \
  --uniform-bucket-level-access

# サービスアカウントに権限付与（後で作成）
```

## 4. Secret Manager セットアップ

```bash
# シークレット作成
echo -n "YOUR_OPENAI_API_KEY" | gcloud secrets create openai-api-key --data-file=-
echo -n "YOUR_DB_PASSWORD" | gcloud secrets create db-password --data-file=-
```

## 5. Backend API デプロイ

```bash
# ビルド＆デプロイ
gcloud run deploy screening-api \
  --source=./backend \
  --region=$REGION \
  --platform=managed \
  --allow-unauthenticated \
  --set-env-vars="ENVIRONMENT=production" \
  --set-env-vars="GCP_PROJECT_ID=$PROJECT_ID" \
  --set-env-vars="GCS_BUCKET=${PROJECT_ID}-screening-storage" \
  --add-cloudsql-instances=${PROJECT_ID}:${REGION}:screening-db \
  --set-secrets="OPENAI_API_KEY=openai-api-key:latest" \
  --set-secrets="DATABASE_PASSWORD=db-password:latest" \
  --memory=512Mi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=10
```

## 6. Worker デプロイ

```bash
# Workerはポーリング型なので常時起動が必要
gcloud run deploy screening-worker \
  --source=./worker \
  --region=$REGION \
  --platform=managed \
  --no-allow-unauthenticated \
  --set-env-vars="ENVIRONMENT=production" \
  --set-env-vars="GCP_PROJECT_ID=$PROJECT_ID" \
  --set-env-vars="GCS_BUCKET=${PROJECT_ID}-screening-storage" \
  --add-cloudsql-instances=${PROJECT_ID}:${REGION}:screening-db \
  --set-secrets="OPENAI_API_KEY=openai-api-key:latest" \
  --set-secrets="DATABASE_PASSWORD=db-password:latest" \
  --memory=1Gi \
  --cpu=1 \
  --min-instances=1 \
  --max-instances=3
```

## 7. Frontend デプロイ

```bash
# API URLを取得
API_URL=$(gcloud run services describe screening-api --format='value(status.url)')

# Frontendデプロイ
gcloud run deploy screening-frontend \
  --source=./frontend \
  --region=$REGION \
  --platform=managed \
  --allow-unauthenticated \
  --set-env-vars="NEXT_PUBLIC_API_URL=$API_URL" \
  --memory=512Mi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=5
```

## 8. カスタムドメイン設定（オプション）

```bash
# ドメインマッピング
gcloud run domain-mappings create \
  --service=screening-frontend \
  --domain=app.example.com \
  --region=$REGION

gcloud run domain-mappings create \
  --service=screening-api \
  --domain=api.example.com \
  --region=$REGION
```

## 環境変数一覧

### Backend API

| 変数 | 説明 |
|------|------|
| DATABASE_URL | Cloud SQL接続URL（自動構築） |
| DATABASE_PASSWORD | DBパスワード（Secret Manager） |
| OPENAI_API_KEY | OpenAI APIキー（Secret Manager） |
| GCS_BUCKET | Cloud Storageバケット名 |
| ENVIRONMENT | production |

### Worker

Backend APIと同様

### Frontend

| 変数 | 説明 |
|------|------|
| NEXT_PUBLIC_API_URL | Backend API URL |

## コスト見積もり（目安）

| サービス | 見積もり |
|---------|---------|
| Cloud Run (API) | $0〜（無料枠内で開始可能） |
| Cloud Run (Worker) | $10〜30/月（常時起動） |
| Cloud Run (Frontend) | $0〜（無料枠内で開始可能） |
| Cloud SQL (db-f1-micro) | $10〜15/月 |
| Cloud Storage | $0.02/GB/月 |

## トラブルシューティング

### Cloud SQL接続エラー

```bash
# 接続名の確認
gcloud sql instances describe screening-db --format='value(connectionName)'

# Cloud Run サービスアカウントに権限付与
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
  --role="roles/cloudsql.client"
```

### ログ確認

```bash
# APIログ
gcloud run services logs read screening-api --region=$REGION

# Workerログ
gcloud run services logs read screening-worker --region=$REGION
```
