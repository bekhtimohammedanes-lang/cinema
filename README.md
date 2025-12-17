################################################################################################## 
############## Build du docker

télécharger le projet zip à partir du dépot git:



>> unzip cinema_project.zip -d .

>> cd cinema_project

>> docker compose down -v
>> docker compose build --no-cache
>> docker compose up



################################################################################################## 
############## Accès admin: http://localhost:8000/admin
un super user est créé automatiquement au moment du build:
username: admin
email: test@test.com
password: ChangeMe15698@



##################################################################################################

##### Intégration API TMDb #####

##### 1. La commande django qui récupère les informations de films, auteurs afin de les enregistrer en base

>> docker compose exec web python manage.py import_tmdb


#### 2. filtre dans la route API des films et auteurs pour récupérer uniquement ceux qui sont créés depuis l’admin ou depuis import via TMDb

## Exemple: Lister uniquement les auteurs importés depuis TMDB / ADMIN
>> curl -X GET "http://localhost:8000/api/authors/?source=TMDB"

## Lister uniquement les films importés depuis TMDB / ADMIN
>> curl -X GET "http://localhost:8000/api/films/?source=ADMIN"


################################################################################################## 
############## API Cinema – Documentation http://localhost:8000/api/


########## API Endpoints
| Fonction                         | Méthode   | URL                            |
| -------------------------------- | --------- | ------------------------------ |
| Lister auteurs                   | GET       | `/api/authors/`                |
| Détail auteur                    | GET       | `/api/authors/{id}/`           |
| Modifier auteur                  | PUT/PATCH | `/api/authors/{id}/`           |
| Supprimer auteur (si aucun film) | DELETE    | `/api/authors/{id}/`           |
| Lister films                     | GET       | `/api/films/`                  |
| Lister films par statut          | GET       | `/api/films/?status=published` |
| Détail film                      | GET       | `/api/films/{id}/`             |
| Modifier film                    | PUT/PATCH | `/api/films/{id}/`             |
| Archiver film                    | POST      | `/api/films/{id}/archive/`     |
| Inscription spectateur           | POST      | `/api/auth/register/`          |
| Login JWT                        | POST      | `/api/auth/login/`             |
| Logout JWT                       | POST      | `/api/auth/logout/`            |
| Refresh JWT                      | POST      | `/api/auth/token/refresh/`     |
| Noter un film                    | POST      | `/api/ratings/films/`          |
| Noter un auteur                  | POST      | `/api/ratings/authors/`        |
| Ajouter favori                   | POST      | `/api/favorites/`              |
| Retirer favori                   | DELETE    | `/api/favorites/{id}/`         |
| Lister favoris                   | GET       | `/api/favorites/`              |


################################################################################################## 

########## Exemples 'curl' API

########## A- Authentification JWT

### 1. S’inscrire en tant que spectateur

>> curl -X POST http://localhost:8000/api/auth/register/ \
-H "Content-Type: application/json" \
-d '{
  "username": "spectateur1",
  "email": "spectateur1@example.com",
  "password": "motdepasse",
  "bio": "J’aime le cinéma"
}'

### 2. Se connecter (JWT)

>> curl -X POST http://localhost:8000/api/auth/login/ \
-H "Content-Type: application/json" \
-d '{
  "username": "spectateur1",
  "password": "motdepasse"
}'
#Réponse :
{
  "refresh": "<refresh_token>",
  "access": "<access_token>"
}


### 3. Se  déconnecter
>> curl -X POST http://localhost:8000/api/auth/logout/ \
-H "Content-Type: application/json" \
-H "Authorization: Bearer <access_token>" \
-d '{"refresh": "<refresh_token>"}'


### 4.Tester le refresh avec le token révoqué
>> curl -X POST http://localhost:8000/api/auth/token/refresh/ \
-H "Content-Type: application/json" \
-d '{"refresh": "<refresh_token>"}'
#Résultat attendu :
{
  "detail": "Token is blacklisted",
  "code": "token_not_valid"
}


#################################################### 
########## B- Auteurs

### 1. Lister tous les auteurs (lecture publique)
>> curl -X GET http://localhost:8000/api/authors/ \
-H "Accept: application/json"


### 2. Récupérer un auteur par ID
>> curl -X GET http://localhost:8000/api/authors/1/ \
-H "Accept: application/json"


### 3. Modifier un auteur (JWT requis)
>> curl -X PATCH http://localhost:8000/api/authors/1/ \
-H "Authorization: Bearer <access_token>" \
-H "Content-Type: application/json" \
-d '{
  "date_naissance": "1980-05-12"
}'
#Si pas d'authentification: retour 
   {"detail":"Informations d'authentification non fournies."}


### 4. Supprimer un auteur (s’il n’a pas de film)
>> curl -X DELETE http://localhost:8000/api/authors/1/ \
-H "Authorization: Bearer <access_token>"

#####################################################
########## C- Films

### 1. Lister tous les films
>> curl -X GET http://localhost:8000/api/films/ \
-H "Accept: application/json"


### 2. Lister les films avec statut spécifique (DRAFT, PUBLISHED, ARCHIVED)
>> curl -X GET "http://localhost:8000/api/films/?status=PUBLISHED" \
-H "Accept: application/json"
  


### 3. Récupérer un film par ID
>> curl -X GET http://localhost:8000/api/films/1/ \
-H "Accept: application/json"

### 4. Modifier un film (JWT requis)
>> curl -X PATCH http://localhost:8000/api/films/1/ \
-H "Authorization: Bearer <access_token>" \
-H "Content-Type: application/json" \
-d '{
  "title": "Nouveau titre"
}'

### 5. Archiver un film (JWT requis)
>> curl -X POST http://localhost:8000/api/films/1/archive/ \
-H "Authorization: Bearer <access_token>"

###################################################### 
########## D- Notes et favoris (Spectateur JWT requis)

### 1. Noter un film
>> curl -X POST http://localhost:8000/api/ratings/films/ \
-H "Authorization: Bearer <access_token>" \
-H "Content-Type: application/json" \
-d '{
  "film": 1,
  "note": 4
}'


### 2. Noter un auteur
>> curl -X POST http://localhost:8000/api/ratings/authors/ \
-H "Authorization: Bearer <access_token>" \
-H "Content-Type: application/json" \
-d '{
  "author": 1,
  "note": 5
}'
### 3. Ajouter un film aux favoris
>> curl -X POST http://localhost:8000/api/favorites/ \
-H "Authorization: Bearer <access_token>" \
-H "Content-Type: application/json" \
-d '{
  "film": 1
}'

### 4. Retirer un film des favoris
>> curl -X DELETE http://localhost:8000/api/favorites/1/ \
-H "Authorization: Bearer <access_token>"

### 5. Lister ses films favoris
>> curl -X GET http://localhost:8000/api/favorites/ \
-H "Authorization: Bearer <access_token>"

##################################################### 
########## Notes importantes

### Remplacer <access_token> par le token JWT obtenu lors de la connexion.

### Les endpoints GET publics (authors, films) sont accessibles sans JWT.

### Tous les endpoints qui modifient des données (POST, PATCH, DELETE) nécessitent JWT.

### Tous les envois de données utilisent Content-Type: application/json.

### Après deconnexion, les refresh tokens seront blacklistés, rendant impossible l’émission d’un nouvel access token avec un token révoqué.

### Les access tokens existants restent valides jusqu’à expiration, comme prévu sur le setting "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15).






