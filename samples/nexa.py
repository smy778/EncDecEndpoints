import requests
import base64
from urllib.parse import quote

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "Referer": "https://nexa.mov/"
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

# Movie format: <https://providers.nexa.mov/?platform={platform_name}&id={tmdb_id}&server={server_name}>
# Tv format: <https://providers.nexa.mov/?platform={platform_name}&id={tmdb_id}&server={server_name}&season={season_number}&episode={episode_number}>

# --- Game of Thrones ---
title = "Game of Thrones"
type = "tv"
year = "2011"
imdb_id = "tt0944947"
tmdb_id = "1399"
season = "1"
episode = "1"

# Get sample server
# Note: there are multiple server options, you can change the server by changing the index
# For reference, run: print(servers)
servers = requests.get("https://providers.nexa.mov/v1/status", headers=HEADERS).json()['sources']
server = servers[0]['codename'] # last four servers: kyoto, tokyo, hokkaido, fuji are exclusively anime sources with platform 'anilist' using anilist ids. Will not work with tmdb.

# Encrypt server data
url = f"https://providers.nexa.mov/?platform=tmdb&id={tmdb_id}&server={server}&season={season}&episode={episode}"

enc_nexa = f"{API}/enc-nexa?url={quote(url)}"
encoded = validate(requests.get(enc_nexa).json(), enc_nexa)
bytes = base64.b64decode(encoded, validate=True)

# Get encrypted server response
HEADERS["Content-Type"] = "application/octet-stream"
encrypted = requests.post("https://providers.nexa.mov/v1/playlist", data=bytes, headers=HEADERS).content.hex()

# Decrypt
dec_nexa = f"{API}/dec-nexa"
decrypted = validate(requests.post(dec_nexa, json={"text": encrypted, "server": server}).json(), dec_nexa)

print(f"\n{'-'*25} Decrypted Data {'-'*25}\n")
print(f"Referer: {HEADERS['Referer']}\n")
print(decrypted)
