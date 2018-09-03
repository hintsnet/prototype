from webapp import flask_app
print(" * Preset secret key is: %s" % flask_app.config['SECRET_KEY'])
