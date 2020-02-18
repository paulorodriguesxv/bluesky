BlueSky - Lightweight OAuth2 Server and Social Login
=====================================================

Experimental Python OAuth2 server forged with the powerful FastAPI

From Zero to Hero:
------------------
In case you want to run BlueSky effortlessly, just start the docker-compose
```bash
 docker-compose up -d
```

Enviromment variables:
-----------------------
      - DATABASE_URI=postgresql://postgres:admin@bluesky-db/postgres
        Database URI

      - ACCESS_TOKEN_PRIVATE_KEY=./security/private.pem
        Private key used to data encrypt

      - ACCESS_TOKEN_PUBLIC_KEY=./security/public.pem
        Public key used to perform token validation

      - ACCESS_TOKEN_EXPIRE_MINUTES=60
        Access token lifetime
 
      - REFRESH_TOKEN_EXPIRE_MINUTES=10440
        Refresh token lifetime

      - APP_ENV=dev
        Enviromment type (dev, prod, test)

Install
---------
To install BlueSky:
```bash
pip install -r requirements.txt 
```

To run the first migration:
```bash
   alembic upgrade head
```  

To run server:
```bash
   uvicorn asgi:app --reload
```

To run tests:
```bash
   pytest --cov=app  --cov-report html .\tests\ -s 
```   

Swagger API:
--------------
http://localhost:8000/docs


ReDoc API:
--------------
http://localhost:8000/redocs

API:
--------------
  - users
    - register new user
    - read users
    - read current user (for specific token)

  - auth
    - Endpoints to perform following actions:
      - get new access token
      - get new refresh token
      - swap social token (see supported social services) for access token
      - get .well-know with jkws public token 
Usage
-------


Contributing
-------------
Contributing is always welcome, so, feel free to getting in touch and contribute.

TODOs
-------------
-   Increase test percentage for project.
-   Create sphinx docs
-   Create travis
-   Extend Api
  
Star if you like it.
---------------------
If you like or use this project, consider showing your support by starring it.

