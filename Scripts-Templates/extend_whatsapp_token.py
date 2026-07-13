"""
extend_whatsapp_token.py — Extiende el token de WhatsApp de 24h a 60 dias.
Ejecutar: python Scripts-Templates/extend_whatsapp_token.py
"""
import httpx

APP_ID     = "4427867694155743"
APP_SECRET = "4dc1607ca2c7a7868bbdf49fe02c4ecc"

short_token = input("Pega el WHATSAPP_TOKEN actual (de Render): ").strip()

resp = httpx.get(
    "https://graph.facebook.com/oauth/access_token",
    params={
        "grant_type":       "fb_exchange_token",
        "client_id":        APP_ID,
        "client_secret":    APP_SECRET,
        "fb_exchange_token": short_token,
    }
)

data = resp.json()
if "access_token" in data:
    print("\n[OK] Token extendido a 60 dias:")
    print(data["access_token"])
    print(f"\nExpira en: {data.get('expires_in', '?')} segundos (~60 dias)")
    print("\n>>> Copia este token y reemplaza WHATSAPP_TOKEN en Render <<<")
else:
    print(f"\n[ERROR] {data}")
