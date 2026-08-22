import requests
import base64
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

# Helper functions
def base64url_encode(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

def base64url_decode(data):
    data += "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data)

# Note that there are different servers, find them here: https://api.shegu.st/servers

# Movie format: <https://api.shegu.st/?title={title}&type=movie&year={year}&imdb={imdb_id}&tmdb={tmdb_id}&server={server}>
# Tv format: <https://api.shegu.st/?title={title}&type=series&year={year}&imdb={imdb_id}&tmdb={tmdb_id}&server={server}&season={season_number}&episode={episode_number}>

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
servers = requests.get("https://api.shegu.st/servers", headers=HEADERS).json()['servers']
server = servers[0]['name']

# Get encrypted text and state
url = f"https://api.shegu.st/?title={quote(title)}&type={type}&year={year}&imdb={imdb_id}&tmdb={tmdb_id}&server={server}&season={season}&episode={episode}"

enc_cinejoy = f"{API}/enc-cinejoy?url={quote(url)}"
response = requests.get(enc_cinejoy).json()

enc = validate(response, enc_cinejoy)
data = enc['data']
state = enc['state']

encrypted = requests.post(f"https://api.shegu.st/g", data=base64url_decode(enc['data']), headers=HEADERS).content

# Decrypt
dec_cinejoy = f"{API}/dec-cinejoy"
response = requests.post(dec_cinejoy, json={"text": base64url_encode(encrypted), "state": state}).json()
decrypted = validate(response, dec_cinejoy)

print(f"\n{'-'*25} Decrypted Data {'-'*25}\n")
print(f"Referer: {HEADERS['Referer']}\n")
print(decrypted)
