# introduction

This README summarizes how to use grafana tempo with Kubernetes.

## Step1: GrafanaTempo Install

### 1.1. [cert-manager](https://cert-manager.io/docs/installation/#default-static-install) Install

Execute the following command

```:terminal
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.15.3/cert-manager.yaml
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

```:terminal

```

## Step3: Grafana Install

Execute the following command

```:terminal
❯ kubectl apply -k grafana
```

## Step4: operation check

Execute the following command

```:terminal
❯ kubectl apply -k sample_manifest/kubernetes/apm_tempo/flexiblemockserver/
```
