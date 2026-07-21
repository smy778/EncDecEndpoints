import requests
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "Referer": "https://vidcore.net/",
    "X-Requested-With": "XMLHttpRequest"
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

# Movie format: <https://vidcore.net/movie/{IMDB_ID or TMDB_ID}>
# Tv format: <https://vidcore.net/tv/{IMDB_ID or TMDB_ID}/{season_number}/{episode_number}>

# --- Game of Thrones ---
title = "Game of Thrones"
type = "tv"
year = "2011"
imdb_id = "tt0944947"
tmdb_id = "1399"
season = "1"
episode = "1"

# Fetch page content
base_url = f"https://vidcore.net/tv/{tmdb_id}/{season}/{episode}/"
response = requests.get(base_url).text

# Extract text
match = re.search(r'\\"(?:en|token)\\":\\"(.*?)\\"', response)
text = match.group(1)

# Get vidcore urls
enc_vidcore = f"{API}/enc-vidcore?text={text}"
response = requests.get(enc_vidcore).json()
parts = validate(response, enc_vidcore)
servers = parts['servers']
stream = parts['stream']
token = parts['token']

# Update headers with token
HEADERS["X-CSRF-Token"] = token

# Get streaming servers and decrypt
servers_encrypted = requests.post(servers, headers=HEADERS).text

dec_vidcore = f"{API}/dec-vidcore"
response = requests.post(dec_vidcore, json={"text": servers_encrypted}).json()
servers_decrypted = validate(response, dec_vidcore)

# Sample the first server
# Note: there are multiple server options in servers_decrypted, create the stream urls with different 'data' values.
# For reference, run: print(servers_decrypted)
server = servers_decrypted[0]
data = server['data']

# Get stream and decrypt
stream = f"{stream}/{data}"
stream_encrypted = requests.post(stream, headers=HEADERS).text

dec_vidcore = f"{API}/dec-vidcore"
response = requests.post(dec_vidcore, json={"text": stream_encrypted}).json()
stream_decrypted = validate(response, dec_vidcore)

print(f"\n{'-'*25} Decrypted Data {'-'*25}\n")
print(f"Referer: {HEADERS['Referer']}\n")
print(stream_decrypted)
