"""Datenbank: SQLAlchemy-Modelle und Verbindung.

Lokal und in den Tests wird SQLite verwendet, produktiv PostgreSQL (Neon).
Welche Datenbank genutzt wird, steuert die Umgebungsvariable DATABASE_URL.
"""

from __future__ import annotations

import os
from datetime import UTC, datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    String,
    UniqueConstraint,
    create_engine,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


def now_utc() -> datetime:
    return datetime.now(UTC).replace(tzinfo=None)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(40), unique=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc)


class Progress(Base):
    """Lernstand pro Benutzer und Item (Verb, Zeit, Person)."""

    __tablename__ = "progress"
    __table_args__ = (UniqueConstraint("user_id", "verb", "tense", "person"),)
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    verb: Mapped[str] = mapped_column(String(40))
    tense: Mapped[str] = mapped_column(String(30))
    person: Mapped[int] = mapped_column(Integer)
    box: Mapped[int] = mapped_column(Integer, default=1)
    correct: Mapped[int] = mapped_column(Integer, default=0)
    wrong: Mapped[int] = mapped_column(Integer, default=0)
    due_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class Attempt(Base):
    """Jede einzelne Antwort, für Verlauf und Auswertung."""

    __tablename__ = "attempts"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    verb: Mapped[str] = mapped_column(String(40))
    tense: Mapped[str] = mapped_column(String(30))
    person: Mapped[int] = mapped_column(Integer)
    answer: Mapped[str] = mapped_column(String(80))
    status: Mapped[str] = mapped_column(String(10))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now_utc)


def database_url() -> str:
    url = os.getenv("DATABASE_URL", "sqlite:///./coniuga.db")
    # Neon und Render liefern "postgres://" oder "postgresql://"; SQLAlchemy
    # braucht den Treibernamen psycopg.
    if url.startswith("postgres://"):
        url = "postgresql://" + url[len("postgres://") :]
    if url.startswith("postgresql://"):
        url = "postgresql+psycopg://" + url[len("postgresql://") :]
    return url


def make_engine(url: str | None = None):
    url = url or database_url()
    kwargs = (
        {"connect_args": {"check_same_thread": False}}
        if url.startswith("sqlite")
        else {"pool_pre_ping": True}
    )
    return create_engine(url, **kwargs)


engine = make_engine()
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def init_db(bind=None) -> None:
    Base.metadata.create_all(bind or engine)
