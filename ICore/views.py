from flask import current_app as app, render_template, request, redirect, abort, jsonify, json as json_mod, url_for, session, Blueprint, Response
from ICore.utils import get_config, set_config, TimeToStr, TimeToStrFeed
from ICore.models import db, Links, Articles, Categorys

import os
import sys
import time

views = Blueprint('views', __name__)


@views.route("/")
@views.route("/index.htm", methods=['GET'])
@views.route("/index.php", methods=['GET'])
@views.route("/index.asp", methods=['GET'])
@views.route("/index.aspx", methods=['GET'])
@views.route("/index.jsp", methods=['GET'])
def jumpindex():
    return redirect('/index.html')


# Index
@views.route("/index.html", methods=['GET'])
@views.route("/index/<page>", methods=['GET'])
def index(page=1):
    page = abs(int(page))
    results_per_page = 10
    page_start = results_per_page * (page - 1)
    page_end = results_per_page * (page - 1) + results_per_page
    articles = Articles.query.order_by(Articles.date.desc()).join(Categorys, Articles.cid == Categorys.id)\
        .add_columns(Articles.route, Articles.title, Articles.date, Articles.content, Articles.count)\
        .add_columns(Categorys.name.label('cname'), Categorys.route.label('croute'))\
        .slice(page_start, page_end).all()
    count = db.session.query(db.func.count(Articles.id)).first()[0]
    pages = int(count / results_per_page) + (count % results_per_page > 0)
    return render_template('index.html', pagetitle=False, index=articles, pages=pages, curr_page=page)


# Search
@views.route("/search", methods=['GET', 'POST'])
def Search():
    search = request.args.get('search')
    page = request.args.get('page')
    if not search:
        return redirect('/index.html')
    if not page:
        page = 1
    page = abs(int(page))
    results_per_page = 10
    page_start = results_per_page * (page - 1)
    page_end = results_per_page * (page - 1) + results_per_page
    articles = Articles.query.order_by(Articles.date.desc()).join(Categorys, Articles.cid == Categorys.id)\
        .add_columns(Articles.route, Articles.title, Articles.date, Articles.content, Articles.count)\
        .add_columns(Categorys.name.label('cname'), Categorys.route.label('croute'))\
        .filter(Articles.content.like("%"+search+"%")).slice(page_start, page_end).all()
    count = db.session.query(db.func.count(Articles.id)).filter(
        Articles.content.like("%"+search+"%")).first()[0]
    pages = int(count / results_per_page) + (count % results_per_page > 0)
    if articles:
        return render_template('search.html', pagetitle='Results : '+search, index=articles, pages=pages, curr_page=page, search=search)
    else:
        return render_template('search.html', pagetitle='Nothing~~', index=[], pages=1, curr_page=1, search=search)


# Category Articles
@views.route('/category/<route>.html', methods=['GET'])
@views.route('/category/<route>/<page>', methods=['GET'])
def categorys(route="index", page=1):
    routes = Categorys.query.add_columns(Categorys.route).all()
    routelist = []
    for i in routes:
        routelist.append(i[1])
    if route not in routelist or route == "index":
        return redirect('/index.html')
    page = abs(int(page))
    results_per_page = 20
    page_start = results_per_page * (page - 1)
    page_end = results_per_page * (page - 1) + results_per_page
    articles = Articles.query.order_by(Articles.date.desc()).join(Categorys, Articles.cid == Categorys.id)\
        .add_columns(Articles.route, Articles.title, Articles.date, Articles.content, Articles.count)\
        .add_columns(Categorys.name.label('cname'), Categorys.route.label('croute'))\
        .filter_by(route=route).slice(page_start, page_end).all()
    count = db.session.query(db.func.count(Articles.id)).first()[0]
    pages = int(count / results_per_page) + (count % results_per_page > 0)
    if articles:
        return render_template('category.html', pagetitle=articles[0].cname, index=articles, pages=pages, curr_page=page)
    else:
        abort(500)


# Article
@views.route('/<route>.html', methods=['GET'])
def article(route):
    post = Articles.query.filter_by(route=route).join(Categorys, Articles.cid == Categorys.id)\
        .add_columns(Articles.route, Articles.title, Articles.date, Articles.content, Articles.count)\
        .add_columns(Categorys.name.label('cname'), Categorys.route.label('croute')).first()
    if post:
        a = Articles.query.filter_by(route=route).first()
        if a:
            a.count = a.count + 1
            db.session.commit()
            db.session.close()
        if post.title in post.content:
            atitle = False
        else:
            atitle = post.title
        return render_template('article.html', pagetitle=post.title, post=post, atitle=atitle)
    elif os.path.exists('ICore/templates/static/'+route+'.html'):
        return render_template(route+'.html')
    else:
        abort(404)


# About
@views.route('/about.html', methods=['GET'])
def about():
    return render_template('about.html')


# JumpTo
@views.route('/jumpto/<lid>', methods=['GET'])
def jumpto(lid):
    lid = int(lid[5:])
    link = Links.query.filter_by(id=lid).first()
    print link
    if link:
        link.count = link.count + 1
        href = link.href
        db.session.commit()
        db.session.close()
        if 'http' not in href:
            return redirect('http://'+href)
        else:
            return redirect(href)
    else:
        return redirect('/')


# Feed & RSS
@views.route('/feed', methods=['GET'])
@views.route('/feed.xml', methods=['GET'])
@views.route('/rss', methods=['GET'])
@views.route('/rss.xml', methods=['GET'])
def feed():
    reqtype = request.path[1:]
    items = []
    item = {}
    articles = Articles.query.order_by(Articles.date.desc())\
        .add_columns(Articles.route, Articles.title, Articles.date, Articles.content)\
        .slice(0, 20).all()
    for article in articles:
        item = {
            "title": article.title,
            "url": app.config['DOMAIN']+"/"+article.route+".html",
            "date": TimeToStrFeed(article.date),
            "creator": get_config('rootuser'),
            "description": article.content[:100],
            "content": article.content
        }
        items.append(item)
    feed = {
        "reqtype": reqtype,
        "host": app.config['DOMAIN']+"/",
        "date": time.strftime("%a, %d %b %Y %X +0800", time.localtime())}
    return render_template('feed.xml', feed=feed, items=items), 200, {'Content-Type': 'application/rss+xml; charset=utf-8'}


# Sitemap
@views.route('/sitemap', methods=['GET'])
@views.route('/sitemap.xml', methods=['GET'])
def sitemap():
    items = []
    item = {}
    articles = Articles.query.order_by(Articles.date.desc())\
        .add_columns(Articles.route, Articles.date).slice(0, 50).all()
    for article in articles:
        item = {
            "url": app.config['HOST']+"/"+article.route+".html",
            "date": time.strftime("%Y-%m-%dT%X+08:00", time.localtime(float(article.date)))
        }
        items.append(item)
    date = time.strftime("%Y-%m-%dT%X+08:00", time.localtime())
    return render_template('sitemap.xml', date=date, items=items), 200, {'Content-Type': 'application/xml; charset=utf-8'}
