# intro

## Docker

```:terminal
docker run -p 8080:8080 ghcr.io/s-mishina/flexiblemockserver:latest
```

Currently, it will not work unless the custom rule file exists.

## Docker-Compose

## Kubernetes

To use flexiblemockserver on Kubernetes, please follow the steps below.
This document describes how to use [kind](https://kind.sigs.k8s.io/).

### step 1

Create a cluster using kind.

sample command

```:terminal
flexiblemockserver/sample_manifest/kubernetes(ap-northeast-1)
❯ ls
cluster.yaml		flexiblemockserver
```

```:terminal
❯ kind create cluster -n sandbox-test --config sample_manifest/kubernetes/cluster.yaml
Creating cluster "sandbox-test" ...
 ✓ Ensuring node image (kindest/node:v1.27.3) 🖼
 ✓ Preparing nodes 📦 📦 📦 📦
 ✓ Writing configuration 📜
 ✓ Starting control-plane 🕹️
 ✓ Installing CNI 🔌
 ✓ Installing StorageClass 💾
 ✓ Joining worker nodes 🚜
Set kubectl context to "kind-sandbox-test"
You can now use your cluster with:

kubectl cluster-info --context kind-sandbox-test

Have a question, bug, or feature request? Let us know! https://kind.sigs.k8s.io/#community 🙂
```

### step 2

Please import the required IMAGE onto kind.

sample command

```:terminal
❯ docker pull ghcr.io/s-mishina/flexiblemockserver:latest
```

```:terminal
❯ kind load docker-image ghcr.io/s-mishina/flexiblemockserver:latest ghcr.io/s-mishina/flexiblemockserver:latest -n sandbox-test
Image: "ghcr.io/s-mishina/flexiblemockserver:latest" with ID "sha256:96b36be4d13881b2567a42662dd3a613649740348d0a360d0b686b7eb4c7798e" not yet present on node "sandbox-test-worker2", loading...
Image: "ghcr.io/s-mishina/flexiblemockserver:latest" with ID "sha256:96b36be4d13881b2567a42662dd3a613649740348d0a360d0b686b7eb4c7798e" not yet present on node "sandbox-test-worker3", loading...
Image: "ghcr.io/s-mishina/flexiblemockserver:latest" with ID "sha256:96b36be4d13881b2567a42662dd3a613649740348d0a360d0b686b7eb4c7798e" not yet present on node "sandbox-test-control-plane", loading...
Image: "ghcr.io/s-mishina/flexiblemockserver:latest" with ID "sha256:96b36be4d13881b2567a42662dd3a613649740348d0a360d0b686b7eb4c7798e" not yet present on node "sandbox-test-worker", loading...
```

### step 3

**If you want to use Open Telemetry, please refer to this document to install flexiblemockserver.** <br>
[link](./kubernetes/apm_tempo/README.md)

Finally, let's apply the manifest!

```:terminal
[kind-sandbox-test|default] :ctx
[arm64]⚡️
flexiblemockserver on  feature/sandbox-k8s-manifest

❯ kubectl apply -k sample_manifest/kubernetes/flexiblemockserver
namespace/mockserver created
configmap/custom-rule created
configmap/response created
service/flexiblemockserver created
deployment.apps/flexiblemockserver created
```

### as necessary

This document is intended to confirm the operation of ServiceMesh and Kuberneres.

The following custom operator

#### Reloader

[document](https://github.com/stakater/Reloader?tab=readme-ov-file#vanilla-manifests)

#### istio

[document](https://istio.io/latest/docs/setup/install/istioctl/)


