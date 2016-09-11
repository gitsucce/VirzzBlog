from flask import render_template, request, redirect, abort, jsonify, session, Blueprint
from flask import current_app as app
from ICore.utils import authed, roots_only, GetTime, get_config, set_config, del_config, postPlugin
from ICore.models import db, Articles, Links, Categorys, Config, DatabaseError
import time
import os


roots = Blueprint('roots', __name__)


@roots.route('/install.vir', methods=['GET', 'POST'])
def root_install():
    if request.method == 'POST':
        if get_config('setup'):
            return '0'
        username = request.json['setup']['username']
        password = request.json['setup']['password']
        set_config('rootuser', username)
        set_config('rootpass', password)
        set_config('setup', 1)
        return '1'
    abort(404)


@roots.route('/login.html', methods=['GET', 'POST'])
@roots.route('/logout.html', methods=['GET', 'POST'])
def joke():
    return render_template('errors/joke.html')


@roots.route('/roots', methods=['GET', 'POST'])
@roots.route('/roots/index', methods=['GET', 'POST'])
@roots.route('/roots/index.html', methods=['GET', 'POST'])
def roots_index():
    abort(404)


# Auth ===========================================
@roots.route('/roots/login.vir', methods=['GET', 'POST'])
def roots_login():
    json = {'login': {}}
    if request.method == 'POST':
        name = request.json['login']['username']
        password = request.json['login']['password']
        if name == get_config('rootuser') and password == str(get_config('rootpass')):
            try:
                session.regenerate()
            except:
                pass
            session['username'] = name
            return '1'
    return '0'


@roots.route('/logout')
@roots.route('/roots/logout')
@roots.route('/logout.vir')
@roots.route('/roots/logout.vir')
def logout():
    print authed()
    if authed():
        print 'logout'
        session.clear()
    return redirect('/')


# Setting setting ===========================================
@roots.route('/roots/setting.vir', methods=['GET', 'POST'])
@roots_only
def roots_setting():
    if request.method == 'POST':
        d = request.form.get('del', None)
        if d:
            del_config(d)
            return '1'
        key = request.form.get('key', None)
        value = request.form.get('value', None)
        if set_config(key, value):
            return '1'
    config = Config.query.all()
    if not config:
        config = False
    return render_template('roots/setting.html', pagetitle='Setting', index=config)


# Categorys categorys ===========================================
@roots.route('/roots/categorys.vir', methods=['GET', 'POST'])
@roots_only
def roots_categorys_list():
    categorys = Categorys.query.group_by(Categorys.id).all()
    db.session.close()
    if categorys:
        return render_template('roots/catelist.html', pagetitle='Categorys List', index=categorys)
    else:
        return redirect('/roots/setting.vir')


@roots.route('/roots/categorys/<id>/change.vir', methods=['GET', 'POST'])
@roots_only
def roots_change_category(id):
    if request.method == "POST":
        try:
            pid = request.form.get('pid', 0)
            mid = request.form.get('mid', 0)
            route = request.form.get('route', None)
            name = request.form.get('name', None)
            categorys = Categorys.query.filter_by(id=id).first()
            if categorys:
                categorys.pid = pid
                categorys.mid = mid
                categorys.route = route
                categorys.name = name
                db.session.commit()
                db.session.close()
        except Exception, e:
            print e
        return redirect('/roots/categorys.vir')
    else:
        categorys = Categorys.query.filter_by(id=id).first()
        if not categorys:
            categorys = False
        return render_template('roots/addcate.html', pagetitle='Change Categorys', index=categorys)


@roots.route('/roots/categorys/add.vir', methods=['GET', 'POST'])
@roots_only
def roots_add_category():
    if request.method == "POST":
        try:
            pid = request.form.get('pid', 0)
            mid = request.form.get('mid', 0)
            route = request.form.get('route', None)
            name = request.form.get('name', None)
            categorys = Categorys(pid, mid, route, name)
            if categorys:
                categorys.pid = pid
                categorys.mid = mid
                categorys.route = route
                categorys.name = name
                db.session.add(categorys)
                db.session.commit()
                db.session.close()
            return redirect('/roots/categorys.vir')
        except:
            pass
    else:
        return render_template('roots/addcate.html', pagetitle='Add Categorys', index=0)


@roots.route('/roots/categorys/<id>/delete.vir', methods=['GET', 'POST'])
@roots_only
def roots_delete_category(id):
    try:
        Categorys.query.filter_by(id=id).delete()
        db.session.commit()
        db.session.close()
    except:
        pass
    return redirect('/roots/categorys.vir')


# Links links ===========================================
@roots.route('/roots/links.vir', methods=['GET', 'POST'])
@roots_only
def roots_links_list():
    links = Links.query.order_by(Links.count.desc()).all()
    if links:
        return render_template('roots/linkslist.html', pagetitle='Links List', index=links)
    else:
        return redirect('/roots/setting.vir')


@roots.route('/roots/links/<id>/change.vir', methods=['GET', 'POST'])
@roots_only
def roots_change_link(id):
    if request.method == "POST" and id > 0:
        try:
            title = request.form.get('title', None)
            href = request.form.get('href', None)
            count = request.form.get('count', 0)
            links = Links.query.filter_by(id=id).first()
            if links:
                links.title = title
                links.href = href
                links.count = count
                db.session.commit()
                db.session.close()
        except:
            pass
        return redirect('/roots/links.vir')
    else:
        try:
            links = Links.query.filter_by(id=id).first()
            if not links:
                links = False
        except:
            pass
        return render_template('roots/addlinks.html', pagetitle='Change Links', index=links)


@roots.route('/roots/links/add.vir', methods=['GET', 'POST'])
@roots_only
def roots_add_link():
    if request.method == "POST":
        try:
            title = request.form.get('title', None)
            href = request.form.get('href', None)
            count = request.form.get('count', 0)
            links = Links(title, href)
            if links:
                links.title = title
                links.href = href
                links.count = count
                db.session.add(links)
                db.session.commit()
                db.session.close()
        except Exception, e:
            print e
        return redirect('/roots/links.vir')
    else:
        return render_template('roots/addlinks.html', pagetitle='Add Links', index=0)


@roots.route('/roots/links/<id>/delete.vir', methods=['GET', 'POST'])
@roots_only
def roots_delete_link(id):
    try:
        Links.query.filter_by(id=id).delete()
        db.session.commit()
        db.session.close()
    except:
        pass
    return redirect('/roots/links.vir')


# Articles article ===========================================
@roots.route('/roots/articles.vir', defaults={'page': '1'}, methods=['GET', 'POST'])
@roots.route('/roots/articles.vir/<page>')
@roots_only
def roots_article_list(page):
    page = abs(int(page))
    results_per_page = 30
    page_start = results_per_page * (page - 1)
    page_end = results_per_page * (page - 1) + results_per_page
    articles = Articles.query.order_by(
        Articles.id.desc()).slice(page_start, page_end).all()
    count = db.session.query(db.func.count(Articles.id)).first()[0]
    pages = int(count / results_per_page) + (count % results_per_page > 0)
    db.session.close()
    if articles:
        return render_template('roots/artilist.html', pagetitle='Articles List', index=articles, pages=pages, page=page)
    else:
        return redirect('/roots/setting.vir')


@roots.route('/roots/articles/<id>/editor.vir', methods=['GET', 'POST'])
@roots.route('/roots/articles/editor.vir', methods=['GET', 'POST'])
@roots_only
def roots_edit_article(id=0):
    id = abs(int(id))
    categorys = Categorys.query.all()
    if request.method == "POST":
        try:
            title = request.form.get('title', None)
            route = request.form.get('route', None)
            category = request.form.get('cid', None)
            content = request.form.get('content', None)
        except:
            return redirect('/roots/articles.vir')
        if id > 0:
            try:
                article = Articles.query.filter_by(id=id).first()
                if article:
                    article.cid = category
                    article.title = title
                    article.route = route
                    article.content = content
                    article.date = GetTime()
                    db.session.commit()
                    db.session.close()
                    # Load postPlugin
                    postPlugin(
                        route, "[Change] "+config['HOST']+route+".html "+title+" "+content[:100])
            except:
                pass
            return redirect('/roots/articles.vir')
        else:
            try:
                article = Articles(category, route, title, content)
                if article:
                    article.cid = category
                    article.title = title
                    article.route = route
                    article.content = content
                    db.session.add(article)
                    db.session.commit()
                    db.session.close()
                    # Load postPlugin
                    postPlugin(
                        route, "[New] "+config['HOST']+route+".html "+title+" "+content[:100])
            except:
                pass
            return redirect('/roots/articles.vir')
    else:
        pagetitle = "Add Article"
        article = False
        if id > 0:
            article = Articles.query.filter_by(id=id).first()
            if article:
                pagetitle = "Editor Article"
        return render_template('roots/editor.html', pagetitle=pagetitle, index=article, categorys=categorys)


@roots.route('/roots/articles/<id>/delete.vir', methods=['GET', 'POST'])
@roots_only
def roots_delete_article(id):
    try:
        Articles.query.filter_by(id=id).delete()
        db.session.commit()
    except DatabaseError:
        pass
    return redirect('/roots/articles.vir')
