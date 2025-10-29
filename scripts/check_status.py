import requests, json, datetime

SOURCES = {
    "AWS": "https://status.aws.amazon.com/rss/all.rss",
    "GitHub": "https://www.githubstatus.com/api/v2/status.json",
    "GCP": "https://status.cloud.google.com/incidents.json",
    "Azure": "https://azure.status.microsoft/en-us/status",
}

LINKS = {
    "AWS": "https://health.aws.amazon.com/health/status",
    "GitHub": "https://www.githubstatus.com/",
    "GCP": "https://status.cloud.google.com/",
    "Azure": "https://azure.status.microsoft/en-us/status",
}

def fetch_github():
    r = requests.get(SOURCES["GitHub"])
    data = r.json()
    return {
        "name": "GitHub",
        "status": data["status"]["description"],
        "indicator": data["status"]["indicator"],
        "link": LINKS["GitHub"]
    }

def fetch_gcp():
    r = requests.get(SOURCES["GCP"])
    incidents = r.json()
    
    if not incidents:
        return {
            "name": "GCP",
            "status": "No incidents",
            "has_incident": False,
            "link": LINKS["GCP"]
        }
    
    latest = incidents[0]
    most_recent = latest.get("most_recent_update", {})
    
    # URIから正しいリンクを生成
    incident_uri = latest.get("uri", "")
    incident_link = LINKS["GCP"]
    if incident_uri:
        # URIには既に incidents/ が含まれているので、そのまま使用
        incident_link = f"https://status.cloud.google.com/{incident_uri}"
    
    return {
        "name": "GCP",
        "status": latest.get("external_desc", "Incident detected"),
        "has_incident": True,
        "incident_number": latest.get("number", "Unknown"),
        "service_name": latest.get("service_name", "Unknown service"),
        "severity": latest.get("severity", "Unknown"),
        "created": latest.get("created", ""),
        "modified": most_recent.get("modified", ""),
        "status_impact": most_recent.get("status", "AVAILABLE"),
        "link": incident_link
    }

def fetch_aws():
    r = requests.get(SOURCES["AWS"])
    # 簡易的なRSSパース
    content = r.text
    has_incident = "<item>" in content
    
    return {
        "name": "AWS",
        "status": "Service operational" if not has_incident else "Check status page",
        "has_incident": has_incident,
        "link": LINKS["AWS"]
    }

def fetch_azure():
    try:
        r = requests.get(SOURCES["Azure"], timeout=10)
        # Azureのステータスページは通常HTMLなので、簡易チェック
        # APIが利用可能な場合は別途実装
        if r.status_code == 200:
            return {
                "name": "Azure",
                "status": "Service operational",
                "has_incident": False,
                "link": LINKS["Azure"]
            }
    except:
        pass
    
    return {
        "name": "Azure",
        "status": "Unable to fetch status",
        "has_incident": False,
        "link": LINKS["Azure"]
    }

def main():
    results = [fetch_aws(), fetch_azure(), fetch_github(), fetch_gcp()]
    report = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "statuses": results,
    }
    with open("data/cloud_status.json", "w") as f:
        json.dump(report, f, indent=2)
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
