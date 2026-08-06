# 🚀 Rocket Flight Simulator

Pythonで開発している、2次元ロケット飛行シミュレーション・解析ツールです。

ロケットの飛行を単純な放物運動として扱うのではなく、  
推力・燃料消費・重力・大気・空気抵抗などを考慮しながら、
時間ステップごとに機体状態を計算します。

計算結果はStreamlitを使用したWebダッシュボード上で、
飛行軌跡・各種グラフ・イベント・解析値として確認できます。

> 🚧 現在開発中のプロジェクトです。  
> 今後、風モデル、多段ロケット、機体分離、比較解析、軌道飛行などを追加予定です。

---

## 🎯 Project Goal

このプロジェクトでは、単にロケットを画面上で飛ばすことではなく、

**「入力条件 → 物理計算 → 飛行解析 → 可視化」**

までを一つのシステムとして構築することを目標としています。

また、機能追加を続けながら、

- オブジェクト指向設計
- 責務分離
- 保守性
- 拡張性
- データ可視化
- シミュレーション結果の検証

について学び、実践することも目的としています。

---

## ✨ Current Features

### 🚀 Flight Simulation

- 2次元飛行シミュレーション
- エンジン推力
- 発射角度
- 燃料消費
- 機体質量の変化
- 速度・加速度・位置計算

### 🌍 Environment / Physics

- 高度に応じた重力変化
- 標準大気モデル
- 気温
- 気圧
- 空気密度
- 音速
- 空気抵抗
- 動圧（Dynamic Pressure）

### 📊 Flight Analysis

- 最高高度
- 最高速度
- 最大Mach数
- Max Q
- 飛行時間
- 水平到達距離
- Mach 1突破判定

### 🛰️ Flight Events

飛行中の主要イベントを検出・記録します。

- Launch
- Mach 1
- Max Q
- Burnout
- Apogee
- Landing

### 🖥️ Dashboard

Streamlitを使用したWebダッシュボードを実装しています。

- シミュレーション条件入力
- 飛行サマリー
- 飛行軌跡
- 解析グラフ
- Flight Replay
- イベント表示
- CSV出力

---

## 🧮 Simulation Flow

シミュレーションでは、各時間ステップで機体状態を更新します。

```text
Rocket Configuration
        │
        ▼
Atmosphere / Gravity
        │
        ▼
Thrust / Drag
        │
        ▼
Resultant Force
        │
        ▼
Acceleration
        │
        ▼
Velocity
        │
        ▼
Position
        │
        ▼
Flight Analysis
        │
        ▼
Simulation Result
