from flask import Flask

flask_obj = Flask(__name__)

from webapp import routes
