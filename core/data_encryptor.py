
import pandas as pd
import numpy as np
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import pickle
import zlib
from typing import Optional

class DataEncryptor:
    @staticmethod
    def generate_key(password: str, salt: bytes = None) -> bytes:
        if salt is None:
            salt = b'data_analyser_salt_2024'
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key

    @staticmethod
    def compute_checksum(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def encrypt_data(df: pd.DataFrame, password: str) -> bytes:
        try:
            data_bytes = pickle.dumps(df)
            compressed_data = zlib.compress(data_bytes)
            
            checksum = DataEncryptor.compute_checksum(compressed_data)
            
            key = DataEncryptor.generate_key(password)
            fernet = Fernet(key)
            
            encrypted_data = fernet.encrypt(compressed_data)
            
            header = b'DATAANALYSER_V1'
            checksum_bytes = checksum.encode()
            
            final_data = header + b'|' + checksum_bytes + b'|' + encrypted_data
            
            return final_data
        except Exception as e:
            return b''

    @staticmethod
    def decrypt_data(encrypted_bytes: bytes, password: str) -> Optional[pd.DataFrame]:
        try:
            parts = encrypted_bytes.split(b'|', 2)
            if len(parts) != 3:
                return None
            
            header, checksum_bytes, encrypted_data = parts
            
            if header != b'DATAANALYSER_V1':
                return None
            
            key = DataEncryptor.generate_key(password)
            fernet = Fernet(key)
            
            compressed_data = fernet.decrypt(encrypted_data)
            
            computed_checksum = DataEncryptor.compute_checksum(compressed_data)
            
            if computed_checksum != checksum_bytes.decode():
                return None
            
            data_bytes = zlib.decompress(compressed_data)
            df = pickle.loads(data_bytes)
            
            return df
        except Exception as e:
            return None

    @staticmethod
    def save_encrypted(df: pd.DataFrame, file_path: str, password: str) -> bool:
        try:
            encrypted_data = DataEncryptor.encrypt_data(df, password)
            if encrypted_data:
                with open(file_path, 'wb') as f:
                    f.write(encrypted_data)
                return True
            return False
        except Exception as e:
            return False

    @staticmethod
    def load_encrypted(file_path: str, password: str) -> Optional[pd.DataFrame]:
        try:
            with open(file_path, 'rb') as f:
                encrypted_bytes = f.read()
            
            return DataEncryptor.decrypt_data(encrypted_bytes, password)
        except Exception as e:
            return None

    @staticmethod
    def verify_file(file_path: str) -> bool:
        try:
            with open(file_path, 'rb') as f:
                encrypted_bytes = f.read()
            
            parts = encrypted_bytes.split(b'|', 2)
            if len(parts) != 3:
                return False
            
            header = parts[0]
            return header == b'DATAANALYSER_V1'
        except Exception as e:
            return False
