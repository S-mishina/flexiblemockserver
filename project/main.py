import os
import sys
import time
import yaml
import json
from flask import Flask, jsonify, make_response, Response, request
from logging.config import dictConfig

from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.zipkin.json import ZipkinExporter
from opentelemetry.semconv.resource import ResourceAttributes

if os.getenv('OPEN_TELEMETRY_GRPC_FLG', 'False') == 'True':
    from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
    from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
else:
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.instrumentation.requests import RequestsInstrumentor

from opentelemetry.exporter.prometheus import PrometheusMetricReader

from jsonschema import validate
from prometheus_client import start_http_server

from opentelemetry.instrumentation.requests import RequestsInstrumentor

from redis import Redis

def get_yaml_file_path():
    return os.getenv('CUSTOM_RULE_YAML_FILE', 'config/custom_rule.yaml')

def get_open_telemetry_flg():
    return os.getenv('OPEN_TELEMETRY_FLG', 'False')

def get_debug_flg():
    return os.getenv('DEBUG_FLG', 'False')

def get_file_check(yaml_file,log_flag):
    if not os.path.exists(yaml_file):
        if log_flag==True:
            app.logger.info("{} not found".format(yaml_file))
        return False
    else:
        if log_flag==True:
            app.logger.info("{} file check ok".format(yaml_file))
        return True

def config_check(yaml_file):
    with open(yaml_file, "r") as yaml_file:
        yaml_data = yaml.safe_load(yaml_file)
    try:
        validate(instance=yaml_data, schema=schema)
        app.logger.info("The YAML file is consistent with the schema.")
        for i in range(len(yaml_data["custom_rule"])):
            try:
                with open(yaml_data["custom_rule"][i]["rule"].get("response_body_path"), "r") as response_body_file:
                    response_body = response_body_file.read()
            except Exception as e:
                app.logger.info("response_body_path not found: %s" % str(e))
                sys.exit(1)
    except Exception as e:
        app.logger.info("YAML file does not match schema: %s" % str(e))
        sys.exit(1)

def check_open_telemetry():
    if get_open_telemetry_flg():
        flags = [
            os.getenv('OPEN_TELEMETRY_ZIPKIN_FLG'),
            os.getenv('OPEN_TELEMETRY_OTLP_FLG'),
            os.getenv('OPEN_TELEMETRY_PROMETHEUS_FLG'),
            os.getenv('OPEN_TELEMETRY_CONSOLE_FLG')
        ]
        enabled_flags_count = sum(1 for flag in flags if flag)

        if enabled_flags_count >= 2:
            app.logger.info("Please set only one of OPEN_TELEMETRY_ZIPKIN_FLG and OPEN_TELEMETRY_OTLP_FLG")
            exit(1)

        if os.getenv('OTEL_SERVICE_NAME') is None:
            app.logger.info("Please set OTEL_SERVICE_NAME default: mock-server")
            os.environ['OTEL_SERVICE_NAME'] = 'mock-server'

        provider = TracerProvider()

        # Zipkin Exporter
        if os.getenv('OPEN_TELEMETRY_ZIPKIN_FLG', 'False') == 'True':
            app.logger.info("OpenTelemetry Zipkin Exporter")
            zipkin_exporter = ZipkinExporter(endpoint=os.getenv('ZIPKIN_HOST', 'http://localhost:9411/api/v2/spans'))
            processor = BatchSpanProcessor(zipkin_exporter)
            provider.add_span_processor(processor)
            trace.set_tracer_provider(provider)

        # OTLP Exporter
        elif os.getenv('OPEN_TELEMETRY_OTLP_FLG', 'False') == 'True':
            app.logger.info("OpenTelemetry OTLP Exporter")

            if os.getenv('OPEN_TELEMETRY_GRPC_FLG', 'False') == 'True':
                app.logger.info("OpenTelemetry OTLP gRPC Exporter")
                oltp_host = os.getenv('OTLP_HOST', 'localhost:4317')
                app.logger.info("OTLP_HOST: %s" % oltp_host)
                otlp_exporter = OTLPSpanExporter(endpoint=oltp_host, insecure=True)
                span_processor = BatchSpanProcessor(otlp_exporter)
                provider.add_span_processor(span_processor)
                trace.set_tracer_provider(provider)
            else:
                app.logger.info("OpenTelemetry OTLP HTTP Exporter")
                oltp_host = os.getenv('OTLP_HOST', 'http://localhost:4318/v1/traces')
                app.logger.info("OTLP_HOST: %s" % oltp_host)
                processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=oltp_host))
                provider.add_span_processor(processor)
                trace.set_tracer_provider(provider)
        # Prometheus Exporter
        elif os.getenv('OPEN_TELEMETRY_PROMETHEUS_FLG', 'False') == 'True':
            app.logger.info("OpenTelemetry Prometheus Exporter")
            prometheus_host = os.getenv('PROMETHEHEUS_HOST', 'localhost')
            prometheus_port = int(os.getenv('PROMETHEHEUS_PORT', '9090'))
            app.logger.info("PROMETHEUS_PORT: %s" % prometheus_port)
            app.logger.info("PROMETHEHEUS_HOST: %s" % prometheus_host)
            start_http_server(port=prometheus_port, addr=prometheus_host)
            reader = PrometheusMetricReader()
            provider = MeterProvider(metric_readers=[reader])
            metrics.set_meter_provider(provider)

        # Console Exporter
        elif os.getenv('OPEN_TELEMETRY_CONSOLE_FLG', 'False') == 'True':
            app.logger.info("OpenTelemetry Console Exporter")
            processor = BatchSpanProcessor(ConsoleSpanExporter())
            provider.add_span_processor(processor)
            trace.set_tracer_provider(provider)
            tracer = trace.get_tracer("my.tracer.name")

def get_cache_config():
    if os.getenv('CACHE_FLAG', False) == "True":
        redis_host = os.getenv('REDIS_HOST', 'localhost')
        redis_port = os.getenv('REDIS_PORT', 16379)
    return redis_host, redis_port

def connection_cache():
    if os.getenv('CACHE_CLUSTER_FLAG', True) is True:
        redis_host, redis_port = get_cache_config()
        r = Redis(host=redis_host, port=redis_port, decode_responses=True)
        return r
    else:
        redis_host, redis_port = get_cache_config()
        r = Redis(host=redis_host, port=redis_port)
        return r

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
app = Flask(__name__)

if get_open_telemetry_flg() == 'True':
    check_open_telemetry()
    FlaskInstrumentor().instrument_app(app)
    if os.getenv('OPEN_TELEMETRY_GRPC_FLG', 'False') == 'True':
        app.logger.info("OpenTelemetry gRPC Exporter")
        RequestsInstrumentor().instrument()

HTTP_METHODS = ['GET', 'HEAD', 'POST', 'PUT',
                'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH']
yaml_file = 'config/custom_rule.yaml'
schema = {
    "type": "object",
    "properties": {
        "custom_rule": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "rule": {
                        "type": "object",
                        "properties": {
                            "path": {"type": "string"},
                            "method": {"type": "string"},
                            "sleep_time": {"type": "integer", "minimum": 0},
                            "status_code": {"type": "integer", "minimum": 100, "maximum": 599},
                            "response_body_path": {"type": "string"},
                            "response_header": {"type": "string"}
                        },
                        "required": ["path", "method", "status_code"],
                        "additionalProperties": False
                    }
                },
                "required": ["name", "rule"],
                "additionalProperties": False
            }
        }
    },
    "required": ["custom_rule"],
    "additionalProperties": False
}


@app.before_request
def before_request():
    request.start_time = time.time()

@app.after_request
def after_request(response):
    latency = time.time() - request.start_time
    response_log = {
        "path": request.path,
        "method": request.method,
        "status_code": response.status_code,
        "response_time": latency,
        "request_header": dict(request.headers),
        "response_header": dict(response.headers),
        "query_params": request.args.to_dict(),
    }
    app.logger.info(response_log)
    return response

@app.route('/')
def top():
    data = {'top': 'Hello mock server'}
    if os.getenv('CACHE_FLAG') == 'True':
        r = connection_cache()
        value = r.get("/")
        if value:
            app.logger.info("Hit /")
            return make_response(jsonify(json.loads(value)), 200)
        else:
            app.logger.info("Miss Hit /")
            r.set("/", json.dumps(data))
            return make_response(jsonify(data), 200)
    else:
        return make_response(jsonify(data), 200)

@app.route('/<int:sleep_time>/<int:status_code>', methods=HTTP_METHODS)
@app.route('/<int:sleep_time>/<int:status_code>/', methods=HTTP_METHODS)
def index(sleep_time, status_code):
    if 100 <= status_code <= 599:
        data = {'sleep_time': sleep_time, 'status_code': status_code}
        if os.getenv('CACHE_FLAG') == 'True':
            r = connection_cache()
            value = r.get("{}/{}".format(sleep_time,status_code))
            if value:
                time.sleep(sleep_time)
                app.logger.info("Hit /")
                return make_response(jsonify(json.loads(value)), 200)
            else:
                app.logger.info("Miss Hit /")
                r.set("{}/{}".format(sleep_time,status_code), json.dumps(data))
                return make_response(json.dumps(data), status_code)
        else:
            time.sleep(sleep_time)
            return make_response(json.dumps(data), status_code)
    else:
        return make_response(jsonify(err="Not status code"), 400)

@app.route('/sleep/<int:sleep_time>', methods=HTTP_METHODS)
@app.route('/sleep/<int:sleep_time>/', methods=HTTP_METHODS)
def only_sleep_time(sleep_time):
    data = {'sleep_time': sleep_time, 'status_code': 200}
    if os.getenv('CACHE_FLAG') == 'True':
        r = connection_cache()
        value = r.get("/sleep/{}".format(sleep_time))
        if value:
            time.sleep(sleep_time)
            app.logger.info("Hit /sleep/{}".format(sleep_time))
            return make_response(jsonify(data), 200)
        else:
            app.logger.info("Miss Hit /sleep/{}".format(sleep_time))
            r.set("sleep/{}".format(sleep_time), json.dumps(value))
            time.sleep(sleep_time)
            return make_response(jsonify(data), 200)
    else:
        time.sleep(sleep_time)
        return make_response(jsonify(data), 200)

@app.route('/status/<int:status_code>', methods=HTTP_METHODS)
@app.route('/status/<int:status_code>/', methods=HTTP_METHODS)
def only_status_code(status_code, sleep_time=0):
    if 100 <= status_code <= 599:
        time.sleep(sleep_time)
        data = {'sleep_time': sleep_time, 'status_code': status_code}
        if os.getenv('CACHE_FLAG') == 'True':
            r = connection_cache()
            value = r.get("/status/{}".format(status_code))
            if value:
                app.logger.info("Hit /status/{}".format(status_code))
                return make_response(jsonify(json.loads(value)), 200)
            else:
                app.logger.info("Miss Hit /status/{}".format(status_code))
                r.set("/status/{}".format(status_code), json.dumps(data))
                return make_response(jsonify(data), status_code)
        else:
            return make_response(jsonify(data), status_code)
    else:
        return make_response(jsonify(err="Not status code"), 400)

@app.route('/<int:sleep_time>/<int:status_code>/query', methods=HTTP_METHODS)
def index_query(sleep_time, status_code):
    if 100 <= status_code <= 599:
        data = {'sleep_time': sleep_time, 'status_code': status_code, 'output': str(query_params_dict)}
        if os.getenv('CACHE_FLAG') == 'True':
            r = connection_cache()
            query_params_dict = request.args.to_dict()
            value = r.get("{}/{}/query".format(sleep_time,status_code))
            if value:
                time.sleep(sleep_time)
                app.logger.info("Hit /{}/{}/query".format(sleep_time,status_code))
                return make_response(jsonify(json.loads(value)), 200)
            else:
                app.logger.info("Miss Hit /{}/{}/query".format(sleep_time,status_code))
                r.set("{}/{}/query".format(sleep_time,status_code), json.dumps(data))
                time.sleep(sleep_time)
                return make_response(jsonify(data), status_code)
        else:
            time.sleep(sleep_time)
            query_params_dict = request.args.to_dict()
        return make_response(jsonify(data), status_code)
    else:
        return make_response(jsonify(err="Not status code"), 400)


@app.route('/sleep/<int:sleep_time>/query', defaults={'status_code': 200}, methods=HTTP_METHODS)
def only_sleep_time_query(sleep_time, status_code):
    data = {'sleep_time': sleep_time, 'status_code': status_code, 'output': str(query_params_dict)}
    if os.getenv('CACHE_FLAG') == 'True':
        r = connection_cache()
        query_params_dict = request.args.to_dict()
        value = r.get("sleep/{}/query".format(sleep_time))
        if value:
            time.sleep(sleep_time)
            app.logger.info("Hit /sleep/{}/query".format(sleep_time))
            return make_response(jsonify(json.loads(value)), 200)
        else:
            app.logger.info("Miss Hit /sleep/{}/query".format(sleep_time))
            r.set("sleep/{}/query".format(sleep_time), json.dumps(data))
            time.sleep(sleep_time)
            return make_response(jsonify(data), status_code)
    return make_response(jsonify(data), status_code)


@app.route('/status/<int:status_code>/query', methods=HTTP_METHODS)
def only_status_code_query(status_code, sleep_time=0):
    data = {'sleep_time': sleep_time, 'status_code': status_code, 'output': str(query_params_dict)}
    if 100 <= status_code <= 599:
        if os.getenv('CACHE_FLAG') == 'True':
            r = connection_cache()
            query_params_dict = request.args.to_dict()
            value = r.get("status/{}/query".format(status_code))
            if value:
                app.logger.info("Hit /status/{}/query".format(status_code))
                return make_response(jsonify(json.loads(value)), 200)
            else:
                app.logger.info("Miss Hit /status/{}/query".format(status_code))
                r.set("status/{}/query".format(status_code), json.dumps(data))
                time.sleep(sleep_time)
                return make_response(jsonify(data), status_code)
    else:
        return make_response(jsonify(err="Not status code"), 400)

@app.route('/<path:path>', methods=HTTP_METHODS)
def custom_rule(path):
    yaml_file = get_yaml_file_path()
    file_flag=get_file_check(yaml_file,False)
    if file_flag==False:
        return make_response(404)
    path = '/' + path
    with open(yaml_file, "r") as yaml_file:
        yaml_data = yaml.safe_load(yaml_file)
    for i in range(len(yaml_data["custom_rule"])):
        if yaml_data["custom_rule"][i]["rule"]["path"] == path and yaml_data["custom_rule"][i]["rule"]["method"] == request.method:
            if response_body_pathx := yaml_data["custom_rule"][i]["rule"].get("response_body_path"):
                try:
                    # TODO: Corresponding Redis.
                    with open(response_body_pathx, "r") as response_body_file:
                        response_body = response_body_file.read()
                        if sleep_time := yaml_data["custom_rule"][i]["rule"].get("sleep_time"):
                            time.sleep(sleep_time)
                    return make_response(jsonify(response_body), yaml_data["custom_rule"][i]["rule"]["status_code"])
                except Exception as e:
                    app.logger.info(e)
                    return make_response(jsonify(status=500), 500)
    return make_response(jsonify(status=500), 500)

@app.route('/favicon.ico')
def favicon():
    return '', 204

@app.errorhandler(404)
def page_not_found(e):
    return make_response(404)

if __name__ == '__main__':
    yaml_file = get_yaml_file_path()
    file_flag=get_file_check(yaml_file,True)
    app.logger.info("file_flag: %s" % file_flag)
    if file_flag==True:
        config_check(yaml_file)
    if get_debug_flg() == 'True':
        app.run(host=host, port=port, debug=True)
    else:
        app.run(host=host, port=port)

