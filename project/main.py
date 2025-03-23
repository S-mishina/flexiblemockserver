import os
import sys
import time
import yaml
from flask import Flask, jsonify, make_response, Response, request
from logging.config import dictConfig
from multiprocessing import Process
import math

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

import mysql.connector

def get_yaml_file_path():
    return os.getenv('CUSTOM_RULE_YAML_FILE', 'config/custom_rule.yaml')

def get_open_telemetry_flg():
    return os.getenv('OPEN_TELEMETRY_FLG', 'False')

def get_debug_flg():
    return os.getenv('DEBUG_FLG', 'False')

# def check_get_db_health():


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

def max_out_single_core(duration):
    start_time = time.time()
    while time.time() - start_time < duration:
        math.sqrt(123456789) * math.sqrt(987654321)

def multi_core_cpu_load(duration, core_count):
    processes = []
    for i in range(core_count):
        p = Process(target=max_out_single_core, args=(duration,))
        p.start()
        processes.append(p)
        print(f"Started process {i+1} to max out a core")

    for p in processes:
        p.join()
    print("All processes completed")

def resolve_value(item):
    return os.getenv(item["value"]) if item["type"] == "env" else item["value"]

def mysql_health(endpoint, id, passward, port):
    try:
        cnx = mysql.connector.connect(
            host=endpoint,
            port=port,
            user=id,
            password=passward)
        cur = cnx.cursor()
        cur.execute("SELECT 1")
        row = cur.fetchone()
        app.logger.info("resource:{}".format(row))
        cnx.close()
        return True
    except Exception as e:
        app.logger.info("error:{}".format(e))
        return False

def postgres_health():
    pass

def redis_health():
    pass

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
                    "name": { "type": "string" },
                    "rule": {
                        "type": "object",
                        "properties": {
                            "path": { "type": "string" },
                            "method": { "type": "string" },
                            "sleep_time": { "type": "integer", "minimum": 0 },
                            "status_code": {
                                "type": "integer",
                                "minimum": 100,
                                "maximum": 599,
                            },
                            "response_body_path": { "type": "string" },
                            "response_header": {
                                "type": "object",
                                "additionalProperties": { "type": "string" }
                            }
                        },
                        "required": ["path", "method", "status_code"],
                        "additionalProperties": False,
                    }
                },
                "required": ["name", "rule"],
                "additionalProperties": False,
            }
        },
        "health_check": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name": { "type": "string" },
                    "data_source": { "type": "string", "enum": ["mysql", "postgres", "redis"] },
                    "endpoint": {
                        "type": "object",
                        "properties": {
                            "type": { "type": "string", "enum": ["literal", "env"] },
                            "value": { "type": "string" }
                        },
                        "required": ["type", "value"],
                        "additionalProperties": False,
                    },
                    "id": {
                        "type": "object",
                        "properties": {
                            "type": { "type": "string", "enum": ["literal", "env"] },
                            "value": { "type": "string" }
                        },
                        "required": ["type", "value"],
                        "additionalProperties": False,
                    },
                    "pass": {
                        "type": "object",
                        "properties": {
                            "type": { "type": "string", "enum": ["literal", "env"] },
                            "value": { "type": "string" }
                        },
                        "required": ["type", "value"],
                        "additionalProperties": False,
                    }
                },
                "required": ["name", "data_source", "endpoint"],
                "additionalProperties": False,
            }
        }
    },
    "required": ["custom_rule"],
    "additionalProperties": False,
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

@app.route('/<int:duration>/<int:core>/max-cpu', methods=['GET'])
def max_cpu(duration,core):
    duration = float(request.args.get('duration', duration))
    core_count = int(request.args.get('cores', core))
    p = Process(target=multi_core_cpu_load, args=(duration, core_count))
    p.start()
    return jsonify({"message": f'{core}Core is used for {duration} seconds MAX'}), 200

@app.route('/<int:memory>/max-memory', methods=['GET'])
def max_memory(memory):
    data = bytearray(1024 * 1024 * memory)
    return jsonify({"message": f"{memory} MiB usage"}), 200

@app.route('/<int:storage>/max-storage', methods=['GET'])
def max_storage(storage):
    if storage <= 0:
        return make_response(jsonify(err="Invalid storage value"), 400)
    base_path = '/tmp'
    file_name = f'{storage}MB'
    file_path = os.path.normpath(os.path.join(base_path, file_name))
    if not file_path.startswith(base_path):
        return make_response(jsonify(err="Invalid file path"), 400)
    with open(file_path, 'wb') as f:
        f.write(bytearray(1024 * 1024 * storage))
    return jsonify({"message": f"{storage} MiB storage usage"}), 200

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
                    with open(response_body_pathx, "r") as response_body_file:
                        response_body = response_body_file.read()
                        if sleep_time := yaml_data["custom_rule"][i]["rule"].get("sleep_time"):
                            time.sleep(sleep_time)
                    return make_response(jsonify(response_body), yaml_data["custom_rule"][i]["rule"]["status_code"])
                except Exception as e:
                    app.logger.info(e)
                    return make_response(jsonify(status=500), 500)
    return make_response(jsonify(status=500), 500)

@app.route("/health", methods=['GET'])
def health():
    yaml_file = get_yaml_file_path()
    file_flag=get_file_check(yaml_file,False)
    if file_flag==False:
        return make_response(jsonify(status="ok"), 200)
    with open(yaml_file, "r") as yaml_file:
        yaml_data = yaml.safe_load(yaml_file)
        mysql_checks = [check for check in yaml_data['health_check'] if check.get('data_source') == 'mysql']
        if len(mysql_checks) > 0:
            for mysql_len in range(len(mysql_checks)):
                mysql_endpoint = resolve_value(mysql_checks[mysql_len]["endpoint"])
                mysql_id = resolve_value(mysql_checks[mysql_len]["id"])
                mysql_pass = resolve_value(mysql_checks[mysql_len]["pass"])
                mysql_response=mysql_health(mysql_endpoint, mysql_id, mysql_pass, 3306)
                if mysql_response==False:
                    return make_response(jsonify(mysql_status="ng"), 500)
    return make_response(jsonify(status="ok"), 200)

@app.route('/favicon.ico')
def favicon():
    return '', 204  # 空のレスポンスで204 No Contentを返す

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

