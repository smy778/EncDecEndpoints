import requests
from urllib.parse import quote
from base64 import b64decode

HEADERS = {
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

# Movie format: <https://primesrc.me/api/v1/s?imdb={IMDB_ID}&type=movie>
# Tv format: <https://primesrc.me/embed/tv?imdb={IMDB_ID}&season={season_number}&episode={episode_number}&type=tv>
# Some options may be available with tmdb id instead of imdb

# --- Game of Thrones ---
title = "Game of Thrones"
type = "tv"
year = "2011"
imdb_id = "tt0944947"
tmdb_id = "1399"
season = "1"
episode = "1"

# Request api for primesrc
primesrc_api = f"https://primesrc.me/api/v1/s?imdb={imdb_id}&season={season}&episode={episode}&type={type}"
response = requests.get(primesrc_api, headers=HEADERS).json()

# Sample the first server
# Note: there are multiple server options in response, with different sizes, languages, and qualities.
# For reference, run: print(response)

server = response["servers"][0]
name = server["name"]
key = server["key"]

# Get embed url using api
embed_api = f"https://primesrc.me/api/v1/l?key={key}"
solve_primesrc = f"{API}/solve-primesrc?url={quote(embed_api)}"
response = requests.get(solve_primesrc).json()
link = validate(response, solve_primesrc)

print(f"\n{'-'*25} Requested Link {'-'*25}\n")
print(f"Host: {name}")
print(f"Link: {link}")
print('\n' + b64decode('Rm9yIGVtYmVkIGRlY3J5cHRvcnMsIHJlZmVyZW5jZSB0aGUgZm9sbG93aW5nIHJlcG86IGh0dHBzOi8vZ2l0aHViLmNvbS95b2dlc2gtaGFja2VyL01lZGlhVmFuY2VkL3RyZWUvbWFpbi9zaXRlcw==').decode('utf-8'))