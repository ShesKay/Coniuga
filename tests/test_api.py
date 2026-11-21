def login(client, name="Kay"):
    return client.post("/api/users", json={"name": name})


def test_health(client):
    assert client.get("/api/health").json() == {"status": "ok"}


def test_frontend_is_served(client):
    response = client.get("/")
    assert response.status_code == 200 and "Coniuga" in response.text


def test_verbs_and_table(client):
    verbs = client.get("/api/verbs").json()
    assert len(verbs) >= 50 and verbs[0]["infinitive"] == "essere"
    table = client.get("/api/verbs/andare").json()
    assert table["tenses"]["presente"]["forms"]["noi"] == "andiamo"
    assert client.get("/api/verbs/xyzare").status_code == 404


def test_user_login_is_idempotent(client):
    assert login(client).json()["created"] is True
    assert login(client).json()["created"] is False


def test_invalid_name(client):
    assert client.post("/api/users", json={"name": "<script>"}).status_code == 422


def test_practice_cycle_updates_progress(client):
    login(client)
    ex = client.get("/api/users/Kay/exercise").json()
    assert ex["tense"] == "presente" and ex["new"] is True
    from app.conjugation import conjugate

    right = conjugate(ex["verb"], ex["tense"])[ex["person"]].split("/")[0]
    res = client.post(
        "/api/users/Kay/answers",
        json={
            "verb": ex["verb"],
            "tense": ex["tense"],
            "person": ex["person"],
            "answer": right,
        },
    ).json()
    assert res["status"] == "correct" and res["box_after"] == 2
    wrong = client.post(
        "/api/users/Kay/answers",
        json={
            "verb": ex["verb"],
            "tense": ex["tense"],
            "person": ex["person"],
            "answer": "xxx",
        },
    ).json()
    assert wrong["status"] == "wrong" and wrong["box_after"] == 1
    prog = client.get("/api/users/Kay/progress").json()
    assert prog["attempts"] == 2 and prog["accuracy"] == 0.5
    assert prog["weakest"][0]["verb"] == ex["verb"]


def test_focus_exercise(client):
    login(client)
    ex = client.get(
        "/api/users/Kay/exercise", params={"verb": "fare", "tense": "passato_prossimo"}
    ).json()
    assert (
        ex["verb"] == "fare"
        and ex["tense"] == "passato_prossimo"
        and ex["auxiliary_hint"] == "avere"
    )


def test_unknown_user_and_tense(client):
    assert client.get("/api/users/Nobody/exercise").status_code == 404
    login(client)
    bad = client.post(
        "/api/users/Kay/answers",
        json={"verb": "fare", "tense": "futuro", "person": 0, "answer": "x"},
    )
    assert bad.status_code == 400


def test_examples_endpoint_uses_service(client):
    data = client.get(
        "/api/verbs/andare/examples", params={"tense": "presente", "person": 3}
    ).json()
    assert data["query"] == "andiamo"


def test_parse_tatoeba_response():
    from app.examples import parse_response

    payload = {
        "data": [
            {
                "id": 1,
                "text": "Andiamo!",
                "license": "CC BY 2.0 FR",
                "translations": [[{"lang": "deu", "text": "Los!"}]],
            },
            {
                "id": 2,
                "text": "Senza traduzione",
                "translations": [[{"lang": "eng", "text": "x"}]],
            },
        ]
    }
    result = parse_response(payload)
    assert result == [
        {
            "italian": "Andiamo!",
            "german": "Los!",
            "url": "https://tatoeba.org/de/sentences/show/1",
            "license": "CC BY 2.0 FR",
        }
    ]


def test_database_url_is_converted_for_psycopg(monkeypatch):
    from app.db import database_url

    monkeypatch.setenv("DATABASE_URL", "postgres://u:p@host/db?sslmode=require")
    assert database_url() == "postgresql+psycopg://u:p@host/db?sslmode=require"
    monkeypatch.setenv("DATABASE_URL", "postgresql://u:p@host/db")
    assert database_url() == "postgresql+psycopg://u:p@host/db"


def test_tenses_endpoint(client):
    keys = [t["key"] for t in client.get("/api/tenses").json()]
    assert keys == ["presente", "passato_prossimo"]


def test_tense_selection_is_saved_and_used(client):
    assert login(client).json()["tenses"] is None
    res = client.put("/api/users/Kay/settings", json={"tenses": ["passato_prossimo"]})
    assert res.json()["tenses"] == ["passato_prossimo"]
    assert login(client).json()["tenses"] == ["passato_prossimo"]
    for _ in range(5):
        ex = client.get("/api/users/Kay/exercise").json()
        assert ex["tense"] == "passato_prossimo"
    prog = client.get("/api/users/Kay/progress").json()
    assert prog["practice_tenses"] == ["passato_prossimo"]
    assert prog["unlocked_tenses"] == ["presente"]


def test_reset_selection_to_learning_path(client):
    login(client)
    client.put("/api/users/Kay/settings", json={"tenses": ["passato_prossimo"]})
    assert (
        client.put("/api/users/Kay/settings", json={"tenses": []}).json()["tenses"]
        is None
    )
    assert client.get("/api/users/Kay/exercise").json()["tense"] == "presente"


def test_invalid_tense_selection(client):
    login(client)
    res = client.put("/api/users/Kay/settings", json={"tenses": ["futuro"]})
    assert res.status_code == 422


def test_search_verbs_endpoint(client):
    assert client.get("/api/verbs/search?q=gehen").json() == [
        {"infinitive": "andare", "meaning": "gehen"}
    ]
    assert len(client.get("/api/verbs/search?q=bleiben").json()) == 3
    assert client.get("/api/verbs/search?q=kochen").json() == []
    assert client.get("/api/verbs/search?q=").status_code == 422
    