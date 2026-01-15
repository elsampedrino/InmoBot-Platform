import requests
import json
from datetime import datetime

# Configuración
url = "https://n8n-bot-inmobiliario.onrender.com/webhook/chat-basico"
headers = {
    "Content-Type": "application/json"
}

# Test 1: Consulta específica por departamento para alquilar
payload1 = {
    "message": "busco un departamento para alquilar",
    "sessionId": "test-session-001",
    "timestamp": datetime.now().isoformat(),
    "repo": "1"  # BBR
}

print("=" * 60)
print("TEST 1: Busco un departamento para alquilar")
print("=" * 60)
print(f"Enviando a: {url}")
print(f"Payload: {json.dumps(payload1, indent=2)}")
print()

try:
    response1 = requests.post(url, json=payload1, headers=headers, timeout=30)
    print(f"Status Code: {response1.status_code}")
    print(f"Response Headers: {dict(response1.headers)}")
    print()

    if response1.status_code == 200:
        try:
            data = response1.json()
            print("Response JSON:")
            # Guardar en archivo para evitar problemas de encoding
            with open('response_test1.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print("-> Respuesta guardada en response_test1.json")

            if 'response' in data:
                print("\n" + "=" * 60)
                print("RESPUESTA DEL BOT:")
                print("=" * 60)
                # Escribir a archivo también
                with open('response_test1.txt', 'w', encoding='utf-8') as f:
                    f.write(data['response'])
                print("-> Respuesta del bot guardada en response_test1.txt")

                # Intentar imprimir sin emojis
                response_text = data['response'].encode('ascii', 'replace').decode('ascii')
                print(response_text)
        except json.JSONDecodeError:
            print("ERROR: La respuesta no es JSON válido")
            print("Response text:")
            print(response1.text)
    else:
        print(f"ERROR HTTP: {response1.status_code}")
        print(response1.text)

except requests.exceptions.Timeout:
    print("ERROR: Timeout esperando respuesta del servidor")
except requests.exceptions.RequestException as e:
    print(f"ERROR: {e}")

print("\n" + "=" * 60)
print()

# Test 2: Consulta alternativa
payload2 = {
    "message": "tenes algun departamento para alquilar ?",
    "sessionId": "test-session-002",
    "timestamp": datetime.now().isoformat(),
    "repo": "1"  # BBR
}

print("=" * 60)
print("TEST 2: Tenes algun departamento para alquilar ?")
print("=" * 60)
print(f"Payload: {json.dumps(payload2, indent=2)}")
print()

try:
    response2 = requests.post(url, json=payload2, headers=headers, timeout=30)
    print(f"Status Code: {response2.status_code}")

    if response2.status_code == 200:
        try:
            data = response2.json()
            print("Response JSON:")
            # Guardar en archivo para evitar problemas de encoding
            with open('response_test2.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print("-> Respuesta guardada en response_test2.json")

            if 'response' in data:
                print("\n" + "=" * 60)
                print("RESPUESTA DEL BOT:")
                print("=" * 60)
                # Escribir a archivo también
                with open('response_test2.txt', 'w', encoding='utf-8') as f:
                    f.write(data['response'])
                print("-> Respuesta del bot guardada en response_test2.txt")

                # Intentar imprimir sin emojis
                response_text = data['response'].encode('ascii', 'replace').decode('ascii')
                print(response_text)
        except json.JSONDecodeError:
            print("ERROR: La respuesta no es JSON válido")
            print("Response text:")
            print(response2.text)
    else:
        print(f"ERROR HTTP: {response2.status_code}")
        print(response2.text)

except requests.exceptions.Timeout:
    print("ERROR: Timeout esperando respuesta del servidor")
except requests.exceptions.RequestException as e:
    print(f"ERROR: {e}")
