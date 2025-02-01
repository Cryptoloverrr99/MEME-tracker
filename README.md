# Memecoin Tracker

Ce projet vérifie si une memecoin respecte les conditions suivantes :

- **Dev holding** : max 10%
- **Dev sold** : no
- **Dev multi wallet transfert** : no
- **Dex paid** : yes 
- **Top 10 holder (excepté tous les Dex)** : max 20%
- **MarketCap** : minimum 200000$
- **Volume 1h** : minimum 1 million
- **Holder** : minimum 500
- **TNX** : minimum 5000
- **Liquidity provider** : Low
- **Liquidity locked** : 100%
- **Token score** : Good 
- **Trending sur Dexscreener** : Top #10
- **Social** : Doit obligatoirement avoir un site web, twitter + (telegram optionnel)
- **Social score** : 50/100

Les données sont récupérées via les APIs suivantes :

- **Dexscreener API** : Trending sur Dexscreener, Dex paid, TNX, volume, social, Holder, MarketCap, social sur Dexscreener, dev sold.
- **RugChecker API** : Liquidity provider/locked, token score, dev holding %, Top #10 holder (excluant les Dex).
- **Bubblemap API** : Dev multi wallet transfert.
- **Twitter API** : Pour le social score.
- **Telegram API** : Pour recevoir les notifications sur Telegram.

## Installation et exécution via Termux

Voir le guide complet dans le fichier `INSTALL.md` (ou directement ci-dessous dans le README).

# MEME-tracker
