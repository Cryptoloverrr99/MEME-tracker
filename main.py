import time
import requests

# API URLs
DEXSCREENER_API_URL = "https://api.dexscreener.com/latest/dex/pairs?q=all"
RUGCHECKER_API_URL = "https://api.rugdoc.io/v2/project/{token_address}"
TELEGRAM_API_URL = "https://api.telegram.org/bot{TOKEN}/sendMessage"

# Configuration de l'alerte Telegram
TELEGRAM_BOT_TOKEN = "8048350512:AAGVN4uZEt_D1q-ycNN6jhRo-PMn64ZHgiI"
TELEGRAM_CHAT_ID = "1002359674981"

# Conditions minimales
MIN_MARKET_CAP = 150000
MIN_MARKET = 200
MIN_HOLDER = 100
MIN_VOLUME = 500000
MARKET_CAP_INCREMENT = 50000
DEV_HOLDING_THRESHOLD = 10  # En pourcentage
TOP_10_HOLDER_THRESHOLD = 20  # En pourcentage
LIQUIDITY_LOCKED_THRESHOLD = 100  # En pourcentage
REQUIRED_TOKEN_SCORE = "Good"

def send_telegram_message(message):
    """Envoie une alerte via Telegram"""
    url = TELEGRAM_API_URL.format(TOKEN=TELEGRAM_BOT_TOKEN)
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    try:
        requests.post(url, json=payload)
    except requests.RequestException as e:
        print(f"Erreur lors de l'envoi Telegram : {e}")

def get_dexscreener_data():
    """Récupère les données Dexscreener"""
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    try:
        response = requests.get(DEXSCREENER_API_URL, headers=headers)
        response.raise_for_status()
        return response.json()  # Correction ici (suppression de .get("pairs"))
    except requests.RequestException as e:
        print(f"Erreur API Dexscreener: {e}")
        return []

def get_rugchecker_data(token_address):
    """Récupère les données RugChecker pour un token"""
    try:
        response = requests.get(RUGCHECKER_API_URL.format(token_address=token_address))
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Erreur API RugChecker: {e}")
        return {}

def check_conditions(pair, rugchecker_data):
    """Vérifie les conditions pour une alerte"""
    market_cap = pair.get("marketCap", 0) or 0
    trending_position = pair.get("trending_rank", 999)
    
    # Valeurs sécurisées avec .get()
    dev_holding = rugchecker_data.get("devHolding", 100)
    top_10_holder = rugchecker_data.get("top10Holder", 100)
    liquidity_locked = rugchecker_data.get("liquidityLocked", 0)
    token_score = rugchecker_data.get("tokenScore", "Bad")

    return (
        market_cap >= MIN_MARKET_CAP and
        pair.get("market", 0) >= MIN_MARKET and
        pair.get("holders", 0) >= MIN_HOLDER and
        pair.get("volume", 0) >= MIN_VOLUME and
        trending_position <= 10 and
        dev_holding <= DEV_HOLDING_THRESHOLD and
        top_10_holder <= TOP_10_HOLDER_THRESHOLD and
        liquidity_locked == LIQUIDITY_LOCKED_THRESHOLD and
        token_score == REQUIRED_TOKEN_SCORE
    )

def main():
    """Fonction principale pour surveiller les memecoins"""
    previous_market_cap = 0

    while True:
        pairs = get_dexscreener_data()
        
        for pair in pairs:
            token_address = pair.get("tokenAddress")
            if not token_address:
                continue

            rugchecker_data = get_rugchecker_data(token_address)
            
            if check_conditions(pair, rugchecker_data):
                message = (
                    f"🚨 Nouvelle détection de memecoin 🚨\n"
                    f"- MarketCap : {pair.get('marketCap', 0)}$\n"
                    f"- Holders : {pair.get('holders', 0)}\n"
                    f"- Volume : {pair.get('volume', 0)}$\n"
                    f"- Trending : #{pair.get('trending_rank', 'Inconnu')}\n"
                    f"- Dev Holding : {rugchecker_data.get('devHolding', 'Inconnu')}%\n"
                    f"- Top 10 Holder : {rugchecker_data.get('top10Holder', 'Inconnu')}%"
                )
                send_telegram_message(message)
                previous_market_cap = pair.get("marketCap", 0)

        # Vérification de l'augmentation du MarketCap
        for pair in pairs:
            market_cap = pair.get("marketCap", 0)
            if market_cap - previous_market_cap >= MARKET_CAP_INCREMENT:
                send_telegram_message(f"🔄 MarketCap +50k$ ! Nouveau : {market_cap}$")
                previous_market_cap = market_cap

        time.sleep(120)

if __name__ == "__main__":
    print("🔍 Démarrage du tracker de memecoins...")
    main()
