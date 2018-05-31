from flask import Flask
from flask import request, render_template, session, make_response

import json
import logging
import datetime


app = Flask(__name__)


def extract_info(val):
    info = {}
    for key in val:
        info[str(key)] = str(val.get(key))
    return info


def log_request(request, session):
    print("--------------------------")
    print("Request: headers, query params, form data, cookies, session")
    logging.error(request.headers)
    logging.error(request.headers.get('Host'))
    logging.error(request.args)
    logging.error(request.form)
    logging.error(request.cookies)
    logging.error(session)
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
    context = {'title': 'MunkTech', 'request_info': request_info}
    response = make_response(render_template('home.html', **context))
    response.set_cookie('dt', get_now())
    return response


@app.route('/api/', methods=['GET', 'POST'])
def api_home():
    request_info = extract_request(request, session)
    context = {'title': 'MunkTech', 'request_info': request_info}
    response = make_response(json.dumps(context))
    response.set_cookie('dt', get_now())
    return response


if __name__ == '__main__':
    app.secret_key = 'this needs to be changed in production'
    app.debug = True
    app.run()
