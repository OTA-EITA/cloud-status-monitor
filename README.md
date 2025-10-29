# Cloud Status Monitor

AWS・GitHub・GCP のクラウドサービス稼働状況を毎日自動監視するシステム

## 概要

GitHub Actions を使用して、主要クラウドサービスの稼働状況を定期的にチェックし、以下を自動実行します：

- ステータス情報を JSON 形式で保存
- GitHub Issue でレポート作成
- 毎日の監視履歴を Git で管理

## 監視対象

- **AWS**: Amazon Web Services のシステム稼働状況
- **GitHub**: GitHub のサービス稼働状況
- **GCP**: Google Cloud Platform のインシデント情報

## 仕組み

1. **毎日 09:00 JST** に自動実行（cron スケジュール）
2. 各クラウドサービスの公開 API からステータス取得
3. `data/cloud_status.json` に結果を保存
4. 自動コミット & プッシュ
5. GitHub Issue でデイリーレポート作成

## セットアップ

このリポジトリは単独で動作します。特別な設定は不要です。

### 必要な権限

GitHub Actions が以下を実行できるよう、リポジトリ設定を確認してください：

- **Settings** → **Actions** → **General** → **Workflow permissions**
  - ✅ "Read and write permissions" を選択
  - ✅ "Allow GitHub Actions to create and approve pull requests" を有効化

### 手動実行

Actions タブから「Cloud Service Status Monitor」を選択し、「Run workflow」で手動実行できます。

## ファイル構成

```
.
├── scripts/
│   └── check_status.py            # ステータス取得スクリプト
├── data/
│   └── cloud_status.json          # 最新のステータス（自動更新）
├── .github/
│   └── workflows/
│       ├── cloud-status.yml       # メイン監視ワークフロー
│       └── issue-report.yml       # Issue 作成ワークフロー
└── README.md
```

## 出力サンプル

```json
{
  "timestamp": "2025-10-29T00:00:00Z",
  "statuses": [
    {
      "name": "AWS",
      "status": "All systems operational"
    },
    {
      "name": "GitHub",
      "status": "All Systems Operational"
    },
    {
      "name": "GCP",
      "status": "No incidents"
    }
  ]
}
```

## 今後の拡張案

- Slack/Discord への通知連携
- 前日との差分検知
- README への稼働バッジ表示
- Cloudflare、Vercel などの監視追加
- 月次レポートのアーカイブ機能

## ライセンス

MIT
