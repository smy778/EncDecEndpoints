import requests
from Crypto.Random import get_random_bytes

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "Referer": "https://hexa.su/",
    "Accept": "text/plain",
    "X-Fingerprint-Lite": "e9136c41504646444"
}

API = "https://enc-dec.app/api"

# Also works with https://flixer.su/
# Movie format: <https://theemoviedb.hexa.su/api/tmdb/movie/{tmdb_id}/images>
# Tv format: <https://theemoviedb.hexa.su/api/tmdb/tv/{tmdb_id}/season/{season_number}/episode/{episode_number}/images>

# --- Cyberpunk Edgerunners ---
title = "Cyberpunk: Edgerunners"
type = "tv"
year = "2022"
imdb_id = "tt12590266"
tmdb_id = "105248"
season = "1"
episode = "1"

# Generate 32-byte hex key for header
key = get_random_bytes(32).hex()
HEADERS["X-Api-Key"] = key

# Get challenge token
response = requests.get(f"{API}/enc-hexa").json()['result']
token = response['token']
HEADERS["X-Cap-Token"] = token

# Get encrypted text
url = f"https://theemoviedb.hexa.su/api/tmdb/tv/{tmdb_id}/season/{season}/episode/{episode}/images"
encrypted = requests.get(url, headers=HEADERS).text

# Decrypt
decrypted = requests.post(f"{API}/dec-hexa", json={"text": encrypted, "key": key}).json()['result']
print(f"\n{'-'*25} Decrypted Data {'-'*25}\n")
print(f"Referer: {HEADERS['Referer']}\n")
print(decrypted)
