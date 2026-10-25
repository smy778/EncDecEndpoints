import requests
import json
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "Origin": "https://megaplay.buzz",
    "Referer": "https://megaplay.buzz/",
    "X-Requested-With": "XMLHttpRequest"
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

# Stream format (MAL): https://megaplay.buzz/stream/mal/{mal_id}/{episode_number}{voice_type}
# Stream format (Anilist): https://megaplay.buzz/stream/ani/{anilist_id}/{episode_number}{voice_type}

# The following format may also be used on sites embedding this player (like anikoto), which interally map episode IDs:
# Stream format (Episode ID): https://megaplay.buzz/stream/s-2/{episode_id}/{voice_type}

'''
# Get all domains: 

domains = requests.get("https://megaplay.buzz/domains").json()["enc"]
decrypted = requests.post(f"{API}/dec-megaplay", json={"text": domains}).json()
print(decrypted)
'''

# --- Cyberpunk Edgerunners ---
mal_id = "42310"
episode = "1"
voice_type = "dub" # "sub" or "dub"
url = f"https://megaplay.buzz/stream/mal/{mal_id}/{episode}/{voice_type}"

# Get internal content id
response = requests.get(url, headers=HEADERS).text
content_id = re.search(r"<title>(?:File (\d+)|Error) - MegaPlay</title>", response).group(1)
if not content_id:
    raise SystemExit("Megaplay content ID not found.")

# Get stream data
stream_url = f"https://megaplay.buzz/stream/getSources?id={content_id}&platform=OTHER"
stream_response = requests.get(stream_url, headers=HEADERS).json()

# Decrypt
dec_megaplay = f"{API}/dec-megaplay"
dec_response = requests.post(dec_megaplay, json={"text": stream_response['enc']}).json()
stream = validate(dec_response, dec_megaplay)

stream_response.pop("enc", None)
stream_response.update(stream)

print(f"\nHeaders: {json.dumps(HEADERS)}")
print(f"\n{'-'*25} Decrypted Data {'-'*25}\n")
print(stream_response)
