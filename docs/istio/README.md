# istio sandbox

## Istioとは？

istioとは、ざっくり説明すると数あるサービスメッシュツールのうちの1つです。

公式のサイトには、以下のように書かれています。

サービスメッシュは、アプリケーションにゼロトラストセキュリティ、可観測性、高度なトラフィック管理などの機能をコード変更なしで提供するインフラストラクチャ層です。Istioは最も人気があり、強力で信頼されているサービスメッシュです。Istioは2016年にGoogle、IBM、Lyftによって設立され、KubernetesやPrometheusのようなプロジェクトと並んでCloud Native Computing Foundationの卒業プロジェクトです。

> A service mesh is an infrastructure layer that gives applications capabilities like zero-trust security, observability, and advanced traffic management, without code changes. Istio is the most popular, powerful, and trusted service mesh. Founded by Google, IBM and Lyft in 2016, Istio is a graduated project in the Cloud Native Computing Foundation alongside projects like Kubernetes and Prometheus.

ref: https://istio.io/latest/about/service-mesh/#what-is-istio

![Istioの構成](../image/4.svg)

ref: https://istio.io/latest/about/service-mesh/

サービスメッシュの該当でも解説したことと重複するところもありますが、
Istioは、Istio Control Planeによって通信の設定が追加、更新、削除されると、連携しているプロキシ設定を注入することができます。

また、Istio Control Planeは通信制御の設定の注入だけでなく、証明書管理やトラフィックの監視も行います。

これにより、Istioはマイクロサービス間の通信を効率的かつセキュアに管理することができます。

### もう少しわかりやすく図を書くと...

#### Discovery

TUB

#### Configuration

![Configuration](../image/5.png)

日本語の図に直すとこんな形になります。

開発者がサービスメッシュに関わる設定をapplyするとIstio Control Planeがクラスター内に無数にあるproxyに対して、設定を追加、更新、削除を行なってくれるということです。

#### certificates

TUB

## Istioで提供されるproxyについて

### アンビエントメッシュ

### サイドカーモード

TUB

### アンビエントモード

TUB

## 各機能の検証

### Gateway-API

[Gateway-APIの検証](./VirtualService/README.md)

### VirtualService

[VirtualServiceの検証](./VirtualService/README.md)

### DestinationRule

[DestinationRuleの検証](./DestinationRule/README.md)
