import time
import requests

# API URLs
DEXSCREENER_API_URL = "https://api.dexscreener.com/token-boosts/latest/v1"
RUGCHECKER_API_URL = "https://api.rugchecker.com/risk/{token_address}"
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
    requests.post(url, json=payload)

def get_dexscreener_data():
    """Récupère les données Dexscreener"""
    try:
        response = requests.get(DEXSCREENER_API_URL)
        response.raise_for_status()
        return response.json().get("pairs", [])
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
    market_cap = pair.get("marketCap", 0)
    market = pair.get("market", 0)
    holder = pair.get("holders", 0)
    volume = pair.get("volume", 0)
    trending_position = pair.get("trending_rank", 999)  # Supposons que 999 signifie hors du classement

    # Vérifications RugChecker
    dev_holding = rugchecker_data.get("devHolding", 100)
    top_10_holder = rugchecker_data.get("top10Holder", 100)
    liquidity_locked = rugchecker_data.get("liquidityLocked", 0)
    token_score = rugchecker_data.get("tokenScore", "Bad")

    return (
        market_cap >= MIN_MARKET_CAP and
        market >= MIN_MARKET and
        holder >= MIN_HOLDER and
        volume >= MIN_VOLUME and
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
        # Récupération des données Dexscreener
        pairs = get_dexscreener_data()
        for pair in pairs:
            token_address = pair.get("tokenAddress")
            if not token_address:
                continue

            # Récupération des données RugChecker
            rugchecker_data = get_rugchecker_data(token_address)

            if check_conditions(pair, rugchecker_data):
                # Construction du message d'alerte
                dex_paid = pair.get("dex_paid", "Inconnu")
                message = (
                    f"🚨 Nouvelle détection de memecoin 🚨\n"
                    f"- MarketCap : {pair.get('marketCap')}$\n"
                    f"- Market : {pair.get('market')}\n"
                    f"- Holders : {pair.get('holders')}\n"
                    f"- Volume : {pair.get('volume')}$\n"
                    f"- Trending sur Dexscreener : #{pair.get('trending_rank')}\n"
                    f"- Dev Holding : {rugchecker_data.get('devHolding')}%\n"
                    f"- Top 10 Holder : {rugchecker_data.get('top10Holder')}%\n"
                    f"- Liquidity Locked : {rugchecker_data.get('liquidityLocked')}%\n"
                    f"- Token Score : {rugchecker_data.get('tokenScore')}\n"
                    f"- Dex Paid : {dex_paid}"
                )
                send_telegram_message(message)
                previous_market_cap = pair.get("marketCap", 0)

        # Vérification de l'augmentation du MarketCap
        for pair in pairs:
            market_cap = pair.get("marketCap", 0)
            if market_cap - previous_market_cap >= MARKET_CAP_INCREMENT:
                message_update = f"🔄 Mise à jour : MarketCap a augmenté de 50k$ ! Nouveau MarketCap : {market_cap}$"
                send_telegram_message(message_update)
                previous_market_cap = market_cap

        # Pause de 2 minutes
        time.sleep(120)

if __name__ == "__main__":
    print("🔍 Démarrage du tracker de memecoins...")
    main()
    
