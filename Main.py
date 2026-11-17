# Main.py

from database.connection import engine, test_connection
from database.models import Base
import database.models  # Ensures models are registered with Base

from database.users import (
    create_user,
    get_user,
    get_user_by_username,
    get_all_users,
    update_username,
    delete_user
)

def initialize_database():
    print("Testing database connection...")

    if not test_connection():
        print("Database initialization aborted.")
        return

    print("\nCreating database tables...")
    Base.metadata.create_all(bind=engine)
    print("\nDatabase tables initialized successfully!")

    print("\nRegistered tables:")
    for table in Base.metadata.sorted_tables:
        print(f" - {table.name}")


def test_user_crud():
    print("\n========== USER CRUD TEST ==========\n")

    # CREATE
    print("1. Creating user...")

    try:
        user = create_user("TestPlayer")

        print(f"Created: {user.username}")
        print(f"User ID: {user.user_id}")

        user_id = user.user_id

    except ValueError as error:
        print(error)
        return

     # READ
    print("\n2. Retrieving user...")

    user = get_user(user_id)

    if user:
        print(f"Found user: {user.username}")

    # READ BY USERNAME
    print("\n3. Searching by username...")

    user = get_user_by_username("TestPlayer")

    if user:
        print(f"Found: {user.username}")

    # READ ALL
    print("\n4. Retrieving all users...")

    users = get_all_users()

    for user in users:
        print(f"{user.user_id}: {user.username}")

    # UPDATE
    print("\n5. Updating username...")

    user = update_username(user_id, "UpdatedPlayer")

    if user:
        print(f"Updated username: {user.username}")

    # DELETE
    print("\n6. Deleting user...")

    deleted = delete_user(user_id)

    print(f"Deleted successfully: {deleted}")

    # VERIFY DELETE
    print("\n7. Verifying deletion...")

    user = get_user(user_id)

    print(f"User exists: {user is not None}")

    print("\n========== TEST COMPLETE ==========")


if __name__ == "__main__":
    # 1. First, create the tables in MySQL
    initialize_database()
    
    # 2. Then, run your tests
    test_user_crud()