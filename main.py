import spotipy
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

# UTF-8 configuration
sys.stdout.reconfigure(encoding='utf-8')

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Load environment variables and initialize Spotify client
load_dotenv()
spotify_client = spotipy.Spotify(auth_manager=SpotifyOAuth(
    client_id=os.getenv('SPOTIFY_CLIENT_ID'),
    client_secret=os.getenv('SPOTIFY_CLIENT_SECRET'),
    redirect_uri=os.getenv('SPOTIFY_REDIRECT_URI'),
    scope='user-read-currently-playing'
))

# Fetch user info
try:
    user_info = spotify_client.me()
    logging.info(f"Logged in as: {user_info['display_name']}")
except Exception as e:
    logging.error("Failed to authenticate with Spotify API", exc_info=e)
    sys.exit(1)

# Global variables for track info
song_info = {}
song_info_lock = Lock()

def update_track_info():
    global song_info
    while True:
        try:
            current_track = spotify_client.current_user_playing_track()
            with song_info_lock:
                if current_track and current_track.get('is_playing'):
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
            logging.debug(f"Updated song info: {song_info}")
        except Exception as e:
            logging.error("Error fetching track info", exc_info=e)
        time.sleep(5)

@app.route('/current-track', methods=['GET'])
def current_track():
    with song_info_lock:
        return jsonify(song_info)

if __name__ == '__main__':
    threading.Thread(target=update_track_info, daemon=True).start()
    app.run(debug=True)
