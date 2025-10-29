import requests
import sys
import json

def send_slack_notification(webhook_url, status_file):
    # ステータスファイルを読み込む
    with open(status_file, 'r') as f:
        data = json.load(f)
    
    # 各サービスのステータスを整形
    status_lines = []
    for service in data['statuses']:
        name = service['name']
        status = service['status']
        status_lines.append(f"• *{name}*: {status}")
    
    status_text = "\n".join(status_lines)
    
    payload = {
        "text": f"☁️ Cloud Status Monitor Report\n\n{status_text}\n\nTimestamp: {data['timestamp']}"
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
