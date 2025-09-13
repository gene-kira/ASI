import winreg
from config import default_coords

def set_registry(path, name, value):
    key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, path)
    winreg.SetValueEx(key, name, 0, winreg.REG_SZ, value)
    winreg.CloseKey(key)

def reset_location():
    lat, lon = default_coords
    set_registry(r"Software\\Microsoft\\Windows\\CurrentVersion\\Location", "Latitude", lat)
    set_registry(r"Software\\Microsoft\\Windows\\CurrentVersion\\Location", "Longitude", lon)

