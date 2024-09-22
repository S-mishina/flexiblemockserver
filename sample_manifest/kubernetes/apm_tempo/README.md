# introduction

This README summarizes how to use grafana tempo with Kubernetes.

## Step1: GrafanaTempo Install

### 1.1. [cert-manager](https://cert-manager.io/docs/installation/#default-static-install) Install

Execute the following command

```:terminal
❯ kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.15.3/cert-manager.yaml
```

### 1.2. GrafanaTempo Operator Install

```:terminal
❯ kubectl apply -f https://github.com/grafana/tempo-operator/releases/latest/download/tempo-operator.yaml
```

### 1.3. [MinIO](https://min.io/)Install

Execute the following command

```:terminal
❯ kubectl apply -f https://raw.githubusercontent.com/grafana/tempo-operator/main/minio.yaml
```

### 1.4. Install TempoCR

Execute the following command

```:terminal
❯ kubectl apply -k sample_manifest/kubernetes/apm_tempo/tempo/
```

## Step2: OpenTelemetry Controller Install

TBU(Can work without install)

Execute the following command

### 2.1. OpenTelemetry Operator Install

```:terminal
kubectl apply -f https://github.com/open-telemetry/opentelemetry-operator/releases/latest/download/opentelemetry-operator.yaml
```

### 2.2. Install OpenTelemetry Collector Configuration

```:terminal
kubectl apply -f otel-controller/config.yaml
```

## Step3: Grafana Install

## Step4: Prometheus Install

Execute the following command

```:terminal

```

## Step5: operation check

Execute the following command

```:terminal
❯ kubectl apply -k sample_manifest/kubernetes/apm_tempo/flexiblemockserver/
```

```:terminal
❯ curl http://localhost:8081/sleep/1 -v
*   Trying [::1]:8081...
* Connected to localhost (::1) port 8081
> GET /sleep/1 HTTP/1.1
> Host: localhost:8081
> User-Agent: curl/8.4.0
> Accept: */*
>
< HTTP/1.1 200 OK
< Server: Werkzeug/3.0.3 Python/3.12.6
< Date: Tue, 17 Sep 2024 05:46:55 GMT
< Content-Type: application/json
< Content-Length: 35
< Connection: close
<
{"sleep_time":1,"status_code":200}
* Closing connection
```

![image](./image/image.png)
