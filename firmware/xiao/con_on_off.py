import subprocess
import re
import time

def toggle_interface(interface, state):
    """Włącza/wyłącza interfejs sieciowy"""
    try:
        cmd = f"networksetup -setairportpower {interface} {state}"
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"  ↳ {'Włączono' if state == 'on' else 'Wyłączono'} interfejs {interface}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Błąd podczas {state} interfejsu {interface}:")
        print(f"  ↳ {e.stderr.strip()}")
        return False

def get_esp_mac():
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
            mac_address = mac_match.group(0).upper()  # Zmiana na wielkie litery
            print(f" Adres MAC urządzenia: {mac_address}")
            last_two_pairs = ":".join(mac_address.split(":")[-2:])
            print(f"✨ Ostatnie 5 znaków MAC: {last_two_pairs}")
            return last_two_pairs
        else:
            print("❌ Nie znaleziono adresu MAC w output")
            return None

    except Exception as e:
        print(f" Krytyczny błąd podczas pobierania MAC: {e}")
        return None

def verify_connection(ip_address="192.168.4.1"):
    """Sprawdza połączenie za pomocą pinga i loguje wynik."""
    try:
        ping_result = subprocess.run(["ping", "-c", "1", ip_address], check=True, capture_output=True, text=True)
        print(f"  ↳ Ping do {ip_address} powiódł się:")
        print(f"  ↳ {ping_result.stdout.strip()}")
        return True  # Ping powiódł się
    except subprocess.CalledProcessError as e:
        print(f"  ↳ Ping do {ip_address} nie powiódł się:")
        print(f"  ↳ {e.stderr.strip()}")
        return False  # Ping nie powiódł się

def connect_to_wifi(interface, mac_suffix):
    network_name = f"TempSenso_{mac_suffix}"
    password = "TempSenso"

    print(f"\n Przygotowanie interfejsu {interface}...")
    if not toggle_interface(interface, "off"):
        return False
    time.sleep(2)

    if not toggle_interface(interface, "on"):
        return False
    time.sleep(5)

    print(f"\n Próba połączenia z siecią {network_name}...")
    cmd = [
        "networksetup",
        "-setairportnetwork",
        interface,
        network_name,
        password
    ]

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        time.sleep(5)  # Zwiększone opóźnienie przed weryfikacją.

        if verify_connection(): # Użyj pinga do weryfikacji
            print(f"✅ Pomyślnie połączono z {network_name}")
            return True
        else:
            print(f"❌ Nie udało się zweryfikować połączenia z {network_name}")
            return False

    except subprocess.CalledProcessError as e:
        print(f"❌ Błąd podczas łączenia z {network_name}:")
        print(f"  ↳ {e.stderr.strip() if e.stderr else 'Brak szczegółów'}")
        return False

if __name__ == "__main__":
    print("\n" + "="*50)
    print("️  Skrypt łączenia z siecią TempSenso")
    print("="*50 + "\n")

    interface = "en0"
    mac_last_five = get_esp_mac()

    if mac_last_five:
        print("\n" + "-"*50)
        print(f" Tworzenie nazwy sieci: TempSenso_{mac_last_five}")
        print("-"*50 + "\n")

        success = connect_to_wifi(interface, mac_last_five)

        print("\n" + "="*50)
        if success:
            print(" Skrypt zakończony powodzeniem!")
        else:
            print(" Nie udało się nawiązać połączenia")
        print("="*50)
    else:
        print("\n❌ Nie można kontynuować bez adresu MAC")