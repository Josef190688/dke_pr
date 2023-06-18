from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_cors import CORS
from app.currency_converter import CurrencyConverter

app = Flask(__name__)
app.config.from_object(Config)

CORS(app, resources={r"/*": {"origins": [
                            "http://127.0.0.1:50050",
                            "http://127.0.0.1:50051",
                            "http://127.0.0.1:50052",
                            "http://localhost:50050",
                            "http://localhost:50051",
                            "http://localhost:50052"]}})

login = LoginManager(app)
login.login_view = 'login'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
bootstrap = Bootstrap(app)
converter = CurrencyConverter()

from app import routes, models, api