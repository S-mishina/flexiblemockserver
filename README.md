# introduction

This is a mock server used to verify the operation of service mesh tools. Service mesh tools refer to Istio, Linkerd, and Kuma.

## Usage

For use cases where you just want to check the operation of ServiceMesh, please click here.

* Clsuter build and pure mockserver install
  * [Usage README](./sample_manifest/README.md)
    * Please click here to see the install for clusters.
Click here to use Open Telemetry

* OpenTelemetry + ServiceMesh
  * progressive delivery DEMO
    * flagger
      * [Usage README](./docs/flagger/README.md)
  * istio DEMO
    * [Usage README](./docs/istio/README.md)

## Example

Here are the environment variables for changing the port and endpoint of a Flask application:

* `HOST`: The host that the Flask application will use.
* `PORT`: The port on which the Flask application will run.

These environment variables allow you to customize the configuration of your Flask application as needed.

### default

#### GET sleep 1s status 200(/<sleep_time>/<status_code>)

```:terminal
❯ curl http://localhost:8080/1/200 -v
*   Trying 127.0.0.1:8080...
* Connected to localhost (127.0.0.1) port 8080 (#0)
> GET /1/200 HTTP/1.1
> Host: localhost:8080
> User-Agent: curl/7.88.1
> Accept: */*
>
< HTTP/1.1 200 OK
< Server: Werkzeug/2.3.4 Python/3.11.6
< Date: Tue, 28 Nov 2023 04:54:37 GMT
< Content-Type: application/json
< Content-Length: 35
< Connection: close
<
{"sleep_time":1,"status_code":200}
* Closing connection 0
```

#### GET status 200(/status/<status_code>)

```:terminal
❯ curl http://localhost:8080/status/200 -v
*   Trying 127.0.0.1:8080...
* Connected to localhost (127.0.0.1) port 8080 (#0)
> GET /status/200 HTTP/1.1
> Host: localhost:8080
> User-Agent: curl/7.88.1
> Accept: */*
>
< HTTP/1.1 200 OK
< Server: Werkzeug/2.3.4 Python/3.11.6
< Date: Tue, 28 Nov 2023 04:56:05 GMT
< Content-Type: application/json
< Content-Length: 35
< Connection: close
<
{"sleep_time":0,"status_code":200}
* Closing connection 0
```

#### GET sleep 1s(/sleep/<sleep_time>)

```:terminal
❯ curl http://localhost:8080/sleep/1/ -v
*   Trying 127.0.0.1:8080...
* Connected to localhost (127.0.0.1) port 8080 (#0)
> GET /sleep/1/ HTTP/1.1
> Host: localhost:8080
> User-Agent: curl/7.88.1
> Accept: */*
>
< HTTP/1.1 200 OK
< Server: Werkzeug/2.3.4 Python/3.11.6
< Date: Tue, 28 Nov 2023 04:57:37 GMT
< Content-Type: application/json
< Content-Length: 35
< Connection: close
<
{"sleep_time":1,"status_code":200}
* Closing connection 0
```

#### With query parameters

* /<sleep_time>/<status_code>/query
* /status/<status_code>/query
* /sleep/<sleep_time>/query

```:terminal
❯ curl "http://localhost:8080/1/200/query?aa=aa&bb=bb" -v
*   Trying 127.0.0.1:8080...
* Connected to localhost (127.0.0.1) port 8080 (#0)
> GET /1/200/query?aa=aa&bb=bb HTTP/1.1
> Host: localhost:8080
> User-Agent: curl/7.88.1
> Accept: */*
>
< HTTP/1.1 200 OK
< Server: Werkzeug/2.3.4 Python/3.11.6
< Date: Tue, 28 Nov 2023 05:02:28 GMT
< Content-Type: application/json
< Content-Length: 71
< Connection: close
<
{"output":"{'aa': 'aa', 'bb': 'bb'}","sleep_time":1,"status_code":200}
* Closing connection 0
```

### custom rule

You can load custom rules by setting the `CUSTOM_RULE_YAML_FILE` before running the flexiblemockserver.
By default, config/custom_rule.yaml is applied. The schema for custom_rule is as follows:

```json:custom_rule.yaml
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
```

```yaml:
custom_rule:
  - name: <rule_name> # string (Required)
    rule: # (Required)
        path: <path> # string (Required)
        method: <method> # string (Required)
        sleep_time: <sleep_time> # integer 0 ~ (Optional)
        status_code: <status_code> # integer 100 ~ 599 (Required)
        response_body_path: <response_body_path> # string (Optional)
```

* config/custom_rule.yaml

```terminal:config/custom_rule.yaml
custom_rule:
  - name: "Custom Rule"
    rule:
        path: "/example"
        method: "GET"
        status_code: 200
        response_body_path: "config/json/response1.json"
```

* config/json/response1.json

```terminal:config/custom_rule.yaml
{"response","Hello, World!"}
```

```terminal:
❯ curl http://127.0.0.1:8080/example -v
*   Trying 127.0.0.1:8080...
* Connected to 127.0.0.1 (127.0.0.1) port 8080 (#0)
> GET /example HTTP/1.1
> Host: 127.0.0.1:8080
> User-Agent: curl/7.84.0
> Accept: */*
>
* Mark bundle as not supporting multiuse
< HTTP/1.1 200 OK
< Server: Werkzeug/3.0.1 Python/3.11.7
< Date: Sun, 09 Jun 2024 10:21:14 GMT
< Content-Type: application/json
< Content-Length: 37
< Connection: close
<
"{\"response\",\"Hello, World!\"}\n"
* Closing connection 0
```

#### How to Execute

```terminal:
docker run -p 8080:8080 -e CUSTOM_RULE_YAML_FILE=/config/custom_rule.yaml ghcr.io/s-mishina/flexiblemockserver:latest
```
