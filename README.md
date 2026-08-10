# 🚀 Rocket Flight Simulator

Pythonで開発している、**2次元ロケット飛行シミュレーション・解析ツール**です。

ロケットの飛行を単純な放物運動として扱うのではなく、
推力・推進剤消費・機体質量・重力・大気・空気抵抗・風などを考慮しながら、
時間ステップごとに機体状態を計算します。

計算結果はStreamlitを使用したWebダッシュボード上で、
飛行軌跡・各種グラフ・飛行イベント・エンジン性能などとして確認できます。

> 🚧 **現在開発中のプロジェクトです。**
>
> Phase 4「Wind & Environment」まで実装済みです。  
> 次はPhase 5「Multi-stage Rocket」の実装を予定しています。

---

## 🎯 Project Goal

このプロジェクトでは、単にロケットを画面上で飛ばすのではなく、

**「入力条件 → 物理計算 → 状態記録 → 飛行解析 → 可視化」**

までを一つのシステムとして構築することを目標としています。

機能追加を続けながら、

- オブジェクト指向設計
- 責務分離
- モジュール分割
- 保守性
- 拡張性
- データ可視化
- シミュレーション結果の検証

について学び、実践することも目的としています。

---

# ✨ Current Features

## 🚀 Flight Simulation

- 2次元飛行シミュレーション
- X / Y方向の位置計算
- X / Y方向の速度計算
- X / Y方向の加速度計算
- 発射角度
- 推力計算
- 推進剤消費
- 機体質量変化
- 発射台待機判定
- リフトオフ判定
- 着地判定

---

## 🔥 Engine / Propulsion

エンジン性能を独立した計算処理として扱い、
時間経過に応じた推力と推進剤消費を計算します。

- Engine Performance Model
- Thrust Curve
- Propellant Mass Flow
- Specific Impulse
- Thrust-to-Weight Ratio
- Total Impulse
- Ignition Detection
- Burnout Detection
- Launch Pad Hold
- Liftoff Detection

### Thrust Curve

エンジン推力は常に一定ではなく、

1. 推力立ち上がり
2. 定常燃焼
3. 推力減衰
4. 燃焼終了

の状態を持つ簡易推力曲線としてモデル化しています。

---

## 🌍 Environment / Physics

- 高度に応じた重力変化
- 標準大気モデル
- 気温
- 気圧
- 空気密度
- 音速
- 空気抵抗
- 動圧（Dynamic Pressure）
- Mach数
- 一定風
- 高度依存風
- 2次元モデル上の横風
- 指定時間だけ発生する突風
- 相対風速を用いた空気抵抗計算

### Wind Model

風は速度と方向からX / Y成分へ分解し、
ロケットの地上速度との差から対気速度を計算します。

```text
Relative Air Velocity
    = Rocket Velocity - Wind Velocity
```

空気抵抗・動圧・Mach数は、
機体の地上速度ではなく**大気に対する相対速度**を基準として計算します。

現在の風モデルでは、

- 基準風速
- 風向
- 高度に応じた風速変化
- 突風追加風速
- 突風開始時刻
- 突風継続時間

を設定できます。

突風などの追加項目はStreamlitの **⚙️ 詳細設定** にまとめています。

---

## 📊 Flight Analysis

飛行結果から以下の値を解析します。

- 最高高度
- 最高速度
- 最大Mach数
- Max Q
- 飛行時間
- 水平到達距離
- Mach 1突破判定
- 最大推力
- 最大推進剤流量
- 比推力
- 最大推力重量比
- 総力積
- リフトオフ時刻

---

## 🛰️ Flight Events

飛行中の状態変化から主要イベントを検出・記録します。

- Ignition
- Launch
- Mach 1
- Max Q
- Burnout
- Apogee
- Landing

各イベントでは、発生時刻や高度などの飛行状態を記録し、
ダッシュボード上で確認できます。

---

## 🖥️ Dashboard

Streamlitを使用したWebダッシュボードを実装しています。

### Simulation

- ロケット条件入力
- 機体・エンジン・空力・風のカテゴリ別設定
- 詳細設定
- シミュレーション実行
- 飛行サマリー
- 飛行軌跡
- Flight Replay
- Flight Events

### Detailed Analysis

解析画面を複数カテゴリに分けて表示します。

- 運動解析
- 空力・環境
- 機体状態
- 推進性能

### Output

- 各種解析グラフ
- CSV出力
- シミュレーション結果表示

---

# 🧮 Simulation Flow

```text
Rocket Configuration
        │
        ▼
Atmosphere / Gravity
        │
        ▼
Wind Model
        │
        ▼
Engine / Thrust
        │
        ▼
Relative Air Velocity
        │
        ▼
Aerodynamic Drag
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
State Recording
        │
        ▼
Flight Analysis / Events
        │
        ▼
Simulation Result
```

---

# 🧩 Architecture

```text
Rocket Flight Simulator
│
├── core/
│   ├── atmosphere.py
│   ├── engine.py
│   ├── gravity.py
│   ├── physics_calculator.py
│   ├── rocket_simulation.py
│   └── wind.py
│
├── models/
│   └── simulation_models.py
│
├── analysis/
│   ├── flight_analysis.py
│   └── flight_event.py
│
├── recording/
│   ├── simulation_recorder.py
│   └── data_exporter.py
│
├── visualization/
│   ├── dashboard_visualizer.py
│   └── console_reporter.py
│
├── portfolio_pages/
│   ├── home.py
│   ├── simulation.py
│   ├── physics.py
│   ├── architecture.py
│   └── roadmap.py
│
├── assets/
├── tests/
└── streamlit_app.py
```

---

# 📐 Physics Models

## Gravity

```text
g(h) = g₀ × (R / (R + h))²
```

## Aerodynamic Drag

```text
D = 1/2 × ρ × Cd × A × Vrel²
```

風モデル導入後は、機体の地上速度ではなく
**相対風速と反対方向に空気抵抗が作用する**ようにしています。

## Dynamic Pressure

```text
q = 1/2 × ρ × Vrel²
```

## Specific Impulse

```text
Isp = F / (ṁ × g₀)
```

## Thrust-to-Weight Ratio

```text
TWR = F / (m × g)
```

## Total Impulse

```text
I = ∫ F(t) dt
```

---

# 🛠️ Technologies

- Python
- Streamlit
- Plotly
- Matplotlib
- Pandas
- Pillow
- Dataclasses
- Object-Oriented Programming
- Git / GitHub

---

# ⚠️ Current Limitations

- 実観測の風データ連携
- 3次元方向の風
- ランダム・確率的な乱気流
- 地球の自転
- 地球曲率を考慮した座標系
- 揚力
- 詳細な姿勢制御
- 高度・大気圧による詳細なエンジン性能変化
- 多段ロケット
- ブースター分離
- フェアリング分離
- 軌道力学
- 再突入時の加熱

---

# 🗺️ Development Roadmap

## ✅ Phase 1 — Basic Flight Simulation
**Status: Completed**

## ✅ Phase 2 — Analysis Dashboard
**Status: Completed**

## ✅ Phase 3 — Propulsion & Vehicle Performance
**Status: Completed**

## ✅ Phase 4 — Wind & Environment

- Constant Wind
- Wind Direction
- Altitude-dependent Wind
- 2D Crosswind
- Gust Model
- Relative Airspeed
- Wind Effects on Aerodynamic Drag
- Wind / Gust UI Settings
- Advanced Settings UI
- Wind Model Behavior Validation

**Status: Completed**

## 🚧 Phase 5 — Multi-stage Rocket

- Multi-stage Configuration
- Stage-specific Mass / Fuel / Engine
- Stage Separation
- Booster Separation
- Fairing Separation
- Mass Change after Separation
- Separation Events

**Status: Next**

## Phase 6 — Guidance & Flight Control
## Phase 7 — Comparative Analysis
## Phase 8 — Orbital Flight
## Phase 9 — Visualization & Presentation
## Phase 10 — Validation & Engineering Quality

---

# 🚀 Run Locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run streamlit_app.py
```

---

# 📌 Project Status

**Phase 4 Completed ✅**

現在は、

**Basic Flight Simulation → Analysis Dashboard → Propulsion / Vehicle Performance → Wind & Environment**

まで実装しています。

次のPhaseでは、**多段ロケット（Multi-stage Rocket）**へ進みます。
