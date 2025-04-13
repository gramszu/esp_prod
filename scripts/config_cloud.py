import requests
from urllib.parse import urlencode
import time

CONFIG = {
    'ssid': 'NJU_Swiatlowod_6510',
    'password': '6LUZPMV3HL6U'
}

ESP_URL = "http://192.168.4.1/saveData"

def send_wifi_config():
    try:
        print("📤 Wysyłam konfigurację WiFi...")
        start_time = time.time()
        
        # Wersja z bardzo krótkim timeout
        try:
            response = requests.post(
                ESP_URL,
                data=urlencode(CONFIG),
                headers={'Content-Type': 'application/x-www-form-urlencoded'},
                timeout=3  # Krótki timeout
            )
            print(f"✅ ESP32 odpowiedział: {response.text}")
        except requests.exceptions.ReadTimeout:
            # Ignorujemy timeout, jeśli dane mogły zostać wysłane
            print("⚠️ Timeout, ale dane prawdopodobnie wysłane")
            print("ESP32 może restartować interfejs WiFi")
        
        print(f"Czas wykonania: {time.time() - start_time:.2f}s")

    except Exception as e:
        print(f"❌ Krytyczny błąd: {str(e)}")

if __name__ == "__main__":
    print("\n=== Konfigurator WiFi ESP32 ===")
    send_wifi_config()
    print("\nℹ️ Uwaga: Jeśli ESP32 restartuje interfejs WiFi,")
    print("timeout jest oczekiwanym zachowaniem")
    time.sleep(5)