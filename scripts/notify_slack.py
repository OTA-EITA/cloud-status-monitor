import requests
import sys
import json
from datetime import datetime

def format_status_line(service):
    """各サービスのステータスを整形"""
    name = service['name']
    link = service.get('link', '#')
    
    if name == 'AWS':
        has_incident = service.get('has_incident', False)
        status = service.get('status', 'Unknown')
        emoji = "🔴" if has_incident else "🟢"
        return {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"{emoji} *<{link}|Amazon Web Services>*\n{status}"
            }
        }
    
    elif name == 'Azure':
        has_incident = service.get('has_incident', False)
        status = service.get('status', 'Unknown')
        emoji = "🔴" if has_incident else "🟢"
        return {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"{emoji} *<{link}|Microsoft Azure>*\n{status}"
            }
        }
    
    elif name == 'GitHub':
        status = service.get('status', 'Unknown')
        indicator = service.get('indicator', 'none')
        emoji = "🟢" if indicator == 'none' else "🔴"
        return {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"{emoji} *<{link}|GitHub>*\n{status}"
            }
        }
    
    elif name == 'GCP':
        has_incident = service.get('has_incident', False)
        if not has_incident:
            return {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"🟢 *<{link}|Google Cloud Platform>*\nNo incidents"
                }
            }
        
        # インシデントがある場合
        status = service.get('status', 'Incident detected')
        service_name = service.get('service_name', 'Unknown service')
        severity = service.get('severity', 'Unknown')
        incident_number = service.get('incident_number', 'Unknown')
        
        # 日付を整形
        created = service.get('created', '')
        if created:
            try:
                dt = datetime.fromisoformat(created.replace('+00:00', ''))
                date_str = dt.strftime('%Y-%m-%d %H:%M UTC')
            except:
                date_str = created
        else:
            date_str = 'Unknown'
        
        incident_link = service.get('link', '#')
        
        return {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"🔴 *<{incident_link}|Google Cloud Platform>*\n*Service impact:* {status}\n_{service_name}_ | Severity: {severity} | Incident #{incident_number}\nCreated: {date_str}"
            }
        }
    
    return {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": f"❓ *{name}*\nUnknown"
        }
    }

def send_slack_notification(webhook_url, status_file):
    # ステータスファイルを読み込む
    with open(status_file, 'r') as f:
        data = json.load(f)
    
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
    
    # ブロックを作成
    blocks = [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "☁️ Cloud Status Monitor",
                "emoji": True
            }
        },
        {
            "type": "divider"
        }
    ]
    
    # 各サービスのステータスブロックを追加
    for service in data['statuses']:
        blocks.append(format_status_line(service))
        blocks.append({"type": "divider"})
    
    # フッター
    blocks.append({
        "type": "context",
        "elements": [
            {
                "type": "mrkdwn",
                "text": f"Checked at: {time_str}"
            }
        ]
    })
    
    payload = {
        "blocks": blocks
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
