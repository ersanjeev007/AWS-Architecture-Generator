import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class CredentialEncryption:
    """Secure encryption/decryption for AWS credentials"""
    
    def __init__(self):
        # Get encryption key from environment or generate one
        self.encryption_key = self._get_or_create_key()
        self.cipher_suite = Fernet(self.encryption_key)
    
    def _get_or_create_key(self) -> bytes:
        """Get encryption key from environment or create new one"""
        key_env = os.getenv('CREDENTIAL_ENCRYPTION_KEY')
        
        if key_env:
            return key_env.encode()
        
        # Generate new key from a password (in production, use a secure secret)
        password = os.getenv('ENCRYPTION_PASSWORD', 'default-dev-password-change-in-production').encode()
        salt = os.getenv('ENCRYPTION_SALT', 'default-salt-change-in-production').encode()
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password))
        return key
    
    def encrypt(self, plaintext: str) -> str:
        """Encrypt sensitive data"""
        if not plaintext:
            return ""
        
        encrypted_bytes = self.cipher_suite.encrypt(plaintext.encode())
        return base64.urlsafe_b64encode(encrypted_bytes).decode()
    
    def decrypt(self, encrypted_text: str) -> str:
        """Decrypt sensitive data"""
        if not encrypted_text:
            return ""
        
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_text.encode())
            decrypted_bytes = self.cipher_suite.decrypt(encrypted_bytes)
            return decrypted_bytes.decode()
        except Exception:
            raise ValueError("Failed to decrypt credential data")

# Global instance
credential_encryption = CredentialEncryption()