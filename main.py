import time
import requests

# API URLs
DEXSCREENER_API_URL = "https://api.dexscreener.com/latest/dex/tokens"
SOLSCAN_API_URL = "https://api.solscan.io/account/{address}"
TELEGRAM_API_URL = "https://api.telegram.org/bot{TOKEN}/sendMessage"

# Configuration
SOLSCAN_API_KEY = "votre_cle_api_solscan"  # Mettez votre clé API Solscan
TELEGRAM_BOT_TOKEN = "8048350512:AAGVN4uZEt_D1q-ycNN6jhRo-PMn64ZHgiI"
TELEGRAM_CHAT_ID = "1002359674981"

# Conditions minimales
MIN_MARKET_CAP = 150000
MIN_LIQUIDITY = 90000
LIQUIDITY_LOCKED_THRESHOLD = 99
MIN_HOLDER = 100
MIN_VOLUME = 500000
DEV_HOLDING_THRESHOLD = 10
TOP_10_HOLDER_THRESHOLD = 25
MARKET_CAP_INCREMENT = 50000

def send_telegram_message(message):
    """Envoie une alerte via Telegram."""
    url = TELEGRAM_API_URL.format(TOKEN=TELEGRAM_BOT_TOKEN)
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
    requests.post(url, json=payload)

def get_dexscreener_data():
    """Récupère les données Dexscreener."""
    try:
        response = requests.get(DEXSCREENER_API_URL)
        response.raise_for_status()
        return response.json().get("pairs", [])
    except requests.RequestException as e:
        print(f"Erreur API Dexscreener: {e}")
        return []

def get_solscan_data(address):
    """Récupère les données Solscan pour une adresse."""
    headers = {"Accept": "application/json", "Token": SOLSCAN_API_KEY}
    try:
        response = requests.get(SOLSCAN_API_URL.format(address=address), headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Erreur API Solscan: {e}")
        return {}

def check_dex_conditions(pair):
    """Vérifie les conditions Dexscreener pour une alerte."""
    market_cap = pair.get("marketCap", 0)
    liquidity = pair.get("liquidity", {}).get("usd", 0)
    holder = pair.get("holders", 0)
    volume = pair.get("volume", 0)
    liquidity_locked = pair.get("liquidity_locked", 0)  # Simulation pour ce champ

    return (
        market_cap >= MIN_MARKET_CAP and
        liquidity >= MIN_LIQUIDITY and
        holder >= MIN_HOLDER and
        volume >= MIN_VOLUME and
        liquidity_locked >= LIQUIDITY_LOCKED_THRESHOLD
    )

def check_solscan_conditions(solscan_data):
    """Vérifie les conditions Solscan pour une alerte."""
    dev_holding = solscan_data.get("devHolding", 100)
    top_10_holder = solscan_data.get("top10Holder", 100)
    dev_sold = solscan_data.get("devSold", 1)  # Simulation pour ce champ

    return (
        dev_holding <= DEV_HOLDING_THRESHOLD and
        top_10_holder <= TOP_10_HOLDER_THRESHOLD and
        dev_sold <= 1  # Pas de vente significative du développeur
    )

def main():
    """Fonction principale pour surveiller les memecoins."""
    previous_market_caps = {}

    while True:
        # Récupération des données Dexscreener
        pairs = get_dexscreener_data()
        for pair in pairs:
            token_address = pair.get("tokenAddress")
            if not token_address:
                continue

            # Vérification des conditions Dexscreener
            if check_dex_conditions(pair):
                # Récupération des données Solscan
                solscan_data = get_solscan_data(token_address)

                # Vérification des conditions Solscan
                if check_solscan_conditions(solscan_data):
                    # Construction du message d'alerte
                    message = (
                        f"🚨 Nouvelle détection de memecoin 🚨\n"
                        f"- MarketCap : {pair.get('marketCap')}$\n"
                        f"- Liquidity : {pair.get('liquidity', {}).get('usd', 0)}$\n"
                        f"- Liquidity Locked : {pair.get('liquidity_locked', 'Inconnu')}%\n"
                        f"- Dev Holding : {solscan_data.get('devHolding', 'Inconnu')}%\n"
                        f"- Top 10 Holder : {solscan_data.get('top10Holder', 'Inconnu')}%\n"
                        f"- Dev Sold > 1% (premières 10 minutes) : Non\n"
                        f"- Holders : {pair.get('holders')}\n"
                        f"- Volume : {pair.get('volume')}$"
                    )
                    send_telegram_message(message)

                    # Vérification de l'augmentation du MarketCap
                    current_market_cap = pair.get("marketCap", 0)
                    previous_market_cap = previous_market_caps.get(token_address, 0)

                    if current_market_cap - previous_market_cap >= MARKET_CAP_INCREMENT:
                        message_update = (
                            f"🔄 Mise à jour : MarketCap a augmenté de 50k$ pour {token_address} ! "
                            f"Nouveau MarketCap : {current_market_cap}$"
                        )
                        send_telegram_message(message_update)
                        previous_market_caps[token_address] = current_market_cap

        # Pause de 2 minutes
        time.sleep(120)

if __name__ == "__main__":
    print("🔍 Démarrage du tracker de memecoins...")
    main()
    
