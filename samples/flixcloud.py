import requests
import re
import json5
from urllib.parse import urlencode

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "Referer": "https://flixcloud.cc/"
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

# Sample flixcloud url (compatible with sites using this hoster e.g reanime.to, 1anime.app, etc)
url = "https://flixcloud.cc/e/5o4rjvbx8ad0"

# Fetch page content and extract embedded data
response = requests.get(url, headers=HEADERS).text
match = re.search(r'type:\s*"data",\s*data:\s*(\{.*?\})\s*,\s*uses:', response, re.S)
data = json5.loads(match.group(1))
subtitles = data.pop("subtitles") # Optional subtitles

# Resolve stream token
dec_token = f"{API}/dec-flixcloud?type=token"
token_response = requests.post(dec_token, json={"data": data}).json()
token_validated = validate(token_response, dec_token)

# Fetch encrypted stream
stream = f"https://flixcloud.cc/api/m3u8/{token_validated['token']}"
stream_response = requests.get(stream, headers=HEADERS).json()

# Decrypt stream
dec_stream = f"{API}/dec-flixcloud?type=stream"
stream_payload = {
    "data": {
        "context": token_validated["context"],
        "stream_response": stream_response
    }
}

stream_response = requests.post(dec_stream, json=stream_payload).json()
stream_resolved = validate(stream_response, dec_stream)

print(f"\n{'-'*25} Decrypted Url {'-'*25}\n")
print(f"Referer: {HEADERS['Referer']}\n")
print(stream_resolved["stream"])
# Note: subtitles available under data["subtitles"]

# Get manifest (feed to players as normal, audio/video tracks are decrypted automatically)
# Note: The parse endpoint does not host or proxy any media segments.

params = urlencode({
    "url": stream_resolved["stream"],
    "w_payload": stream_resolved["context"]["w_payload"]
})

parse_manifest = f"{API}/parse-flixcloud?{params}"
manifest_response = requests.get(parse_manifest)

print(f"\n{'-'*25} Decrypted Manifest {'-'*25}\n")
print(manifest_response.text)
