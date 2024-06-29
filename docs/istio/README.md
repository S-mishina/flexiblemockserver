# istio sandbox

## Istioとは？

istioとは、ざっくり説明すると数あるサービスメッシュツールのうちの1つです。

公式のサイトには、以下のように書かれています。

サービスメッシュは、アプリケーションにゼロトラストセキュリティ、可観測性、高度なトラフィック管理などの機能をコード変更なしで提供するインフラストラクチャ層です。Istioは最も人気があり、強力で信頼されているサービスメッシュです。Istioは2016年にGoogle、IBM、Lyftによって設立され、KubernetesやPrometheusのようなプロジェクトと並んでCloud Native Computing Foundationの卒業プロジェクトです。

> A service mesh is an infrastructure layer that gives applications capabilities like zero-trust security, observability, and advanced traffic management, without code changes. Istio is the most popular, powerful, and trusted service mesh. Founded by Google, IBM and Lyft in 2016, Istio is a graduated project in the Cloud Native Computing Foundation alongside projects like Kubernetes and Prometheus.

ref: [The Istio service mesh](https://istio.io/latest/about/service-mesh/#what-is-istio)

![Istioの構成](../image/4.svg)

ref: [The Istio service mesh](https://istio.io/latest/about/service-mesh/)

サービスメッシュの該当でも解説したことと重複するところもありますが、
Istioは、Istio Control Planeによって通信の設定が追加、更新、削除されると、連携しているプロキシ設定を注入することができます。

また、Istio Control Planeは通信制御の設定の注入だけでなく、証明書管理やトラフィックの監視も行います。

これにより、Istioはマイクロサービス間の通信を効率的かつセキュアに管理することができます。

### もう少しわかりやすく図を書くと

#### Discovery

![Discovery](../image/5.png)

Istioが有効化された状態でかつ、proxyがServiceに導入されることが有効化された状態で新規サービスをKubernetes上に構築すると、Istio Control Planeによって新しいサービスに自動的にProxyが注入されます。

ref: [Use discovery selectors to configure namespaces for your Istio service mesh](https://istio.io/latest/blog/2021/discovery-selectors/)

#### Configuration

![Configuration](../image/6.png)

開発者がサービスメッシュに関わる設定をapplyするとIstio Control Planeがクラスター内に無数にあるproxyに対して、設定を追加、更新、削除を行なってくれるということです。

#### Security

自分もあまりIstioのcertificatesの部分について詳しくはないのでこのドキュメントあたりが参考になると思うので貼っておきます。

ref: [Security](https://istio.io/latest/docs/concepts/security/)

## Istioで提供されるProxyについて

Istioで提供されるProxyはEnvoyをベースに作られています。

ドキュメントには以下のように書かれています。

最初から、IstioはLyftによって初めて構築された高性能サービスプロキシであるEnvoyプロキシによって駆動されてきました。IstioはEnvoyを採用した最初のプロジェクトであり、Istioチームは最初の外部コミッターでした。Envoyはその後、Google Cloudを支えるロードバランサーおよびほぼすべての他のサービスメッシュプラットフォームのプロキシとなりました。

Istioは、Envoyのすべてのパワーと柔軟性を引き継ぎ、Istioチームによって開発されたWebAssemblyを使用した世界クラスの拡張性を備えています。

> From the beginning, Istio has been powered by the Envoy proxy, a high performance service proxy initially built by Lyft. Istio was the first project to adopt Envoy, and the Istio team were the first external committers. Envoy would go on to become the load balancer that powers Google Cloud as well as the proxy for almost every other service mesh platform.

Istio inherits all the power and flexibility of Envoy, including world-class extensibility using WebAssembly that was developed in Envoy by the Istio team.

ref: [The Envoy proxy](https://istio.io/latest/docs/overview/why-choose-istio/#envoy)

基本的にIstioとはEnvoyの設定を抽象化したものであり、開発者がEnvoyのconfigを簡略化されたCRDを書いてそれをKubernetes clusterにapplyすると、それをIstio Control Planeが解釈してProxy(Envoy)に設定を注入します。

なので、IstioにおけるProxy(Istio-Proxy)とはすなわちEnvoyだと思っていただいて問題ないと思います。

## Istioで提供されるproxyモードについて

### サイドカーモード

ドキュメントには以下のように書かれています。

クラスター内で起動する各ポッドと一緒にEnvoyプロキシが展開されるか、またはVM上で稼働するサービスの横で実行されます。

> which deploys an Envoy proxy along with each pod that you start in your cluster, or running alongside services running on VMs.

ref: [How it works(sidecar mode)](https://istio.io/latest/docs/overview/what-is-istio/#how-it-works)

### アンビエントモード

ドキュメントには以下のように書かれています。

各ノードにLayer 4プロキシを使用し、オプションで各ネームスペースにLayer 7機能を持つEnvoyプロキシを使用します。

> which uses a per-node Layer 4 proxy, and optionally a per-namespace Envoy proxy for Layer 7 features.

ref: [How it works(ambient mode)](https://istio.io/latest/docs/overview/what-is-istio/#how-it-works)

#### 補足の解説

TUB

## 各機能の検証

### Gateway-API

[Gateway-APIの検証](./VirtualService/README.md)

### VirtualService

[VirtualServiceの検証](./VirtualService/README.md)

### DestinationRule

[DestinationRuleの検証](./DestinationRule/README.md)
