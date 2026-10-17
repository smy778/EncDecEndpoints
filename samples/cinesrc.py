import json
import requests
import base64

from challenge.cinesrc import solve_stage1, solve_stage2

HEADERS = {
    "Origin": "https://cinesrc.st",
    "Referer": "https://cinesrc.st/",
    "Content-Type": "text/plain;charset=UTF-8",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.37 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.37"
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

# Challenge solving utilities
def pow(url, cookies):
    headers = {**HEADERS, **cookies}

    challenge1 = requests.get("https://cinesrc.st/api/c/issue", headers=headers).json()

    payload = {
        "data": {
            "url": url,
            "user_agent": HEADERS["User-Agent"],
            "challenge_data": challenge1
        },
        "type": "seed"
    }

    enc_cinesrc = f"{API}/enc-cinesrc"
    response = requests.post(enc_cinesrc, json=payload).json()
    data = validate(response, enc_cinesrc)

    seed = data["seed"]
    state = data["state"]

    stage1 = {
        "challenge": challenge1,
        "solution": solve_stage1(challenge1, seed)
    }

    challenge2 = requests.get("https://cinesrc.st/api/c/stage2/issue", headers=headers).json()
    stage2 = {
        "challenge": challenge2,
        "solution": solve_stage2(challenge2)
    }

    return {
        "challenge_data": {
            "stage1": stage1,
            "stage2": stage2
        },
        "state": state
    }

# Cookie utilities
def cookie(type, tmdb_id, season, episode):
    fields = [type, tmdb_id, season, episode]
    encoded = base64.urlsafe_b64encode(json.dumps(fields, separators=(",", ":")).encode()).decode().rstrip("=")
    
    headers = {**HEADERS, "x-cs-q": encoded}
    bootstrap = requests.post("https://cinesrc.st/api/c/bootstrap", headers=headers).json()
    
    return {
        "x-cs-b": "20261014-a",
        "x-cs-q": encoded,
        "x-cs-r": bootstrap["r"],
        "x-cs-p": bootstrap["p"],
    }

# Movie format: <https://cinesrc.st/embed/movie/{IMDB_ID}>
# Tv format: <https://cinesrc.st/embed/tv/{IMDB_ID}?s={season_number}&e={episode_number}>

# --- Game of Thrones ---
title = "Game of Thrones"
type = "tv"
year = "2011"
imdb_id = "tt0944947"
tmdb_id = "1399"
season = "1"
episode = "1"

url = f"https://cinesrc.st/embed/tv/{tmdb_id}?s={season}&e={episode}"

# Get challenges and solve
cookies = cookie(type, tmdb_id, season, episode)
data = pow(url, cookies)

# Get encrypted token and headers
enc_cinesrc = f"{API}/enc-cinesrc"
payload = {
    "data": {
        "url": url,
        "user_agent": HEADERS["User-Agent"],
        **data
    },
    "type": "encrypt"
}

response = requests.post(enc_cinesrc, json=payload).json()
data = validate(response, enc_cinesrc)

token = f"{data['token']}::c3::{cookies['x-cs-r']}"
headers = data["headers"]
state = data["state"]

getProviderList = headers["getProviderList"]
getStream = headers["getStream"]

# Get providers and parse
headers = {**HEADERS, "Next-Action": getProviderList}
payload = []

providers_text = requests.post(url, headers=headers, data=json.dumps(payload)).text
line = providers_text.splitlines()[1].split(":", 1)[1]
providers = json.loads(line)

# Sample second provider and parse encrypted data
server_index = 0 # <- sample server index, inspect the providers list for more details with: print(providers)
provider = providers[server_index]["id"]
headers = {**HEADERS, "Next-Action": getStream}
payload = [
    tmdb_id,
    "show" if type == "tv" else type,
    season if type == "tv" else "$undefined",
    episode if type == "tv" else "$undefined",
    token,
    provider
]

response = requests.post(url, headers=headers, data=json.dumps(payload))

# Validate the response status code, 500 -> retry with another provider from list
if response.status_code != 200:
    print(f"Try another server.\nProvider error: {provider} -> {response.status_code}")
    raise SystemExit

encrypted = response.text

# Decrypt
dec_cinesrc = f"{API}/dec-cinesrc"
response = requests.post(dec_cinesrc, json={"text": encrypted, "state": state}).json()
decrypted = validate(response, dec_cinesrc)

print(f"\n{'-'*25} Decrypted Data {'-'*25}\n")
print(f"Referer: {HEADERS['Referer']}\n")
print(decrypted)
