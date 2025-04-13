import requests
import re
import subprocess
import time
import os
from datetime import datetime

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
    url = "https://login.simcloud.pl/tempsens/jason.php?mac=XX:XX:XX:XX:XX:EC&limit=5" # Zmieniono limit na 5

    if mac_address:
        url = url.replace("XX:XX:XX:XX:XX:EC", mac_address)

    try:
        time.sleep(5)  # Dodano opóźnienie 5 sekund

        response = requests.get(url)
        response.raise_for_status()  # Sprawdź, czy nie ma błędów HTTP

        data = response.json()

        if data and isinstance(data, list) and len(data) == 5:
            filtered_data = []
            for item in data:
                if 'temperature' in item and 'timestamp' in item:
                    filtered_data.append({
                        'temperature': item['temperature'],
                        'timestamp': item['timestamp']
                    })

            if len(filtered_data) == 5:
                time1 = datetime.strptime(filtered_data[0]['timestamp'], '%Y-%m-%d %H:%M:%S')
                time5 = datetime.strptime(filtered_data[4]['timestamp'], '%Y-%m-%d %H:%M:%S')
                diff = abs((time5 - time1).total_seconds())

                date_error = False
                if diff > 25:
                    print("+" + "-" * 80 + "+")
                    print("| BŁĄD DATY: Różnica czasu między pierwszym a ostatnim odczytem przekracza 25 sekund. |")
                    print("+" + "-" * 80 + "+")
                    date_error = True

                temp_error = False
                temp = float(filtered_data[0]['temperature']) # Pobierz temperaturę tylko z pierwszego odczytu
                if temp == 0:
                    print("+" + "-" * 80 + "+")
                    print("| BŁĄD CZUJNIKA: Temperatura wynosi 0. |")
                    print("+" + "-" * 80 + "+")
                    temp_error = True
                elif temp == -127:
                    print("+" + "-" * 80 + "+")
                    print("| BŁĄD: Temperatura wynosi -127. |")
                    print("+" + "-" * 80 + "+")
                    temp_error = True
                elif temp == 85:
                    print("+" + "-" * 80 + "+")
                    print("| BŁĄD: Nieprawidłowa temperatura. |")
                    print("+" + "-" * 80 + "+")
                    temp_error = True

                if not date_error and not temp_error and 10 <= temp <= 40:
                    print("+" + "-" * 80 + "+")
                    print("| Temperatura w zakresie 10-40, uruchamiam reset... |")
                    print("+" + "-" * 80 + "+")
                    subprocess.run(["python", "scripts/reset.py"]) # Uruchamianie skryptu reset.py
                elif not date_error and not temp_error:
                    print("Temperatura OK.")
            else:
                print("+" + "-" * 80 + "+")
                print("| BŁĄD: Nie znaleziono danych temperatury i daty dla wszystkich odczytów. |")
                print("+" + "-" * 80 + "+")
        else:
            print("+" + "-" * 80 + "+")
            print("| BŁĄD: Nie otrzymano pięciu odczytów. |")
            print("+" + "-" * 80 + "+")

    except requests.exceptions.RequestException as e:
        print("+" + "-" * 80 + "+")
        print(f"| Błąd podczas pobierania danych: {e} |")
        print("+" + "-" * 80 + "+")
    except ValueError as e:
        print("+" + "-" * 80 + "+")
        print(f"| Błąd podczas parsowania JSON: {e} |")
        print("+" + "-" * 80 + "+")
    except KeyError as e:
        print("+" + "-" * 80 + "+")
        print(f"| Błąd klucza w danych JSON: {e} |")
        print("+" + "-" * 80 + "+")

if __name__ == "__main__":
    mac_address = get_esp_mac()
    fetch_and_display_data(mac_address)