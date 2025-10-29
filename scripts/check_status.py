import requests, json, datetime

SOURCES = {
    "AWS": "https://status.aws.amazon.com/rss/all.rss",
    "GitHub": "https://www.githubstatus.com/api/v2/status.json",
    "GCP": "https://status.cloud.google.com/incidents.json",
}

def fetch_github():
    r = requests.get(SOURCES["GitHub"])
    data = r.json()
    return {"name": "GitHub", "status": data["status"]["description"]}

def fetch_gcp():
    r = requests.get(SOURCES["GCP"])
    incidents = r.json()
    latest = incidents[0] if incidents else {}
    return {
        "name": "GCP",
        "status": latest.get("most_recent_update", "No incidents"),
        "service": latest.get("service_name", "none"),
    }

def fetch_aws():
    r = requests.get(SOURCES["AWS"])
    return {"name": "AWS", "status": "Fetched RSS feed", "preview": r.text[:200]}

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
