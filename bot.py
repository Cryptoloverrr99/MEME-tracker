import requests

response = requests.get(
    "https://api.dexscreener.com/latest/dex/pairs?q=all",
    headers={},
)
data = response.json()
