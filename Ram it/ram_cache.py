import subprocess

def create_ramdisk(size_mb):
    subprocess.run([
        "imdisk", "-a", "-s", f"{size_mb}M", "-m", "R:", "-p", "/fs:ntfs /q /y"
    ])

def remove_ramdisk():
    subprocess.run(["imdisk", "-D", "-m", "R:"])

