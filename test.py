# app.py
from flask import Flask
import time
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor

app = Flask(__name__)

# OpenTelemetry Tracing setup
trace.set_tracer_provider(TracerProvider())
tracer = trace.get_tracer(__name__)

# Setup OTLP exporter to send traces to OpenTelemetry Collector
otlp_exporter = OTLPSpanExporter(endpoint="localhost:4317", insecure=True)
span_processor = BatchSpanProcessor(otlp_exporter)
trace.get_tracer_provider().add_span_processor(span_processor)

# Instrument Flask and HTTP requests
FlaskInstrumentor().instrument_app(app)
RequestsInstrumentor().instrument()

@app.route("/")
def hello_world():
    with tracer.start_as_current_span("hello-world-span"):
        time.sleep(0.1)  # Simulate some processing time
        return "Hello, World!"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)

