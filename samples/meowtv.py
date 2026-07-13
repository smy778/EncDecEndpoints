import requests
from urllib.parse import quote

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "Origin": "https://meowtv.ru",
    "Referer": "https://meowtv.ru/"
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

servers = [
    {"id": "pseudo", "label": "Psuedo"},
    {"id": "lynx", "label": "Lynx"},
    {"id": "tik", "label": "TCloud"},
    {"id": "ipcloud", "label": "IPcloud"},
    {"id": "v4:English", "label": "English"},
    {"id": "turkce", "label": "Türkçe"},
    {"id": "v5:Hindi", "label": "Hindi"},
    {"id": "v4:Hindi", "label": "Hindi v2"},
    {"id": "v6:Hindi", "label": "Hindi v3"},
]

# Movie format: <https://api.meowtv.ru/streams/movie/{tmdb_id}?s={server_id}>
# Tv format: <https://api.meowtv.ru/streams/tv/{tmdb_id}/{season_number}/{episode_number}?s={server_id}>
# Subtitles: <https://api.meowtv.ru/subs/{type}/{tmdb_id}/{season_number_IF_SERIES}/{episode_number_IF_SERIES}>

# --- Game of Thrones ---
title = "Game of Thrones"
type = "tv"
year = "2011"
imdb_id = "tt0944947"
tmdb_id = "1399"
season = "1"
episode = "1"

# Build url and get encrypted data
# Sample server, you can change the server by changing the index
server = servers[0]
url = f"https://api.meowtv.ru/streams/{type}/{tmdb_id}/{season}/{episode}?s={quote(server['id'])}"
request = requests.get(url, headers=HEADERS)

# Status code validation
if request.status_code != 200:
    print(f"\n{'-'*25} SOURCE ERROR {'-'*25}\n")
    print(f"Path: {url}")
    print(f"Code: {request.status_code}")
    print("Try another server.")
    raise SystemExit

data = request.json()

# Decrypt
dec_meowtv = f"{API}/dec-meowtv"
response = requests.post(dec_meowtv, json={"data": data}).json()
decrypted = validate(response, dec_meowtv)

print(f"\n{'-'*25} Decrypted Data {'-'*25}\n")
print(f"Referer: {HEADERS['Referer']}\n")
print(decrypted)
