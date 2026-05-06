import requests
import re
import json5
from urllib.parse import urlparse

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "Referer": "https://reanime.to/"
}

API = "https://enc-dec.app/api"

def validate(data, path):
    if data["status"] != 200:
        print(f"\n{'-'*25} API ERROR {'-'*25}\n")
        print(f"Path: {path}")
        print(f"Status Code: {data['status']}")
        print(f"Error: {data.get('error', 'unknown')}")
        raise SystemExit

    return data["result"]

# --- Cyberpunk Edgerunners ---
title = "Cyberpunk Edgerunners"
anilist_id = "120377"
episode = "1"

# Fetch servers
response = requests.get(f"https://reanime.to/api/flix/{anilist_id}/{episode}", headers=HEADERS).json()
servers = response["servers"]

# Sample the first server
# Note: there are multiple server options, with different languages.
# For reference, run: print(servers)
server = servers[0]["dataLink"]
domain = urlparse(server).netloc

# Fetch page content and extract embedded data
response = requests.get(server, headers=HEADERS).text
match = re.search(r'type:\s*"data",\s*data:\s*(\{.*?\})\s*,\s*uses:', response, re.S)
data = json5.loads(match.group(1))
subtitles = data.pop("subtitles") # Optional subtitles

# Resolve stream request state
api_resolve = f"{API}/dec-reanime?type=resolve"
response = requests.post(api_resolve, json={"data": data}).json()
resolved = validate(response, api_resolve)

# Fetch encrypted stream data
stream_api = f"https://{domain}/api/m3u8/{resolved['token']}"
referer = f"https://{domain}/"

stream_headers = HEADERS.copy()
stream_headers["Referer"] = referer

token_response = requests.get(stream_api, headers=stream_headers).json()

# Decrypt stream
api_decrypt = f"{API}/dec-reanime?type=decrypt"
decrypt_payload = {
    "data": {
        "state": resolved["state"],
        "token_response": token_response
    }
}

response = requests.post(api_decrypt, json=decrypt_payload).json()
decrypted = validate(response, api_decrypt)

print(f"\n{'-'*25} Decrypted Data {'-'*25}\n")
print(f"Referer: {referer}\n")
print(decrypted)
# Note: subtitles available under data["subtitles"]
