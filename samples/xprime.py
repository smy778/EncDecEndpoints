import json
import requests
import hashlib
import base64
from time import time
from urllib.parse import quote

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "Referer": "https://mznxiwqjdiq00239q.space/"
}

API = "https://enc-dec.app/api"

# Altcha solving utilities
def solver(data):
    algorithm = data["algorithm"]
    challenge = data["challenge"]
    salt = data["salt"]
    maxnumber = data["maxnumber"]

    t = hex(((1 << 256) - 1) // (maxnumber + 1))[2:].rjust(64, "0")

    lim = maxnumber * 10
    for number in range(lim + 1):
        h = hashlib.sha256(f"{algorithm}:{challenge}:{salt}:{number}".encode()).hexdigest()
        if h <= t:
            return number

    return -1

def solve_altcha():
    url = f"https://mznxiwqjdiq00239q.space/altcha/challenge"
    response = requests.get(url)
    challenge = response.json()

    start = time()
    number = solver(challenge)

    if number < 0:
        raise Exception("PoW solving failed")

    took = int((time() - start) * 1000)

    payload = {
        "algorithm": challenge["algorithm"],
        "challenge": challenge["challenge"],
        "maxnumber": challenge["maxnumber"],
        "number": number,
        "salt": challenge["salt"],
        "signature": challenge["signature"],
        "took": took
    }

    return base64.b64encode(json.dumps(payload).encode()).decode()

# Note that there are different servers, find them here: https://mznxiwqjdiq00239q.space/servers
# Sample servers list: ["primenet", "finger", "primebox", "king", "facile", "lighter", "fed", "eek"]

# Movie format: <https://mznxiwqjdiq00239q.space/{server}?name={title}&year={year}&id={tmdb_id}&imdb={imdb_id}>
# Tv format: <https://mznxiwqjdiq00239q.space/{server}?name={title}&year={year}&id={tmdb_id}&imdb={imdb_id}&season={season_number}&episode={episode_number}>

# --- Cyberpunk Edgerunners ---
title = "Cyberpunk: Edgerunners"
type = "tv"
year = "2022"
imdb_id = "tt12590266"
tmdb_id = "105248"
season = "1"
episode = "1"

# Solve Altcha challenge
altcha = solve_altcha()

# Get encrypted text
server = "primebox"
url = f"https://mznxiwqjdiq00239q.space/{server}?name={quote(title)}&year={year}&id={tmdb_id}&imdb={imdb_id}&season={season}&episode={episode}&altcha={altcha}"
encrypted = requests.get(url, headers=HEADERS).text

# Decrypt
decrypted = requests.post(f"{API}/dec-xprime", json={"text": encrypted}).json()['result']
print(f"\n{'-'*25} Decrypted Data {'-'*25}\n")
print(f"Referer: {HEADERS['Referer']}\n")
print(decrypted)
