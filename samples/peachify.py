import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "Origin": "https://peachify.top",
    "Referer": "https://peachify.top/"
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
    {"label": "Wolf", "path": "air", "api": "https://usa.eat-peach.sbs"},
    {"label": "Spider", "path": "holly", "api": "https://usa.eat-peach.sbs"},
    {"label": "Iron", "path": "moviebox", "api": "https://uwu.eat-peach.sbs"},
    {"label": "Multi", "path": "multi", "api": "https://usa.eat-peach.sbs"},
    {"label": "Dark", "path": "net", "api": "https://uwu.eat-peach.sbs"},
]

# Movie format: <{api}/{path}/movie/{tmdb_id}>
# Tv format: <{api}/{path}/tv/{tmdb_id}/{season_number}/{episode_number}>

# --- Game of Thrones ---
title = "Game of Thrones"
type = "tv"
year = "2011"
imdb_id = "tt0944947"
tmdb_id = "1399"
season = "1"
episode = "1"

# Build url and get encrypted text
# Sample server, you can change the server by changing the index
server = servers[0]
url = f"{server['api']}/{server['path']}/{type}/{tmdb_id}/{season}/{episode}"
enc_data = requests.get(url, headers=HEADERS).json()["data"]

# Decrypt
dec_peachify = f"{API}/dec-peachify"
response = requests.post(dec_peachify, json={"text": enc_data}).json()
decrypted = validate(response, dec_peachify)

print(f"\n{'-'*25} Decrypted Data {'-'*25}\n")
print(f"Referer: {HEADERS['Referer']}\n")
print(decrypted)
