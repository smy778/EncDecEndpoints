import requests
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "Referer": "https://yflix.to/",
    "Accept": "application/json"
}

API = "https://enc-dec.app/api"
YFLIX_AJAX = "https://yflix.to/ajax"

# 1movies and yflix are the same site with different domains, pick either
# --- Cyberpunk Edgerunners ---
url = "https://yflix.to/watch/cyberpunk-edgerunners.b4d24"

"""
Extract content id.
"""
html = requests.get(url, headers=HEADERS).text
content_id = re.search(r'<div[^>]*id="movie-rating"[^>]*data-id="([^"]+)"', html).group(1)

"""
Sample episodes data.

Encrypt content id, then request the episodes list.
Returned HTML is parsed into a structured episodes dictionary.
"""
enc_id = requests.get(f"{API}/enc-movies-flix?text={content_id}").json()["result"]
episodes_resp = requests.get(f"{YFLIX_AJAX}/episodes/list?id={content_id}&_={enc_id}", headers=HEADERS).json()
episodes = requests.post(f"{API}/parse-html", json={"text": episodes_resp["result"]}).json()["result"]

"""
Sample eid to load servers.

The 'episodes' field contains:
    - titles under the 'title' key
    - episode id under the 'eid' key
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
