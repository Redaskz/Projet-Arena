"""Schémas Pydantic de l'authentification.

Pas de schéma d'entrée pour le login : la route utilise OAuth2PasswordRequestForm
fourni par FastAPI (voir routers/auth.py). L'inscription réutilise UserCreate.
"""

from pydantic import BaseModel


# Ce que l'API renvoie après un login réussi (POST /auth/login).
class Token(BaseModel):
    # Les deux noms de champs sont imposés par la norme OAuth2 : c'est ce que
    # le bouton « Authorize » de Swagger lit dans la réponse pour récupérer le
    # token et l'envoyer ensuite dans l'en-tête Authorization.
    access_token: str
    # Toujours "bearer" : le client devra envoyer « Authorization: Bearer <token> ».
    token_type: str = "bearer"
