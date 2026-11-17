
from datetime import datetime

from sqlalchemy import (
    String,
    Integer,
    Boolean,
    DateTime,
    ForeignKey,
    JSON,
    UniqueConstraint,
    CheckConstraint,
    func
)

from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship
)

# BASE MODEL

class Base(DeclarativeBase):
    pass



# USER TABLE

class User(Base):

    __tablename__ = "User"

    user_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    username: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp(),
        nullable=False
    )

    # User relationships
    game_participations: Mapped[list["GamePlayer"]] = relationship(
        back_populates="user"
    )


# GAME TABLE

class Game(Base):

    __tablename__ = "Game"

    game_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    host_id: Mapped[int] = mapped_column(
        ForeignKey("User.user_id"),
        nullable=False
    )

    winner_id: Mapped[int | None] = mapped_column(
        ForeignKey("User.user_id"),
        nullable=True
    )

    lobby_code: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False
    )

    # Lobby configuration
    visibility: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    max_players: Mapped[int] = mapped_column(
        Integer,
        default=2,
        nullable=False
    )

    starting_lives: Mapped[int] = mapped_column(
        Integer,
        default=6,
        nullable=False
    )

    min_word_length: Mapped[int] = mapped_column(
        Integer,
        default=3,
        nullable=False
    )

    max_word_length: Mapped[int] = mapped_column(
        Integer,
        default=15,
        nullable=False
    )

    # Game state
    secret_word: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(20),
        default="Lobby",
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp()
    )

    started_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    # User relationships
    host: Mapped["User"] = relationship(
        foreign_keys=[host_id]
    )

    winner: Mapped["User | None"] = relationship(
        foreign_keys=[winner_id]
    )

    # Game relationships
    players: Mapped[list["GamePlayer"]] = relationship(
        back_populates="game",
        cascade="all, delete-orphan"
    )

    guesses: Mapped[list["GameGuess"]] = relationship(
        back_populates="game",
        cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("max_players >= 2"),
        CheckConstraint("starting_lives > 0"),
        CheckConstraint("min_word_length > 0"),
        CheckConstraint("max_word_length >= min_word_length"),
        CheckConstraint(
            "status IN ('Lobby', 'InProgress', 'Completed', 'Cancelled')"
        ),
    )


# GAME PLAYERS TABLE
class GamePlayer(Base):

    __tablename__ = "GamePlayers"

    participation_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    game_id: Mapped[int] = mapped_column(
        ForeignKey("Game.game_id"),
        nullable=False
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("User.user_id"),
        nullable=False
    )

    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    remaining_guesses: Mapped[int] = mapped_column(
        Integer,
        default=6,
        nullable=False
    )

    result: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True
    )

    joined_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp()
    )

    # Relationships
    game: Mapped["Game"] = relationship(
        back_populates="players"
    )

    user: Mapped["User"] = relationship(
        back_populates="game_participations"
    )

    guesses: Mapped[list["GameGuess"]] = relationship(
        back_populates="player"
    )

    __table_args__ = (
        UniqueConstraint(
            "game_id",
            "user_id",
            name="UQ_GamePlayers_User"
        ),
        CheckConstraint("remaining_guesses >= 0"),
        CheckConstraint("role IN ('Host', 'Guesser')"),
    )



# GAME GUESSES TABLE


class GameGuess(Base):

    __tablename__ = "GameGuesses"

    guess_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    game_id: Mapped[int] = mapped_column(
        ForeignKey("Game.game_id"),
        nullable=False
    )

    participation_id: Mapped[int] = mapped_column(
        ForeignKey("GamePlayers.participation_id"),
        nullable=False
    )

    letter: Mapped[str] = mapped_column(
        String(1),
        nullable=False
    )

    is_correct: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False
    )

    positions: Mapped[list[int] | None] = mapped_column(
        JSON,
        nullable=True
    )

    guess_order: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    guessed_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.current_timestamp()
    )

    # Relationships
    game: Mapped["Game"] = relationship(
        back_populates="guesses"
    )

    player: Mapped["GamePlayer"] = relationship(
        back_populates="guesses"
    )

    __table_args__ = (
        UniqueConstraint(
            "game_id",
            "letter",
            name="UQ_GameGuesses_Letter"
        ),
        UniqueConstraint(
            "game_id",
            "guess_order",
            name="UQ_GameGuesses_Order"
        ),
        CheckConstraint("guess_order > 0"),
    )
