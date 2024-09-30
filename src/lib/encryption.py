from cryptography.fernet import Fernet
from configs.settings import settings


def encrypt(data: str) -> str:
    key = settings.PRIVATE_KEY.encode()
    f = Fernet(key)
    return f.encrypt(data.encode()).decode()


def decrypt(data: str) -> str:
    key = settings.PRIVATE_KEY.encode()
    f = Fernet(key)
    return f.decrypt(data.encode()).decode()
