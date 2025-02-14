from instagrapi import Client
from config import Config

try:
    cl = Client()
    cl.login(username=Config.INSTAGRAM_USERNAME, password=Config.INSTAGRAM_PASSWORD)
    print("Login successful!")  # If this prints, login worked
except Exception as e:
    print(f"Error: {e}")  # Print the *full* error message