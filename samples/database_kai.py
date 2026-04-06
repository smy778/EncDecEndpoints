import requests

API = "https://enc-dec.app/api"
DATABASE = "https://enc-dec.app/db"

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

# Pull megaup mirrors from info field. Pick any that work.
mirrors =  entries[0]["info"]["mirrors"]
megaup = mirrors["megaup"][0]

# Pull episodes from first result in list.
# If doing imprecise search, muliple items may be returned in the outer list.
# 'episodes' field contains titles under 'title' key, and episode tokens under 'token' key.
episodes = entries[0]["episodes"]

# Sample to load embed
season = "1"
episode = "1"
type = "sub"  # other options are dictionary keys: 'sub', 'softsub', 'dub' (if available)
server = "server1"  # server options are keys of sources[type] dictionary: 'server1', 'server2', etc.

media = episodes[season][episode]["sources"][type][server]
url = f"{megaup}{media}"

print(f"\n{'-'*25} Loaded Url {'-'*25}\n")
print(url)

# Reference the megaup.py sample for how to proceeed with the returned url
