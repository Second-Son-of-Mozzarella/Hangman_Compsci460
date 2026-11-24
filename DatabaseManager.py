from database.connection import engine, test_connection
from database.models import Base
import database.models
from uuid import uuid4

from database.users import (
    create_user,
    get_user,
    get_user_by_username,
    get_all_users,
    update_username,
    delete_user
)

from database.games import (
    create_game,
    get_game,
    get_game_by_lobby_code,
    get_open_lobbies,
    update_game_status,
    finish_game
)

from database.game_players import (
    join_game,
    get_game_players
)

from database.game_guesses import (
    create_guess,
    get_game_guesses
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



def test():
    print("\n========== GAME SYSTEM TEST ==========\n")

    # Generate unique test data for every run
    test_id = uuid4().hex[:8].upper()

    host = create_user(f"HostTest_{test_id}")
    guesser = create_user(f"GuesserTest_{test_id}")

    print("1. Creating game...")
    game = create_game(
        host_id=host.user_id,
        lobby_code=f"TEST{test_id}"
    )
    print(f"Game ID: {game.game_id}")
    print(f"Lobby Code: {game.lobby_code}")

    print("\n2. Joining game...")
    player = join_game(
        game_id=game.game_id,
        user_id=guesser.user_id
    )
    print(f"Participation ID: {player.participation_id}")

    print("\n3. Retrieving players...")
    players = get_game_players(game.game_id)
    for p in players:
        print(f"User ID: {p.user_id}, Role: {p.role}")

    print("\n4. Starting game...")
    update_game_status(game.game_id, "InProgress")

    print("\n5. Recording guess...")
    guess = create_guess(
        game_id=game.game_id,
        participation_id=player.participation_id,
        letter="A",
        is_correct=True,
        positions=[0, 3]
    )
    print(f"Guess: {guess.letter}")
    print(f"Correct: {guess.is_correct}")

    print("\n6. Retrieving guesses...")
    guesses = get_game_guesses(game.game_id)
    for g in guesses:
        print(f"{g.guess_order}: {g.letter}")

    print("\n========== TEST COMPLETE ==========")


def get_all_users_info():
    users = get_all_users()
    if not users:
        print("No users found.")
        return []

    print("Registered users:")
    for user in users:
        print(f"User ID: {user.user_id}, Username: {user.username}")
    return users

def updateUser():
    user = getUserByUsername()
    if not user:
        print("User not found.")
        return None
    new_username = input("Enter new username: ")
    if not new_username:
        print("New username cannot be empty.")
        return None
    updated_user = update_username(user.user_id, new_username)
    print(f"Username updated to: {updated_user.username}")
    return updated_user

def deleteUser():
    user = getUserByUsername()
    if not user:
        print("User not found.")
        return None
    confirmation = input(f"Are you sure you want to delete user '{user.username}'? (yes/no): ")
    if confirmation.lower() != "yes":
        print("Deletion cancelled.")
        return None
    delete_user(user.user_id)
    print(f"User '{user.username}' deleted successfully.")


def getUserNameById():
    user_id_input = input("Enter user ID to search: ")
    try:
        user_id = int(user_id_input)
    except ValueError:
        print("Invalid user ID. Please enter a numeric value.")
        return None

    user = get_user(user_id)
    if user:
        print(f"User found: ID {user.user_id}, Username {user.username}")
    else:
        print("User not found.")
    return user

def getGameByLobbyCode():
    lobby_code = input("Enter a lobby code to search: ")
    game = get_game_by_lobby_code(lobby_code)
    if game:
        print(f"Game found: ID {game.game_id}, Lobby Code {game.lobby_code}, Status {game.status}")
    else:
        print("No game found with that lobby code.")
    return game


def finishGame():
    game = getGameByLobbyCode()
    if not game:
        print("Cannot finish a non-existent game.")
        return None

    winner = getUserByUsername()
    winner_id = winner.user_id if winner else None

    finished_game = finish_game(game.game_id, winner_id)
    print(f"Game {finished_game.lobby_code} marked as completed.")
    if winner_id:
        print(f"Winner: {winner.username}")

def createNewUser():
    username = input("Enter a username: ")
    user = create_user(username)
    print(f"User created with ID: {user.user_id} and username: {user.username}")

def getUserByUsername():
    username = input("Enter a username to search: ")
    user = get_user_by_username(username)
    if user:
        print(f"User found: ID {user.user_id}, Username {user.username}")
    else:
        print("User not found.")
    return user

def checkLobbyCode():
    lobby_code = input("Enter a lobby code to check: ")
    game = get_game_by_lobby_code(lobby_code)
    if game:
        print(f"Game found: ID {game.game_id}, Lobby Code {game.lobby_code}, Status {game.status}")
    else:
        print("No game found with that lobby code.")
    return game

def createNewGame():
    host_id = getUserByUsername().user_id
    lobby_code = input("Enter lobby code: ")
    if not lobby_code:
        print("Lobby code cannot be empty.")
        return None
    if get_game_by_lobby_code(lobby_code):
        print("Lobby code already exists. Please choose a different code.")
        return None
    if not host_id:
        print("Host user ID is invalid.")
        return None
    game = create_game(host_id, lobby_code)
    print(f"Game created with ID: {game.game_id} and lobby code: {game.lobby_code}")

def joinExistingGame():
    game = checkLobbyCode()
    if not game:
        print("Cannot join a non-existent game.")
        return None
    user = getUserByUsername()
    if not user:
        print("Cannot join game with a non-existent user.")
        return None
    try:
        player = join_game(game.game_id, user.user_id)
        print(f"User {user.username} joined game {game.lobby_code} as a {player.role}.")
    except ValueError as e:
        print(f"Error joining game: {e}")

def checkGameStatus():
    game = checkLobbyCode()
    if not game:
        print("Cannot check status for a non-existent game.")
        return None
    print(f"Game ID: {game.game_id}, Lobby Code: {game.lobby_code}, Status: {game.status}, Visibility: {game.visibility}")

def updateGameStatus():
    game = checkLobbyCode()
    if not game:
        print("Cannot update status for a non-existent game.")
        return None
    new_status = input("Enter new status (Lobby, InProgress, Completed, Cancelled): ")
    if new_status not in ["Lobby", "InProgress", "Completed", "Cancelled"]:
        print("Invalid status. Please enter one of the following: Lobby, InProgress, Completed, Cancelled.")
        return None
    update_game_status(game.game_id, new_status)
    print(f"Game {game.lobby_code} status updated to {new_status}.")



def findOpenGames():
    with SessionLocal() as session:
        open_games = session.query(Game).filter(Game.status == "Lobby").all()
        if not open_games:
            print("No open games found.")
            return []
        print("Open games:")
        for game in open_games:
            print(f"Game ID: {game.game_id}, Lobby Code: {game.lobby_code}, Host ID: {game.host_id}")
        return open_games


