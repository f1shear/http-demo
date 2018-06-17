from flask import Flask
from flask import request, render_template, session, make_response, Response

from functools import wraps


import json
import logging
import datetime
from datastore import DataStore

logging.getLogger().setLevel(logging.INFO)

app = Flask(__name__, static_folder='static')


def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    # use environment variables instead of hardcoded values for security
    return username == 'admin' and password == 'secret'


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


def extract_info(val):
    info = {}
    for key in val:
        info[str(key)] = str(val.get(key))
    return info


def log_request(request, session):
    print("--------------------------")
    print("Request: headers, query params, form data, cookies, session")
    # Usage:access-request-info
    logging.info(request.headers)
    logging.info(request.headers.get('Host'))
    logging.info(request.args)
    logging.info(request.form)
    logging.info(request.cookies)
    logging.info(session)
    print("---------------------------")
    if 'request_counter' not in session:
        session['request_counter'] = 1
    else:
        session['request_counter'] += 1


def extract_request(request, session):
    log_request(request, session)
    request_info = {
        'headers': extract_info(request.headers),
        'query_params': extract_info(request.args),
        'form': extract_info(request.form),
        'cookies': extract_info(request.cookies),
        'session': extract_info(session)
    }
    return request_info


def get_now():
    return str(datetime.datetime.now())


@app.route('/', methods=['GET'])
def home():
    request_info = extract_request(request, session)
    context = {'title': 'CodeMunk', 'request_info': request_info}
    response = make_response(render_template('home.html', **context))
    response.set_cookie('dt', get_now())
    return response


@app.route('/api/', methods=['GET', 'POST'])
def api_home():
    request_info = extract_request(request, session)
    if request.method == 'POST':
        message = request.form.get('message', '')
        datastore = request.form.get('datastore', '')
        DataStore.store_message(datastore, message)
    context = {'request_info': request_info}
    response = make_response(json.dumps(context))
    response.set_cookie('dt', get_now())
    return response


@app.route('/api/protected/', methods=['GET', 'POST'])
@requires_auth
def secret_page():
    request_info = extract_request(request, session)
    context = {'request_info': request_info}
    response = make_response(json.dumps(context))
    response.set_cookie('dt', get_now())
    return response


if __name__ == '__main__':
    app.secret_key = 'this needs to be changed in production'
    app.debug = True
    app.run()
