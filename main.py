import spotipy as sp
from flask import Flask, jsonify
from flask_cors import CORS
import time
import threading
import os
import sys
import logging
from spotipy.oauth2 import SpotifyOAuth
from dotenv import load_dotenv
from threading import Lock

# Utilizo UTF-8 para evitar problemas con los caracteres especiales 
sys.stdout.reconfigure(encoding='utf-8')

logging.basicConfig(level=logging.DEBUG)

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
        try:
            current_track = spotify_client.current_user_playing_track()
            with song_info_lock:
                if current_track and current_track['is_playing']:
                    song_info = {
                        'playing': True,
                        'song_name': current_track['item']['name'],
                        'artist_name': current_track['item']['artists'][0]['name'],
                        'cover_image_url': current_track['item']['album']['images'][0]['url'],
                        'total_duration_ms': current_track['item']['duration_ms'],
                        'progress_ms': current_track['progress_ms']
                    }
                else:
                    song_info = {'playing': False}
            logging.debug(f"Updated track info: {song_info}")
        except Exception as e:
            logging.error("Error updating track info", exc_info=e)
        time.sleep(5)


@app.route('/current-track', methods=['GET'])
def current_track():
    return jsonify(song_info)

if __name__ == '__main__':
    threading.Thread(target=update_track_info, daemon=True).start()
    app.run(debug=True)
