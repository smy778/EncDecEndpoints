from urllib.parse import urlparse
import requests
import json
import re

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "Referer": "https://vidsrc.cc/"
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

'''
Vidsrc.cc uses two servers: UpCloud and VidPlay
UpCloud - embeds iframe from megacloud / vidcloud
VidPlay - raw hls streams

Note: season / episode parameters should be omitted if the content is not a series
'''

# --- Cyberpunk Edgerunners ---
title = "Cyberpunk: Edgerunners"
type = "tv"
year = "2022"
imdb_id = "tt12590266"
tmdb_id = "105248"
season = "1"
episode = "1"

# Iframe extraction
def from_iframe(url):
    # Get source url
    html_iframe = requests.get(url, headers=HEADERS).text
    source_encoded = re.search(r'var\s+source\s*=\s*"([^"]+)"', html_iframe).group(1)
    source_unescaped = json.loads(f'"{source_encoded}"')

    # Get domain and embed type, 'embed-1' or 'embed-2' etc
    parsed = urlparse(source_unescaped)
    domain = parsed.netloc
    embed_type = parsed.path.split("/", 2)[1]

    # Construct new headers for source requests
    _HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
        "Referer": f"https://{domain}/",
        "X-Requested-With": "XMLHttpRequest"
    }
    
    # Parse source fields
    html_source = requests.get(source_unescaped, headers=_HEADERS).text
    video_id = re.search(r'<title>File\s+#([A-Za-z0-9]+)\s*-', html_source).group(1)
    
    match = re.search(r'\b[a-zA-Z0-9]{48}\b', html_source) or re.search(r'\b([a-zA-Z0-9]{16})\b.*?\b([a-zA-Z0-9]{16})\b.*?\b([a-zA-Z0-9]{16})\b', html_source)
    nonce = ''.join(match.groups()) if match and match.lastindex == 3 else match.group()

    # Get streams data
    api = f"https://{domain}/{embed_type}/v3/e-1/getSources?id={video_id}&_k={nonce}"
    streams_data = requests.get(api, headers=_HEADERS).json()
    return streams_data, _HEADERS["Referer"]

# Request embed
embed = f"https://vidsrc.cc/v2/embed/{type}/{imdb_id}/{season}/{episode}"
html = requests.get(embed, headers=HEADERS).text

# Parse script fields
v = re.search(r'var v = "(.*?)";', html).group(1)
user_id = re.search(r'var userId = "(.*?)";', html).group(1)
movie_id = re.search(r'var movieId = "(.*?)";', html).group(1)

# Generate vrf token
enc_vidsrc = f"{API}/enc-vidsrc?user_id={user_id}&movie_id={movie_id}"
response = requests.get(enc_vidsrc).json()
encrypted = validate(response, enc_vidsrc)

# Get servers
servers = f"https://vidsrc.cc/api/{movie_id}/servers?id={movie_id}&type={type}&v={v}&vrf={encrypted}&imdbId={imdb_id}&season={season}&episode={episode}"
servers_data = requests.get(servers, headers=HEADERS).json()
servers_parsed = {server["name"]: server["hash"] for server in servers_data["data"]}

# Sample 'VidPlay' server
hash_vidplay = servers_parsed.get('VidPlay')
if hash_vidplay:
    source_vidplay = f"https://vidsrc.cc/api/source/{hash_vidplay}"
    data_vidplay = requests.get(source_vidplay, headers=HEADERS).json()
    
    if not data_vidplay['success']:
        raise Exception("Bad response from VidPlay source API")
    streams_vidplay = data_vidplay['data']

    print(f"\n{'-'*25} Streams Data VidPlay {'-'*25}\n")
    print(f"Referer: {HEADERS['Referer']}\n")
    print(streams_vidplay)

# Sample 'UpCloud' server
hash_upcloud = servers_parsed.get('UpCloud')
if hash_upcloud:
    source_upcloud = f"https://vidsrc.cc/api/source/{hash_upcloud}"
    data_upcloud = requests.get(source_upcloud, headers=HEADERS).json()

    if not data_upcloud['success']:
        raise Exception("Bad response from UpCloud source API")
    streams_upcloud, referer = from_iframe(data_upcloud['data']['source'])

    print(f"\n{'-'*25} Streams Data UpCloud {'-'*25}\n")
    print(f"Referer: {referer}\n")
    print(streams_upcloud)
