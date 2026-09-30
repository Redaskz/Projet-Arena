"""Tests de la route de santé de l'API."""


def test_health(client):
    """La route de santé répond correctement."""
    response = client.get("/health")

    assert response.status_code == 200


def test_unknown_route_returns_404(client):
    """Une route inexistante renvoie une erreur 404."""
    response = client.get("/route-qui-nexiste-pas")

    assert response.status_code == 404