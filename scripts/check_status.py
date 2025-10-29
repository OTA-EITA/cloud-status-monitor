import requests, json, datetime

SOURCES = {
    "AWS": "https://status.aws.amazon.com/rss/all.rss",
    "GitHub": "https://www.githubstatus.com/api/v2/status.json",
    "GCP": "https://status.cloud.google.com/incidents.json",
}

LINKS = {
    "AWS": "https://status.aws.amazon.com/",
    "GitHub": "https://www.githubstatus.com/",
    "GCP": "https://status.cloud.google.com/",
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
        "link": f"https://status.cloud.google.com/incidents/{latest.get('uri', '')}" if latest.get('uri') else LINKS["GCP"]
    }

def fetch_aws():
    r = requests.get(SOURCES["AWS"])
    # 簡易的なRSSパース（本格的にはfeedparserを使用）
    content = r.text
    has_incident = "<item>" in content
    
    return {
        "name": "AWS",
        "status": "Service operational" if not has_incident else "Check status page",
        "has_incident": has_incident,
        "link": LINKS["AWS"]
    }

def main():
    results = [fetch_aws(), fetch_github(), fetch_gcp()]
    report = {
        "timestamp": datetime.datetime.utcnow().isoformat(),
        "statuses": results,
    }
    with open("data/cloud_status.json", "w") as f:
        json.dump(report, f, indent=2)
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()
