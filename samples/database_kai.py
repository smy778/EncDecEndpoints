import requests

API = "https://enc-dec.app/api"
DATABASE = "https://enc-dec.app/db"

"""
--- Database Functions ---

Statistics: https://enc-dec.app/db/kai/

Search database by ID: kai_id, mal_id, or anilist_id
    - Example: https://enc-dec.app/db/kai/find?mal_id=42310

Search by title query (optional: type, year)
    - Example: https://enc-dec.app/db/kai/search?query=cyberpunk&type=tv&year=2022
"""

# --- Cyberpunk Edgerunners ---
# https://myanimelist.net/anime/42310/Cyberpunk__Edgerunners
mal_id = "42310"

"""
Sample query database by mal_id.

Returns a list of matching entries.
For exact ID lookups, the first item is usually the target entry.
If using an imprecise search, multiple items may be returned in the list.
"""
entries = requests.get(f"{DATABASE}/kai/find?mal_id={mal_id}").json()

"""
Pull MegaUp mirrors from the info field.
Pick any that works.
"""
mirrors = entries[0]["info"]["mirrors"]
megaup = mirrors["megaup"][0]

"""
Pull episodes from the first result in the list.

The 'episodes' field contains:
    - titles under the 'title' key
    - episode source token under the 'token' key
    - scraped sources and skips under the 'sources' key

Fallback in case sources have issues:
Info on using the 'token' can be found in animekai.py sample, line 49.
"""
episodes = entries[0]["episodes"]

"""
Sample values to load an embed.
Available type keys may include:
    - sub
    - softsub
    - dub

Server options are keys of episodes[season][episode]["sources"][type]: 
    - "server1"
    - "server2"
"""
season = "1"
episode = "1"
type = "sub"
server = "server1"

"""
Build final media URL.
Combine megaup mirror with media path.
"""
media = episodes[season][episode]["sources"][type][server]
url = f"{megaup}{media}"

print(f"\n{'-'*25} Loaded Url {'-'*25}\n")
print(url)

# Reference the megaup.py sample for how to proceeed with the returned url
