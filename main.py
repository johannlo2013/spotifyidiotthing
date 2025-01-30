import tkinter as tk
from tkinter import messagebox
import requests
from PIL import Image, ImageTk
import threading
import webbrowser
from io import BytesIO

# Spotify API credentials
CLIENT_ID = '193c038b988e474496a09b04f0f8131b'
CLIENT_SECRET = '7fd55f0965da4c1caf838b9fa4dae541'
REDIRECT_URI = 'http://localhost:8888/callback'
AUTH_URL = 'https://accounts.spotify.com/authorize'
TOKEN_URL = 'https://accounts.spotify.com/api/token'

# Scopes for controlling playback
SCOPE = 'user-library-read user-modify-playback-state user-read-playback-state'

# Spotify Web API URLs
BASE_URL = 'https://api.spotify.com/v1'
CURRENT_PLAYBACK_URL = BASE_URL + '/me/player/currently-playing'
NEXT_TRACK_URL = BASE_URL + '/me/player/next'
PREVIOUS_TRACK_URL = BASE_URL + '/me/player/previous'

# Variables for track info and playback state
current_track = {"title": "Demo Track", "album_art": None}
access_token = None


# Step 1: Authorize the user and get the authorization code
def get_authorization_url():
    auth_url = f'{AUTH_URL}?client_id={CLIENT_ID}&response_type=code&redirect_uri={REDIRECT_URI}&scope={SCOPE}'
    return auth_url


# Step 2: Exchange the authorization code for an access token
def get_access_token(auth_code):
    data = {
        'grant_type': 'authorization_code',
        'code': auth_code,
        'redirect_uri': REDIRECT_URI,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    response = requests.post(TOKEN_URL, data=data, headers=headers)

    if response.status_code == 200:
        tokens = response.json()
        return tokens['access_token']
    else:
        messagebox.showerror("Authentication Error", "Failed to authenticate with Spotify API.")
        return None


# Function to fetch current playback info from Spotify API
def get_current_playback():
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(CURRENT_PLAYBACK_URL, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        messagebox.showerror("Error", "Error fetching playback information from Spotify.")
        return None


# Function to skip to the next track
def next_track():
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.post(NEXT_TRACK_URL, headers=headers)
    
    if response.status_code == 204:
        update_current_track_info()
    else:
        messagebox.showerror("Error", "Error skipping to next track.")


# Function to go to the previous track
def previous_track():
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.post(PREVIOUS_TRACK_URL, headers=headers)
    
    if response.status_code == 204:
        update_current_track_info()
    else:
        messagebox.showerror("Error", "Error skipping to previous track.")


# Function to start or pause playback
def toggle_play_pause():
    current_playback = get_current_playback()
    if current_playback and current_playback.get('is_playing'):
        pause_playback()
    else:
        start_playback()


# Function to pause playback
def pause_playback():
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.put(f'{BASE_URL}/me/player/pause', headers=headers)
    
    if response.status_code == 204:
        play_pause_button.config(image=play_icon)


# Function to start playback
def start_playback():
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.put(f'{BASE_URL}/me/player/play', headers=headers)
    
    if response.status_code == 204:
        play_pause_button.config(image=pause_icon)


# Function to update current track info
def update_current_track_info():
    current_playback = get_current_playback()
    if current_playback:
        track_name = current_playback['item']['name']
        album_image_url = current_playback['item']['album']['images'][0]['url']
        current_track['title'] = track_name
        current_track['album_art'] = album_image_url
        update_ui()


# Function to update the UI
def update_ui():
    track_label.config(text=f"{current_track['title']}")
    if current_track["album_art"]:
        fetch_album_art()
    
    current_playback = get_current_playback()
    if current_playback and current_playback.get('progress_ms') is not None:
        timestamp = format_timestamp(current_playback['progress_ms'])
        timestamp_label.config(text=f"Time: {timestamp}")

        progress_ms = current_playback['progress_ms']
        total_ms = current_playback['item']['duration_ms']
        progress_ratio = progress_ms / total_ms
        update_progress(progress_ratio)


# Format the timestamp (milliseconds to minutes:seconds)
def format_timestamp(ms):
    seconds = ms // 1000
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes:02}:{seconds:02}"


# Update progress bar and circular indicator
def update_progress(progress_ratio):
    progress_bar.coords(progress_line, 50, 250, 50 + (400 * progress_ratio), 250)
    progress_bar.coords(progress_dot, 50 + (400 * progress_ratio) - 8, 242, 50 + (400 * progress_ratio) + 8, 258)


# Threaded function to fetch album art
def fetch_album_art():
    threading.Thread(target=download_and_update_image).start()


def download_and_update_image():
    try:
        response = requests.get(current_track["album_art"])
        img_data = response.content
        image = Image.open(BytesIO(img_data))
        image = image.resize((120, 120))  # Resize image to fit the UI
        album_art = ImageTk.PhotoImage(image)

        if not hasattr(album_art_label, "image") or album_art_label.image != album_art:
            album_art_label.config(image=album_art)
            album_art_label.image = album_art  # Keep a reference to prevent garbage collection
    except Exception as e:
        print(f"Error fetching album art: {e}")


# Create UI elements
root = tk.Tk()
root.title("Spotify Car Thing")
root.geometry("480x360")
root.config(bg="white")

# Track information
current_track = {"title": "Demo Track", "album_art": None}

track_label = tk.Label(root, text=f"{current_track['title']}", font=("Inter", 18), bg="white", fg="black")
track_label.pack(pady=10)

# Placeholder for album art
album_art_placeholder = ImageTk.PhotoImage(image=Image.new('RGB', (50, 50), color='white'))  # Gray placeholder
album_art_label = tk.Label(root, image=album_art_placeholder, bg="white")
album_art_label.pack(pady=10)

# Load PNG icons
play_icon = ImageTk.PhotoImage(Image.open("play.png").resize((40, 40)))  # Adjust path as needed
pause_icon = ImageTk.PhotoImage(Image.open("pause.png").resize((40, 40)))  # Adjust path as needed
next_icon = ImageTk.PhotoImage(Image.open("skip-forward.png").resize((40, 40)))  # Adjust path as needed
prev_icon = ImageTk.PhotoImage(Image.open("skip-back.png").resize((40, 40)))  # Adjust path as needed

# Play/Pause Button
skip_buttons_frame = tk.Frame(root, bg="white")

play_pause_button = tk.Button(skip_buttons_frame, image=play_icon, bg="white", bd=0, command=toggle_play_pause)
play_pause_button.pack(side=tk.LEFT, padx=5)

previous_button = tk.Button(skip_buttons_frame, image=prev_icon, bg="white", bd=0, command=previous_track)
previous_button.pack(side=tk.LEFT, padx=5)

next_button = tk.Button(skip_buttons_frame, image=next_icon, bg="white", bd=0, command=next_track)
next_button.pack(side=tk.LEFT, padx=5)

skip_buttons_frame.pack(pady=20)

# Timestamp Display
timestamp_label = tk.Label(root, text="Time: 00:00", font=("Inter", 14), bg="white", fg="black")
timestamp_label.pack(pady=5)

# Progress Bar & Circular Indicator
progress_frame = tk.Frame(root, bg="white")
progress_frame.pack(pady=20)

progress_bar = tk.Canvas(progress_frame, width=400, height=10, bg="gray", bd=0)
progress_bar.pack()

progress_line = progress_bar.create_line(50, 250, 50, 250, width=5, fill="green")
progress_dot = progress_bar.create_oval(50 - 8, 242, 50 + 8, 258, fill="green", outline="green")


# Periodic update (every 500ms)
def periodic_update():
    update_current_track_info()
    root.after(500, periodic_update)  # Update every 500ms


# Start periodic updates
periodic_update()

root.mainloop()
