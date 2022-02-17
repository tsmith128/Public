import os
from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import lxml

# --------------------------------- Read Me------------------------------------------------#
# You will need to use your spotify account to use the API
# Please see API documentation with Spotify
# Author: Terry Smith
# --------------------------------- Read Me------------------------------------------------#

USER = os.getenv('SPOTIFY_CLIENT_ID')
PASSWORD = os.environ.get('SPOTIFY_CLIENT_SECRET')

#Spotify Auth
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        scope="playlist-modify-public",
        redirect_uri="https://example.com",
        client_id=USER,
        client_secret=PASSWORD,
        show_dialog=True,
        cache_path="token.txt"
    )
)
user_id = sp.current_user()["id"]
print(user_id)

# --------------------------------- Getting the 100 songs ------------------------------------#
chosen_date = input("What date to you want to have come rushing back to you? (Please use the format YYYY-MM-DD) ")
print("Please, wait ... I'm getting your songs...")

URL = f"https://www.billboard.com/charts/hot-100/{chosen_date}"

response = requests.get(URL)
page_html = response.text
soup = BeautifulSoup(page_html, "lxml")

music_not_formatted = [item.getText() for item in soup.select(selector="li .o-chart-results-list__item h3")]
songs = [i.strip() for i in music_not_formatted]
print(f"Music: {songs}")

# ------------------------------------ Getting musics URI -------------------------------------#
list_uri = []

user_id = sp.current_user()["id"]

for music in songs:
    result = sp.search(q=f"{music}", type="track", limit=1)
    try:
        uri = result["tracks"]["items"][0]["uri"]
        list_uri.append(uri)
    except IndexError:
        info = f"{music} does not exist in Spotify. Skipped."

print(f"\nList_URI: {list_uri}")

# ---------------------------------- Creating the playlist ------------------------------------#
sp.user_playlist_create(user=user_id, name=f"{chosen_date} Billboard 100")

playlist_id = sp.user_playlists(user=user_id)["items"][0]["id"]
playlist_url = sp.user_playlist(user=user_id, playlist_id=playlist_id)["external_urls"]

# ------------------------------ Adding songs to your playlist -------------------------------#
for uri in list_uri:
    print(f"\nAdding {songs[list_uri.index(uri)]} to your playlist")
    sp.playlist_add_items(playlist_id=playlist_id, items=[uri])

print("\nReady!!")
print(f"\nThe link for your playlist is {playlist_url}")
