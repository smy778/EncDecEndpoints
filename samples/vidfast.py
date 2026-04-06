import requests
import re, time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "Referer": "https://vidfast.pro/",
    "X-Requested-With": "XMLHttpRequest"
}

API = "https://enc-dec.app/api"
VERSION = "1"

# Movie format: <https://vidfast.pro/movie/{IMDB_ID or TMDB_ID}>
# Tv format: <https://vidlink.pro//tv/{IMDB_ID or TMDB_ID}/{season_number}/{episode_number}>

# --- Cyberpunk Edgerunners ---
title = "Cyberpunk: Edgerunners"
type = "tv"
year = "2022"
imdb_id = "tt12590266"
tmdb_id = "105248"
season = "1"
episode = "1"

# Fetch page content
base_url = f"https://vidfast.pro/tv/{tmdb_id}/{season}/{episode}"
response = requests.get(base_url).text

# Extract text
match = re.search(r'\\"en\\":\\"(.*?)\\"', response)
text = match.group(1)

# Get vidfast urls
parts = requests.get(f"{API}/enc-vidfast?text={text}&version={VERSION}").json()['result']
servers = parts['servers']
stream = parts['stream']
token = parts['token']

# Update headers with token
HEADERS["X-CSRF-Token"] = token

# Get streaming servers and decrypt
servers_encrypted = requests.post(servers, headers=HEADERS).text
servers_decrypted = requests.post(f"{API}/dec-vidfast", json={"text": servers_encrypted, "version": VERSION}).json()['result']

# Sample the first server
server = servers_decrypted[0]
data = server['data']

# Get stream and decrypt
stream = f"{stream}/{data}"
stream_encrypted = requests.post(stream, headers=HEADERS).text
stream_decrypted = requests.post(f"{API}/dec-vidfast", json={"text": stream_encrypted, "version": VERSION}).json()

print(f"\n{'-'*25} Decrypted Data {'-'*25}\n")
print(f"Referer: {HEADERS['Referer']}\n")
print(stream_decrypted)
