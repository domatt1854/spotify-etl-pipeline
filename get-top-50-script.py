
import requests
import base64
from json import loads
from datetime import datetime

class SpotifyAPI():
    def __init__(self, client_id=None, client_secret=None, token=None):
        self.base_url = "https://api.spotify.com/v1/"
        
        if token:
            self.token = token
            self.auth_bearer = {'Authorization': 'Bearer {}'.format(token)}
        else:
            self.auth_bearer = self.get_auth_token(client_id, client_secret)
    
    def get_auth_token(self, client_id, client_secret):
        auth_url = "https://accounts.spotify.com/api/token"
        encoded_user_pass_creds = base64.b64encode((client_id + ":" + client_secret).encode("ascii")).decode("ascii")
        headers= {
            "Authorization": "Basic {}".format(encoded_user_pass_creds),
            "Content-Type": "application/x-www-form-urlencoded"
        }
        body = { 
            "grant_type": "client_credentials" 
        }
        response = requests.post(
            auth_url,
            headers=headers,
            params=body
        )
        
        self.token = loads(response.content)['access_token']
        return { "Authorization": "Bearer {}".format(self.token) }
        
    
    def request_spotify_api(self, endpoint, method="GET", params=None):
        response = requests.request(
            method,
            self.base_url + endpoint,
            headers= self.auth_bearer,
            params=params
        )
        return loads(response.content)
    
    def get_playlist(self, playlist_id):
        endpoint = "playlists/{}".format(playlist_id)
        return self.request_spotify_api(endpoint)
    
    def get_track(self, track_id):
        endpoint = "tracks/{}".format(track_id)
        return self.request_spotify_api(endpoint)

    def get_album(self, album_id):
        endpoint = "albums/{}".format(album_id)
        return self.request_spotify_api(endpoint)
    
    def process_playlist_data(self, playlist_data):
        csv_data = "track_id,track_name,track_duration_ms,artists,track_popularity,album_id,album_name,album_genres,album_label,album_popularity\n"
        print(csv_data)
        for track_obj in playlist_data['tracks']['items']:
            track = track_obj['track']
            track_id = track['id']
            track_duration_ms = track['duration_ms']
            track_name = track['name']
            track_artists = ";".join(j['name'] for j in track['artists'])
            track_popularity = track['popularity']
            
            album_id = track['album']['id']
            album_name = track['album']['name']
            
            album = self.get_album(album_id)
            genres = ""
            if album['genres']:
                genres = ";".join(album['genres'])
            album_label = album['label']
            album_popularity = album['popularity']
            
            record_str = "{},{},{},{},{},{},{},{},{},{}".format(
                track_id,
                track_name,
                track_duration_ms,
                track_artists,
                track_popularity,
                album_id,
                album_name,
                genres,
                album_label,
                album_popularity
            )
            csv_data = csv_data + record_str + '\n'
            print(record_str)
        
        with open('data/playlist-data-{}.csv'.format(datetime.now().strftime('%m-%d-%Y')), 'w+') as f:
            f.write(csv_data)
        

spotifyAPI = SpotifyAPI(client_id="<INSERT CLIENT ID HERE>", client_secret="INSERT CLIENT SECRET HERE")
token = spotifyAPI.token

# gets tracks of Top 50 - Global
# https://open.spotify.com/playlist/37i9dQZEVXbMDoHDwVN2tF
TOP_50_GLOBAL_ID = "37i9dQZEVXbMDoHDwVN2tF"

playlist_data = spotifyAPI.get_playlist(TOP_50_GLOBAL_ID)
spotifyAPI.process_playlist_data(playlist_data)