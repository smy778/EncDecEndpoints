import requests
from urllib.parse import quote_plus

HEADERS = {
    "Accept": "*/*",
    "Origin": "https://vidsync.xyz",
    "Referer": "https://vidsync.xyz/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
}

API = "http://127.0.0.1:5000/api"

def validate(data, path):
    if data["status"] != 200:
        print(f"\n{'-'*25} API ERROR {'-'*25}\n")
        print(f"Path: {path}")
        print(f"Status Code: {data['status']}")
        print(f"Error: {data.get('error', 'unknown')}")
        raise SystemExit
    return data["result"]

# Note that there are different servers, find them here: https://vidsync.xyz/api/stream/serverList
# Sample servers list: ["cinevault","cinedub","cinebox","cinevip","cinecloud","cine4k"]

# Movie format: <https://vidsync.xyz/api/stream/fetch?type=movie&title={title}&mediaId={tmdb_id}&releaseYear={year}&serverName={server}>
# Tv format: <https://vidsync.xyz/api/stream/fetch?type=tv&title={title}&mediaId={tmdb_id}&releaseYear={year}&serverName={server}&season={season_number}&episode={episode_number}>

# --- Game of Thrones ---
title = "Game of Thrones"
type = "tv"
year = "2011"
imdb_id = "tt0944947"
tmdb_id = "1399"
season = "1"
episode = "1"

# Note: URL query encoding for title
# Game of Thrones -> Game+of+Thrones
enc_title = quote_plus(title)

# Get encrypted text
server = "cinevault"
url = f"https://vidsync.xyz/api/stream/fetch?title={enc_title}&type={type}&releaseYear={year}&mediaId={tmdb_id}&serverName={server}&season={season}&episode={episode}"
enc_data = requests.get(url, headers=HEADERS).text

# Decrypt
dec_vidsync = f"{API}/dec-vidsync"
response = requests.post(dec_vidsync, json={"text": enc_data, "id": tmdb_id}).json()
decrypted = validate(response, dec_vidsync)

print(f"\n{'-'*25} Decrypted Data {'-'*25}\n")
print(f"Referer: {HEADERS['Referer']}\n")
print(decrypted)
