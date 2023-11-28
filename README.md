# introduction

Mock server that can change status code and response time

## usage rules

* docker

```:terminal
docker run -p 8080:8080 ghcr.io/s-mishina/flexiblemockserver:latest
```

## Example

### GET sleep 1s status 200(/<sleep_time>/<status_code>)

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

### GET status 200(/status/<status_code>)

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

### GET sleep 1s(/sleep/<sleep_time>)

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

### With query parameters

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
