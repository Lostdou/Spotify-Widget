import spotipy as sp
from flask import Flask, jsonify
from flask_cors import CORS
import time
import threading
import os
import sys
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv

# Utilizo UTF-8 para evitar problemas con los caracteres especiales 
sys.stdout.reconfigure(encoding='utf-8')

app = Flask(__name__)
CORS(app)

# Inicializa spotify
load_dotenv()
sp = sp.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv('SPOTIFY_CLIENT_ID'),
    client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
    redirect_uri=os.getenv('SPOTIFY_REDIRECT_URI'),
    scope='user-read-currently-playing'
))

user_info = sp.me()
print(f"Logged in as: {user_info['display_name']}")

song_info = {}
previous_track_id = None

def update_track_info():
    global song_info, previous_track_id
    while True:
        current_track = sp.current_user_playing_track()
        if current_track is not None and current_track['is_playing']:
            song_info= {
                'playing': 'true',
                'song_name' : current_track['item']['name'],
                'artist_name' : current_track['item']['artists'][0]['name'],
                'cover_image_url' : current_track['item']['album']['images'][0]['url'],
                'total_duration_ms' : current_track['item']['duration_ms'],
                'progress_ms' : current_track['progress_ms']
            }
            print (song_infO)


            time.sleep(5)
        else:
            song_info ={
                'playing': 'false'
            }
            time.sleep(5)


@app.route('/current-track', methods=['GET'])
def current_track():
    return jsonify(song_info)

if __name__ == '__main__':
    threading.Thread(target=update_track_info, daemon=True).start()
    app.run(debug=True)
