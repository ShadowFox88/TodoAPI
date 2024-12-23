from __future__ import annotations

import json
import logging
import os


class AppSettings:
    """
    The class that contains the application settings. Will take settings from environment variables, else revert to a default set.
    """  # noqa: E501

    DEBUG: bool = False

    API_PREFIX: str = "api"
    # Can't be changed by user
    ALL_API_VERSIONS: list[str] = ["v1"]
    DEPRECATED_API_VERSIONS: list[str] = []

    ALLOWED_HOSTS: list[str] = []

    LOGGING_LEVEL: int = logging.INFO

    DATABASE_HOST: str = "TodoAPI-DB"
    DATABASE_PORT: int = 5432
    DATABASE_USERNAME: str = "TodoAPI"
    DATABASE_PASSWORD: str | None = None
    DATABASE_NAME: str = "TodoAPI"

    SECRET_KEY: str
    # Can't be changed by user
    ALGORITHM: str = "HS256"
    AUTH_TOKEN_EXPIRATION: int = 3600  # This is in minutes

    GLOBAL_RATELIMIT_INTERVAL: int = 60
    GLOBAL_RATELIMIT_LIMIT: int = 1
    REDIS_PASSWORD: str | None = None

    def __init__(self):
        """
        Calls all the functions to verify the settings exist, and are of the proper type and expected value.
        """
        self.set_debug()
        self.set_api_prefix()
        self.set_deprecated_apis()
        self.set_allowed_hosts()
        self.set_logging_level()
        self.set_database_url()
        self.set_database_port()
        self.set_database_password()
        self.set_secret_key()
        self.set_redis_password()

        self.DATABASE_URL = f"postgresql+asyncpg://{self.DATABASE_USERNAME}:{self.DATABASE_PASSWORD}@{self.DATABASE_HOST}:{self.DATABASE_PORT}/{self.DATABASE_NAME}"
        self.REDIS_URL = f"redis://:{self.REDIS_PASSWORD}@TodoAPI-Redis:6379/0"

    def set_debug(self):
        env_debug = os.getenv("DEBUG")

        if env_debug is None:
            return

        if env_debug.lower() in ["true", "false"]:
            self.DEBUG = env_debug.lower() == "true"
            return

    def set_api_prefix(self):
        env_api_prefix = os.getenv("API_PREFIX")

        if env_api_prefix is None:
            return

        if env_api_prefix.startswith("/"):
            env_api_prefix = env_api_prefix[1:]

        self.API_PREFIX = env_api_prefix

    def set_deprecated_apis(self):
        deprecated_apis = json.loads(os.getenv("DEPRECATED_APIS", "[]"))

        if deprecated_apis is None:
            return

        for i in deprecated_apis:
            if not isinstance(i, str):
                raise ValueError("Deprecated APIs must be a list of strings")
            if not i.startswith("v"):
                raise ValueError("Deprecated APIs must refer to a version")
            if i not in self.ALL_API_VERSIONS:
                raise ValueError("Deprecated APIs must refer to a valid version")

        if len(deprecated_apis) == len(self.ALL_API_VERSIONS):
            raise ValueError("Cannot deprecate all API versions")

        self.DEPRECATED_API_VERSIONS = deprecated_apis

    def set_allowed_hosts(self):
        allowed_hosts = json.loads(os.getenv("ALLOWED_HOSTS", "[]"))

        for i in allowed_hosts:
            if not isinstance(i, str):
                raise ValueError("Allowed hosts must be a list of strings")

        for i in allowed_hosts:
            if not i.startswith("http://") and not i.startswith("https://"):
                raise ValueError("Allowed hosts must start with http:// or https://")

        self.ALLOWED_HOSTS = allowed_hosts

    def set_logging_level(self):
        env_logging_level = os.getenv("LOGGING_LEVEL")

        if env_logging_level is None:
            return

        if env_logging_level.lower() in [
            "debug",
            "info",
            "warning",
            "error",
            "critical",
        ]:
            self.LOGGING_LEVEL = getattr(logging, env_logging_level.upper())
            return

    def set_database_url(self):
        env_database_url = os.getenv("DATABASE_URL")

        if env_database_url is None:
            return

        self.DATABASE_URL = env_database_url

    def set_database_port(self):
        env_database_port = os.getenv("DATABASE_PORT")

        if env_database_port is None:
            return

        if env_database_port.isnumeric():
            self.DATABASE_PORT = int(env_database_port)
            return
        raise ValueError("Database port must be a number")

    def set_database_password(self):
        env_database_password = os.getenv("DATABASE_PASSWORD")

        if env_database_password is None:
            return

        self.DATABASE_PASSWORD = env_database_password

    def set_secret_key(self):
        env_secret_key = os.getenv("SECRET_KEY")

        if env_secret_key is None:
            raise ValueError(
                'Secret key must be set. Generate one using "openssl rand -hex 32"'
            )

        self.SECRET_KEY = env_secret_key

    def set_redis_password(self):
        redis_password = os.getenv("REDIS_PASSWORD")

        if redis_password is None:
            raise ValueError(
                'Secret key must be set. Generate one using "openssl rand -hex 32"'
            )

        self.REDIS_PASSWORD = redis_password
