import psutil
import requests

def ingest_local_system():
    return {
        "cpu": psutil.cpu_percent(),
        "memory": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage('/').percent,
        "network": psutil.net_io_counters().bytes_sent
    }

def ingest_live_web_feeds():
    try:
        news = requests.get("https://api.currentsapi.services/v1/latest-news", params={"apiKey": "your_api_key"}, timeout=5)
        headlines = [item["title"] for item in news.json().get("news", [])[:3]]
    except:
        headlines = ["Web feed unavailable"]
    return {"headlines": headlines}

def ingest_swarm_sync():
    return {"swarm_glyphs": ["node-echo", "fusion-trail", "consensus-pulse"]}

def ingest_all_sources():
    local = ingest_local_system()
    web = ingest_live_web_feeds()
    swarm = ingest_swarm_sync()
    return {**local, **web, **swarm}

