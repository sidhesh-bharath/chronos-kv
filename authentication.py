import os
import hashlib
import secrets
from dotenv import find_dotenv, load_dotenv, set_key

dotenv_file = find_dotenv()

def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    hash_value = hashlib.pbkdf2_hmac(
        'sha256', 
        password.encode('utf-8'), 
        salt.encode('utf-8'), 
        100000
    )
    set_key(dotenv_file, "CHRONOS_KV_HASH", f"{salt}:{hash_value.hex()}")

def verify_password(provided_password):
    stored_string = os.getenv("CHRONOS_KV_HASH")
    salt, original_hash = stored_string.split(":")
    check_hash = hashlib.pbkdf2_hmac(
        'sha256', 
        provided_password.encode('utf-8'), 
        salt.encode('utf-8'), 
        100000
    )
    return secrets.compare_digest(check_hash.hex(), original_hash)
