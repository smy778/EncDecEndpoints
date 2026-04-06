import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "Referer": "https://animekai.to/",
    "Accept": "application/json"
}

API = "https://enc-dec.app/api"
DATABASE = "https://enc-dec.app/db"
KAI_AJAX = "https://animekai.to/ajax"

'''
--- Database Functions ---

Statistics: https://enc-dec.app/api/db/kai/

Search database by ID: kai_id, mal_id, or anilist_id
    - Example: https://enc-dec.app/api/db/kai/find?mal_id=42310
Search by title query (optional: type, year)
    - Example: https://enc-dec.app/api/db/kai/search?query=cyberpunk&type=tv&year=2022
'''

# --- Cyberpunk Edgerunners ---
# https://myanimelist.net/anime/42310/Cyberpunk__Edgerunners
mal_id = "42310"

# Query database by mal_id
entries = requests.get(f"{DATABASE}/kai/find?mal_id={mal_id}").json()

# Pull episodes from first result in list.
# If doing imprecise search, muliple items may be returned.
# 'episodes' field contains titles under 'title' key, and episode tokens under 'token' key.
episodes = entries[0]["episodes"]

# Sample token to load servers
season = "1"
episode = "1"
token = episodes[season][episode]["token"]

enc_token = requests.get(f"{API}/enc-kai?text={token}").json()["result"]
servers_resp = requests.get(f"{KAI_AJAX}/links/list?token={token}&_={enc_token}", headers=HEADERS).json()
servers = requests.post(f"{API}/parse-html", json={"text": servers_resp["result"]}).json()["result"]

# Sample server lid to load embed
type = "sub"  # other options are dictionary keys: 'sub', 'softsub', 'dub'
server_id = "1"  # server options are keys of servers[type] dictionary: '1', '2', etc.
lid = servers[type][server_id]["lid"]

enc_lid = requests.get(f"{API}/enc-kai?text={lid}").json()["result"]
embed_resp = requests.get(f"{KAI_AJAX}/links/view?id={lid}&_={enc_lid}", headers=HEADERS).json()
encrypted = embed_resp["result"]

# Decrypt
decrypted = requests.post(f"{API}/dec-kai", json={"text": encrypted}).json()["result"]
print(f"\n{'-'*25} Decrypted Data {'-'*25}\n")
print(decrypted)

# Reference the megaup.py sample for how to proceeed with the returned url
