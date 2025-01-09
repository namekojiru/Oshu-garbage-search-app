from flask import Flask, request, g
from flask_babel import Babel
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    def get_locale():
        return request.args.get('lang', app.config['BABEL_DEFAULT_LOCALE'])

    babel = Babel(app, locale_selector=get_locale)

    @app.context_processor
    def context_processor():
        return dict(get_locale=get_locale)

    from . import routes
    routes.init_app(app)
    
    return app