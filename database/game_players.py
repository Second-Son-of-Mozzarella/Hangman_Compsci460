
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from database.connection import SessionLocal
from database.models import Game, GamePlayer


# CREATE

def join_game(game_id: int, user_id: int):
    """
    Add a user to an existing game as a Guesser.

    Checks that the lobby exists, is open, and has room.
    """

    with SessionLocal() as session:
        try:
            game = session.get(Game, game_id)

            if game is None:
                raise ValueError("Game does not exist.")

            if game.status != "Lobby":
                raise ValueError("This game is no longer accepting players.")

            player_count = session.scalar(
                select(func.count()).select_from(GamePlayer).where(
                    GamePlayer.game_id == game_id
                )
            )

            if player_count >= game.max_players:
                raise ValueError("This game is full.")

            player = GamePlayer(
                game_id=game_id,
                user_id=user_id,
                role="Guesser",
                remaining_guesses=game.starting_lives
            )

            session.add(player)
            session.commit()
            session.refresh(player)

            return player

        except IntegrityError:
            session.rollback()
            raise ValueError(
                "User is already participating or the user/game does not exist."
            )

        except SQLAlchemyError:
            session.rollback()
            raise


# READ

def get_game_player(participation_id: int):
    """Retrieve a participation record by ID."""

    with SessionLocal() as session:
        return session.get(GamePlayer, participation_id)


def get_game_players(game_id: int):
    """Retrieve all players participating in a game."""

    with SessionLocal() as session:
        statement = select(GamePlayer).where(
            GamePlayer.game_id == game_id
        ).order_by(GamePlayer.participation_id)

        return list(session.scalars(statement).all())


def get_user_games(user_id: int):
    """Retrieve all game participation records for a user."""

    with SessionLocal() as session:
        statement = select(GamePlayer).where(
            GamePlayer.user_id == user_id
        ).order_by(GamePlayer.joined_at.desc())

        return list(session.scalars(statement).all())


# UPDATE

def update_remaining_guesses(participation_id: int, remaining_guesses: int):
    """Update a player's remaining guesses."""

    if remaining_guesses < 0:
        raise ValueError("Remaining guesses cannot be negative.")

    with SessionLocal() as session:
        player = session.get(GamePlayer, participation_id)

        if player is None:
            return None

        player.remaining_guesses = remaining_guesses

        session.commit()
        session.refresh(player)

        return player


def update_player_result(participation_id: int, result: str):
    """Record a player's result in a game."""

    allowed_results = {"Won", "Lost", "Draw"}

    if result not in allowed_results:
        raise ValueError("Invalid player result.")

    with SessionLocal() as session:
        player = session.get(GamePlayer, participation_id)

        if player is None:
            return None

        player.result = result

        session.commit()
        session.refresh(player)

        return player


# DELETE

def leave_game(participation_id: int):
    """Remove a player's participation record."""

    with SessionLocal() as session:
        try:
            player = session.get(GamePlayer, participation_id)

            if player is None:
                return False

            session.delete(player)
            session.commit()

            return True

        except IntegrityError:
            session.rollback()
            raise ValueError(
                "Cannot remove player: existing guesses reference this participation."
            )

        except SQLAlchemyError:
            session.rollback()
            raise
