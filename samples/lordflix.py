import requests
from urllib.parse import quote

HEADERS = {
    "Accept": "*/*",
    "Origin": "https://lordflix.org",
    "Referer": "https://lordflix.org/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
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

# Note that there are different servers, find them here: https://network.hasta-la-vista.site/servers
# Sample servers list: ["Berlin", "Tokyo", "Bogota", "Oslo", "Luna", "LordFlix", "Sakura", "Rio", "Ativa"]

# Movie format: <https://network.hasta-la-vista.site/?title={title}&type=movie&year={year}&imdb={imdb_id}&tmdb={tmdb_id}&server={server}>
# Tv format: <https://network.hasta-la-vista.site/?title={title}&type=series&year={year}&imdb={imdb_id}&tmdb={tmdb_id}&server={server}&season={season_number}&episode={episode_number}>

# --- Game of Thrones ---
title = "Game of Thrones"
type = "series"
year = "2011"
imdb_id = "tt0944947"
tmdb_id = "1399"
season = "1"
episode = "1"

# Get encrypted link and sign
server = "Berlin"
url = f"https://network.hasta-la-vista.site/?title={quote(title)}&type={type}&year={year}&imdb={imdb_id}&tmdb={tmdb_id}&server={server}&season={season}&episode={episode}"

enc_lordflix = f"{API}/enc-lordflix?url={quote(url)}"
response = requests.get(enc_lordflix).json()
data = validate(response, enc_lordflix)

enc_url = data["url"]
sign = data["sign"]

# Get encrypted media data
encrypted = requests.get(enc_url, headers=HEADERS).text

# Decrypt
dec_lordflix = f"{API}/dec-lordflix"
response = requests.post(dec_lordflix, json={"text": encrypted, "sign": sign}).json()
decrypted = validate(response, dec_lordflix)

print(f"\n{'-'*25} Decrypted Data {'-'*25}\n")
print(f"Referer: {HEADERS['Referer']}\n")
print(decrypted)
