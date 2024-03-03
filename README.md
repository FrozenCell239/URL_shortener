# Database initialisation 
Create the database manually then use these lines in `flask shell` to create the database tables.
```python
>>> from app.extensions import db
>>> from app.models.user import User
>>> from app.models.link import Link
>>> db.create_all()
>>> exit()
```
If you don't know how to create manually the database, please refer to PostgreSQL and/or your host documentation.

# Environnement initialisation
Rename the "example.env" file to ".env" then go in it to replace the environnement informations with your ones.

If you don't want to set the secret key in the .env file, you can remove it from it since "config.py" set a random one if no one is set in the .env file. If so, "config.py" uses `os.urandom(INT).hex()` to generate the secret key. I used this way because the required library was already required elsewhere in the same script. But feel free to use something else if you want/need (e.g. : `uuid.uuid4().hex()` from "uuid", `token_urlsafe(INT)` or `token_hex(INT)` from "secrets", or even just remove the `.hex()` from the `os.urandom(INT).hex()`). Just replace the "INT" with any integer.

If you're looking for installing PostgreSQL and/or Python on your server or webhost, please refer to Python, PostgreSQL, and/or your webhost docs.