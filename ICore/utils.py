from ICore.models import db, Config, Categorys, Articles, Links
from flask import current_app as app, g, request, session, render_template, abort, redirect
from sqlalchemy import create_engine
from functools import wraps

import time
import requests


def init_errors(app):

    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(403)
    def forbidden(error):
        return render_template('errors/403.html'), 403

    @app.errorhandler(500)
    def general_error(error):
        return render_template('errors/500.html'), 500

    @app.errorhandler(502)
    def gateway_error(error):
        return render_template('errors/502.html'), 502


def init_utils(app):
    app.jinja_env.globals.update(config=app.config)
    app.jinja_env.globals.update(webcategorys=webcategorys)
    app.jinja_env.globals.update(weblinks=weblinks)
    app.jinja_env.globals.update(TimeToStr=TimeToStr)
    app.jinja_env.globals.update(get_config=get_config)

    @app.context_processor
    def inject_user():
        if session:
            return dict(session)
        return dict()

    @app.before_request
    def needs_setup():
        if request.path == '/install.vir' or request.path.startswith('/static'):
            return
        if not get_config('setup'):
            return 'init'


def TimeToStr(ttt):
    if ttt:
        return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(ttt)))
    else:
        return "Null"


def TimeToStrFeed(ttt):
    if ttt:
        return time.strftime("%a, %d %b %Y %X +0800", time.localtime(float(ttt)))
    else:
        return "Null"


def GetTime():
    return str(time.time())


def authed():
    return bool(session.get('username', False))


def roots_only(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('username', None) is None:
            abort(404)
        return f(*args, **kwargs)
    return decorated_function


def get_config(key):
    config = Config.query.filter_by(key=key).first()
    if config:
        value = config.value
        if value and value.isdigit():
            return int(value)
        else:
            return value
    else:
        set_config(key, None)
        return None


def set_config(key, value):
    config = Config.query.filter_by(key=key).first()
    if config:
        config.value = value
    else:
        config = Config(key, value)
        db.session.add(config)
    db.session.commit()
    return config


def del_config(key):
    try:
        config = Config.query.filter_by(key=key).delete()
        db.session.commit()
        db.session.close()
    except:
        pass


def webcategorys():
    categorys = Categorys.query.filter_by(
        pid=0).order_by(Categorys.mid.asc()).all()
    return categorys


def weblinks(n=0):
    n = int(abs(n))
    if n > 0:
        links = Links.query.order_by(Links.count.desc()).slice(0, 5).all()
    else:
        links = Links.query.order_by(Links.count.desc()).all()
    return links


def postPlugin(route, text):
    # postBaiduSitemap(route):
    t = get_config('baidu_sitemap_token')
    if t:
        res = requests.post(url='http://data.zz.baidu.com/urls?site='+config['DOMAIN']+'&token='+t,
                            data=config['HOST']+route+".html")
    # postWeibo(text):
    if get_config('weibo_open'):
        playload = {
            "access_token": get_config('weibo_access_token'),
            "status": text
        }
        r = requests.post(
            url="https://api.weibo.com/2/statuses/update.json", data=playload)
    # postTwitter(text):
    if get_config('twitter_open') and text:
        token = get_config('twitter_token')
        token_key = get_config('twitter_token_key')
        secret = get_config('twitter_secret')
        secret_key = get_config('twitter_secret_key')
        t = Twitter(
            auth=OAuth(twitter_token, twitter_token_key, twitter_secret, twitter_secret_key))
        if t:
            t.statuses.update(status=text)
