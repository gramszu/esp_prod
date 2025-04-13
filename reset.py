import subprocess
import re
import time

def get_esp_port():
    """Znajdź port ESP32"""
    try:
        result = subprocess.run(
            "ls /dev/cu.* 2>/dev/null | grep -i 'usb' | head -n 1",
            shell=True, text=True, capture_output=True
        )
        return result.stdout.strip() if result.stdout else None
    except Exception:
        return None

def check_chip_id(port, attempt):
    """Sprawdź chip_id ESP32 i zwróć pełne dane"""
    try:
        result = subprocess.run(
            f"esptool.py --port {port} chip_id",
            shell=True, text=True, capture_output=True,
            timeout=5
        )
        
        chip_info = re.search(r"Chip is (ESP32[^\n]+)", result.stdout)
        mac_info = re.search(r"MAC: (([0-9a-fA-F]{2}:){5}[0-9a-fA-F]{2})", result.stdout)
        
        output = {
            'success': chip_info is not None,
            'chip_id': chip_info.group(1) if chip_info else "Nieznany",
            'mac': mac_info.group(1) if mac_info else "Nieznany",
            'output': result.stdout.strip()
        }
        return output
            
    except subprocess.TimeoutExpired:
        return {'success': False, 'error': 'Timeout'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def main():
    print("\n" + "="*50)
    print("🛠️  SKANER CHIP_ID ESP32 (5 PRÓB)")
    print("="*50)
    
    port = get_esp_port()
    if not port:
        print("\n❌ Nie znaleziono portu ESP32!")
        print("Sprawdź podłączenie i spróbuj ponownie")
        return
    
    print(f"\n🔌 Używam portu: {port}")
    print("⏳ Wykonuję 5 prób odczytu...\n")
    
    results = []
    for attempt in range(1, 6):
        print(f"🔍 Próba {attempt}/5 w toku...")
        result = check_chip_id(port, attempt)
        results.append(result)
        
        if result['success']:
            print(f"   ✅ Sukces! Chip: {result['chip_id']}")
        else:
            print(f"   ❌ Niepowodzenie: {result.get('error', 'Błąd odczytu')}")
        
        if attempt < 5:
            time.sleep(1)  # Odczekaj 1 sekundę między próbami
    
    # Podsumowanie ostatniej próby
    last_result = results[-1]
    print("\n" + "="*50)
    print("📋 WYNIK OSTATNIEJ PRÓBY:")
    print(f"Status: {'✅ POWODZENIE' if last_result['success'] else '❌ NIEPOWODZENIE'}")
    print(f"Typ chipa: {last_result['chip_id']}")
    print(f"Adres MAC: {last_result['mac']}")
    print("\nPełne wyjście:")
    print(last_result['output'])
    print("="*50)

if __name__ == "__main__":
    main()