import requests
import re
import subprocess
import time
import os

def get_esp_mac():
    """Pobiera adres MAC z ESP."""
    try:
        print(" Szukam portu USB ESP...")
        port_result = subprocess.run(
            "ls /dev/cu.* 2>/dev/null | grep -i 'usb' | head -n 1",
            shell=True, text=True, capture_output=True
        )

        if not port_result.stdout:
            print("❌ Nie znaleziono portu USB")
            return None

        port = port_result.stdout.strip()
        print(f" Znaleziono port: {port}")

        print(" Pobieram adres MAC urządzenia...")
        esptool_result = subprocess.run(
            f"esptool.py --port {port} chip_id",
            shell=True, text=True, capture_output=True
        )

        mac_pattern = r"([0-9a-fA-F]{2}[:]){5}([0-9a-fA-F]{2})"
        mac_match = re.search(mac_pattern, esptool_result.stdout)

        if mac_match:
            mac_address = mac_match.group(0).upper()
            print(f" Adres MAC urządzenia: {mac_address}")
            return mac_address
        else:
            print("❌ Nie znaleziono adresu MAC w output")
            return None

    except Exception as e:
        print(f" Krytyczny błąd podczas pobierania MAC: {e}")
        return None

def fetch_and_display_data(mac_address=None):
    """Pobiera i wyświetla dane z podanego URL."""
    url = "https://login.simcloud.pl/tempsens/jason.php?mac=XX:XX:XX:XX:XX:EC&limit=1"

    if mac_address:
        url = url.replace("XX:XX:XX:XX:XX:EC", mac_address)

    try:
        print("Czekam 5 sekund na wysłanie danych przez ESP...")
        time.sleep(10)  # Dodano opóźnienie 5 sekund

        response = requests.get(url)
        response.raise_for_status()  # Sprawdź, czy nie ma błędów HTTP

        data = response.json()
        print("Dane z URL:")
        

        if data and isinstance(data, list) and len(data) > 0:
            item = data[0]  # Pobierz pierwszy element z listy
            if 'temperature' in item and item['temperature'] == 0:
                print("BŁĄD CZUJNIKA: Temperatura wynosi 0.")
            elif 'temperature' in item and item['temperature'] == -127:
                print("BŁĄD: Temperatura wynosi -127.")
            elif 'temperature' in item and 10 <= item['temperature'] <= 40:
                print("Temperatura w zakresie 10-40, uruchamiam reset...")
                subprocess.run(["python", "scripts/reset.py"]) # Uruchamianie skryptu reset.py
            elif 'temperature' in item and item['temperature'] == 85:
                print("BŁĄD: Nieprawidłowa temperatura.")
            else:
                print("Temperatura OK.")

    except requests.exceptions.RequestException as e:
        print(f"Błąd podczas pobierania danych: {e}")
    except ValueError as e:
        print(f"Błąd podczas parsowania JSON: {e}")
    except KeyError as e:
        print(f"Błąd klucza w danych JSON: {e}")

if __name__ == "__main__":
    mac_address = get_esp_mac()
    fetch_and_display_data(mac_address)