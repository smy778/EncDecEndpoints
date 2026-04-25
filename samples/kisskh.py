import requests
from urllib.parse import quote

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

# --- KissKH ---

content_id = "192143"

# Get streams content
enc_kisskh_vid = f"{API}/enc-kisskh?text={content_id}&type=vid"
response = requests.get(enc_kisskh_vid).json()
vid_key = validate(response, enc_kisskh_vid)

url = f"https://kisskh.do/api/DramaList/Episode/{content_id}.png?err=false&ts=&time=&kkey={vid_key}"
video_response = requests.get(url, headers=HEADERS).json()

# Get subtitles content
enc_kisskh_sub = f"{API}/enc-kisskh?text={content_id}&type=sub"
response = requests.get(enc_kisskh_sub).json()
sub_key = validate(response, enc_kisskh_sub)

url = f"https://kisskh.do/api/Sub/{content_id}?kkey={sub_key}"
subtitle_response = requests.get(url, headers=HEADERS).json()

# Decrypt first subtitle content
subtitle = subtitle_response[0]['src']
subtitle_decrypt = requests.get(f"{API}/dec-kisskh?url={quote(subtitle)}").text

print(f"\n{'-'*25} Sample Response Data {'-'*25}\n")
print("Video:\n", video_response)
print("\nSubtitle:\n", subtitle_response)
print("\nDecrypted Subtitle:\n", subtitle_decrypt[:200])
