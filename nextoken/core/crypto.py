"""
Cryptographic operations for NexToken
"""

import os
import base64
from typing import Tuple, Optional
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import ed25519
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


class CryptoManager:
    """Manages cryptographic operations for NexToken"""
    
    def __init__(self):
        # Generate Ed25519 key pair for token signing
        self.private_key = ed25519.Ed25519PrivateKey.generate()
        self.public_key = self.private_key.public_key()
        
        # Generate AES key for encrypting sensitive payload fields
        self.aes_key = os.urandom(32)  # 256-bit key
        self.aes_iv = os.urandom(16)   # 128-bit IV
    
    def get_public_key_bytes(self) -> bytes:
        """Get the public key in bytes format"""
        return self.public_key.public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw
        )
    
    def sign_data(self, data: bytes) -> bytes:
        """Sign data using Ed25519"""
        return self.private_key.sign(data)
    
    def verify_signature(self, data: bytes, signature: bytes) -> bool:
        """Verify Ed25519 signature"""
        try:
            self.public_key.verify(signature, data)
            return True
        except Exception:
            return False
    
    def encrypt_field(self, plaintext: str) -> str:
        """Encrypt a field using AES-256-CFB"""
        if not plaintext:
            return ""
        
        cipher = Cipher(
            algorithms.AES(self.aes_key),
            modes.CFB(self.aes_iv),
            backend=default_backend()
        )
        encryptor = cipher.encryptor()
        
        plaintext_bytes = plaintext.encode('utf-8')
        ciphertext = encryptor.update(plaintext_bytes) + encryptor.finalize()
        
        # Return base64 encoded ciphertext
        return base64.b64encode(ciphertext).decode('utf-8')
    
    def decrypt_field(self, encrypted_text: str) -> str:
        """Decrypt a field using AES-256-CFB"""
        if not encrypted_text:
            return ""
        
        try:
            ciphertext = base64.b64decode(encrypted_text.encode('utf-8'))
            
            cipher = Cipher(
                algorithms.AES(self.aes_key),
                modes.CFB(self.aes_iv),
                backend=default_backend()
            )
            decryptor = cipher.decryptor()
            
            plaintext_bytes = decryptor.update(ciphertext) + decryptor.finalize()
            return plaintext_bytes.decode('utf-8')
        except Exception:
            return ""


# Global crypto manager instance
crypto_manager = CryptoManager() 