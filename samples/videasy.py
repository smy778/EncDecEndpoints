import requests
from urllib.parse import quote

HEADERS = {
    "Accept": "*/*",
    "Origin": "https://cineby.sc",
    "Referer": "https://cineby.sc/",
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
-----------------------------------------------------------------------------------------------
Neon       Original     https://api.videasy.net/mb-flix/sources-with-title
Yoru       Original     https://api.videasy.net/cdn/sources-with-title
Cypher     Original     https://api.videasy.net/moviebox/sources-with-title
Sage       Original     https://api.videasy.net/1movies/sources-with-title
Breach     Original     https://api.videasy.net/m4uhd/sources-with-title
Vyse       Original     https://api.videasy.net/hdmovie/sources-with-title  [FILTERS quality == "English"]
Killjoy    German       https://api.videasy.net/meine/sources-with-title?language=german
Harbor     Italian      https://api.videasy.net/meine/sources-with-title?language=italian
Chamber    French       https://api.videasy.net/meine/sources-with-title?language=french  [MOVIE ONLY]
Fade       Hindi        https://api.videasy.net/hdmovie/sources-with-title  [FILTERS quality == "Hindi"]
Omen       Spanish      https://api.videasy.net/lamovie/sources-with-title
Raze       Portuguese   https://api.videasy.net/superflix/sources-with-title

** Note: Use api.videasy.net or api2.videasy.net
'''

# Movie format: <https://api.videasy.net/{server}/sources-with-title?title={title}&mediaType=movie&year={year}&tmdbId={tmdb_id}&imdbId={imdb_id}>
# Tv format: <https://api.videasy.net/{server}/sources-with-title?title={title}&mediaType=tv&year={year}&episodeId={episode_number}&seasonId={season_number}&tmdbId={tmdb_id}&imdbId={imdb_id}>

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

# Get encrypted text
server = "cdn"
url = f"https://api.videasy.net/{server}/sources-with-title?title={enc_title}&mediaType={type}&year={year}&episodeId={episode}&seasonId={season}&tmdbId={tmdb_id}&imdbId={imdb_id}"
enc_data = requests.get(url, headers=HEADERS).text

# Decrypt
dec_videasy = f"{API}/dec-videasy"
response = requests.post(dec_videasy, json={"text": enc_data, "id": tmdb_id}).json()
decrypted = validate(response, dec_videasy)

print(f"\n{'-'*25} Decrypted Data {'-'*25}\n")
print(f"Referer: {HEADERS['Referer']}\n")
print(decrypted)
