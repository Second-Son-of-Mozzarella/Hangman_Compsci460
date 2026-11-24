
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

import DatabaseManager


from uuid import uuid4


def testBasic():
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


def test():
    print("\n========== DATABASE MANAGER TEST ==========\n")

    test_id = uuid4().hex[:8].upper()

    host_username = f"Host_{test_id}"
    guesser_username = f"Guesser_{test_id}"
    temporary_username = f"Delete_{test_id}"
    lobby_code = f"TEST_{test_id}"

    try:

        print("\n[1] TESTING USER MANAGEMENT")

        # Create users
        host = create_user(host_username)
        guesser = create_user(guesser_username)

        assert host is not None
        assert guesser is not None

        print("PASS: Users created.")


        retrieved_host = get_user(host.user_id)

        assert retrieved_host is not None
        assert retrieved_host.username == host_username

        print("PASS: Retrieve user by ID.")

  
        retrieved_guesser = get_user_by_username(guesser_username)

        assert retrieved_guesser is not None
        assert retrieved_guesser.user_id == guesser.user_id

        print("PASS: Retrieve user by username.")


        users = get_all_users()

        assert any(u.user_id == host.user_id for u in users)
        assert any(u.user_id == guesser.user_id for u in users)

        print("PASS: Retrieve all users.")

        updated_username = f"Updated_{test_id}"

        updated_host = update_username(
            host.user_id,
            updated_username
        )

        assert updated_host.username == updated_username

        print("PASS: Update username.")

        try:
            create_user(updated_username)
            raise AssertionError("Duplicate username was accepted.")

        except ValueError:
            print("PASS: Duplicate username rejected.")

        print("\n[2] TESTING GAME MANAGEMENT")

        game = create_game(
            host_id=host.user_id,
            lobby_code=lobby_code
        )

        assert game is not None
        assert game.host_id == host.user_id
        assert game.lobby_code == lobby_code
        assert game.status == "Lobby"

        print("PASS: Create game.")

        retrieved_game = get_game(game.game_id)

        assert retrieved_game is not None
        assert retrieved_game.game_id == game.game_id

        print("PASS: Retrieve game by ID.")

        retrieved_game = get_game_by_lobby_code(lobby_code)

        assert retrieved_game is not None
        assert retrieved_game.game_id == game.game_id

        print("PASS: Retrieve game by lobby code.")


        print("\n[3] TESTING PLAYER MANAGEMENT")

        players = get_game_players(game.game_id)

        assert len(players) == 1
        assert players[0].user_id == host.user_id
        assert players[0].role == "Host"

        print("PASS: Host automatically added to game.")

        guesser_player = join_game(
            game_id=game.game_id,
            user_id=guesser.user_id
        )

        assert guesser_player is not None
        assert guesser_player.user_id == guesser.user_id
        assert guesser_player.role == "Guesser"

        print("PASS: User joins game.")

        players = get_game_players(game.game_id)

        assert len(players) == 2

        print("PASS: Retrieve game participants.")


        print("\n[4] TESTING GAME STATUS MANAGEMENT")

        update_game_status(game.game_id, "InProgress")

        updated_game = get_game(game.game_id)

        assert updated_game.status == "InProgress"

        print("PASS: Update game status to InProgress.")


        print("\n[5] TESTING GUESS MANAGEMENT")

        guess = create_guess(
            game_id=game.game_id,
            participation_id=guesser_player.participation_id,
            letter="A",
            is_correct=True,
            positions=[0, 3]
        )

        assert guess is not None
        assert guess.letter == "A"
        assert guess.is_correct is True

        print("PASS: Record correct guess.")

        incorrect_guess = create_guess(
            game_id=game.game_id,
            participation_id=players[0].participation_id,
            letter="Z",
            is_correct=False,
            positions=[]
        )

        assert incorrect_guess is not None
        assert incorrect_guess.letter == "Z"
        assert incorrect_guess.is_correct is False

        print("PASS: Record incorrect guess.")

        guesses = get_game_guesses(game.game_id)

        assert len(guesses) == 2

        print("PASS: Retrieve game guesses.")

        assert guesses[0].guess_order < guesses[1].guess_order

        print("PASS: Guess ordering.")


        try:
            create_guess(
                game_id=game.game_id,
                participation_id=guesser_player.participation_id,
                letter="A",
                is_correct=True,
                positions=[0, 3]
            )

            raise AssertionError("Duplicate guess was accepted.")

        except ValueError:
            print("PASS: Duplicate guess rejected.")

        print("\n[6] TESTING GAME COMPLETION")

        finished_game = finish_game(
            game.game_id,
            guesser.user_id
        )

        assert finished_game is not None
        assert finished_game.status == "Completed"
        assert finished_game.winner_id == guesser.user_id

        print("PASS: Finish game.")

        retrieved_game = get_game(game.game_id)

        assert retrieved_game.status == "Completed"
        assert retrieved_game.winner_id == guesser.user_id

        print("PASS: Verify completed game and winner.")

        print("\n[7] TESTING USER DELETION")

        temporary_user = create_user(temporary_username)

        assert temporary_user is not None

        delete_user(temporary_user.user_id)

        deleted_user = get_user(temporary_user.user_id)

        assert deleted_user is None

        print("PASS: Delete user.")

        
        print("\n==========================================")
        print("ALL DATABASE TESTS PASSED!")
        print("==========================================")

        print("\nTest Records:")
        print(f"Host: {updated_username}")
        print(f"Guesser: {guesser_username}")
        print(f"Lobby: {lobby_code}")
        print(f"Game ID: {game.game_id}")

    except Exception as error:
        print("\n==========================================")
        print("DATABASE TEST FAILED!")
        print("==========================================")
        print(f"Error: {type(error).__name__}: {error}")

        raise
