"""Utils for handling user auth functions."""

import base64
import hashlib

from passlib.hash import bcrypt


def hash_password(password: str) -> str:
    """
    Hashes a password.

    This first hashes the password using SHA256, then hashes and salts the result with bcrypt.
    """ # noqa: E501
    password = password.encode("utf-8")
    sha_password = base64.b64encode(hashlib.sha256(password).digest())

    return bcrypt.hash(sha_password)


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify a password against a hashed password.
    """
    created_hashed_password = hash_password(password)

    return bcrypt.verify(created_hashed_password, hashed_password)
