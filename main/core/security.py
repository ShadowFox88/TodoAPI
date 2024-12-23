import base64
import hashlib

from passlib.hash import bcrypt


def verify_password(plain_password: str, hashed_password: str):
    password = plain_password.encode("utf-8")
    sha_password = base64.b64encode(hashlib.sha256(password).digest())

    return bcrypt.verify(sha_password, hashed_password)


def hash_password(user_password: str):
    password = user_password.encode("utf-8")
    sha_password = base64.b64encode(hashlib.sha256(password).digest())

    return bcrypt.hash(sha_password)
