#!/bin/bash

# Update and upgrade the system
echo "Updating and upgrading the system..."
sudo apt-get update -y
sudo apt-get upgrade -y

# Install Python3 and pip if not already installed
echo "Installing Python3 and pip..."
sudo apt-get install python3 python3-pip -y

# Install dependencies for Tkinter (GUI)
echo "Installing Tkinter..."
sudo apt-get install python3-tk -y

# Install additional dependencies
echo "Installing required Python libraries..."

# Install Spotipy (Spotify API library)
sudo pip3 install spotipy

# Install Requests (for HTTP requests)
sudo pip3 install requests

# Install Pillow (for image handling)
sudo pip3 install pillow

# If you don't have threading installed (it's usually built-in in Python), you can install it.
# However, threading is part of the standard library, so it should be available by default.

echo "All dependencies installed successfully."

# Verify installation
echo "Verifying installation..."
python3 -c "import tkinter; import spotipy; import requests; import PIL; print('Dependencies verified!')"

echo "Installation complete!"
