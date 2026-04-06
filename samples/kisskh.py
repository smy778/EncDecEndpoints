import requests
from urllib.parse import quote

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "Accept": "application/json"
}

API = "https://enc-dec.app/api"

# --- KissKH ---

content_id = "192143"

# Get streams content
vid_key = requests.get(f"{API}/enc-kisskh?text={content_id}&type=vid").json()['result']
url = f"https://kisskh.do/api/DramaList/Episode/{content_id}.png?err=false&ts=&time=&kkey={vid_key}"
video_response = requests.get(url, headers=HEADERS).json()

# Get subtitles content
sub_key = requests.get(f"{API}/enc-kisskh?text={content_id}&type=sub").json()['result']
url = f"https://kisskh.do/api/Sub/{content_id}?kkey={sub_key}"
subtitle_response = requests.get(url, headers=HEADERS).json()

# Decrypt first subtitle content
subtitle = subtitle_response[0]['src']
subtitle_decrypt = requests.get(f"{API}/dec-kisskh?url={quote(subtitle)}").text

print(f"\n{'-'*25} Sample Response Data {'-'*25}\n")
print("Video:\n", video_response)
print("\nSubtitle:\n", subtitle_response)
print("\nDecrypted Subtitle:\n", subtitle_decrypt[:200])
