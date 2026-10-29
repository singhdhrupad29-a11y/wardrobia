"""Password hashing for the login flow — PBKDF2-HMAC-SHA256, stdlib only.

Stored format (one string column, no extra table):

    pbkdf2_sha256$200000$<salt hex>$<digest hex>

The salt is 16 random bytes per user and the iteration count is stored with
the hash, so both can be raised later without invalidating existing accounts.
"""

import hashlib
import hmac
import os

ALGORITHM = "pbkdf2_sha256"
ITERATIONS = 200_000
MIN_PASSWORD_LENGTH = 6


def hash_password(password: str) -> str:
    """Hash a plaintext password into the storable format."""
    if len(password) < MIN_PASSWORD_LENGTH:
        raise ValueError(f"Password must be at least {MIN_PASSWORD_LENGTH} characters.")
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, ITERATIONS)
    return f"{ALGORITHM}${ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str | None) -> bool:
    """Constant-time check of a plaintext password against a stored hash."""
    if not stored:
        return False
    try:
        algorithm, iterations, salt_hex, digest_hex = stored.split("$")
        if algorithm != ALGORITHM:
            return False
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            bytes.fromhex(salt_hex),
            int(iterations),
        )
        return hmac.compare_digest(digest.hex(), digest_hex)
    except (ValueError, TypeError):
        return False
