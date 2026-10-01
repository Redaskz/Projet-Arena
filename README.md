# Arena

Plateforme de gestion de tournois e-sport : catalogue de jeux, équipes et joueurs,
tournois, génération automatique du calendrier des rencontres et calcul du
classement.

Projet réalisé en binôme de modules : une API REST **FastAPI** et une interface
**React / TypeScript** qui la consomme.

---

## Sommaire

- [Stack technique](#stack-technique)
- [Structure du dépôt](#structure-du-dépôt)
- [Prérequis](#prérequis)
- [Installation et lancement du backend](#installation-et-lancement-du-backend)
- [Installation et lancement du frontend](#installation-et-lancement-du-frontend)
- [Configuration](#configuration)
- [Comptes de démonstration](#comptes-de-démonstration)
- [Les routes de l'API](#les-routes-de-lapi)
- [Authentification et sécurisation](#authentification-et-sécurisation)
- [Fonctionnalités métier avancées](#fonctionnalités-métier-avancées)
- [Architecture du backend](#architecture-du-backend)
- [Problèmes fréquents](#problèmes-fréquents)
- [Répartition du travail](#répartition-du-travail)
- [Limites connues](#limites-connues)

---

## Stack technique

**Backend**

| Composant | Choix |
|---|---|
| Framework | FastAPI |
| ORM | SQLAlchemy 2 (`Mapped` / `mapped_column`) |
| Base de données | PostgreSQL 16 (conteneur Docker) |
| Validation | Pydantic v2 |
| Authentification | JWT (PyJWT) + hachage bcrypt (passlib) |
| API externe | RAWG (enrichissement automatique des jeux) |
| Pilote PostgreSQL | psycopg2 |

**Frontend**

| Composant | Choix |
|---|---|
| Build | Vite |
| Framework | React 18 + TypeScript (mode strict) |
| Routage | React Router 7 |
| Styles | CSS écrit à la main, sans framework |
| Qualité | ESLint 9 (flat config) |

---

## Structure du dépôt

```
arena/
├── backend/
│   ├── app/
│   │   ├── core/           configuration, connexion base, sécurité (hachage, JWT)
│   │   ├── models/         tables SQLAlchemy — structure uniquement
│   │   ├── schemas/        schémas Pydantic — validation entrée / sortie
│   │   ├── repositories/   accès aux données — SQL uniquement
│   │   ├── services/       règles métier — seule couche à lever HTTPException
│   │   ├── routers/        routes HTTP — porte d'entrée, sans logique
│   │   ├── external/       clients d'API tierces (RAWG)
│   │   └── main.py         assemblage de l'application
│   ├── tests/
│   ├── seed.py             script de peuplement de démonstration
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   └── src/
│       ├── api/            client HTTP, authentification et appels par ressource
│       ├── types/          types partagés, alignés sur les schémas du backend
│       ├── hooks/          hooks réutilisables (authentification, stockage local)
│       ├── components/     composants réutilisables
│       ├── pages/          une page par route
│       └── mocks/          données simulées (interrupteur USE_MOCKS)
├── docker-compose.yml      service PostgreSQL
└── README.md
```

Une ressource = un fichier par couche, nommé au **singulier** (`game.py`), pour un
préfixe d'URL au **pluriel** (`/games`).

---

## Prérequis

- **Python 3.11 ou supérieur**
- **Node.js 18 ou supérieur**
- **Docker Desktop** (pour PostgreSQL)
- Une clé d'API **RAWG** (gratuite, sur [rawg.io/apidocs](https://rawg.io/apidocs)).
  Le projet fonctionne sans, l'enrichissement des jeux sera simplement vide.

> **Windows** — si la commande `python` ouvre le Microsoft Store, utilisez `py` à
> la place, y compris pour pip : `py -m pip install ...`. Les paquets doivent être
> installés dans le même interpréteur que celui qui exécutera les scripts.
> Si PowerShell refuse `npm` (« l'exécution de scripts est désactivée »), utilisez
> `npm.cmd` et `npx.cmd`.

---

## Installation et lancement du backend

### 1. Créer le fichier de configuration

```bash
cd backend
cp .env.example .env
```

Sous PowerShell :

```powershell
cd backend
Copy-Item .env.example .env
```

Voir la section [Configuration](#configuration) pour le détail des variables.

### 2. Démarrer la base de données

Depuis la **racine du dépôt** :

```bash
docker compose up -d
docker compose ps
```

Le service `db` doit apparaître en `running` avec le port `5432` publié.
Au premier lancement, laissez-lui une dizaine de secondes pour s'initialiser :

```bash
docker compose logs db --tail 20
```

Attendez la ligne `database system is ready to accept connections`.

### 3. Installer les dépendances

```bash
cd backend
pip install -r requirements.txt
```

### 4. Peupler la base

```bash
python seed.py
```

Le script crée un jeu de données cohérent : 2 utilisateurs, 5 jeux, 7 équipes,
33 joueurs, 2 tournois, le calendrier complet de l'un d'eux (6 matchs répartis
sur 3 rounds) et 3 scores, de façon à ce que le classement ait quelque chose à
afficher dès le premier lancement.

Le script est **idempotent** : relancé sur une base déjà peuplée, il ne duplique
rien et ne supprime rien. Un second lancement affiche des compteurs à zéro.

### 5. Lancer le serveur

```bash
uvicorn app.main:app --reload
```

Si `uvicorn` n'est pas dans le PATH :

```bash
python -m uvicorn app.main:app --reload
```

L'API est disponible sur **http://localhost:8000**.
La documentation interactive Swagger est sur **http://localhost:8000/docs**.

### 6. Vérifier

```bash
curl http://localhost:8000/health
```

Réponse attendue :

```json
{"status": "ok", "database": "connected"}
```

---

## Installation et lancement du frontend

Le backend doit tourner : le frontend consomme l'API réelle.

```bash
cd frontend
npm install
npm run dev
```

L'interface est disponible sur **http://localhost:5173**.
Connectez-vous avec les [comptes de démonstration](#comptes-de-démonstration).

Autres commandes utiles :

```bash
npm run lint        # analyse statique
npx tsc --noEmit    # vérification des types
npm run build       # build de production
```

L'origine `http://localhost:5173` est déjà autorisée côté CORS dans `app/main.py`.

### Mode hors ligne

Le frontend sait aussi tourner **sans backend**. Un interrupteur `USE_MOCKS` dans
`src/mocks/index.ts` bascule toutes les ressources sur des données simulées,
typées sur les mêmes interfaces que l'API réelle et reproduisant ses erreurs.

Il vaut `false` par défaut. Le passer à `true` permet de développer l'interface
sans dépendre du serveur — c'est ce qui a permis aux deux équipes d'avancer en
parallèle pendant le projet.

---

## Configuration

Toute la configuration du backend passe par `backend/.env`, lu au démarrage par
Pydantic Settings. Ce fichier n'est **jamais versionné** : il est ignoré par
`.gitignore`, et seul `.env.example` est suivi par Git.

```dotenv
# Identifiants du conteneur PostgreSQL
POSTGRES_USER=arena
POSTGRES_PASSWORD=arena
POSTGRES_DB=arena

# Connexion de l'application à cette même base
DATABASE_URL=postgresql+psycopg2://arena:arena@localhost:5432/arena

# Secret de signature des jetons JWT
JWT_SECRET=change_me

# Clé de l'API RAWG
RAWG_API_KEY=change_me
```

Deux points d'attention :

- Les trois variables `POSTGRES_*` sont transmises au conteneur par
  `docker-compose.yml`. Les identifiants qu'elles contiennent doivent être
  **identiques** à ceux de `DATABASE_URL`, sans quoi l'authentification échoue.
- Le pilote doit être écrit explicitement : `postgresql+psycopg2://`. Avec une URL
  `postgresql://` simple, SQLAlchemy 2.1 cherche psycopg 3, que le projet
  n'installe pas.

---

## Comptes de démonstration

Créés par `seed.py`, et réaffichés à la fin de son exécution.

| Rôle | Identifiant | Mot de passe |
|---|---|---|
| Administrateur | `admin` | `Admin1234!` |
| Joueur | `joueur` | `Joueur1234!` |

Ce sont des comptes de **démonstration**. Leurs mots de passe ne sont écrits en
clair que dans `seed.py` ; en base, seul leur hachage bcrypt est stocké.

Ils servent aussi bien à se connecter sur l'interface qu'à utiliser les routes
protégées depuis Swagger : appelez `POST /auth/login`, copiez la valeur
`access_token`, puis cliquez sur **Authorize** en haut à droite et collez-la.

---

## Les routes de l'API

La liste complète et interactive est sur `/docs`. Vue d'ensemble :

### Authentification — `/auth`

| Méthode | Route | Description |
|---|---|---|
| `POST` | `/auth/register` | Crée un compte |
| `POST` | `/auth/login` | Renvoie un jeton JWT (formulaire OAuth2, champs `username` et `password`) |
| `GET` | `/auth/me` | Renvoie l'utilisateur authentifié 🔒 |

Le champ `username` de `/auth/login` accepte aussi bien un nom d'utilisateur
qu'une adresse e-mail.

### Ressources CRUD

Chaque ressource expose les cinq opérations : liste, détail, création,
modification partielle (`PATCH`) et suppression.

| Ressource | Préfixe | Filtres disponibles |
|---|---|---|
| Jeux | `/games` | `genre` |
| Équipes | `/teams` | `game_id`, `search` |
| Joueurs | `/players` | `team_id` |
| Utilisateurs | `/users` | — |
| Tournois | `/tournaments` | `game_id`, `status` |
| Matchs | `/matches` | `tournament_id` |

### Routes imbriquées et fonctionnalités avancées

| Méthode | Route | Description |
|---|---|---|
| `GET` | `/teams/{id}/players` | Effectif d'une équipe |
| `GET` | `/tournaments/{id}/matches` | Calendrier d'un tournoi |
| `POST` | `/tournaments/{id}/schedule` | Génère le calendrier 🔒 |
| `GET` | `/tournaments/{id}/standings` | Classement calculé à la volée |

### Technique

| Méthode | Route | Description |
|---|---|---|
| `GET` | `/health` | État du serveur et de la connexion à la base |

---

## Authentification et sécurisation

L'authentification repose sur des **jetons JWT** signés avec `JWT_SECRET`. Les
mots de passe sont hachés avec **bcrypt** et ne sont jamais stockés en clair.

Deux dépendances contrôlent l'accès :

- `get_current_user` — exige un jeton valide
- `get_current_admin` — exige en plus le rôle administrateur

La règle appliquée dans tout le projet :

- **La lecture est publique.** Consulter le catalogue, les équipes, les tournois,
  le calendrier et le classement ne demande aucun compte. C'est un choix métier :
  un visiteur doit pouvoir parcourir la plateforme avant de s'inscrire.
- **L'écriture exige un compte.** Toutes les routes `POST`, `PATCH` et `DELETE`
  sont protégées, ainsi que la génération de calendrier.
- **Deux routes sont réservées aux administrateurs** : la création et la
  suppression d'un jeu, qui est une donnée de référence du catalogue.

Un appel d'écriture sans jeton répond **401**, un appel avec un jeton mais sans
les droits suffisants répond **403**.

Côté frontend, le jeton est conservé dans le stockage local du navigateur et
réinjecté dans l'en-tête `Authorization` de chaque requête. Une réponse 401 vide
la session et renvoie l'utilisateur vers la page de connexion.

---

## Fonctionnalités métier avancées

### Génération du calendrier — `services/schedule.py`

`POST /tournaments/{id}/schedule` construit l'ensemble des rencontres d'un
tournoi selon la **méthode du cercle** : la première équipe reste fixe, les
autres tournent d'un cran à chaque round, et les rencontres sont formées par les
positions en vis-à-vis. Pour *n* équipes, on obtient *n* − 1 rounds et
*n* × (*n* − 1) / 2 matchs. Un nombre impair d'équipes est traité par l'ajout
d'une équipe fictive : l'équipe qui lui fait face est exempte pour ce round.

Les matchs sont écrits en une seule transaction : le calendrier est enregistré en
entier ou pas du tout.

Erreurs gérées : 404 si le tournoi n'existe pas, 400 s'il y a moins de deux
équipes, 409 si un calendrier existe déjà.

### Calcul du classement — `services/standings.py`

`GET /tournaments/{id}/standings` parcourt les matchs joués du tournoi et calcule
pour chaque équipe le nombre de rencontres, victoires, nuls, défaites, points
(3 / 1 / 0), buts pour, buts contre et différence. Le tri se fait par points
décroissants, puis par différence, puis par nom.

Aucune table de classement n'existe en base : le calcul est fait à la volée à
chaque appel, ce qui garantit qu'il ne peut jamais être désynchronisé des scores.

---

## Architecture du backend

Le backend suit une **séparation stricte en couches**, appliquée à chaque
ressource sans exception :

| Couche | Rôle | Interdits |
|---|---|---|
| `models/` | Structure des tables | Aucune logique |
| `schemas/` | Validation Pydantic, contrats d'entrée et de sortie | Aucun accès base |
| `repositories/` | Requêtes SQL | Aucun vocabulaire HTTP, aucune `HTTPException` |
| `services/` | Règles métier | Seule couche autorisée à lever une `HTTPException` |
| `routers/` | Routes HTTP | Aucun appel au repository, aucune règle métier |
| `external/` | Clients d'API tierces | — |

Cette séparation a une conséquence concrète : `seed.py` passe par les
**repositories** et non par les services, parce qu'un script en ligne de commande
n'a rien à faire du vocabulaire du web. Et le service `schedule` est appelé
directement par le script, sans passer par HTTP.

### Intégration de l'API RAWG

À la création d'un jeu, `external/rawg.py` interroge l'API RAWG pour récupérer
jaquette, note et date de sortie, et enrichit automatiquement la fiche.

Le client gère les défaillances du service externe : délai dépassé, hôte
injoignable, codes 4xx et 5xx, réponse illisible. Dans tous ces cas il journalise
un avertissement et renvoie un enrichissement vide. **La création du jeu réussit
quand même** : une panne de RAWG ne bloque jamais la plateforme.

---

## Problèmes fréquents

### `No module named 'psycopg'`

Votre `DATABASE_URL` utilise `postgresql://` au lieu de
`postgresql+psycopg2://`. Voir [Configuration](#configuration).

### `password authentication failed for user "arena"`

Les identifiants du conteneur ne correspondent pas à ceux de `DATABASE_URL`.

PostgreSQL fixe ses identifiants **une seule fois**, à la création de son volume.
Modifier le `.env` après coup n'a donc aucun effet. Pour repartir proprement :

```bash
docker compose down -v
docker compose up -d
```

Le `-v` supprime le volume : la base repart vide, `seed.py` la repeuple.

### La connexion échoue alors que le conteneur tourne

Vérifiez qu'**aucun autre PostgreSQL n'occupe le port 5432**. Une installation
native de PostgreSQL sous Windows démarre automatiquement et prend le port avant
le conteneur — Docker affiche pourtant `0.0.0.0:5432->5432` sans erreur, mais les
connexions n'arrivent jamais jusqu'à lui.

Pour vérifier et arrêter le service concurrent, en PowerShell administrateur :

```powershell
Get-Service postgresql*
Stop-Service postgresql-x64-18
Set-Service postgresql-x64-18 -StartupType Manual
```

Puis `docker compose restart db`.

### `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe9`

Erreur trompeuse : la connexion échoue réellement, mais le message d'erreur de
PostgreSQL est renvoyé dans la locale du système et ne peut pas être décodé en
UTF-8, ce qui masque la vraie cause. Pour la faire apparaître, forcez les
messages en anglais avant de relancer :

```powershell
$env:LC_MESSAGES="C"
```

### `Python est introuvable` sous Windows

Le raccourci du Microsoft Store intercepte la commande. Utilisez `py` à la place,
et `py -m pip` pour l'installation des dépendances.

### `npm : l'exécution de scripts est désactivée sur ce système`

Politique d'exécution de PowerShell. Utilisez `npm.cmd` et `npx.cmd`, ou
autorisez les scripts une fois pour toutes :

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### `ESLint couldn't find an eslint.config file`

Vous n'êtes pas dans le bon dossier : les commandes npm se lancent depuis
`frontend/`, pas depuis la racine.

---

## Répartition du travail

| Membre | Périmètre |
|---|---|
| **Reda** | Jeux, équipes, joueurs · intégration de l'API RAWG · mise en place de l'architecture en couches · script de peuplement · sécurisation des routes d'écriture · branchement du frontend sur l'API · intégration des branches |
| **Victor** | Utilisateurs · authentification JWT, hachage bcrypt, dépendances `get_current_user` et `get_current_admin` |
| **Yanis** | Tournois et matchs |
| **Othmane** | Inscriptions, commentaires et tests |

Côté frontend, chacun a pris en charge un périmètre de pages : socle partagé et
ressources jeux/équipes pour Reda, authentification et tournois pour Victor,
client d'API et page des matchs pour Yanis, page de détail d'un tournoi pour
Othmane.

Le travail s'est fait sur des **branches par fonctionnalité**, intégrées dans
`dev` puis fusionnées dans `main`.

---

## Limites connues

Points identifiés et assumés, plutôt que dissimulés :

- **Les inscriptions et les commentaires ne sont pas exposés par l'API.** Leurs
  modèles, schémas et repositories existent sur la branche `dev`, et leurs
  services sur la branche `feature/test-infrastructure`, mais les routeurs n'ont
  pas été écrits : aucune route n'est donc servie pour ces deux ressources.
- **La génération du calendrier prend toutes les équipes du jeu** du tournoi, et
  non les équipes qui y sont inscrites, puisque la table des inscriptions n'est
  pas encore active. Le jour où elle le sera, le changement tient en une ligne
  dans `services/schedule.py`.
- **Les tests ne sont pas intégrés.** Une configuration de tests (base SQLite en
  mémoire, surcharge de `get_db`) et plusieurs fichiers de tests existent sur la
  branche `feature/test-infrastructure`, mais celle-ci part d'un point ancien de
  l'historique et n'a pas pu être fusionnée en l'état.
- **L'unicité du nom d'équipe** est garantie par une contrainte en base doublée
  d'une vérification dans le service. Sous forte concurrence, deux requêtes
  simultanées pourraient franchir la vérification avant que la contrainte ne
  tranche : c'est alors la base qui refuse, et le client reçoit une erreur moins
  explicite que le 409 attendu.
