import requests
import json
import re
from urllib.parse import urlsplit

# Please reference challenge/byse_optimized.js for js-native pow solver if porting to another language. It's more efficient.
from challenge.byse import solve_pow

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

"""
Extractor works with any site that embeds this player.

Sample sites:
- https://animenosub.to/ -> https://bysesayeveum.com/e/49cza26barcw (embed_origin: https://bysesayeveum.com, code: 49cza26barcw)
- https://1hd.one/ -> https://mfw09.org/e/g2o9pjloqhzb (embed_origin: https://mfw09.org, code: g2o9pjloqhzb)
etc.

Sample setup for 1hd.one.
Note: Set referer to https://1hd.one/ and get embed_url from location response header: request.headers.get("Location")
- Movie: https://0123movie.space/mv/{imdb_id}/{tmdb_id}/
- Series: https://0123movie.space/pl/{tmdb_id}/{season}/{episode}
"""

embed_url = "https://byseraguci.com/d/8o1smi9vfgi2"
embed_origin, code = re.match(r"^(https?://[^/]+)/[A-Za-z]/([^/?#]+)", embed_url).groups()

# Set base headers
HEADERS["Referer"] = embed_url
HEADERS["Origin"] = embed_origin

# Get content details
details_url = f"{embed_origin}/api/videos/{code}/details"
details = requests.get(details_url, headers=HEADERS).json()
frame_url = details["embed_frame_url"]
parsed = urlsplit(frame_url)
frame_base = f"{parsed.scheme}://{parsed.netloc}"

# Update headers for in-frame
HEADERS["Referer"] = frame_url
HEADERS["Origin"] = frame_base

# Get challenge data and encrypt
challenge_url = f"{frame_base}/api/videos/access/challenge"
challenge = requests.post(challenge_url, headers=HEADERS).json()

enc_byse = f"{API}/enc-byse"
enc_response = requests.post(enc_byse, json={"data": challenge}).json()
challenge_response = validate(enc_response, enc_byse)

# Get attestation data for fp and cookie
attest_url = f"{frame_base}/api/videos/access/attest"
attest = requests.post(attest_url, headers=HEADERS, json=challenge_response).json()

fingerprint = {
    "fingerprint": {
        "token": attest["token"],
        "viewer_id": attest["viewer_id"],
        "device_id": attest["device_id"],
        "confidence": attest["confidence"],
    }
}

HEADERS["X-Embed-Parent"] = embed_url
HEADERS["Cookie"] = f"byse_viewer_id={attest['viewer_id']}; byse_device_id={attest['device_id']}"

# Get captcha and solve
captcha_url = f"{frame_base}/api/videos/{code}/embed/captcha"
captcha = requests.post(captcha_url, headers=HEADERS, json=fingerprint).json()
solution = solve_pow(captcha)

# Verify captcha
verify_url = f"{frame_base}/api/videos/{code}/embed/captcha/verify"
verify_json = {
    "pow_token": captcha["pow_token"],
    "solution": solution,
    **fingerprint
}
verify = requests.post(verify_url, headers=HEADERS, json=verify_json).json()
HEADERS["X-Captcha-Token"] = verify["token"]

# Get playback and decrypt
playback_url = f"{frame_base}/api/videos/{code}/embed/playback"
playback = requests.post(playback_url, headers=HEADERS, json=fingerprint).json()

dec_byse = f"{API}/dec-byse"
dec_response = requests.post(dec_byse, json={"data": playback}).json()
decrypted = validate(dec_response, dec_byse)

_headers = { "User-Agent": HEADERS["User-Agent"], "Referer": frame_base, "Origin": frame_base }
print(f"\nHeaders: {json.dumps(_headers)}")
print(f"\n{'-'*25} Decrypted Data {'-'*25}\n")
print(decrypted)
