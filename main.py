import time
import requests

# Définir les constantes
DEXSCREENER_API_URL = "https://api.dexscreener.com/token-boosts/latest/v1"
RUGCHECKER_API_URL = "https://api.rugchecker.com/risk"
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

def send_telegram_message(message):
    """Envoie une alerte via Telegram"""
    url = TELEGRAM_API_URL.format(TOKEN=TELEGRAM_BOT_TOKEN)
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }
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

def check_conditions(pair):
    """Vérifie les conditions pour une alerte"""
    market_cap = pair.get("marketCap", 0)
    market = pair.get("market", 0)
    holder = pair.get("holders", 0)
    volume = pair.get("volume", 0)
    trending_position = pair.get("trending_rank", 999)  # Supposons que 999 signifie hors du classement

    return (
        market_cap >= MIN_MARKET_CAP and
        market >= MIN_MARKET and
        holder >= MIN_HOLDER and
        volume >= MIN_VOLUME and
        trending_position <= 10
    )

def main():
    """Fonction principale pour surveiller les memecoins"""
    previous_market_cap = 0

    while True:
        # Récupération des données Dexscreener
        pairs = get_dexscreener_data()
        for pair in pairs:
            if check_conditions(pair):
                # Construction du message d'alerte
                dex_paid = pair.get("dex_paid", "Inconnu")
                message = (
                    f"🚨 Nouvelle détection de memecoin 🚨\n"
                    f"- MarketCap : {pair.get('marketCap')}$\n"
                    f"- Market : {pair.get('market')}\n"
                    f"- Holders : {pair.get('holders')}\n"
                    f"- Volume : {pair.get('volume')}$\n"
                    f"- Trending sur Dexscreener : #{pair.get('trending_rank')}\n"
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
    
