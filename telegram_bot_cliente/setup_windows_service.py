import os
import sys
import subprocess
from pathlib import Path

SERVICE_NAME = "TelegramClientBot"
SERVICE_DISPLAY_NAME = "Telegram Client Registration Bot"
SERVICE_DESCRIPTION = "Collects client data via Telegram and generates Excel files"

def install_service():
    script_path = Path(__file__).parent
    python_exe = sys.executable

    print(f"Installing {SERVICE_NAME} service...")
    print(f"Python: {python_exe}")
    print(f"Script: {script_path}")

    try:
        result = subprocess.run(["nssm", "status", SERVICE_NAME], capture_output=True)
        if result.returncode == 0:
            print(f"Service {SERVICE_NAME} already exists. Removing...")
            subprocess.run(["nssm", "remove", SERVICE_NAME, "confirm"])
    except FileNotFoundError:
        print("[ERROR] nssm not found.")
        print("Please install NSSM (Non-Sucking Service Manager) first:")
        print("  Option 1: Using Chocolatey: choco install nssm")
        print("  Option 2: Download from: https://nssm.cc/download")
        print("After installation, run this script again.")
        return

    subprocess.run([
        "nssm", "install", SERVICE_NAME,
        python_exe,
        "-m", "bot.main"
    ], cwd=str(script_path))

    subprocess.run(["nssm", "set", SERVICE_NAME, "AppDirectory", str(script_path)])
    subprocess.run(["nssm", "set", SERVICE_NAME, "Description", SERVICE_DESCRIPTION])
    subprocess.run(["nssm", "set", SERVICE_NAME, "DisplayName", SERVICE_DISPLAY_NAME])

    print(f"\n[SUCCESS] Service {SERVICE_NAME} installed!")
    print(f"Start service: nssm start {SERVICE_NAME}")
    print(f"Stop service: nssm stop {SERVICE_NAME}")
    print(f"Service status: nssm status {SERVICE_NAME}")
    print(f"Remove service: nssm remove {SERVICE_NAME} confirm")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "install":
        install_service()
    else:
        print("Usage: python setup_windows_service.py install")
