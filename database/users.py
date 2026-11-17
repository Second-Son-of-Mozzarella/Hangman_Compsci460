from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from database.connection import SessionLocal
from database.models import User

# CREATE

def create_user(username: str):
    """
    Create a new user in the database.

    Returns:
        User object if successful.
        Raises ValueError if username already exists.
    """

    with SessionLocal() as session:
        try:
            new_user = User(username=username)

            session.add(new_user)
            session.commit()

            session.refresh(new_user)

            return new_user

        except IntegrityError:
            session.rollback()
            raise ValueError("Username already exists.")

        except SQLAlchemyError:
            session.rollback()
            raise


# READ

def get_user(user_id: int):
    """
    Retrieve a user using their UserID.
    """

    with SessionLocal() as session:

        statement = select(User).where(
            User.user_id == user_id
        )

        return session.scalar(statement)


def get_user_by_username(username: str):
    """
    Retrieve a user using their username.
    """

    with SessionLocal() as session:

        statement = select(User).where(
            User.username == username
        )

        return session.scalar(statement)


def get_all_users():
    """
    Retrieve every registered user.
    """

    with SessionLocal() as session:

        statement = select(User).order_by(User.user_id)

        return list(session.scalars(statement).all())


# UPDATE

def update_username(user_id: int, new_username: str):
    """
    Update an existing user's username.
    """

    with SessionLocal() as session:
        try:
            user = session.get(User, user_id)

            if user is None:
                return None

            user.username = new_username

            session.commit()
            session.refresh(user)

            return user

        except IntegrityError:
            session.rollback()
            raise ValueError("Username already exists.")

        except SQLAlchemyError:
            session.rollback()
            raise


# DELETE


def delete_user(user_id: int): # Working on handling children
    """
    Delete a user using their UserID.

    """

    with SessionLocal() as session:
        try:
            user = session.get(User, user_id)

            if user is None:
                return False

            session.delete(user)
            session.commit()

            return True

        except IntegrityError:
            session.rollback()
            raise ValueError(
                "Cannot delete user: existing game records reference this user."
            )

        except SQLAlchemyError:
            session.rollback()
            raise
