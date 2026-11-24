
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from database.connection import SessionLocal
from database.models import Game, GamePlayer


# CREATE

def create_game(
    host_id: int,
    lobby_code: str,
    visibility: bool = True,
    max_players: int = 2,
    starting_lives: int = 6,
    min_word_length: int = 3,
    max_word_length: int = 15
):
    """
    Create a game and its host participation record.

    Both records are committed in one transaction.
    Returns the new Game object.
    """

    with SessionLocal.begin() as session:

        game = Game(
            host_id=host_id,
            lobby_code=lobby_code,
            visibility=visibility,
            max_players=max_players,
            starting_lives=starting_lives,
            min_word_length=min_word_length,
            max_word_length=max_word_length,
            status="Lobby"
        )

        session.add(game)
        session.flush()  # Generate game_id before creating participation.

        host = GamePlayer(
            game_id=game.game_id,
            user_id=host_id,
            role="Host",
            remaining_guesses=starting_lives
        )

        session.add(host)
        session.flush()

        session.refresh(game)
        return game


# READ

def get_game(game_id: int):
    """Retrieve a game by its ID."""

    with SessionLocal() as session:
        return session.get(Game, game_id)


def get_game_by_lobby_code(lobby_code: str):
    """Retrieve a game using its lobby code."""

    with SessionLocal() as session:
        statement = select(Game).where(
            Game.lobby_code == lobby_code
        )
        return session.scalar(statement)


def get_all_games():
    """Retrieve all games."""

    with SessionLocal() as session:
        statement = select(Game).order_by(Game.game_id)
        return list(session.scalars(statement).all())


def get_open_lobbies():
    """Retrieve publicly visible games that are still accepting players."""

    with SessionLocal() as session:
        statement = select(Game).where(
            Game.visibility == True,
            Game.status == "Lobby"
        ).order_by(Game.created_at)

        return list(session.scalars(statement).all())


# UPDATE

def update_game_settings(
    game_id: int,
    visibility=None,
    max_players=None,
    starting_lives=None,
    min_word_length=None,
    max_word_length=None
):
    """Update lobby settings before the game starts."""

    with SessionLocal() as session:
        try:
            game = session.get(Game, game_id)

            if game is None:
                return None

            if game.status != "Lobby":
                raise ValueError("Cannot change settings after the game starts.")

            if visibility is not None:
                game.visibility = visibility

            if max_players is not None:
                game.max_players = max_players

            if starting_lives is not None:
                game.starting_lives = starting_lives

            if min_word_length is not None:
                game.min_word_length = min_word_length

            if max_word_length is not None:
                game.max_word_length = max_word_length

            session.commit()
            session.refresh(game)
            return game

        except (IntegrityError, SQLAlchemyError):
            session.rollback()
            raise


def update_game_status(game_id: int, new_status: str):
    """Change the status of a game."""

    allowed_statuses = {
        "Lobby", "InProgress", "Completed", "Cancelled"
    }

    if new_status not in allowed_statuses:
        raise ValueError("Invalid game status.")

    with SessionLocal() as session:
        game = session.get(Game, game_id)

        if game is None:
            return None

        game.status = new_status
        session.commit()
        session.refresh(game)

        return game


def finish_game(game_id: int, winner_id: int = None):
    """Mark a game completed and optionally record its winner."""

    from datetime import datetime

    with SessionLocal() as session:
        game = session.get(Game, game_id)

        if game is None:
            return None

        game.status = "Completed"
        game.winner_id = winner_id
        game.finished_at = datetime.now()

        session.commit()
        session.refresh(game)

        return game


# DELETE

def delete_game(game_id: int):
    """Delete a game and its associated records."""

    with SessionLocal() as session:
        try:
            game = session.get(Game, game_id)

            if game is None:
                return False

            session.delete(game)
            session.commit()

            return True

        except IntegrityError:
            session.rollback()
            raise ValueError(
                "Cannot delete game: other records reference this game."
            )

        except SQLAlchemyError:
            session.rollback()
            raise
