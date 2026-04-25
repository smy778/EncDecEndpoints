import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "Accept": "application/json"
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

# Note: this decryptor supports any url returned by animekai, regardless the domain
# --- Cyberpunk Edgerunners ---
url = "https://animekai.to/ajax/links/view?id=dIG98qei6A&_=xQm9tJfLwGhz_0Eq8S_YAHYkwp-qSvLfm50W5X1nyd2NnAcpzTUWyAgck4I"
enc = requests.get(url, headers=HEADERS).json()["result"]
dec = decrypted = requests.post(f"{API}/dec-kai", json={"text": enc}).json()["result"]
embed = dec["url"]

# Get referer
referer = embed.split("/e/")[0] + "/"
HEADERS["Referer"] = referer

# Replace /e/ with /media/
media = embed.replace("/e/", "/media/")

# Get encrypted media data
encrypted = requests.get(media, headers=HEADERS).json()['result']

# Decrypt
dec_mega = f"{API}/dec-mega"
response = requests.post(dec_mega, json={"text": encrypted, "agent": HEADERS["User-Agent"]}).json()
decrypted = validate(response, dec_mega)

print(f"\n{'-'*25} Decrypted Data {'-'*25}\n")
print(f"Referer: {HEADERS['Referer']}\n") # or the embed url's domain
print(decrypted)
