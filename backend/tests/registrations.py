"""Tests des inscriptions aux tournois."""


def test_registration_tournament_not_found(client):
    """L'inscription à un tournoi inexistant renvoie 404."""
    response = client.post(
        "/registrations",
        json={
            "tournament_id": 999999,
            "team_id": 999999,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Tournoi introuvable."


def test_registration_not_found(client):
    """La lecture d'une inscription inexistante renvoie 404."""
    response = client.get("/registrations/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Inscription introuvable."