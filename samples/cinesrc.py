import json
import requests
import hashlib
import base64

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
def solve_stage1(data):
    challenge = data["p"]
    difficulty = data["d"]

    hash = hashlib.sha256(challenge.encode())

    for i in range(1 << 64):
        key = format(i, "x")

        digest = hash.copy()
        digest.update(key.encode("utf-8"))

        if int.from_bytes(digest.digest(), "big") >> (256 - difficulty) == 0:
            return key

    raise RuntimeError("no solution found")

def solve_stage2(data):
    target = data["pack"][0][::-1]
    salt = data["pack"][3][::-1]
    r = data["pack"][4][::-1]

    decode = lambda s: base64.urlsafe_b64decode(s + "=" * (-len(s) % 4)).decode()

    body = decode(r.split(".")[1])
    payload = decode(body.split(".", 1)[1])
    difficulty = json.loads(payload)["d"]

    width = (difficulty + 3) // 4

    for counter in range(1 << difficulty):
        key = format(counter, "x").zfill(width)
        digest = hashlib.sha256((salt + key).encode()).hexdigest()

        if digest == target:
            return key

    raise RuntimeError("no solution found")

def pow():
    challenge1 = requests.get("https://cinesrc.st/api/c/issue", headers=HEADERS).json()
    stage1 = {
        "challenge": challenge1,
        "solution": solve_stage1(challenge1)
    }

    challenge2 = requests.get("https://cinesrc.st/api/c/stage2/issue", headers=HEADERS).json()
    stage2 = {
        "challenge": challenge2,
        "solution": solve_stage2(challenge2)
    }

    return {
        "stage1": stage1,
        "stage2": stage2
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

url = f"https://cinesrc.st/embed/tv/{imdb_id}?s={season}&e={episode}"

# Get challenges and solve
challenge_data = pow()

# Get encrypted token and headers
enc_cinesrc = f"{API}/enc-cinesrc"
payload = {
    "url": url,
    "agent": HEADERS["User-Agent"],
    "challenge_data": challenge_data
}

response = requests.post(enc_cinesrc, json=payload).json()
data = validate(response, enc_cinesrc)

token = data["token"]
key = data["key"]

headers = data["headers"]
getProviderList = headers["getProviderList"]
getStream = headers["getStream"]

# Get providers and parse
headers = {**HEADERS, "Next-Action": getProviderList}
payload = []

providers_text = requests.post(url, headers=headers, data=json.dumps(payload)).text
line = providers_text.splitlines()[1].split(":", 1)[1]
providers = json.loads(line)

# Sample second provider and parse encrypted data
provider = providers[1]["id"]
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

streams_text = response.text
line = streams_text.splitlines()[1]
encrypted = line.split(",", 1)[1].split(":", 1)[0]

# Decrypt
dec_cinesrc = f"{API}/dec-cinesrc"
response = requests.post(dec_cinesrc, json={"text": encrypted, "key": key}).json()
decrypted = validate(response, dec_cinesrc)

print(f"\n{'-'*25} Decrypted Data {'-'*25}\n")
print(f"Referer: {HEADERS['Referer']}\n")
print(decrypted)
