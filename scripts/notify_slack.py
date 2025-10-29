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
        emoji = "⚠️" if has_incident else "✅"
        return f"{emoji} *<{link}|{name}>*: {status}"
    
    elif name == 'GitHub':
        status = service.get('status', 'Unknown')
        indicator = service.get('indicator', 'none')
        emoji = "✅" if indicator == 'none' else "⚠️"
        return f"{emoji} *<{link}|{name}>*: {status}"
    
    elif name == 'GCP':
        has_incident = service.get('has_incident', False)
        if not has_incident:
            return f"✅ *<{link}|{name}>*: No incidents"
        
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
        
        return f"⚠️ *<{link}|{name}>*: {status}\n   _Service:_ {service_name}\n   _Severity:_ {severity}\n   _Incident #:_ {incident_number}\n   _Created:_ {date_str}"
    
    return f"❓ *{name}*: Unknown"

def send_slack_notification(webhook_url, status_file):
    # ステータスファイルを読み込む
    with open(status_file, 'r') as f:
        data = json.load(f)
    
    # 各サービスのステータスを整形
    status_lines = []
    for service in data['statuses']:
        status_lines.append(format_status_line(service))
    
    status_text = "\n\n".join(status_lines)
    
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
