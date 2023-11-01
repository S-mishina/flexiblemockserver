from flask import Flask, jsonify, make_response , Response
import time
import os

app = Flask(__name__)

host = os.environ.get('HOST', '0.0.0.0')
port = os.environ.get('PORT', 8080)

@app.route('/<int:sleep_time>/<int:status_code>')
def index(sleep_time, status_code):
    if 100 <= status_code <= 599:
        time.sleep(sleep_time)
        return make_response(jsonify(sleep_time=sleep_time,status_code=status_code), status_code)
    else:
        return make_response(jsonify(err="Not status code"), 400)

@app.route('/<int:sleep_time>/', defaults={'status_code': 200})
@app.route('/<int:sleep_time>')
def only_sleep_time(sleep_time, status_code):
    time.sleep(sleep_time)
    return make_response(jsonify(sleep_time=sleep_time, status_code=status_code), status_code)

@app.route('/status/<int:status_code>')
def only_status_code(status_code, sleep_time=0):
    if 100 <= status_code <= 599:
        time.sleep(sleep_time)
        return make_response(jsonify(sleep_time=sleep_time, status_code=status_code), status_code)
    else:
        return make_response(jsonify(err="Not status code"), 400)

if __name__ == '__main__':
    app.run(host=host, port=port)

