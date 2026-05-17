import os
from cryptography.fernet import Fernet
from dotenv import load_dotenv

load_dotenv()

PAYMENT_ENCRYPTION_KEY = os.getenv("PAYMENT_ENCRYPTION_KEY")

if not PAYMENT_ENCRYPTION_KEY:
    raise RuntimeError("PAYMENT_ENCRYPTION_KEY missing in .env")

fernet = Fernet(PAYMENT_ENCRYPTION_KEY.encode())


def encrypt_text(value: str | None) -> str | None:
    if not value:
        return None
    return fernet.encrypt(value.encode()).decode()


def decrypt_text(value: str | None) -> str | None:
    if not value:
        return None
    return fernet.decrypt(value.encode()).decode()