
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from database.connection import SessionLocal
from database.models import Game, GamePlayer, GameGuess


# CREATE

def create_guess(
    game_id: int,
    participation_id: int,
    letter: str,
    is_correct: bool,
    positions=None
):
    """
    Record a letter guess.

    Guess order is generated automatically.
    Positions contains the indexes where the letter appears.
    """

    letter = letter.strip().upper()

    if len(letter) != 1 or not letter.isalpha():
        raise ValueError("Guess must be a single letter.")

    with SessionLocal() as session:
        try:
            game = session.get(Game, game_id)

            if game is None:
                raise ValueError("Game does not exist.")

            if game.status != "InProgress":
                raise ValueError("Guesses can only be submitted during an active game.")

            player = session.get(GamePlayer, participation_id)

            if player is None or player.game_id != game_id:
                raise ValueError("Invalid player participation.")

            if player.remaining_guesses <= 0:
                raise ValueError("Player has no guesses remaining.")

            # Determine the next guess order.
            current_order = session.scalar(
                select(func.max(GameGuess.guess_order)).where(
                    GameGuess.game_id == game_id
                )
            )

            next_order = (current_order or 0) + 1

            guess = GameGuess(
                game_id=game_id,
                participation_id=participation_id,
                letter=letter,
                is_correct=is_correct,
                positions=positions,
                guess_order=next_order
            )

            session.add(guess)
            session.commit()
            session.refresh(guess)

            return guess

        except IntegrityError:
            session.rollback()
            raise ValueError(
                "This letter has already been guessed or the guess order conflicts."
            )

        except SQLAlchemyError:
            session.rollback()
            raise


# READ

def get_guess(guess_id: int):
    """Retrieve a guess by its ID."""

    with SessionLocal() as session:
        return session.get(GameGuess, guess_id)


def get_game_guesses(game_id: int):
    """Retrieve all guesses for a game in chronological order."""

    with SessionLocal() as session:
        statement = select(GameGuess).where(
            GameGuess.game_id == game_id
        ).order_by(GameGuess.guess_order)

        return list(session.scalars(statement).all())


def get_player_guesses(participation_id: int):
    """Retrieve all guesses submitted by a specific player."""

    with SessionLocal() as session:
        statement = select(GameGuess).where(
            GameGuess.participation_id == participation_id
        ).order_by(GameGuess.guess_order)

        return list(session.scalars(statement).all())


def get_guessed_letters(game_id: int):
    """Retrieve the letters already guessed in a game."""

    with SessionLocal() as session:
        statement = select(GameGuess.letter).where(
            GameGuess.game_id == game_id
        ).order_by(GameGuess.guess_order)

        return list(session.scalars(statement).all())


# UPDATE

def update_guess(
    guess_id: int,
    is_correct: bool = None,
    positions=None
):
    """Correct an existing guess record."""

    with SessionLocal() as session:
        guess = session.get(GameGuess, guess_id)

        if guess is None:
            return None

        if is_correct is not None:
            guess.is_correct = is_correct

        if positions is not None:
            guess.positions = positions

        session.commit()
        session.refresh(guess)

        return guess


# DELETE

def delete_guess(guess_id: int):
    """Delete a guess record."""

    with SessionLocal() as session:
        try:
            guess = session.get(GameGuess, guess_id)

            if guess is None:
                return False

            session.delete(guess)
            session.commit()

            return True

        except SQLAlchemyError:
            session.rollback()
            raise
