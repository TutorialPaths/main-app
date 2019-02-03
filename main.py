from flask import Flask, request, redirect, abort
import datetime
import json
import user_handler
import html_processor
import markdown2
from urllib.request import urlopen

# basic Flask setup
app = Flask(__name__)


# basic functions
def loadFile(url):
    try:
        html = open(url, "r")
        return html.read()
    except:
        return None


def loadDOM(url):
    try:
        html = urlopen("https://dom.tutorialpaths.com" + url + "/_index.html")
        return html.read()
    except:
        abort(404)


def loadDOMAbs(url):
    try:
        html = urlopen("https://dom.tutorialpaths.com" + url)
        return html.read()
    except:
        return None


def strDateToPython(date):
    return datetime.strptime(date, '%Y-%m-%dT%H:%M:%S.%fZ')


def pythonToStrDate(d):
    return json.dumps(d.isoformat())


# functions
@app.route('/auth', methods=["GET"])
def auth():
    if request.cookies.get('sr:id'):
        return redirect("https://tutorialpaths.com/u/me", code=302)

    return loadDOM("/auth")


@app.route('/u/<user>')
def user(user):
    if user == 'me':
        if request.cookies.get('sr:id'):
            # get the current user and redirect there
            res = user_handler.verify_session(request.cookies.get('sr:id'), request.remote_addr)
            if res:
                res = user_handler.get_user("`ur:id`", res)
                if res:
                    return redirect("https://tutorialpaths.com/u/" + res['u:id'], code=302)

        return redirect("https://tutorialpaths.com/auth?r=/u/me", code=302)

    else:
        # go to the specific user
        res = user_handler.get_user("u:id", user)
        if res:
            return "Information for user:\n " + str(res)
        else:
            res = user_handler.get_user("`ur:id`", user)
            if res:
                return redirect("https://tutorialpaths.com/u/" + res['u:id'], 302)
            else:
                return "User not found"


@app.route('/t', methods=["GET"])
def tutorialviewnone():
    return redirect("https://tutorialpaths.com", 302)


@app.route('/t/<tutorial>/', methods=["GET"])
def tutorialview(tutorial):
    html = urlopen("https://dom.tutorialpaths.com/t/_index.html").read()

    processed = html_processor.process(html, {
        "support-pages": '[]',
        "user": bool(request.cookies.get('sr:id'))
    }).replace("<html", "<html " + ("dark" if request.cookies.get("theme") == "dark" else ""))

    return processed


@app.route('/t/<tutorial>', methods=["GET"])
def tutorialviewwrong(tutorial):
    return redirect("https://tutorialpaths.com/t/" + tutorial + "/")


@app.route('/', methods=["GET"])
def home():
    html = urlopen("https://dom.tutorialpaths.com/home/_index.html").read()

    processed = html_processor.process(html, {
        "support-pages": '[]',
        "user": bool(request.cookies.get('sr:id'))
    }).replace("<html", "<html " + ("dark" if request.cookies.get("theme") == "dark" else ""))

    return processed


@app.route('/search', methods=["GET"])
def searchtag():
    return request.args.get('q')
    try:
        q = request.args.get('q')
    except:
        # huh, they didn't put any query in. we'll just redirect them home
        return redirect("https://tutorialpaths.com", 302)

    if q[:1] == "#":
        return redirect("https://tutorialpaths.com/tag/" + q[1:], code=302)

    return 'search results for "' + q + '" should go here'


@app.route('/tag/#<tag>', methods=["GET"])
def taginf(tag):
    html = urlopen("https://dom.tutorialpaths.com/tag/_index.html").read()

    processed = html_processor.process(html, {
        "support-pages": '[]',
        "user": bool(request.cookies.get('sr:id'))
    }).replace("<html", "<html " + ("dark" if request.cookies.get("theme") == "dark" else ""))

    return processed


@app.route('/tag/<tag>', methods=["GET"])
def tagredir(tag):
    return redirect("https://tutorialpaths.com/tag/#" + tag, code=302)


@app.route('/tp/<page>', methods=["GET"])
def staticpage(page):
    page_fl = loadDOMAbs('/st/' + page + '.md')
    if page_fl:
        md = markdown2.markdown(page_fl).replace('\n', '')
        html = loadDOM("/static")
        if html:
            return html_processor.process(html, {
                "support-pages": '[]',
                "user": bool(request.cookies.get('sr:id')),
                "markdown": md
            }).replace("<html", "<html " + ("dark" if request.cookies.get("theme") == "dark" else ""))

    abort(404)


@app.route('/<path:path>', methods=["GET"])
def no_page_found(path):
    abort(404)
