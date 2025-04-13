import subprocess
import sys

def check_ping(host):
    try:
        # Wykonanie polecenia ping z 1 pakietem (dla Windowsa '-n', dla Linuxa '-c')
        param = '-n' if sys.platform.lower() == 'win32' else '-c'
        command = ['ping', param, '1', host]
        response = subprocess.call(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return response == 0
    except Exception as e:
        print(f"Błąd podczas pingowania: {e}")
        return False

def main():
    host = "192.168.4.1"
    print(f"Sprawdzam ping do {host}...")
    
    if check_ping(host):
        print("Odpowiedź pozytywna. Uruchamiam skrypt config_cloud.py...")
        try:
            subprocess.run(["python", "config_cloud.py"], check=True)
        except subprocess.CalledProcessError as e:
            print(f"Błąd podczas uruchamiania skryptu: {e}")
        except FileNotFoundError:
            print("Nie znaleziono pliku config_cloud.py")
    else:
        print("Brak odpowiedzi. Zamykanie programu.")
        sys.exit(1)

if __name__ == "__main__":
    main()