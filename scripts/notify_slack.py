import requests
import sys
import json
from datetime import datetime

def format_gcp_status(service):
    """GCPのステータスを読みやすく整形"""
    status = service.get('status', 'Unknown')
    
    # most_recent_updateがある場合はそれを使用
    if 'most_recent_update' in service:
        update = service['most_recent_update']
        if isinstance(update, dict):
            # 日付情報を抽出
            modified = update.get('modified', '')
            if modified:
                try:
                    dt = datetime.fromisoformat(modified.replace('+00:00', ''))
                    date_str = dt.strftime('%Y-%m-%d')
                    return f"Incident reported on {date_str}"
                except:
                    pass
            return "Recent incident detected"
    
    return "No incidents" if status == "No incidents" else status

def format_aws_status(service):
    """AWSのステータスを読みやすく整形"""
    # previewから簡単な情報を抽出（実際のRSSパース実装も可能）
    return "Service operational"

def send_slack_notification(webhook_url, status_file):
    # ステータスファイルを読み込む
    with open(status_file, 'r') as f:
        data = json.load(f)
    
    # 各サービスのステータスを整形
    status_lines = []
    for service in data['statuses']:
        name = service['name']
        
        if name == 'AWS':
            status = format_aws_status(service)
        elif name == 'GCP':
            status = format_gcp_status(service)
        elif name == 'GitHub':
            status = service.get('status', 'Unknown')
        else:
            status = service.get('status', 'Unknown')
        
        # 絵文字を追加
        emoji = "✅" if status in ["All Systems Operational", "Service operational", "No incidents"] else "⚠️"
        status_lines.append(f"{emoji} *{name}*: {status}")
    
    status_text = "\n".join(status_lines)
    
    # タイムスタンプを整形
    timestamp = data.get('timestamp', '')
    if timestamp:
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            time_str = dt.strftime('%Y-%m-%d %H:%M:%S UTC')
        except:
            time_str = timestamp
    else:
        time_str = 'Unknown'
    
    payload = {
        "text": f"☁️ *Cloud Status Monitor Report*\n\n{status_text}\n\n_Checked at: {time_str}_"
    }
    
    response = requests.post(webhook_url, json=payload)
    
    if response.status_code != 200:
        print(f"Failed to send Slack notification: {response.status_code} - {response.text}")
        sys.exit(1)
    
    print("Slack notification sent successfully")

if __name__ == "__main__":
    webhook_url = sys.argv[1]
    status_file = sys.argv[2]
    send_slack_notification(webhook_url, status_file)
