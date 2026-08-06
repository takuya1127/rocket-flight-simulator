# 🚀 Rocket Flight Simulator

Pythonで開発している、2次元ロケット飛行シミュレーション・解析ツールです。

ロケットの飛行を単純な放物運動として扱うのではなく、  
推力・燃料消費・重力・大気・空気抵抗などを考慮しながら、
時間ステップごとに機体状態を計算します。

計算結果はStreamlitを使用したWebダッシュボード上で、
飛行軌跡・各種グラフ・イベント・解析値として確認できます。

> 🚧 **現在開発中のプロジェクトです。**  
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
```

計算結果はダッシュボード、グラフ、CSVなどの
複数の出力処理から利用できる構成にしています。

---

## 🧩 Architecture

計算・解析・記録・表示処理を分離し、
それぞれの責務を明確にすることを意識して設計しています。

```text
RocketConfig
    │
    ▼
Simulation Engine
    │
    ├── AtmosphereCalculator
    ├── GravityCalculator
    ├── PhysicsCalculator
    ├── FlightAnalyzer
    ├── FlightEventManager
    └── SimulationRecorder
    │
    ▼
SimulationResult
    │
    ├── Streamlit Dashboard
    ├── Analysis Graphs
    ├── Flight Replay
    └── CSV Export
```

今後モデルが複雑になっても、
既存コードへの影響をできるだけ小さくできる構成を目指しています。

---

## 🛠️ Technologies

- Python
- Streamlit
- Plotly
- Matplotlib
- Pandas
- Pillow
- Dataclasses
- Object-Oriented Programming

---

## 📐 Current Physics Models

### Gravity

高度に応じて重力加速度を変化させます。

```text
g(h) = g₀ × (R / (R + h))²
```

### Aerodynamic Drag

```text
D = 1/2 × ρ × Cd × A × v²
```

### Dynamic Pressure

```text
q = 1/2 × ρ × v²
```

大気密度と機体速度から動圧を計算し、
飛行中に最大となるMax Qを検出します。

---

## ⚠️ Current Limitations

現在は開発途中のため、実際のロケット飛行に存在する
すべての物理現象を再現しているわけではありません。

現在、主に以下の要素を簡略化または未実装としています。

- 風・突風
- 地球の自転
- 地球曲率を考慮した座標系
- 揚力
- 詳細な姿勢制御
- エンジン推力の時間変化
- 高度によるエンジン性能変化
- 多段ロケット
- ブースター・フェアリング分離
- 軌道力学
- 再突入時の加熱

これらは今後、段階的に追加していく予定です。

---

## 🗺️ Development Roadmap

### Phase 1 — Basic Flight Simulation

- [x] 2D Flight Simulation
- [x] Gravity
- [x] Atmosphere
- [x] Aerodynamic Drag
- [x] Fuel Consumption
- [x] Mach Number
- [x] Max Q
- [x] Flight Events

### Phase 2 — Analysis Dashboard

- [x] Streamlit Dashboard
- [x] Flight Summary
- [x] Analysis Graphs
- [x] CSV Export
- [x] Flight Replay

### Phase 3 — Vehicle Performance

- [ ] Specific Impulse
- [ ] Propellant Mass Flow
- [ ] Thrust Curve
- [ ] Engine Performance Model

### Phase 4 — Wind Model

- [ ] Constant Wind
- [ ] Altitude-dependent Wind
- [ ] Crosswind
- [ ] Gust Model

### Phase 5 — Multi-stage Rocket

- [ ] Multi-stage Configuration
- [ ] Stage Separation
- [ ] Booster Separation
- [ ] Fairing Separation

### Phase 6 — Comparative Analysis

- [ ] Multiple Simulation Comparison
- [ ] Trajectory Comparison
- [ ] Parameter Study

### Phase 7 — Orbital Flight

- [ ] Earth Curvature
- [ ] Gravity Turn
- [ ] Orbital Injection
- [ ] Orbital Mechanics

### Phase 8 — Visualization

- [ ] Improved Flight Animation
- [ ] Camera Tracking
- [ ] Altitude-dependent Background
- [ ] Improved Flame / Smoke Effects

---

## 🚀 Run Locally

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Start the Streamlit application

```bash
streamlit run streamlit_app.py
```

ブラウザでRocket Flight Simulatorが起動します。

---

## 📌 Status

**Under Development 🚧**

現在も機能追加・物理モデルの改善・UI改善を継続しています。
