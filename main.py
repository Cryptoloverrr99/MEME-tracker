import requests
import time
import logging
from config import (
    DEXSCREENER_API_KEY,
    RUGCHECKER_API_KEY,
    BUBBLEMAP_API_KEY,
    TWITTER_API_KEY,
    TELEGRAM_BOT_TOKEN,
    TELEGRAM_CHAT_ID
)

# Configuration du module logging pour afficher infos et erreurs dans la console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)

# Fonction pour envoyer un message via Telegram
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{8048350512:AAGVN4uZEt_D1q-ycNN6jhRo-PMn64ZHgiI}/sendMessage"
    payload = {"chat_id": 1002359674981, "text": message}
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        logging.info("Notification Telegram envoyée.")
    except Exception as e:
        logging.error("Erreur lors de l'envoi de la notification Telegram : %s", e)

# Exemple de fonction pour récupérer les données de Dexscreener (à adapter selon la documentation réelle)
def check_dexscreener():
    url = "https://api.dexscreener.com/tokens/v1/{chainId}/{tokenAddresses}"
    params = {"api_key": DEXSCREENER_API_KEY}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        logging.info("Données Dexscreener récupérées.")
        return data
    except Exception as e:
        logging.error("Erreur lors de la récupération des données Dexscreener : %s", e)
        return {}

# Exemple de fonction pour récupérer les données de RugChecker
def check_rugchecker():
    url = "rugcheck_api.Risk"  # URL fictive, à adapter
    params = {"api_key": RUGCHECKER_API_KEY}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        logging.info("Données RugChecker récupérées.")
        return data
    except Exception as e:
        logging.error("Erreur lors de la récupération des données RugChecker : %s", e)
        return {}

# Exemple de fonction pour récupérer les données de Bubblemap
def check_bubblemap():
    url = "https://api.bubblemap.com/check"  # URL fictive, à adapter
    params = {"api_key": BUBBLEMAP_API_KEY}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        logging.info("Données Bubblemap récupérées.")
        return data
    except Exception as e:
        logging.error("Erreur lors de la récupération des données Bubblemap : %s", e)
        return {}

# Exemple de fonction pour récupérer les données de Twitter (social score)
def check_twitter_social_score():
    url = "https://api.twitter.com/2/tweets"  # URL fictive, à adapter selon la documentation
    headers = {"Authorization": f"Bearer {TWITTER_API_KEY}"}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        logging.info("Données Twitter récupérées.")
        return data
    except Exception as e:
        logging.error("Erreur lors de la récupération des données Twitter : %s", e)
        return {}

# Traitement des données et vérification de chaque condition
def check_conditions():
    conditions_valides = True

    # Récupération des données
    dexscreener_data = check_dexscreener()
    rugchecker_data = check_rugchecker()
    bubblemap_data = check_bubblemap()
    twitter_data = check_twitter_social_score()

    # --- Vérifications d'exemple (à adapter selon le retour réel des APIs) ---

    # 1. Vérifier le MarketCap (exemple depuis Dexscreener)
    market_cap = dexscreener_data.get("marketCap", 0)
    if market_cap < 200000:
        conditions_valides = False

    # 2. Vérifier le volume sur 1h
    volume_1h = dexscreener_data.get("volume1h", 0)
    if volume_1h < 1000000:
        conditions_valides = False

    # 3. Vérifier le nombre de holders
    holders = dexscreener_data.get("holders", 0)
    if holders < 500:
        conditions_valides = False

    # 4. Vérifier Dev Holding via RugChecker (en pourcentage)
    dev_holding = rugchecker_data.get("devHolding", 100)
    if dev_holding > 10:
        conditions_valides = False

    # 5. Vérifier que Dev n'a pas vendu (doit être False ou "no")
    dev_sold = dexscreener_data.get("devSold", True)
    if dev_sold:
        conditions_valides = False

    # Vous pouvez ajouter ici d'autres vérifications (ex. Dex paid, Top 10 holder, TNX, Liquidity locked, Token score, etc.)

    return conditions_valides

# Boucle principale qui s'exécute en continu
def main():
    logging.info("Démarrage du tracker de memecoin en exécution continue...")
    while True:
        if check_conditions():
            # Si toutes les conditions sont strictement remplies, on envoie une notification Telegram.
            message = "La memecoin respecte toutes les conditions définies."
            send_telegram_message(message)
            # Pause de 2 minutes après une alerte
            time.sleep(120)
        else:
            # Si les conditions ne sont pas remplies, aucun message n'est envoyé.
            logging.info("Les conditions ne sont pas toutes remplies. Aucune notification envoyée.")
            # Pause courte avant de refaire une vérification (exemple : 60 secondes)
            time.sleep(60)

if __name__ == "__main__":
    main()
      
