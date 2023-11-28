# Database initialisation 
Create the database manually then use these lines in `flask shell` to create the database tables.
```python
 from app.extensions import db
 from app.models.user import User
 from app.models.link import Link
 db.create_all()
 exit()
```

# Environnement initialisation
Create a ".env" file then put the environnement informations. Here is the template below, modify the values as you need.
```sh
SECRET_KEY="YOUR_OWN_SECRET_KEY"
DATABASE_URI="DATABASE_SERVICE://USER:PASSWORD@HOST:DATABASE_PORT/DATABASE_NAME"
FLASK_RUN_HOST="0.0.0.0"
FLASK_RUN_PORT=5000
FLASK_APP=app
FLASK_ENV=development
```
TIPS :
- Example for the database URI using PostGreSQL... :
```sh
DATABASE_URI="postgresql+psycopg2://postgres:root@127.0.0.1:5432/url_shortener"
```
- If you don't want to set the secret key here, you can remove it from here since "config.py" set a random one if no one is set here. If so, "config.py" uses `os.urandom(INT).hex()` to generate the secret key. I used this way because the required library was already required elsewhere in it. But feel free to use something else if you want/need (e.g. : `uuid.uuid4().hex()` from "uuid", `token_urlsafe(INT)` or `token_hex(INT)` from "secrets", or even just remove the `.hex()` from the `os.urandom(INT).hex()`). Just replace the "INT" with any integer.