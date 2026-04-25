import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "Referer": "https://smashystream.top/"
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

# --- Shawshank Redemption ---
title = "Shawshank Redemption"
type = "movie"
year = "1994"
imdb_id = "tt0111161"
tmdb_id = "278"

'''
Working servers:
Player SY - smashystream [type 1]
Player SM - short2embed [type 2]
Player O - videoophim [type 2]
Player FS - videofsh [type 2]

Sample player urls:
https://api.smashystream.top/api/v1/__SERVER__/__IMDB_ID__/__TMDB_ID__?token=__TOKEN__&user_id=__ID__ - Movie
https://api.smashystream.top/api/v1/__SERVER__/__IMDB_ID__/__TMDB_ID__/__S__/__E__?token=__TOKEN__&user_id=__ID__ - TV Show S-E

* Also note that /dec-vidstack endpoint uses 'type' field, if not specified defaults to '1'
'''

def listParser(text):
    items = []
    result = {}

    text = text.strip().rstrip(',').replace(' or ', ',')
    for s in text.split(','):
        if s := s.strip():
            items.append(s)
    
    for s in items:
        if s.startswith('[') and ']' in s:
            key, val = s[1:].split(']', 1)
            result[key.strip()] = val.strip()
        else:
            result.setdefault('default', []).append(s)

    return result

# Get token data to load player
token_data = requests.get(f"{API}/enc-vidstack").json()['result']

# === Sample smashystream [type 1] ===

# Get player parts
url = f"https://api.smashystream.top/api/v1/videosmashyi/{imdb_id}?token={token_data['token']}&user_id={token_data['user_id']}"
response = requests.get(url, headers=HEADERS).json()
host, id = response['data'].split("/#")

# Get encrypted stream data
stream_url = f"{host}/api/v1/video?id={id}"
encrypted = requests.get(stream_url, headers=HEADERS).text

# Decrypt
dec_vidstack = f"{API}/dec-vidstack"
response = requests.post(dec_vidstack, json={"text": encrypted, "type": "1"}).json()
decrypted = validate(response, dec_vidstack)

print(f"\n{'-'*25} Type 1 Decrypted Data {'-'*25}\n")
print(f"Referer: {HEADERS['Referer']}\n")
print(decrypted)

# === Sample videofsh [type 2] ===

# Get player parts
url = f"https://api.smashystream.top/api/v1/videofsh/{tmdb_id}?token={token_data['token']}&user_id={token_data['user_id']}"
response = requests.get(url, headers=HEADERS).json()

# Get encrypted file
file = response['data']['sources'][0]['file']
subtitles = response['data'].get('tracks', "")

# Decrypt
dec_vidstack = f"{API}/dec-vidstack"
response = requests.post(dec_vidstack, json={"text": file, "type": "2"}).json()
decrypted = validate(response, dec_vidstack)

print(f"\n{'-'*25} Type 2 Decrypted Data {'-'*25}\n")
print(f"Referer: {HEADERS['Referer']}\n")
print(listParser(decrypted))
print(listParser(subtitles))
