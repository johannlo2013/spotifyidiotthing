import tkinter as tk
from tkinter import messagebox
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.exceptions import SpotifyException
from PIL import Image, ImageTk
import requests
from io import BytesIO
import threading

# Spotify authentication
SPOTIPY_CLIENT_ID = '193c038b988e474496a09b04f0f8131b'
SPOTIPY_CLIENT_SECRET = '7fd55f0965da4c1caf838b9fa4dae541'
SPOTIPY_REDIRECT_URI = 'http://localhost:8888/callback'

# Set up Spotipy authentication
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=SPOTIPY_CLIENT_ID,
                                               client_secret=SPOTIPY_CLIENT_SECRET,
                                               redirect_uri=SPOTIPY_REDIRECT_URI,
                                               scope="user-library-read user-modify-playback-state user-read-playback-state"))

# Create a basic window
root = tk.Tk()
root.title("Spotify Idiot Thing")
root.geometry("480x360")  # Adjusted window size to 480x360
root.config(bg="white")

# Simulated track information (will update dynamically)
current_track = {
    "title": "Demo Track",
    "album_art": None  # Initially set to None, will be updated with real album art
}

# Format the timestamp (milliseconds to minutes:seconds)
def format_timestamp(ms):
    seconds = ms // 1000
    minutes = seconds // 60
    seconds = seconds % 60
    return f"{minutes:02}:{seconds:02}"

# Update track info and UI based on the current track
def update_ui():
    # Update track title only if it has changed
    if track_label.cget("text") != current_track["title"]:
        track_label.config(text=f"{current_track['title']}")
    
    if current_track["album_art"]:
        # Only fetch the album art if it's not already downloaded
        fetch_album_art()

    # Update timestamp only if it has changed
    current_playback = sp.current_playback()
    if current_playback and current_playback.get('progress_ms') is not None:
        timestamp = format_timestamp(current_playback['progress_ms'])
        if timestamp_label.cget("text") != f"Time: {timestamp}":
            timestamp_label.config(text=f"Time: {timestamp}")
        
        progress_ms = current_playback['progress_ms']
        total_ms = current_playback['item']['duration_ms']
        progress_ratio = progress_ms / total_ms
        update_progress(progress_ratio)

def fetch_album_art():
    # Download album art image asynchronously
    threading.Thread(target=download_and_update_image).start()

def download_and_update_image():
    try:
        response = requests.get(current_track["album_art"])
        img_data = response.content
        image = Image.open(BytesIO(img_data))
        image = image.resize((120, 120))  # Resize image to fit the UI
        album_art = ImageTk.PhotoImage(image)

        # Only update album art if it has changed
        if not hasattr(album_art_label, "image") or album_art_label.image != album_art:
            album_art_label.config(image=album_art)
            album_art_label.image = album_art  # Keep a reference to prevent garbage collection
    except Exception as e:
        print(f"Error fetching album art: {e}")

# Update progress bar and circular indicator
def update_progress(progress_ratio):
    # Update line progress (horizontal line)
    progress_bar.coords(progress_line, 50, 250, 50 + (400 * progress_ratio), 250)
    
    # Update circular indicator (dot moves along the line)
    progress_bar.coords(progress_dot, 50 + (400 * progress_ratio) - 8, 242, 50 + (400 * progress_ratio) + 8, 258)

# Play/Pause function
def toggle_play_pause():
    try:
        current_playback = sp.current_playback()
        if current_playback['is_playing']:
            sp.pause_playback()
            play_pause_button.config(image=play_icon)  # Change icon to Play
        else:
            sp.start_playback()
            play_pause_button.config(image=pause_icon)  # Change icon to Pause
    except SpotifyException as e:
        messagebox.showerror("Spotify Error", f"Error while toggling play/pause: {e}")

# Skip to the next track
def next_track():
    try:
        sp.next_track()
        update_current_track_info()
    except SpotifyException as e:
        messagebox.showerror("Spotify Error", f"Error while skipping to next track: {e}")

# Go to the previous track
def previous_track():
    try:
        sp.previous_track()
        update_current_track_info()
    except SpotifyException as e:
        messagebox.showerror("Spotify Error", f"Error while going to previous track: {e}")

# Update the track info from Spotify API
def update_current_track_info():
    try:
        current_playback = sp.current_playback()
        if current_playback and current_playback.get('item'):
            track_name = current_playback['item']['name']
            album_image_url = current_playback['item']['album']['images'][0]['url']

            # Save current track information
            current_track['title'] = track_name
            current_track['album_art'] = album_image_url

            # Update the UI with the new information
            update_ui()
    except SpotifyException as e:
        messagebox.showerror("Spotify Error", f"Error while fetching track info: {e}")

# Create UI elements
track_label = tk.Label(root, text=f"{current_track['title']}", font=("Inter", 18), bg="white", fg="black")
track_label.pack(pady=10)

# Placeholder for album art (replace with actual image if you have one)
album_art_placeholder = ImageTk.PhotoImage(image=Image.new('RGB', (50, 50), color='white'))  # Gray placeholder
album_art_label = tk.Label(root, image=album_art_placeholder, bg="white")
album_art_label.pack(pady=10)

# Load PNG icons
play_icon = ImageTk.PhotoImage(Image.open("/Users/johannlo/idiotthing/play.png").resize((40, 40)))  # Adjust size as necessary
pause_icon = ImageTk.PhotoImage(Image.open("/Users/johannlo/idiotthing/play.png").resize((40, 40)))  # Adjust size as necessary
next_icon = ImageTk.PhotoImage(Image.open("/Users/johannlo/idiotthing/skip-forward.png").resize((40, 40)))  # Adjust size as necessary
prev_icon = ImageTk.PhotoImage(Image.open("/Users/johannlo/idiotthing/skip-back.png").resize((40, 40)))  # Adjust size as necessary

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

# Progress bar (horizontal line)
progress_bar = tk.Canvas(progress_frame, width=400, height=10, bg="white", bd=0)
progress_bar.pack()

# Progress line (initially empty)
progress_line = progress_bar.create_line(50, 250, 50, 250, width=5, fill="green")

# Circular indicator (dot moving along the line)
progress_dot = progress_bar.create_oval(50 - 8, 242, 50 + 8, 258, fill="green", outline="green")

# Set up the periodic update (every 1000 ms = 1 second)
def periodic_update():
    update_current_track_info()
    root.after(500, periodic_update)  # Call this function again after 0.5 second for quicker updates

# Start the periodic updates
periodic_update()

root.mainloop()
