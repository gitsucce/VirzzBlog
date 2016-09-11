from flask import Flask, render_template, request, redirect, abort, session, jsonify, json as json_mod, url_for, Response
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from logging.handlers import RotatingFileHandler
from flaskext.markdown import Markdown

import os
import sqlalchemy


class MyResponse(Response):

    def __init__(self, response, **kwargs):
        # Fake HTTP Hearders
        kwargs['headers'] = {
            'X-Powered-By': 'PHP/5.5.7', 'Server': 'nginx/1.4.4'}
        return super(MyResponse, self).__init__(response, **kwargs)


def create_app(config='ICore.config'):
    app = Flask("ICore")
    with app.app_context():
        app.config.from_object(config)

        Session(app)
        Markdown(app)

        from ICore.models import db, Links, Articles, Categorys

        db.init_app(app)
        db.create_all()
        app.db = db

        from ICore.views import views
        from ICore.roots import roots
        from ICore.utils import init_utils, init_errors

        init_utils(app)
        init_errors(app)

        app.register_blueprint(views)
        app.register_blueprint(roots)

        app.response_class = MyResponse

        return app
