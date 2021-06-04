import logging
import requests
from datetime import datetime

from util import db

logger = logging.getLogger(__name__)

# The number of Wei per Ether.
wei_in_ether = 1000000000000000000

# The base URL for Etherscan's API.
etherscan_url = "https://api.etherscan.io/api"

# A simple wrapper around Etherscan APIs.
#
# I wanted to use a Python client (etherscan-python), but Replit's
# auto-installation will forcibly install another library (etherscan) that
# causes a module collision. Thus both libraries are unusable. It's unfortunate
# that there's no way to disable that "feature."


def balance(api_key: str, address: str) -> dict:
    """Fetches the balance of an Ethereum address and its value in USD."""
    logger.info("Fetching ETH balance for address %s", address)
    res = requests.get(f"{etherscan_url}?module=account&action=balance&address={address}&tag=latest&apikey={api_key}")
    db.increment_etherscan_calls()
    payload = res.json()

    result = payload["result"]
    if payload["message"] != "OK":
        return {
            "error": result,
        }

    # Fetch the current ETH price to do a USD conversion.
    pricing = price(api_key)
    if "error" in pricing:
        return pricing

    # Calculate the wallet value in USD.
    wei = int(result)
    ether = wei / wei_in_ether
    usd = ether * pricing["ethusd"]
    return {
        "wei": wei,
        "ether": ether,
        "usd": usd,
        "timestamp": pricing["timestamp"],
    }


def price(api_key: str) -> dict:
    """Fetches the current Ethereum price in USD."""
    logger.info("Fetching ETH price")
    res = requests.get(f"{etherscan_url}?module=stats&action=ethprice&apikey={api_key}")
    db.increment_etherscan_calls()
    payload = res.json()

    result = payload["result"]
    if payload["message"] != "OK":
        return {
            "error": result,
        }
    return {
        "ethusd": float(result["ethusd"]),
        "timestamp": datetime.fromtimestamp(int(result["ethusd_timestamp"])),
    }
