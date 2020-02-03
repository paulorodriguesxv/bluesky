BlueSky - Lightweight OAuth2 Server and Social Login
=====================================================

Experimental OAuth2 server forged with the powerful FastAPI


Install
---------
To install BlueSky:
```bash
pip install -r requirements.txt 
```

If you want to install from source, then use:
```bash
git clone https://github.com/paulorodriguesxv/pyOMT5.git
pip install -e pyOMT5
```

Usage
-------

Register New User
=====================


Contributing
-------------
Contributing is always welcome, so, feel free to getting in touch and contribute.

TODOs
-------------
-   Add test for library.
-   Create sphinx docs
-   Create travis
-   Extend Api
  
Star if you like it.
---------------------
If you like or use this project, consider showing your support by starring it.

Experimental OAuth2 Server for Waander

To run the first migration:
- alembic upgrade head

To run server:
 - uvicorn asgi:app --reload

pytest --cov=app  --cov-report html .\tests\ -s 