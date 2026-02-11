import os
import base64
from dotenv import load_dotenv

# Load .env into environment
load_dotenv()

# Read secret key string from env and encode to bytes
secret_key_str = os.getenv("JWT_SECRET_KEY")
if secret_key_str is None:
    raise RuntimeError("SECRET_KEY not found in environment")
_SECRET_KEY = secret_key_str.encode("utf-8")


def encrypt_int(i: int) -> str:
    """
    Encrypts an integer into a URL-safe base64 string using XOR and a secret key.
    """
    if i < 0:
        raise ValueError("Only non-negative integers are supported")
    # Convert integer to bytes (minimal length)
    byte_length = (i.bit_length() + 7) // 8 or 1
    data = i.to_bytes(byte_length, "big")
    # XOR with secret key
    xored = bytes(data[j] ^ _SECRET_KEY[j % len(_SECRET_KEY)] for j in range(len(data)))
    # URL-safe Base64 encode
    return base64.urlsafe_b64encode(xored).decode("utf-8")


def decrypt_string(s: str) -> int:
    """
    Decrypts the string back into the original integer.
    """
    # Base64-decode
    xored = base64.urlsafe_b64decode(s.encode("utf-8"))
    # Reverse XOR with secret key
    data = bytes(xored[j] ^ _SECRET_KEY[j % len(_SECRET_KEY)] for j in range(len(xored)))
    # Convert bytes back to integer
    return int.from_bytes(data, "big")
