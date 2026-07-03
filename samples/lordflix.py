import requests
import hashlib
import base64
import json
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

# Challenge solving utilities
def solver(data):
    max_number = data["maxnumber"]
    challenge = data["challenge"]
    salt = data["salt"]

    for number in range(max_number + 1):
        digest = hashlib.sha256(f'{salt}{number}'.encode()).hexdigest()
        if digest == challenge:
            return number

def solve_challenge():
    url = "https://snowhouse.lordflix.club/challenge"
    response = requests.get(url, headers=HEADERS)
    challenge = response.json()

    number = solver(challenge)

    payload = {
        "algorithm": challenge["algorithm"],
        "challenge": challenge["challenge"],
        "number": number,
        "salt": challenge["salt"],
        "signature": challenge["signature"],
    }

    return base64.b64encode(json.dumps(payload).encode()).decode()

# Note that there are different servers, find them here: https://snowhouse.lordflix.club/servers

# Movie format: <https://snowhouse.lordflix.club/?title={title}&type=movie&year={year}&imdb={imdb_id}&tmdb={tmdb_id}&server={server}>
# Tv format: <https://snowhouse.lordflix.club/?title={title}&type=series&year={year}&imdb={imdb_id}&tmdb={tmdb_id}&server={server}&season={season_number}&episode={episode_number}>

# --- Game of Thrones ---
title = "Game of Thrones"
type = "series"
year = "2011"
imdb_id = "tt0944947"
tmdb_id = "1399"
season = "1"
episode = "2"

# Get sample server
servers = requests.get("https://snowhouse.lordflix.club/servers", headers=HEADERS).json()['servers']
server = servers[0]['name']

# Get encrypted link and sign
url = f"https://snowhouse.lordflix.club/?title={quote(title)}&type={type}&year={year}&imdb={imdb_id}&tmdb={tmdb_id}&server={server}&season={season}&episode={episode}"

enc_lordflix = f"{API}/enc-lordflix?url={quote(url)}"
response = requests.get(enc_lordflix).json()
data = validate(response, enc_lordflix)

enc_url = data["url"]

# Solve challenge
HEADERS["x-attest"] = solve_challenge()

# Get encrypted media data
encrypted = requests.get(enc_url, headers=HEADERS).text

# Decrypt
dec_lordflix = f"{API}/dec-lordflix"
response = requests.post(dec_lordflix, json={"text": encrypted}).json()
decrypted = validate(response, dec_lordflix)

print(f"\n{'-'*25} Decrypted Data {'-'*25}\n")
print(f"Referer: {HEADERS['Referer']}\n")
print(decrypted)
