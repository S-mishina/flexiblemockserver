# progressive deliveryの動きを確認してみる(Flagger編)

## 概要

このページではprogressive deliveryの動きを目で見て確認しようというものになります。
このドキュメントでは、Flaggerをベースに解説します。

## 前提

Flaggerの動作確認はistioをベースに動作させます。

> [!NOTE]
> こちらのドキュメントを参考に全ての手順を踏んでから実施してください。
> <br> ref: [link](../../sample_manifest/kubernetes/apm_tempo/README.md)

## progressive deliveryとは？

TBU

ref: [link](https://docs.flagger.app/usage/deployment-strategies#canary-release)

### flaggerのInstall

```:terminal

```

ref: [link](https://docs.flagger.app/usage/deployment-strategies#canary-release)

### flaggerを動作確認するためのmock serverを用意する

```:terminal
❯ kubectl apply -k sample_manifest/kubernetes/flagger/
```

```:terminal
❯ kubectl apply -f https://raw.githubusercontent.com/fluxcd/flagger/main/artifacts/flagger/crd.yaml
```

ref: [link]()

### 実際に動作させてみよう

### 検証用のアプリのInstall

TBU

#### 成功パターン

TBU

#### 失敗パターン

TBU

### tips
