import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "Referer": "https://yflix.to/",
    "Accept": "application/json"
}

API = "https://enc-dec.app/api"
DATABASE = "https://enc-dec.app/db"
YFLIX_AJAX = "https://yflix.to/ajax"

"""
--- Database Functions ---

Statistics: https://enc-dec.app/db/flix/

Search database by ID: flix_id, tmdb_id, imdb_id (optional: type)
    - Example: https://enc-dec.app/db/flix/find?tmdb_id=1399&type=tv

Search by title query (optional: type, year)
    - Example: https://enc-dec.app/db/flix/search?query=game+of+thrones&type=tv&year=2011
"""

# --- Game Of Thrones ---
# https://www.themoviedb.org/tv/1399-game-of-thrones
tmdb_id = "1399"

"""
Sample query database by tmdb_id.

Returns a list of matching entries.
For exact ID lookups, the first item is usually the target entry.
If using an imprecise search, multiple items may be returned in the list.
"""
entries = requests.get(f"{DATABASE}/flix/find?tmdb_id={tmdb_id}").json()

"""
Pull episodes from the first result in the list.

The 'episodes' field contains:
    - titles under the 'title' key
    - episode id under the 'eid' key

Unlike kai database, flix database does not include scraped 'sources'.
"""
episodes = entries[0]["episodes"]

"""
Sample eid to load servers.
"""
season = "1"
episode = "1"
eid = episodes[season][episode]["eid"]

"""
Sample servers data.

Encrypt eid, then request the servers list.
Returned HTML is parsed into a structured servers dictionary.
"""
enc_eid = requests.get(f"{API}/enc-movies-flix?text={eid}").json()["result"]
servers_resp = requests.get(f"{YFLIX_AJAX}/links/list?eid={eid}&_={enc_eid}", headers=HEADERS).json()
servers = requests.post(f"{API}/parse-html", json={"text": servers_resp["result"]}).json()["result"]

"""
Sample server lid to load embed.
Available type keys may include:
    - default

Server options are keys of servers[type]: 
    - "1"
    - "2"
"""
type = "default"
server_id = "1"
lid = servers[type][server_id]["lid"]

"""
Encrypt lid, then request embed data.
"""
enc_lid = requests.get(f"{API}/enc-movies-flix?text={lid}").json()["result"]
embed_resp = requests.get(f"{YFLIX_AJAX}/links/view?id={lid}&_={enc_lid}", headers=HEADERS).json()
encrypted = embed_resp["result"]

# Decrypt
# Note: subtitles url is passed as urlencoded sub.list parameter
decrypted = requests.post(f"{API}/dec-movies-flix", json={"text": encrypted}).json()["result"]
print(f"\n{'-'*25} Decrypted Data {'-'*25}\n")
print(decrypted)

# Reference the rapidshare.py sample for how to proceeed with the returned url
