"""Externer Webdienst: echte Beispielsätze von Tatoeba.

Tatoeba (https://tatoeba.org) ist eine freie Sammlung von Sätzen mit
Übersetzungen, Lizenz CC BY 2.0 FR. Gesucht wird nach der konjugierten Form,
damit der Satz genau die geübte Form enthält. Fällt der Dienst aus, liefert
die Funktion eine leere Liste; die App funktioniert dann ohne Beispiele weiter.
"""

from __future__ import annotations

import httpx

API_URL = "https://api.tatoeba.org/unstable/sentences"
TIMEOUT = 4.0
_cache: dict[str, list[dict]] = {}


def _german_translations(sentence: dict) -> list[str]:
    result = []
    for group in sentence.get("translations", []):
        items = group if isinstance(group, list) else [group]
        for t in items:
            if isinstance(t, dict) and t.get("lang") == "deu" and t.get("text"):
                result.append(t["text"])
    return result


def parse_response(payload: dict, limit: int = 3) -> list[dict]:
    examples = []
    for s in payload.get("data", []):
        translations = _german_translations(s)
        if not s.get("text") or not translations:
            continue
        examples.append(
            {
                "italian": s["text"],
                "german": translations[0],
                "url": f"https://tatoeba.org/de/sentences/show/{s.get('id')}",
                "license": s.get("license") or "CC BY 2.0 FR",
            }
        )
        if len(examples) >= limit:
            break
    return examples


def fetch_examples(
    form: str, limit: int = 3, client: httpx.Client | None = None
) -> dict:
    """Beispielsätze, die genau diese Form enthalten (z. B. 'andiamo')."""
    query = form.split("/")[0].strip()
    if query in _cache:
        return {"source": "tatoeba", "query": query, "examples": _cache[query]}
    params = {
        "lang": "ita",
        "q": f'="{query}"',
        "trans:lang": "deu",
        "sort": "words",
        "limit": 10,
    }
    try:
        http = client or httpx.Client(timeout=TIMEOUT)
        response = http.get(API_URL, params=params)
        response.raise_for_status()
        examples = parse_response(response.json(), limit)
    except (httpx.HTTPError, ValueError):
        return {"source": "unavailable", "query": query, "examples": []}
    _cache[query] = examples
    return {"source": "tatoeba", "query": query, "examples": examples}
