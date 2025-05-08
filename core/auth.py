import hashlib
from cryptography.fernet import Fernet
import base64
import os
from core.logger import setup_logger

logger = setup_logger("Auth")

class AuthManager:
    """负责Token加密和验证"""
    def __init__(self, key_file="config/auth.key"):
        self.key_file = key_file
        self.key = self._load_or_create_key()
        self.cipher = Fernet(self.key)
    
    def _load_or_create_key(self):
        """加载或创建加密密钥"""
        if os.path.exists(self.key_file):
            with open(self.key_file, "rb") as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            os.makedirs(os.path.dirname(self.key_file), exist_ok=True)
            with open(self.key_file, "wb") as f:
                f.write(key)
            return key
    
    def encrypt_token(self, token):
        """加密Twitter Token"""
        try:
            return self.cipher.encrypt(token.encode()).decode()
        except Exception as e:
            logger.error(f"加密Token失败: {str(e)}")
            raise
    
    def decrypt_token(self, encrypted_token):
        """解密Twitter Token"""
        try:
            return self.cipher.decrypt(encrypted_token.encode()).decode()
        except Exception as e:
            logger.error(f"解密Token失败: {str(e)}")
            raise
    
    @staticmethod
    def hash_token(token):
        """生成Token的哈希值用于标识"""
        return hashlib.sha256(token.encode()).hexdigest()