"""User bootstrap for the demo: the seeded accounts and their passwords.

Both accounts are created (or backfilled with a password hash) by
`python -m digital_wardrobe.seed`, so every row in `User` can log in.
"""

from sqlmodel import Session, select

from digital_wardrobe.auth import hash_password
from digital_wardrobe.models import User

DEMO_EMAIL = "demo@atelier.local"
DEMO_PASSWORD = "demo1234"

SECOND_EMAIL = "sam@atelier.local"
SECOND_PASSWORD = "sam1234"


def get_or_create_user(session: Session, email: str, name: str, password: str) -> User:
    """Fetch a user by email, creating it (or backfilling its hash) as needed."""
    user = session.exec(select(User).where(User.email == email)).first()
    if user is None:
        user = User(email=email, name=name, password_hash=hash_password(password))
        session.add(user)
        session.commit()
        session.refresh(user)
    elif not user.password_hash:
        user.password_hash = hash_password(password)
        session.add(user)
        session.commit()
        session.refresh(user)
    return user


def get_or_create_demo_user(session: Session) -> User:
    return get_or_create_user(session, DEMO_EMAIL, "Demo User", DEMO_PASSWORD)


def get_or_create_second_user(session: Session) -> User:
    return get_or_create_user(session, SECOND_EMAIL, "Sam Rivera", SECOND_PASSWORD)
