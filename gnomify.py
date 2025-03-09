from dotenv import load_dotenv
from tqdm import tqdm
import requests
import argparse
import time
import re
import os
load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_sec = os.getenv("CLIENT_SEC")

token = "IDK"

def is_token_expired(token):
    url = "https://api.spotify.com/v1/me"  # Test endpoint
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    
    if response.status_code == 401:  # Unauthorized (Token Expired)
        error_data = response.json()
        return True  # Token is expired
    return False  # Token is valid



def getToken():
    url = "https://accounts.spotify.com/api/token"
    data = {
    "grant_type": "client_credentials",
    "client_id": client_id,
    "client_secret": client_sec
    }
    response = requests.post(url, data=data)

    if response.status_code == 200:
        return response.json()["access_token"]
        print(f"Access Token: {token}")

### fetch playlist
def get_playlist_name(playlist_id, access_token):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get("name", "Unknown Playlist")
    return "Unknown Playlist"

def fetchPlaylist(playlist_id,token):
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    params = {"limit": 100, "offset": 0}
    tracks_info = []
    while True:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200:
            print("Error fetching data:", response.json())
            return None
        
        data = response.json()
        if params["offset"] == 0:
            playlist_name = get_playlist_name(playlist_id, token)
        
        for item in data.get("items", []):
            track = item.get("track")
            if track:
                isrc = track["external_ids"].get("isrc", "N/A")
                tracks_info.append({
                    "song_name": track["name"],
                    "isrc": isrc
                })
        
        if not data.get("next"):
            break
        params["offset"] += 100
    
    return {"playlist_name": playlist_name, "tracks": tracks_info}

### fetch track

def fetchDownloadLink(isrc):
    api_url = f"https://eu.qobuz.squid.wtf/api/get-music?q={isrc}&offset=0"
    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()
        # Extract the first track's ID
        first_track_id = data["data"]["tracks"]["items"][0]["id"] if data["data"]["tracks"]["items"] else None
    else:
        print(f"Error: {response.status_code}, {response.text}")
    res = requests.get(f"https://eu.qobuz.squid.wtf/api/download-music?track_id={first_track_id}&quality=27")

    if res.status_code == 200:
        data = res.json()

        # Extract the first track's ID
        link = data["data"]["url"]

        # Print the result
        return link
    else:
        print(f"Error: {response.status_code}, {response.text}")


### Download song

def downloader(dir,songname,link):
    ## add file existing check
    file_path = f"{dir}/{songname}.flac"
    attempt = 0 
    while attempt < 2:
        try:
            # Send a GET request with stream mode
            response = requests.get(link, stream=True)
            response.raise_for_status()

            # Get the total file size in bytes
            total_size = int(response.headers.get("content-length", 0))

            # Open file and write in chunks
            with open(file_path, "wb") as file, tqdm(
                total=total_size, unit="B", unit_scale=True, desc="Downloading"
            ) as progress_bar:
                for chunk in response.iter_content(chunk_size=8192):
                    file.write(chunk)
                    progress_bar.update(len(chunk))

            print(f"Download complete: {file_path}")
            return True
        except Exception as e:
            print(f"Download failed (Attempt {attempt+1}/3): {e}")
            time.sleep(2)
    print(f"something went wrong could not download {songname}")
    return False


def extract_spotify_playlist_id(url):
    """Extracts the playlist ID from a given Spotify playlist URL."""
    match = re.search(r"playlist/([a-zA-Z0-9]+)", url)
    return match.group(1)

### main 

token = getToken()

parser = argparse.ArgumentParser(description="Download a FLAC file from a given URL.")
parser.add_argument("-u","--url", help="URL of the FLAC file to download")
args = parser.parse_args()
playlist_id = extract_spotify_playlist_id(args.url)
pl = fetchPlaylist(playlist_id,token)
print(f"Downloading: {pl['playlist_name']} | Total Tracks {len(pl['tracks'])} ")
## add dir check
if os.path.exists(pl["playlist_name"]):
    print("Adding to exisiting folder")
else:
    print(f"creating folder for playlist : {pl['playlist_name']}")
    os.mkdir(pl["playlist_name"])
for i in pl["tracks"]:
    print(f"Fetching: {i['song_name']}... ")
    link = fetchDownloadLink(i["isrc"])
    if os.path.exists(f"{pl['playlist_name']}/{i['song_name']}.flac"):
        print(f"{i['song_name']} exist ... Skiping!")
    else:
        downloader(pl["playlist_name"],i["song_name"],link)