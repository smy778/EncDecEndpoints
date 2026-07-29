import requests
import hashlib
import base64
import json
from urllib.parse import quote

HEADERS = {
    "Accept": "*/*",
    "Origin": "https://cinejoy.to",
    "Referer": "https://cinejoy.to/",
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
def count_leading_zero_bits(data):
    count = 0

    for value in data:
        if value == 0:
            count += 8
            continue

        count += 8 - value.bit_length()
        break

    return count

def solver(data):
    salt = bytes.fromhex(data["s"])

    for counter in range(2**63):
        payload = f'{data["b"]}:{data["s"]}:{counter}'.encode()

        result = hashlib.scrypt(
            payload,
            salt=salt,
            n=data["n"],
            r=data["r"],
            p=data["p"],
            dklen=32,
        )

        if count_leading_zero_bits(result) >= data["d"]:
            return base64.b64encode(json.dumps({**data, "c": counter}, separators=(",", ":")).encode()).decode()

def solve_challenge(rid):
    url = f"https://api.shegu.xyz/challenge?rid={rid}"
    response = requests.get(url, headers=HEADERS)
    challenge = response.json()

    return solver(challenge)

# Note that there are different servers, find them here: https://api.shegu.xyz/servers

# Movie format: <https://api.shegu.xyz/?title={title}&type=movie&year={year}&imdb={imdb_id}&tmdb={tmdb_id}&server={server}>
# Tv format: <https://api.shegu.xyz/?title={title}&type=series&year={year}&imdb={imdb_id}&tmdb={tmdb_id}&server={server}&season={season_number}&episode={episode_number}>

# --- Game of Thrones ---
title = "Game of Thrones"
type = "series"
year = "2011"
imdb_id = "tt0944947"
tmdb_id = "1399"
season = "1"
episode = "1"

# Get sample server
# Note: there are multiple server options, you can change the server by changing the index
# For reference, run: print(servers)
servers = requests.get("https://api.shegu.xyz/servers", headers=HEADERS).json()['servers']
server = servers[0]['name']

# Get encrypted text
url = f"https://api.shegu.xyz/?title={quote(title)}&type={type}&year={year}&imdb={imdb_id}&tmdb={tmdb_id}&server={server}&season={season}&episode={episode}"

enc_cinejoy = f"{API}/enc-cinejoy?url={quote(url)}"
response = requests.get(enc_cinejoy).json()
enc = validate(response, enc_cinejoy)

# Solve challenge
HEADERS["x-at"] = solve_challenge(enc)

# Get encrypted media data
encrypted = requests.get(f"https://api.shegu.xyz/{enc}", headers=HEADERS).text

# Decrypt
dec_cinejoy = f"{API}/dec-cinejoy"
response = requests.post(dec_cinejoy, json={"text": encrypted}).json()
decrypted = validate(response, dec_cinejoy)

print(f"\n{'-'*25} Decrypted Data {'-'*25}\n")
print(f"Referer: {HEADERS['Referer']}\n")
print(decrypted)
