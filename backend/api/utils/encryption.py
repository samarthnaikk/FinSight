import json
from cryptography.fernet import Fernet
from django.conf import settings


class EncryptionService:
    def __init__(self):
        key = settings.FIELD_ENCRYPTION_KEY
        if not key:
            raise ValueError("FIELD_ENCRYPTION_KEY is not set")
        self.cipher = Fernet(key.encode())

    def encrypt(self, data: dict) -> str:
        json_data = json.dumps(data)
        encrypted = self.cipher.encrypt(json_data.encode())
        return encrypted.decode()

    def decrypt(self, encrypted_data: str) -> dict:
        decrypted = self.cipher.decrypt(encrypted_data.encode())
        return json.loads(decrypted.decode())


encryption_service = EncryptionService()
