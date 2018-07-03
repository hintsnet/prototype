from flask import Flask
from config import Config

flask_obj = Flask(__name__)
flask_obj.config.from_object(Config)

from webapp import routes
