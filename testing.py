import requests
from config import Config

access_token="EAAJIy77ivtIBO6ZAeJYSSAE4HpFgR22xuxph7iaCn8s3eOLNFNHo7JUOvd59PsseZCwOjhzZAlpPAql2cXbGYoz0eFc1saZBIrCOwVbjMs26BVBf0oSXrIEhSz1NhscAYsf2FZBOsXmZBGZBHjyJ4kE1Efu8kubBvymIcw80hBZBGmKBYwy5ZBdYaundGtvxPLMUpFUkk2WhjM81DFZAgzZAIpmSe0oBv6eGzpk8vkZD"  # Get from config.py

api_url = "https://graph.instagram.com/me/instagram_accounts"
params = {"access_token": access_token}

try:
    response = requests.get(api_url, params=params)
    print(response.status_code)  # Print the status code
    print(response.text)        # Print the full response text
    response.raise_for_status()  # Check for HTTP errors

    data = response.json()
    print(data) # print the json data

except requests.exceptions.RequestException as e:
    print(f"Error: {e}")