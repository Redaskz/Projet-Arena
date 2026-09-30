"""Tests des commentaires."""


def test_comment_not_found(client):
    """La lecture d'un commentaire inexistant renvoie 404."""
    response = client.get("/comments/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Commentaire introuvable."


def test_comment_content_too_long(client):
    """Un commentaire de plus de 500 caractères est rejeté."""
    response = client.post(
        "/comments",
        json={
            "tournament_id": 1,
            "content": "a" * 501,
        },
    )

    # Pydantic rejette le contenu avant l'exécution de la route.
    assert response.status_code == 422