import requests
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "Referer": "https://animekai.to/",
    "Accept": "application/json"
}

API = "https://enc-dec.app/api"
KAI_AJAX = "https://animekai.to/ajax"

# --- Cyberpunk Edgerunners ---
url = "https://animekai.to/watch/cyberpunk-edgerunners-x6qm"

"""
Extract content id.
"""
html = requests.get(url, headers=HEADERS).text
content_id = re.search(r'<div[^>]*id="anime-rating"[^>]*data-id="([^"]+)"', html).group(1)

"""
Sample episodes data.

Encrypt content id, then request the episodes list.
Returned HTML is parsed into a structured episodes dictionary.
"""
enc_id = requests.get(f"{API}/enc-kai?text={content_id}").json()["result"]
episodes_resp = requests.get(f"{KAI_AJAX}/episodes/list?ani_id={content_id}&_={enc_id}", headers=HEADERS).json()
episodes = requests.post(f"{API}/parse-html", json={"text": episodes_resp["result"]}).json()["result"]

"""
Sample token to load servers.

The 'episodes' field contains:
    - titles under the 'title' key
    - episode source token under the 'token' key
"""
season = "1"
episode = "1"
token = episodes[season][episode]["token"]

"""
Sample servers data.

Encrypt token, then request the servers list.
Returned HTML is parsed into a structured servers dictionary.
"""
enc_token = requests.get(f"{API}/enc-kai?text={token}").json()["result"]
servers_resp = requests.get(f"{KAI_AJAX}/links/list?token={token}&_={enc_token}", headers=HEADERS).json()
servers = requests.post(f"{API}/parse-html", json={"text": servers_resp["result"]}).json()["result"]

"""
Sample server lid to load embed.
Available type keys may include:
    - sub
    - softsub
    - dub

Server options are keys of servers[type]: 
    - "1"
    - "2"
"""
type = "sub"
server_id = "1"
lid = servers[type][server_id]["lid"]

"""
Encrypt lid, then request embed data.
"""
enc_lid = requests.get(f"{API}/enc-kai?text={lid}").json()["result"]
embed_resp = requests.get(f"{KAI_AJAX}/links/view?id={lid}&_={enc_lid}", headers=HEADERS).json()
encrypted = embed_resp["result"]

# Decrypt
decrypted = requests.post(f"{API}/dec-kai", json={"text": encrypted}).json()["result"]
print(f"\n{'-'*25} Decrypted Data {'-'*25}\n")
print(decrypted)

# Reference the megaup.py sample for how to proceeed with the returned url
