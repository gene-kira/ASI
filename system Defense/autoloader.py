import subprocess
import sys

required_libs = ["cryptography"]

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def ensure_dependencies():
    for lib in required_libs:
        try:
            if lib == "cryptography":
                import cryptography
        except ImportError:
            print(f"[Autoloader] Missing: {lib} → Installing...")
            install(lib)
            print(f"[Autoloader] Installed: {lib}")

