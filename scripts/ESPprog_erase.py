#!/usr/bin/env python3
import subprocess
import time
import os
from datetime import datetime

# Ścieżka do katalogu z plikami firmware
ESP_DIRECTORY = "firmware/ESP"

FIRMWARE_FILES = {
    'bootloader': 'bootloader.bin',
    'partitions': 'partitions.bin',
    'firmware': 'firmware.bin'
}

def get_firmware_paths():
    """Pobiera pełne ścieżki do plików firmware z katalogu /ESP"""
    file_paths = {}
    for key, filename in FIRMWARE_FILES.items():
        file_path = os.path.join(ESP_DIRECTORY, filename)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Nie znaleziono pliku {filename} w katalogu {ESP_DIRECTORY}")
        file_paths[key] = file_path
    return file_paths

def log_step(message, level=0):
    indent = "  " * level
    timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"{timestamp} {indent}{message}")

def program_esp():
    try:
        log_step("🛠️  Rozpoczynanie programowania ESP32", 0)

        # Sprawdź dostępność plików firmware
        log_step("Sprawdzam pliki firmware...", 1)
        firmware_paths = get_firmware_paths()
        log_step("Znaleziono wszystkie pliki firmware", 1)

        # Znajdź port ESP
        log_step("Szukam portu ESP...", 1)
        port_result = subprocess.run(
            "ls /dev/cu.* 2>/dev/null | grep -i 'usbmodem' | head -n 1",
            shell=True, text=True, capture_output=True
        )

        if not port_result.stdout:
            log_step("❌ Nie znaleziono portu ESP", 1)
            return False

        port = port_result.stdout.strip()
        log_step(f"Znaleziono port: {port}", 1)

        # Wymaż flash
        log_step("Wymazuję flash...", 1)
        erase_cmd = [
            "esptool.py",
            "--port", port,
            "erase_flash"
        ]

        erase_process = subprocess.run(
            erase_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        if erase_process.returncode != 0:
            log_step("❌ Błąd wymazywania flash", 1)
            log_step(erase_process.stderr.strip(), 2)
            return False

        log_step("✅ Flash wymazany pomyślnie", 1)

        # Wgraj firmware
        log_step("Rozpoczynam programowanie...", 1)
        cmd = [
            "esptool.py",
            "--port", port,
            "--baud", "460800",
            "write_flash",
            "0x0", firmware_paths['bootloader'],
            "0x8000", firmware_paths['partitions'],
            "0x10000", firmware_paths['firmware']
        ]

        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Realtime logging
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                log_step(output.strip(), 2)

        if process.poll() == 0:
            log_step("✅ Programowanie zakończone sukcesem", 1)
            return True
        else:
            log_step("❌ Błąd programowania", 1)
            return False

    except FileNotFoundError as e:
        log_step(f"❌ {str(e)}", 1)
        return False
    except Exception as e:
        log_step(f"❌ Błąd: {str(e)}", 1)
        return False

if __name__ == "__main__":
    print("\n" + "="*60)
    print("🔥 ESP32 Programmer")
    print("="*60 + "\n")

    if program_esp():
        print("\n✅ Programowanie zakończone pomyślnie")
        time.sleep(10)
    else:
        print("\n❌ Wystąpiły błędy podczas programowania")