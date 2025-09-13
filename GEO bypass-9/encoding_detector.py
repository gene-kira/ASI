import re

def detect_encoding(data: bytes) -> dict:
    if data.startswith(b'\xff\xfe'):
        return {"encoding": "utf-16le", "confidence": 1.0}
    elif data.startswith(b'\xfe\xff'):
        return {"encoding": "utf-16be", "confidence": 1.0}
    elif data.startswith(b'\xef\xbb\xbf'):
        return {"encoding": "utf-8-sig", "confidence": 1.0}
    try:
        data.decode("ascii")
        return {"encoding": "ascii", "confidence": 0.99}
    except UnicodeDecodeError:
        pass
    try:
        data.decode("utf-8")
        return {"encoding": "utf-8", "confidence": 0.95}
    except UnicodeDecodeError:
        pass
    if re.search(rb'[\x80-\xFF]', data):
        return {"encoding": "ISO-8859-1", "confidence": 0.80}
    return {"encoding": "windows-1252", "confidence": 0.50}

