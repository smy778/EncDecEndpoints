import requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
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

# --- OneTouchTV ---

content_url = "https://api3.devcorp.me/web/vod/150294-ghost-train-2024/episode/1"

# Get encrypted data
encrypted = requests.get(content_url, headers=HEADERS).text

# Decrypt
dec_onetouchtv = f"{API}/dec-onetouchtv"
response = requests.post(dec_onetouchtv, json={"text": encrypted}).json()
decrypted = validate(response, dec_onetouchtv)

print(f"\n{'-'*25} Decrypted Data {'-'*25}\n")
print(decrypted)
