from flask import Flask, jsonify, make_response, Response, request
import time
import os

app = Flask(__name__)

host = os.environ.get('HOST', '0.0.0.0')
port = os.environ.get('PORT', 8080)

HTTP_METHODS = ['GET', 'HEAD', 'POST', 'PUT',
                'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH']


@app.route('/')
def top():
    return make_response(jsonify(top='Hello mock server'), 200)


@app.route('/<int:sleep_time>/<int:status_code>', methods=HTTP_METHODS)
def index(sleep_time, status_code):
    if 100 <= status_code <= 599:
        time.sleep(sleep_time)
        return make_response(jsonify(sleep_time=sleep_time, status_code=status_code), status_code)
    else:
        return make_response(jsonify(err="Not status code"), 400)


@app.route('/sleep/<int:sleep_time>/', defaults={'status_code': 200}, methods=HTTP_METHODS)
def only_sleep_time(sleep_time, status_code):
    time.sleep(sleep_time)
    return make_response(jsonify(sleep_time=sleep_time, status_code=status_code), status_code)


@app.route('/status/<int:status_code>', methods=HTTP_METHODS)
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


if __name__ == '__main__':
    app.run(host=host, port=port)
