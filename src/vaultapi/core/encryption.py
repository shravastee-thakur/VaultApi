from cryptography.fernet import Fernet
from src.vaultapi.core.config import settings

fernet = Fernet(settings.ENCRYPTION_KEY.encode())


def encrypt_data(data: str) -> str:
    return fernet.encrypt(data.encode()).decode()


def decrypt_data(encrypted_content: str) -> str:
    return fernet.decrypt(encrypted_content.encode()).decode()
