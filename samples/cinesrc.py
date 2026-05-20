import re
import json
import requests
from urllib.parse import quote

HEADERS = {
    "Origin": "https://cinesrc.st",
    "Referer": "https://cinesrc.st/",
    "Content-Type": "text/plain;charset=UTF-8",
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

# Movie format: <https://cinesrc.st/embed/movie/{IMDB_ID}>
# Tv format: <https://cinesrc.st/embed/tv/{IMDB_ID}?s={season_number}&e={episode_number}>

# --- Game of Thrones ---
title = "Game of Thrones"
type = "tv"
year = "2011"
imdb_id = "tt0944947"
tmdb_id = "1399"
season = "1"
episode = "1"

url = f"https://cinesrc.st/embed/tv/{imdb_id}?s={season}&e={episode}"

# Get encrypted token and headers
enc_cinesrc = f"{API}/enc-cinesrc?url={quote(url)}&agent={quote(HEADERS['User-Agent'])}" # Url-encode params
response = requests.get(enc_cinesrc).json()
data = validate(response, enc_cinesrc)

token = data["token"]
headers = data["headers"]

getProviderList = headers["getProviderList"]
getStream = headers["getStream"]

# Get providers and parse
headers = {**HEADERS, "Next-Action": getProviderList}
payload = []

providers_text = requests.post(url, headers=headers, data=json.dumps(payload)).text
line = providers_text.splitlines()[1].split(":", 1)[1]
providers = json.loads(line)

# Sample second provider and parse encrypted data
provider = providers[1]["id"]
headers = {**HEADERS, "Next-Action": getStream}
payload = [
    tmdb_id,
    "show" if type == "tv" else type,
    season if type == "tv" else "$undefined",
    episode if type == "tv" else "$undefined",
    token,
    provider
]

response = requests.post(url, headers=headers, data=json.dumps(payload))

# Validate the response status code, 500 -> retry with another provider from list
if response.status_code != 200:
    print(f"Try another server.\nProvider error: {provider} -> {response.status_code}")
    raise SystemExit

streams_text = response.text
line = streams_text.splitlines()[1]
encrypted = line.split(",", 1)[1].split(":", 1)[0]

# Decrypt
dec_cinesrc = f"{API}/dec-cinesrc"
response = requests.post(dec_cinesrc, json={"text": encrypted}).json()
decrypted = validate(response, dec_cinesrc)

print(f"\n{'-'*25} Decrypted Data {'-'*25}\n")
print(f"Referer: {HEADERS['Referer']}\n")
print(decrypted)
