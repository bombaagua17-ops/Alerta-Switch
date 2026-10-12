import os
import re
import requests

STORES = {
    "MediaMarkt": "https://www.mediamarkt.es/es/product/_consola-nintendo-switch-2-edicion-zelda-40-aniversario-79-full-hd-hdr-120-hz-256-gb-magnetic-joy-con-2-con-modo-raton-1674231.html",
    "Nintendo Store": "https://store.nintendo.com/es-es/nintendo-switch-2-edicin-40-aniversario-de-the-legend-of-zelda-P00211",
    "Amazon": "https://amzn.eu/d/07Eaa4Fn",
    "GAME": "https://www.game.es/hardware/consola/nintendo-switch-2/nintendo-switch-2-edicion-zelda-40th/267689",
    "Carrefour": "",  # pega aquí el enlace cuando exista
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept-Language": "es-ES,es;q=0.9",
}

OUT_WORDS = ["agotado", "sin stock", "no disponible", "currently unavailable"]
IN_WORDS = ["añadir a la cesta", "añadir al carrito", "comprar ahora", "add-to-cart-button"]


def check(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
    except requests.RequestException:
        return "error"
    if r.status_code != 200:
        return "bloqueada"
    html = r.text.lower()
    if "validatecaptcha" in html or "robot check" in html:
        return "bloqueada"
    m = re.search(r"schema\.org/(instock|limitedavailability|preorder|outofstock|soldout|discontinued)", html)
    if m:
        return "stock" if m.group(1) in ("instock", "limitedavailability", "preorder") else "agotado"
    if any(w in html for w in OUT_WORDS):
        return "agotado"
    if any(w in html for w in IN_WORDS):
        return "stock"
    return "desconocido"


def send(text):
    token = os.environ["TELEGRAM_TOKEN"]
    chat = os.environ["TELEGRAM_CHAT_ID"]
    requests.post(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data={"chat_id": chat, "text": text},
        timeout=30,
    )


def main():
    resumen = []
    for name, url in STORES.items():
        if not url:
            continue
        status = check(url)
        resumen.append(f"{name}: {status}")
        if status == "stock":
            send(f"🎮 ¡Posible stock en {name}!\n{url}")
    if os.environ.get("SUMMARY") == "true":
        send("Prueba del bot:\n" + "\n".join(resumen))


main()
