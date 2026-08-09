# 🚀 Rocket Flight Simulator

Pythonで開発している、**2次元ロケット飛行シミュレーション・解析ツール**です。

ロケットの飛行を単純な放物運動として扱うのではなく、  
推力・推進剤消費・機体質量・重力・大気・空気抵抗などを考慮しながら、
時間ステップごとに機体状態を計算します。

計算結果はStreamlitを使用したWebダッシュボード上で、
飛行軌跡・各種グラフ・飛行イベント・エンジン性能などとして確認できます。

> 🚧 **現在開発中のプロジェクトです。**
>
> Phase 3「推進・機体性能」まで実装済みです。  
> 今後は風モデル、多段ロケット、比較解析、軌道飛行などへ拡張予定です。

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

シミュレーションでは、一定の時間ステップごとに
ロケットの状態を更新します。

```text
Rocket Configuration
        │
        ▼
Atmosphere / Gravity
        │
        ▼
Engine / Thrust
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

計算結果を直接UIへ依存させず、
記録・解析したデータを複数の出力処理から利用できる構成を目指しています。

---

# 🧩 Architecture

プロジェクトの規模拡大に合わせて、
計算・解析・記録・表示などの責務を分離しています。

```text
Rocket Flight Simulator
│
├── core/
│   ├── atmosphere.py
│   ├── engine.py
│   ├── gravity.py
│   ├── physics_calculator.py
│   └── rocket_simulation.py
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
│
├── tests/
│
└── streamlit_app.py
```

各ディレクトリは以下の責務を持ちます。

| Directory | Responsibility |
|---|---|
| `core` | シミュレーション・物理計算 |
| `models` | シミュレーションで使用するデータモデル |
| `analysis` | 飛行結果・イベント解析 |
| `recording` | 状態記録・データ出力 |
| `visualization` | グラフ・リプレイなどの可視化 |
| `portfolio_pages` | Streamlitの各ページ |
| `assets` | ロケット・炎・煙・雲などの画像 |
| `tests` | テストコード |

この構成により、今後モデルが複雑になっても、
既存コードへの影響をできるだけ小さくしながら機能追加できる設計を目指しています。

---

# 📐 Physics Models

## Gravity

高度に応じて重力加速度を変化させます。

```text
g(h) = g₀ × (R / (R + h))²
```

- `g₀` : 地表付近の重力加速度
- `R` : 地球半径
- `h` : 高度

---

## Aerodynamic Drag

空気抵抗は以下の式を基礎として計算します。

```text
D = 1/2 × ρ × Cd × A × v²
```

- `ρ` : 空気密度
- `Cd` : 抗力係数
- `A` : 基準面積
- `v` : 機体速度

---

## Dynamic Pressure

```text
q = 1/2 × ρ × v²
```

大気密度と機体速度から動圧を計算し、
飛行中に最大となる地点を **Max Q** として検出します。

---

## Specific Impulse

```text
Isp = F / (ṁ × g₀)
```

- `F` : 推力
- `ṁ` : 推進剤質量流量
- `g₀` : 標準重力加速度

エンジンが単位推進剤重量あたり、
どれだけ長く推力を発生できるかを表す指標として使用します。

---

## Thrust-to-Weight Ratio

```text
TWR = F / (m × g)
```

推力と機体重量の比率を計算します。

`TWR > 1` となり、その他の条件を満たした場合に
機体が発射台から離れる判定へ利用します。

---

## Total Impulse

```text
I = ∫ F(t) dt
```

時間変化する推力を飛行データから積算し、
エンジンが燃焼中に発生した総力積を求めます。

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

現在は開発途中のため、
実際のロケット飛行に存在するすべての物理現象を
再現しているわけではありません。

現在、主に以下の要素を簡略化または未実装としています。

- 風・突風
- 地球の自転
- 地球曲率を考慮した座標系
- 揚力
- 詳細な姿勢制御
- 高度による詳細なエンジン性能変化
- 多段ロケット
- ブースター分離
- フェアリング分離
- 軌道力学
- 再突入時の加熱

今後のPhaseで段階的に追加していく予定です。

---

# 🗺️ Development Roadmap

## ✅ Phase 1 — Basic Flight Simulation

- 2D Flight Simulation
- Gravity
- Atmosphere
- Aerodynamic Drag
- Fuel Consumption
- Mach Number
- Max Q
- Flight Events

**Status: Completed**

---

## ✅ Phase 2 — Analysis Dashboard

- Streamlit Dashboard
- Flight Summary
- Analysis Graphs
- CSV Export
- Flight Replay
- Detailed Analysis

**Status: Completed**

---

## ✅ Phase 3 — Propulsion & Vehicle Performance

- Engine Performance Model
- Thrust Curve
- Propellant Mass Flow
- Specific Impulse
- Thrust-to-Weight Ratio
- Total Impulse
- Ignition Event
- Launch Pad Hold
- Liftoff Detection
- Engine Performance Summary

**Status: Completed**

---

## 🚧 Phase 4 — Wind Model

- Constant Wind
- Altitude-dependent Wind
- Crosswind
- Gust Model
- Relative Airspeed
- Wind Effects on Aerodynamic Drag

**Status: Next**

---

## Phase 5 — Multi-stage Rocket

- Multi-stage Configuration
- Stage-specific Parameters
- Stage Separation
- Booster Separation
- Fairing Separation
- Mass Change after Separation

---

## Phase 6 — Comparative Analysis

- Multiple Simulation Comparison
- Trajectory Comparison
- Performance Comparison
- Parameter Study
- Simulation History

---

## Phase 7 — Orbital Flight

- Earth Curvature
- Gravity Turn
- Orbital Injection
- Orbital Velocity
- Orbital Mechanics

---

## Phase 8 — Visualization

- Improved Flight Animation
- Camera Tracking
- Altitude-dependent Background
- Improved Flame / Smoke Effects
- Additional Flight Visualization

---

# 🚀 Run Locally

## 1. Clone repository

```bash
git clone <repository-url>
cd rocket-flight-simulator
```

## 2. Create virtual environment

Windows:

```powershell
python -m venv .venv
```

## 3. Activate virtual environment

PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

## 4. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

## 5. Start application

```powershell
python -m streamlit run streamlit_app.py
```

ブラウザでRocket Flight Simulatorが起動します。

---

# 📌 Project Status

**Phase 3 Completed ✅**

現在は、

**Basic Flight Simulation → Analysis Dashboard → Propulsion / Vehicle Performance**

まで実装しています。

次のPhaseでは**風モデル（Wind Model）**を導入し、

```text
Ground Velocity
        +
Wind Velocity
        ↓
Relative Air Velocity
        ↓
Aerodynamic Drag
        ↓
Rocket Motion
```

という形で、機体速度だけではなく
**大気に対する相対速度を使用した空力計算**へ拡張していく予定です。

---

## 🚀 Future Goal

最終的には、

**機体設定 → エンジン → 大気 → 飛行 → 多段化 → 軌道投入 → 解析**

まで扱えるロケット飛行シミュレーターへの発展を目指します。