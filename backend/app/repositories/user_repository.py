"""
User repository — database operations for the User model.

Follows the same repository pattern as ExecutionRepository and
ExecutionIterationRepository: receives a db session in __init__,
exposes focused query/mutation methods, commits within each method.
"""

from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.db.models.user import User
import bcrypt

class UserRepository:

    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, user_id) -> User | None:
        """Fetch a user by primary key."""
        return (
            self.db.query(User)
            .filter(User.id == user_id)
            .first()
        )

    def get_by_google_id(self, google_id: str) -> User | None:
        """Fetch a user by their Google sub claim."""
        return (
            self.db.query(User)
            .filter(User.google_id == google_id)
            .first()
        )

    def get_by_email(self, email: str) -> User | None:
        """Fetch a user by email address."""
        return (
            self.db.query(User)
            .filter(User.email == email)
            .first()
        )

    def upsert_from_google(
        self,
        google_id: str,
        email: str,
        name: str | None = None,
        picture: str | None = None,
    ) -> User:
        """
        Create a user on first login, or update profile on subsequent logins.

        The match key is ``google_id`` (Google's stable ``sub`` claim).
        On every login we update ``email``, ``name``, and ``profile_picture``
        in case the user changed their Google profile.
        """
        user = self.get_by_google_id(google_id)

        if user is None:
            user = User(
                google_id=google_id,
                email=email,
                name=name or email.split("@")[0].capitalize(),
                profile_picture=picture,
            )
            self.db.add(user)
        else:
            # Update mutable fields on every login
            user.email = email
            user.name = name or user.name
            user.profile_picture = picture

        self.db.commit()
        self.db.refresh(user)
        return user

    def register_by_email(
        self,
        email: str,
        password: str,
    ) -> User | None:
        """
        Register a new user by email and password.
        Returns None if the email is already taken.
        """
        user = self.get_by_email(email)
        if user is not None:
            return None  # email already exists

        name = email.split('@')[0].capitalize()
        salt = bcrypt.gensalt()
        password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
        user = User(
            email=email,
            name=name,
            password_hash=password_hash,
        )
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def login_by_email(
        self,
        email: str,
        password: str,
    ) -> User | None:
        """
        Authenticate an existing user by email and password.
        Returns None if the user doesn't exist or password is wrong.
        """
        user = self.get_by_email(email)
        if user is None:
            return None

        if not user.password_hash:
            # User registered via Google OAuth — no password set
            return None

        if bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            return user
        return None

    def get_or_create_by_email_and_password(
        self,
        email: str,
        password: str,
    ) -> User | None:
        """
        Fetch a user by email, or create a new user profile on first login.
        If user exists, verify password. Returns None if password fails.
        """
        user = self.get_by_email(email)

        if user is None:
            name = email.split('@')[0].capitalize()
            salt = bcrypt.gensalt()
            password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
            user = User(
                email=email,
                name=name,
                password_hash=password_hash,
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            return user
        
        # User exists, verify password
        if user.password_hash:
            if bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
                return user
        return None

