"""Outils de sécurité : hachage des mots de passe et jetons JWT.

Ce module ne connaît ni la base de données ni les utilisateurs : il manipule
uniquement des chaînes (mot de passe, hash, token) et des identifiants.
C'est le service d'authentification (services/auth.py) qui l'utilise pour
prendre les décisions : qui est connecté, qui a le droit de faire quoi.
"""

from datetime import datetime, timedelta, timezone

import jwt
from fastapi import HTTPException, status
from passlib.context import CryptContext

# La clé et l'algorithme sont lus dans la configuration, elle-même alimentée
# par le fichier .env. Une clé écrite en dur dans le code finirait sur GitHub,
# et n'importe qui pourrait alors fabriquer un token valide.
from app.core.config import settings

SECRET_KEY = settings.jwt_secret
ALGORITHM = settings.jwt_algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = settings.access_token_expire_minutes

# CryptContext centralise le choix de l'algorithme de hachage.
# bcrypt est volontairement LENT et ajoute un sel aléatoire à chaque hash :
# deux utilisateurs avec le même mot de passe n'ont donc pas le même hash, et
# une attaque par force brute sur une base volée devient très coûteuse.
# deprecated="auto" : si on change un jour d'algorithme, les anciens hash
# restent vérifiables et sont signalés comme à mettre à jour.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Renvoie le hash bcrypt d'un mot de passe en clair.

    Le mot de passe en clair n'est JAMAIS stocké : seule cette empreinte va en
    base. Même un administrateur de la base ne peut pas retrouver le mot de passe.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Vérifie qu'un mot de passe en clair correspond à un hash stocké.

    On ne « déchiffre » pas le hash, c'est impossible : passlib relit le sel
    contenu dans le hash, rehache le mot de passe saisi avec ce même sel, et
    compare les deux empreintes.
    """
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(user_id: int) -> str:
    """Fabrique un JWT signé identifiant l'utilisateur.

    Le token contient deux informations (les « claims ») :
    - "sub" (subject) : l'identifiant de l'utilisateur. La norme JWT impose une
      chaîne de caractères, d'où la conversion str().
    - "exp" (expiration) : au-delà de cette date, le token est refusé. Un token
      volé ne reste donc exploitable que quelques minutes.
    """
    # Toujours en UTC : l'expiration ne doit pas dépendre du fuseau horaire du
    # serveur qui fabrique le token ni de celui qui le vérifie.
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expire}

    # La signature garantit que le contenu n'a pas été modifié : le payload est
    # lisible par tous (il est seulement encodé en base64), mais sans la clé
    # secrète personne ne peut en fabriquer un faux ou changer le "sub".
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> dict:
    """Vérifie un JWT et renvoie son contenu, ou lève une 401.

    jwt.decode vérifie à la fois la signature ET la date d'expiration.
    """
    try:
        # `algorithms` est une LISTE fermée : on refuse tout token signé avec
        # un autre algorithme que celui choisi, y compris l'algorithme "none"
        # qui permettrait de fabriquer un token sans signature.
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except jwt.InvalidTokenError:
        # InvalidTokenError est la classe mère de toutes les erreurs PyJWT :
        # signature fausse, token expiré (ExpiredSignatureError), format cassé...
        # Toutes aboutissent à la même réponse : 401, « je ne sais pas qui tu es ».
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token invalide ou expiré.",
            # En-tête imposé par la norme HTTP pour une réponse 401 : il indique
            # au client quel mode d'authentification est attendu.
            headers={"WWW-Authenticate": "Bearer"},
        )
