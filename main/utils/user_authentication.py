from passlib.hash import bcrypt
import base64
import hashlib


def hash_password(password: str) -> str:
    password = password.encode("utf-8")
    sha_password = base64.b64encode(hashlib.sha256(password).digest())

    return bcrypt.hash(sha_password)


def verify_password(password: str, hashed_password: str) -> bool:
    created_hashed_password = hash_password(password)

    return bcrypt.verify(created_hashed_password, hashed_password)
