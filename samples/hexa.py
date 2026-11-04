import requests
from Crypto.Random import get_random_bytes

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "Referer": "https://hexa.su/",
    "Accept": "text/plain",
    "X-Fingerprint-Lite": "e9136c41504646444"
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

# Challenge solving utilities
def token():
    challenge_headers = {
        "accept-language": "en-US,en;q=0.9,ru;q=0.8,fr;q=0.7,bg;q=0.6,pl;q=0.5,id;q=0.4,zh-CN;q=0.3,zh;q=0.2,ja;q=0.1,es;q=0.1",
        "origin": "https://hexa.su",
        "referer": "https://hexa.su/",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36 OPR/129.0.0.0 (Edition std-2)"
    }
    
    challenge = requests.post("https://cap.hexa.su/15d2cf0395/challenge", headers=challenge_headers).json()

    enc_hexa = f"{API}/enc-hexa"
    response = validate(requests.post(enc_hexa, json={"challenge_data": challenge}).json(), enc_hexa)

    redeem = requests.post("https://cap.hexa.su/15d2cf0395/redeem", json=response).json()
    return redeem["token"]

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

# Get challenge token
# Note: token is valid for 20 invocations
HEADERS["X-Cap-Token"] = token()

# Generate 32-byte hex key for header
key = get_random_bytes(32).hex()
HEADERS["X-Api-Key"] = key

# Get encrypted text
url = f"https://theemoviedb.hexa.su/api/tmdb/tv/{tmdb_id}/season/{season}/episode/{episode}/images"
encrypted = requests.get(url, headers=HEADERS).text

# Decrypt
dec_hexa = f"{API}/dec-hexa"
response = requests.post(dec_hexa, json={"text": encrypted, "key": key}).json()
decrypted = validate(response, dec_hexa)

print(f"\n{'-'*25} Decrypted Data {'-'*25}\n")
print(f"Referer: {HEADERS['Referer']}\n")
print(decrypted)
