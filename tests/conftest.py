import os
import tempfile
from pathlib import Path

import pytest

# Eigene SQLite-Datenbank für die Tests, bevor die App importiert wird
_tmp = Path(tempfile.mkdtemp()) / "test.db"
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp}"

from fastapi.testclient import TestClient  # noqa: E402

from app import examples  # noqa: E402
from app.db import Base, engine  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture
def client(monkeypatch):
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    # Der externe Dienst wird in den Tests nicht wirklich aufgerufen
    monkeypatch.setattr(
        examples,
        "fetch_examples",
        lambda form, limit=3, client=None: {
            "source": "test",
            "query": form,
            "examples": [],
        },
    )
    with TestClient(app) as c:
        yield c
