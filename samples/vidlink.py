import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "Origin": "https://vidlink.pro",
    "Referer": "https://vidlink.pro/"
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

# Movie format: <https://vidlink.pro/api/b/movie/{encrypted_id}>
# Tv format: <https://vidlink.pro/api/b/tv/{encrypted_id}/{season_number}/{episode_number}>

# --- Cyberpunk Edgerunners ---
title = "Cyberpunk: Edgerunners"
type = "tv"
year = "2022"
imdb_id = "tt12590266"
tmdb_id = "105248"
season = "1"
episode = "1"

# Get encrypted tmdb id text
enc_vidlink = f"{API}/enc-vidlink?text={tmdb_id}"
response = requests.get(enc_vidlink).json()
encrypted = validate(response, enc_vidlink)

# Request vidlink url
url = f"https://vidlink.pro/api/b/{type}/{encrypted}/{season}/{episode}"
data = requests.get(url, headers=HEADERS).json()
print(f"\n{'-'*25} Decrypted Data {'-'*25}\n")
print(f"Referer: {HEADERS['Referer']}\n")
print(data)
