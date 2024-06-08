from flask import Flask, jsonify, make_response, Response, request
import logging
from logging.config import dictConfig
import time
import os

app = Flask(__name__)

@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    latency = time.time() - request.start_time
    response_log = {
        "response_time": latency,
        "request_header": dict(request.headers),
        "response_header": dict(response.headers),
        "query_params": request.args.to_dict(),
    }
    app.logger.info(response_log)
    return response

dictConfig({
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] in %(module)s: %(message)s',
        }
    },
    'handlers': {
        'wsgi': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'
        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

host = os.environ.get('HOST', '0.0.0.0')
port = os.environ.get('PORT', 8080)

HTTP_METHODS = ['GET', 'HEAD', 'POST', 'PUT',
                'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH']

@app.route('/')
def top():
    return make_response(jsonify(top='Hello mock server'), 200)

@app.route('/<int:sleep_time>/<int:status_code>', methods=HTTP_METHODS)
@app.route('/<int:sleep_time>/<int:status_code>/', methods=HTTP_METHODS)
def index(sleep_time, status_code):
    if 100 <= status_code <= 599:
        time.sleep(sleep_time)
        return make_response(jsonify(sleep_time=sleep_time, status_code=status_code), status_code)
    else:
        return make_response(jsonify(err="Not status code"), 400)

@app.route('/sleep/<int:sleep_time>', methods=HTTP_METHODS)
@app.route('/sleep/<int:sleep_time>/', methods=HTTP_METHODS)
def only_sleep_time(sleep_time):
    time.sleep(sleep_time)
    return make_response(jsonify(sleep_time=sleep_time, status_code=200), 200)

@app.route('/status/<int:status_code>', methods=HTTP_METHODS)
@app.route('/status/<int:status_code>/', methods=HTTP_METHODS)
def only_status_code(status_code, sleep_time=0):
    if 100 <= status_code <= 599:
        time.sleep(sleep_time)
        return make_response(jsonify(sleep_time=sleep_time, status_code=status_code), status_code)
    else:
        return make_response(jsonify(err="Not status code"), 400)

@app.route('/<int:sleep_time>/<int:status_code>/query', methods=HTTP_METHODS)
def index_query(sleep_time, status_code):
    if 100 <= status_code <= 599:
        time.sleep(sleep_time)
        query_params_dict = request.args.to_dict()
        return make_response(jsonify(sleep_time=sleep_time, status_code=status_code, output=str(query_params_dict)), status_code)
    else:
        return make_response(jsonify(err="Not status code"), 400)


@app.route('/sleep/<int:sleep_time>/query', defaults={'status_code': 200}, methods=HTTP_METHODS)
def only_sleep_time_query(sleep_time, status_code):
    time.sleep(sleep_time)
    query_params_dict = request.args.to_dict()
    return make_response(jsonify(sleep_time=sleep_time, status_code=status_code, output=str(query_params_dict)), status_code)


@app.route('/status/<int:status_code>/query', methods=HTTP_METHODS)
def only_status_code_query(status_code, sleep_time=0):
    if 100 <= status_code <= 599:
        time.sleep(sleep_time)
        query_params_dict = request.args.to_dict()
        return make_response(jsonify(sleep_time=sleep_time, status_code=status_code, output=str(query_params_dict)), status_code)
    else:
        return make_response(jsonify(err="Not status code"), 400)

@app.errorhandler(404)
def page_not_found(e):
    return make_response(jsonify(err="Nonexistent Path"), 404)

if __name__ == '__main__':
    app.run(host=host, port=port)
