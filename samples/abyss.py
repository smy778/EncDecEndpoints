import requests
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "Origin": "https://playhydrax.com",
    "Referer": "https://playhydrax.com/"
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

# --- Abyss ---

content_id = "K8R6OOjS7"

# Get encrypted datas
url = f"https://playhydrax.com/?v={content_id}"
response = requests.get(url, headers=HEADERS).text
match = re.search(r'const\s+datas\s*=\s*"([^"]*)"', response)
encrypted = match.group(1)

# Decrypt
dec_abyss = f"{API}/dec-abyss"
response = requests.post(dec_abyss, json={"text": encrypted}).json()
decrypted = validate(response, dec_abyss)

print(f"\n{'-'*25} Decrypted Data {'-'*25}\n")
print(f"Referer: {HEADERS['Referer']}\n")
print(decrypted)
