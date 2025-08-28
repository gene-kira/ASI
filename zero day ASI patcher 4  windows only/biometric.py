def biometric_unlock():
    print("🔐 Fingerprint scan required...")
    # Simulate scan
    return input("Place finger and type 'yes' to confirm: ").strip().lower() == "yes"

