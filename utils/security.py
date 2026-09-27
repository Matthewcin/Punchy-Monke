from cryptography.fernet import Fernet
from config import ENCRYPTION_KEY

cipher_suite = Fernet(ENCRYPTION_KEY.encode())

def encrypt_data(data: str) -> str:
    return cipher_suite.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data: str) -> str:
    try:
        return cipher_suite.decrypt(encrypted_data.encode()).decode()
    except Exception:
        return "decryption_error"