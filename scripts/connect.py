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
        return False

def get_current_network(interface):
    """Sprawdza aktualną sieć WiFi"""
    try:
        result = subprocess.run(
            f"networksetup -getairportnetwork {interface}",
            shell=True, capture_output=True, text=True
        )
        if "Current Wi-Fi Network:" in result.stdout:
            return result.stdout.split(":")[1].strip()
        return None
    except Exception:
        return None

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
            mac_address = mac_match.group(0).upper()
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
    """Sprawdza połączenie za pomocą pinga"""
    try:
        ping_result = subprocess.run(
            ["ping", "-c", "1", "-W", "1", ip_address],
            capture_output=True, text=True
        )
        if ping_result.returncode == 0:
            print(f"  ↳ Ping do {ip_address} powiódł się")
            return True
        else:
            print(f"  ↳ Ping do {ip_address} nie powiódł się")
            return False
    except Exception as e:
        print(f"  ↳ Błąd ping: {e}")
        return False

def connect_to_wifi_with_retry(interface, mac_suffix, max_retries=2):
    """Próbuje połączyć się z WiFi z ponawianiem"""
    time.sleep(4)
    network_name = f"TempSenso_{mac_suffix}"
    password = "TempSenso"
    first_attempt = True
    
    for attempt in range(1, max_retries + 1):
        print(f"\n=== Próba {attempt}/{max_retries} ===")
        
        # Sprawdź czy już jesteśmy połączeni
        current_network = get_current_network(interface)
        if current_network == network_name:
            if verify_connection():
                print(f"  ↳ Już połączony z {network_name} i ping jest OK")
                print("✅ Połączenie aktywne i poprawne")
                return True
            else:
                print(f"  ↳ Już połączony z {network_name}, ale ping się nie powiódł")
                print("⚠️ Połączenie jest, ale brak komunikacji")
        
        # Tylko pierwsza próba resetuje interfejs
        if first_attempt:
            print(" Przygotowanie interfejsu...")
            if not toggle_interface(interface, "off"):
                continue
            time.sleep(1)
            if not toggle_interface(interface, "on"):
                continue
            time.sleep(3)
            first_attempt = False

        print(f" Łączenie z {network_name}...")
        try:
            subprocess.run(
                ["networksetup", "-setairportnetwork", interface, network_name, password],
                check=True, capture_output=True, text=True
            )
            
            # Po każdej próbie czekamy 3 sekundy i sprawdzamy połączenie
            time.sleep(3)
            
            # Dodano: Sprawdź ping przed kontynuacją
            if verify_connection():
                print("✅ Połączenie udane!")
                return True
            else:
                print("❌ Nie udało się połączyć (brak odpowiedzi na ping)")
                
        except subprocess.CalledProcessError as e:
            print(f"❌ Błąd: {e.stderr.strip() if e.stderr else 'Brak szczegółów'}")
        
        if attempt < max_retries:
            print(f" Czekam 3 sekundy przed kolejną próbą...")
            time.sleep(3)
    
    return False

if __name__ == "__main__":
    print("\n" + "="*50)
    print("️  Skrypt łączenia z siecią TempSenso")
    print("="*50 + "\n")

    interface = "en0"
    mac_last_five = get_esp_mac()

    if mac_last_five:
        print("\n" + "-"*50)
        print(f" Sieć docelowa: TempSenso_{mac_last_five}")
        print("-"*50 + "\n")

        if connect_to_wifi_with_retry(interface, mac_last_five):
            print("\n✅ Połączenie nawiązane pomyślnie!")
        else:
            print("\n❌ Nie udało się nawiązać połączenia")
        
        print("\n" + "="*50)
    else:
        print("\n❌ Nie można kontynuować bez adresu MAC")