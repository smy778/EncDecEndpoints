import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "Accept": "application/json"
}

API = "https://enc-dec.app/api"

# Note: this decryptor supports any url returned by yflix and 1movies, regardless the domain
# --- Cyberpunk Edgerunners ---
url = "https://yflix.to/ajax/links/view?id=cYe--KWj5g&_=VU7EzW-r3IptzPzkwFi43K6fMXG1W-twXRnEjr7jYvY2mi6oJTqlmYTf"
enc = requests.get(url, headers=HEADERS).json()["result"]
dec = decrypted = requests.post(f"{API}/dec-movies-flix", json={"text": enc}).json()["result"]
embed = dec["url"]

# Get referer
referer = embed.split("/e/")[0] + "/"
HEADERS["Referer"] = referer

# Replace /e/ with /media/
media = embed.replace("/e/", "/media/")

# Get encrypted media data
encrypted = requests.get(media, headers=HEADERS).json()['result']

# Decrypt
decrypted = requests.post(f"{API}/dec-rapid", json={"text": encrypted, "agent": HEADERS["User-Agent"]}).json()['result']
print(f"\n{'-'*25} Decrypted Data {'-'*25}\n")
print(f"Referer: {HEADERS['Referer']}\n") # or the embed url's domain
print(decrypted)
