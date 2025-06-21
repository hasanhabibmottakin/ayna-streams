import os
import json
import time
import requests

APP_DATA_FOLDER = "app_data"
TOKEN_FILE = os.path.join(APP_DATA_FOLDER, "ayna_token.txt")
CHANNEL_JSON_URL = "https://aynaott.yflix.top/fuck_api.json"
TOKEN_API_URL = "https://aynatoken.linkchur.top/?action=token"
STREAM_API_BASE = "https://web.aynaott.com/api/player/streams"
OUTPUT_FILE = "api.json"

os.makedirs(APP_DATA_FOLDER, exist_ok=True)

def get_token():
    if os.path.exists(TOKEN_FILE):
        if time.time() - os.path.getmtime(TOKEN_FILE) < 4 * 3600:
            with open(TOKEN_FILE, "r") as f:
                return f.read().strip()
    try:
        res = requests.get(TOKEN_API_URL, timeout=10)
        if res.status_code == 200:
            token = res.json().get("token")
            if token:
                with open(TOKEN_FILE, "w") as f:
                    f.write(token)
                return token
    except Exception as e:
        print("Error fetching token:", e)
    return None

def fetch_channel_data():
    try:
        res = requests.get(CHANNEL_JSON_URL, timeout=10)
        if res.status_code == 200:
            data = res.json()
            result = []
            for block in data.get("content", {}).get("data", []):
                for item in block.get("items", {}).get("data", []):
                    result.append({
                        "id": item.get("id"),
                        "name": item.get("title"),
                        "image": item.get("image", ""),
                        "landscapeImage": item.get("landscapeImage", "")
                    })
            return result
    except Exception as e:
        print("Error fetching channel list:", e)
    return []

def fetch_stream_url(media_id, token):
    headers = {
        "Authorization": f"Bearer {token}"
    }
    params = {
        "language": "en",
        "operator_id": "1fb1b4c7-dbd9-469e-88a2-c207dc195869",
        "device_id": "543EC512DAD9426545939C5DA824B619",
        "density": 1.5,
        "client": "browser",
        "platform": "web",
        "os": "windows",
        "media_id": media_id
    }
    try:
        res = requests.get(STREAM_API_BASE, headers=headers, params=params, timeout=10)
        for item in res.json().get("content", []):
            url = item.get("src", {}).get("url")
            if url:
                name = url.split("/")[3].split("?")[0] if len(url.split("/")) > 3 else "unknown"
                return name, url
    except Exception as e:
        print(f"Error fetching stream for {media_id}:", e)
    return None, None

def build_api_json():
    token = get_token()
    if not token:
        print("❌ Failed to retrieve token")
        return

    channels = fetch_channel_data()
    if not channels:
        print("❌ Failed to retrieve channel list")
        return

    output = []
    for ch in channels:
        name, m3u8 = fetch_stream_url(ch["id"], token)
        if m3u8:
            output.append({
                "id": name,
                "m3u8": m3u8,
                "image": ch["image"],
                "landscapeImage": ch["landscapeImage"],
                "name": ch["name"],
                "author": "https://t.me/fredflixceo"
            })
        else:
            print(f"Skipped: {ch['name']}")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"✅ Done! Saved {len(output)} channels to {OUTPUT_FILE}")

# === Run ===
build_api_json()
