# Database initialisation 
Create the database manually then use these lines in `flask shell` to create the database tables.
```python
>>> from app.extensions import db
>>> from app.models.user import User
>>> from app.models.link import Link, File
>>> db.create_all()
>>> exit()
```
If you don't know how to create manually the database, please refer to PostgreSQL and/or your host documentation.

# Environnement initialisation
Create a ".env" file then put the environnement informations. Here is the template below, modify the values as you need.
```properties
# Running environnement config
FLASK_RUN_HOST="0.0.0.0"
FLASK_RUN_PORT=8052
FLASK_APP=app
FLASK_ENV=production

# Security config
SECRET_KEY="YOUR_OWN_SECRET_KEY"

# Database config
DATABASE_URI="DATABASE_SERVICE://USER:PASSWORD@HOST:DATABASE_PORT/DATABASE_NAME"

# Mail config
MAIL_SERVER="127.0.0.1"
MAIL_PORT=465
MAIL_DEFAULT_SENDER="no-reply@yourdomainname.com"
MAIL_USERNAME="YOUR_USERNAME"
MAIL_PASSWORD="YOUR_PASSWORD"
MAIL_USE_TLS=False
MAIL_USE_SSL=True
```
TIPS :
- Example for the database URI using PostGreSQL... :
```properties
DATABASE_URI="postgresql+psycopg2://postgres:root@127.0.0.1:5432/url_shortener"
```
- If you don't want to set the secret key in the .env file, you can remove it from it since "config.py" set a random one if no one is set in the .env file. If so, "config.py" uses `os.urandom(INT).hex()` to generate the secret key. I used this way because the required library was already required elsewhere in the same script. But feel free to use something else if you want/need (e.g. : `uuid.uuid4().hex()` from "uuid", `token_urlsafe(INT)` or `token_hex(INT)` from "secrets", or even just remove the `.hex()` from the `os.urandom(INT).hex()`). Just replace the "INT" with any integer.

If you're looking for installing PostgreSQL and/or Python on your server or webhost, please refer to Python, PostgreSQL, and/or your webhost docs.