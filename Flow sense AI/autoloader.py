# autoloader.py

import subprocess
import sys

def autoload():
    required = [
        'tkinter', 'threading', 'time', 'random',
        'collections', 'math', 'json', 'os'
    ]
    for lib in required:
        try:
            __import__(lib)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

