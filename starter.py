import subprocess
import os

def uruchom_skrypty_z_folderu():
    """Uruchamia skrypty ESP_prog.py i connect_wifi.py z folderu Desktop/ESP_prod/scripts."""

    sciezka_folderu = os.path.join(os.path.expanduser("~"), "Desktop", "ESP_prod", "scripts")  # Ścieżka do folderu

    if not os.path.exists(sciezka_folderu):
        print(f"Folder {sciezka_folderu} nie istnieje.")
        return

    skrypty = ["ESPprog_erase.py", "connect.py", "config_cloud.py", "reset.py"]  # Lista skryptów do uruchomienia

    try:
        for skrypt in skrypty:
            sciezka_skryptu = os.path.join(sciezka_folderu, skrypt)
            print(f"\nUruchamianie {skrypt}...")
            subprocess.run(["python", sciezka_skryptu], check=True)
            print(f"✅ Skrypt {skrypt} został uruchomiony pomyślnie.")

    except subprocess.CalledProcessError as e:
        print(f"\n❌ Błąd podczas uruchamiania skryptu: {e}")
    except FileNotFoundError as e:
        print(f"\n❌ Nie znaleziono skryptu: {e}")
    except Exception as e:
        print(f"\n❌ Nieoczekiwany błąd: {e}")

if __name__ == "__main__":
    print("="*50)
    print("Uruchamianie sekwencji skryptów ESP")
    print("="*50)
    uruchom_skrypty_z_folderu()
    print("\nZakończono uruchamianie sekwencji skryptów.")