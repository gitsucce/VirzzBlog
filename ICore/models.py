from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import DatabaseError
import time


def get_ip():
    remote_addr = request.remote_addr
    return remote_addr


def GetTime():
    return str(time.time())

db = SQLAlchemy()


# Categorys
class Categorys(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pid = db.Column(db.Integer)
    mid = db.Column(db.Integer)
    route = db.Column(db.String(128), unique=True)
    name = db.Column(db.String(128))

    def __init__(self, pid, mid, route, name):
        self.pid = pid
        self.mid = mid
        self.route = route
        self.name = name

    def __repr__(self):
        return '<catalog %r>' % self.name


# Articles
class Articles(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cid = db.Column(db.Integer, db.ForeignKey('categorys.id'))
    route = db.Column(db.String(128), unique=True)
    title = db.Column(db.String(128))
    date = db.Column(db.String(20))
    content = db.Column(db.Text)
    count = db.Column(db.Integer)

    def __init__(self, cid, route, title, content, date=None):
        self.cid = cid
        self.route = route
        self.title = title
        if date == None:
            date = GetTime()
        self.date = date
        self.content = content
        self.count = 0

    def __repr__(self):
        return '<articles %r>' % self.title


# Links
class Links(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128))
    href = db.Column(db.String(128))
    count = db.Column(db.Integer, default=0)

    def __init__(self, title, href):
        self.title = title
        self.href = href
        self.count = 0

    def __repr__(self):
        return '<Links %r>' % self.title


class Config(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.Text)
    value = db.Column(db.Text)

    def __init__(self, key, value):
        self.key = key
        self.value = value
