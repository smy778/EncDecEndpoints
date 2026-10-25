import requests
from urllib.parse import quote

HEADERS = {
    "Accept": "*/*",
    "Origin": "https://vidy.st",
    "Referer": "https://vidy.st/",
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

'''
Server     Language     URL
--------------------------------------------------------------------------------------------------------
Miami      Original     https://api.wecollege.net/miami/sources [May have 4K]
Boise      Original     https://api.wecollege.net/boise/sources [May have 4K]
Vegas      Original     https://api.wecollege.net/vegas/sources
Reno       Original     https://api.wecollege.net/reno/sources
Oakland    Original     https://api.wecollege.net/oakland/sources
Seattle    Original     https://api.wecollege.net/seattle/sources
Phoenix    Original     https://api.wecollege.net/phoenix/sources
Atlanta    Original     https://api.wecollege.net/atlanta/sources
Portland   Original     https://api.wecollege.net/portland/sources
Austin     Original     https://api.wecollege.net/austin/sources [FILTERS quality == "English"]
Dallas     Original     https://api.wecollege.net/dallas/sources
Tampa      Original     https://api.wecollege.net/tampa/sources
Orlando    Original     https://api.wecollege.net/orlando/sources
Munich     German       https://api.wecollege.net/munich/sources?language=german
Berlin     German       https://api.wecollege.net/berlin/sources [USES German altTitle when available]
Paris      French       https://api.wecollege.net/paris/sources
Delhi      Hindi        https://api.wecollege.net/delhi/sources [FILTERS quality == "Hindi"]
Cancun     Spanish      https://api.wecollege.net/cancun/sources
'''

# Movie format: <https://api.wecollege.net/{server}/sources?title={title}&mediaType=movie&year={year}&tmdbId={tmdb_id}&imdbId={imdb_id}>
# Tv format: <https://api.wecollege.net/{server}/sources?title={title}&mediaType=tv&year={year}&episodeId={episode_number}&seasonId={season_number}&tmdbId={tmdb_id}&imdbId={imdb_id}>

# --- Game of Thrones ---
title = "Game of Thrones"
type = "tv"
year = "2011"
imdb_id = "tt0944947"
tmdb_id = "1399"
season = "1"
episode = "1"

# Note: double URL-encoding for title
# Game of Thrones -> Game%20of%20Thrones -> Game%2520of%2520Thrones
enc_title = quote(quote(title, safe=""), safe="")

# Get seed data
seed_data = requests.get(f"https://api.wecollege.net/seed?mediaId={tmdb_id}", headers=HEADERS).json()
seed = seed_data["seed"]
enc = "2"  # Algorithm version

# Get encrypted text
server = "miami"
url = f"https://api.wecollege.net/{server}/sources?title={enc_title}&mediaType={type}&year={year}&episodeId={episode}&seasonId={season}&tmdbId={tmdb_id}&imdbId={imdb_id}&enc={enc}&seed={seed}"
enc_data = requests.get(url, headers=HEADERS).text

# Decrypt
dec_videasy = f"{API}/dec-videasy"
response = requests.post(dec_videasy, json={"text": enc_data, "id": tmdb_id, "seed": seed}).json()
decrypted = validate(response, dec_videasy)

print(f"\n{'-'*25} Decrypted Data {'-'*25}\n")
print(f"Referer: {HEADERS['Referer']}\n")
print(decrypted)
