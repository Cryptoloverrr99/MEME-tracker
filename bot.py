import requests

response = requests.get(
    "https://api.dexscreener.com/token-boosts/latest/v1",
    headers={},
)
data = response.json()
