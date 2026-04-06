import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "Referer": "https://megaup.live/",
    "Accept": "application/json"
}

API = "https://enc-dec.app/api"

# Note: this decryptor supports any url returned by animekai, regardless the domain
# --- Cyberpunk Edgerunners ---
embed = "https://megaup.live/e/1sitL2f3WS2JcOLwGLtN7RfpCQ"

# Replace /e/ with /media/
media = embed.replace("/e/", "/media/")

# Get encrypted media data
encrypted = requests.get(media, headers=HEADERS).json()['result']

# Decrypt
decrypted = requests.post(f"{API}/dec-mega", json={"text": encrypted, "agent": HEADERS["User-Agent"]}).json()['result']
print(f"\n{'-'*25} Decrypted Data {'-'*25}\n")
print(f"Referer: {HEADERS['Referer']}\n") # or the embed url's domain
print(decrypted)
