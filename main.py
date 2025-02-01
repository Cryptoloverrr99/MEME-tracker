import requests
import logging

logging.basicConfig(level=logging.INFO)

DEXSCREENER_API_URL = "https://api.dexscreener.com/token-boosts/latest/v1"
RUGCHECKER_API_URL = "https://api.rugchecker.com/check"

# Paramètres de Telegram
TELEGRAM_API_URL = "https://api.telegram.org/bot{}/sendMessage"
TELEGRAM_BOT_TOKEN = "8048350512:AAGVN4uZEt_D1q-ycNN6jhRo-PMn64ZHgiI"  # Remplacez par votre token
TELEGRAM_CHAT_ID = "1002359674981"  # Remplacez par votre chat ID


def send_telegram_message(message):
    """Envoie une alerte sur Telegram."""
    try:
        url = TELEGRAM_API_URL.format(TELEGRAM_BOT_TOKEN)
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message}
        response = requests.post(url, json=payload)
        response.raise_for_status()
        logging.info("Message envoyé sur Telegram.")
    except Exception as e:
        logging.error(f"Erreur lors de l'envoi sur Telegram : {e}")


def get_dexscreener_data():
    try:
        response = requests.get(DEXSCREENER_API_URL)
        response.raise_for_status()
        return response.json().get("data", [])
    except Exception as e:
        logging.error(f"Erreur lors de la récupération des données Dexscreener : {e}")
        return []


def get_rugchecker_data(token_address):
    try:
        response = requests.get(f"{RUGCHECKER_API_URL}?token={token_address}")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logging.error(f"Erreur lors de la récupération des données RugChecker : {e}")
        return {}


def check_conditions():
    dexscreener_data = get_dexscreener_data()
    if not dexscreener_data:
        return False

    market_cap = dexscreener_data[0].get("marketCap", 0)
    volume_1h = dexscreener_data[0].get("volume", {}).get("1h", 0)
    transactions = dexscreener_data[0].get("txns", {}).get("count", 0)
    holders = dexscreener_data[0].get("holders", 0)
    dex_paid = dexscreener_data[0].get("dexPaid", False)
    trending_rank = dexscreener_data[0].get("trendingRank", 999)

    if market_cap < 200000:
        logging.info("MarketCap inférieur au seuil requis.")
        return False
    if volume_1h < 1000000:
        logging.info("Volume 1h inférieur au seuil requis.")
        return False
    if transactions < 5000:
        logging.info("Nombre de transactions insuffisant.")
        return False
    if holders < 500:
        logging.info("Nombre de holders insuffisant.")
        return False
    if not dex_paid:
        logging.info("Token non payé sur Dex.")
        return False
    if trending_rank > 10:
        logging.info("Le token n'est pas dans le top 10 sur Dexscreener.")
        return False

    token_address = "0xYourTokenAddressHere"
    rugchecker_data = get_rugchecker_data(token_address)
    if not rugchecker_data:
        return False

    dev_holding = rugchecker_data.get("devHolding", 0)
    top_10_holder_percentage = rugchecker_data.get("top10HolderPercentage", 0)
    liquidity_locked = rugchecker_data.get("liquidityLocked", 0)
    token_score = rugchecker_data.get("tokenScore", "")

    if dev_holding > 10:
        logging.info("Le pourcentage de détention des développeurs est trop élevé.")
        return False
    if top_10_holder_percentage > 20:
        logging.info("Le pourcentage des 10 premiers détenteurs (hors Dex) est trop élevé.")
        return False
    if liquidity_locked < 100:
        logging.info("La liquidité n'est pas entièrement verrouillée.")
        return False
    if token_score != "Good":
        logging.info("Le score du token n'est pas 'Good'.")
        return False

    logging.info("Toutes les conditions sont respectées.")
    return True


def main():
    logging.info("Démarrage du tracker de memecoin...")
    if check_conditions():
        alert_message = "🚀 ALERTE : Ce memecoin respecte toutes les conditions !"
        send_telegram_message(alert_message)
        logging.info(alert_message)
    else:
        logging.info("Aucune alerte déclenchée.")


if __name__ == "__main__":
    main()
        
