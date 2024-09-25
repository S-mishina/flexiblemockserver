# progressive deliveryの動きを確認してみる(Flagger編)

## 概要

このページではprogressive deliveryの動きを目で見て確認しようというものになります。
このドキュメントでは、Flaggerをベースに解説します。



## 前提

Flaggerの動作確認はistioをベースに動作させます。

> [!NOTE]
> こちらのドキュメントを参考に全ての手順を踏んでから実施してください。(サービスメッシュの概要)
> <br> ref: [link](../README.md)

## progressive deliveryとは？

TBU

ref: [link](https://docs.flagger.app/usage/deployment-strategies#canary-release)

### flaggerのInstall

```:terminal
❯ kubectl apply -k sample_manifest/kubernetes/flagger/
```

ref: [link](https://docs.flagger.app/usage/deployment-strategies#canary-release)

### flaggerを動作確認するためのmock serverを用意する

```:terminal
❯ kubectl apply -f https://raw.githubusercontent.com/fluxcd/flagger/main/artifacts/flagger/crd.yaml
```

```:terminal
❯ kubectl apply -k sample_manifest/kubernetes/flagger/canary-test-flexiblemockserver
```

### 実際に動作させてみよう

#### 成功パターン

labelに差分を入れて、動作を確認してみる。

```:terminal
TBU
```

```:terminal
❯ kubectl apply -k sample_manifest/kubernetes/flagger/canary-test-flexiblemockserver
```

実際にapplicationが実行されたら、負荷試験ツールを用いてリクエストを流してみる。

```:terminal
❯ kubectl apply -k sample_manifest/kubernetes/locust/sample/
```

開始

```:terminal

```

実行中

```:terminal

```

終了

```:terminal

```

試験が終わったら`locust`を削除しましょう。

```:terminal
❯ kubectl delete -k sample_manifest/kubernetes/locust/sample/
```

#### 失敗パターン

```:terminal
❯ kubectl apply -k sample_manifest/kubernetes/locust/sample/
```

開始

```:terminal

```

実行中

```:terminal

```

終了

```:terminal

```

試験が終わったら`locust`を削除しましょう。

```:terminal
❯ kubectl delete -k sample_manifest/kubernetes/locust/sample/
```

### tips
