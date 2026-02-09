import os
from mongoengine import connect


def _get_env_bool(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default
    return str(value).lower() in {"1", "true", "yes", "on"}


def _build_local_uri(db_name):
    host = os.getenv("MONGODB_HOST", "localhost")
    port = os.getenv("MONGODB_PORT", "27017")
    return f"mongodb://{host}:{port}/{db_name}"


def connect_databases():
    """
    Connect to MongoDB using local URIs by default.

    Env vars:
    - MONGODB_URI / MONGODB_LOGS_URI override local defaults.
    - MONGODB_TLS and MONGODB_TLS_ALLOW_INVALID toggle TLS settings.
    """
    main_uri = os.getenv("MONGODB_URI") or _build_local_uri("main_db")
    logs_uri = os.getenv("MONGODB_LOGS_URI") or _build_local_uri("logs_db")

    tls_enabled = _get_env_bool("MONGODB_TLS", False)
    tls_allow_invalid = _get_env_bool("MONGODB_TLS_ALLOW_INVALID", True)

    connect(
        db="main_db",
        host=main_uri,
        alias="default",
        tls=tls_enabled,
        tlsAllowInvalidCertificates=tls_allow_invalid,
        uuidRepresentation='standard',
    )

    connect(
        db="logs_db",
        host=logs_uri,
        alias="logs",
        tls=tls_enabled,
        tlsAllowInvalidCertificates=tls_allow_invalid,
        uuidRepresentation='standard',
    )

