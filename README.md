# 🚀 Rocket Flight Simulator

Pythonで開発している、**2次元ロケット飛行シミュレーション・解析ツール**です。

推力・推進剤消費・機体質量・重力・大気・空気抵抗・風を考慮しながら、
時間ステップごとにロケットの状態を計算します。

現在は、単段ロケットに加えて、**多段ロケット・ブースター・フェアリング分離**と、
**Guidance & Flight Control（姿勢誘導・重力ターン・簡易姿勢制御）**まで実装しています。

計算結果はStreamlitダッシュボード上で、
飛行軌跡・解析グラフ・飛行イベント・Flight Replayとして確認できます。

> 🚧 **現在開発中のプロジェクトです。**
>
> Phase 7「Comparative Analysis」まで実装済みです。
> 次はPhase 8「Orbital Flight」の開発に進みます。

---

## 🎯 Project Goal

このプロジェクトでは、

**入力条件 → 物理計算 → 状態更新 → 解析 → 可視化**

までを一つのシステムとして構築することを目標としています。

また、機能追加を通して以下を実践しています。

- オブジェクト指向設計
- 責務分離・モジュール分割
- 保守性・拡張性
- データ可視化
- シミュレーション結果の検証

---

## ✨ Current Features

### 🚀 Flight Simulation

- 2次元飛行シミュレーション
- 推力・重力・空気抵抗による運動計算
- 推進剤消費と機体質量変化
- 発射角度による推力方向計算
- 時間ベースの姿勢変更
- Pitch Program
- Gravity Turn
- Pitch Rate制限による簡易姿勢制御
- Liftoff / Apogee / Landing判定

### 🔥 Propulsion

- 推力曲線
- 推進剤流量
- 比推力（Isp）
- 推力重量比（T/W）
- 総力積
- Ignition / Burnout判定

### 🌍 Environment

- 高度に応じた重力変化
- 標準大気モデル
- 気温・気圧・空気密度・音速
- 動圧（Dynamic Pressure）
- Mach数
- 高度依存風
- 風向・横風
- 突風
- 相対風速を使用した空気抵抗

### 🧱 Multi-stage Rocket

- 単段 / 多段ロケット切り替え
- ステージごとの機体・エンジン設定
- ステージ分離
- ブースター分離
- フェアリング分離

### 📊 Flight Analysis

- 最高高度
- 最高速度
- 最大Mach数
- Max Q
- 飛行時間
- 水平到達距離
- 推力・推進剤流量・Isp・T/W
- 機体質量・燃料残量の推移
- 飛行角度・目標姿勢角・姿勢角の時系列解析

### 🔍 Comparative Analysis

- 複数条件の連続シミュレーション
- パラメータスイープ
- 比較結果テーブル
- ベスト条件の自動ハイライト
- 飛行軌跡比較
- 最高高度・最高速度・最大Mach数・飛行時間の性能比較
- 比較結果CSV出力

### 🖥️ Dashboard

- シミュレーション条件入力
- 飛行サマリー
- 飛行軌跡
- Flight Replay
- Flight Events
- 詳細解析グラフ
- CSV出力
- 単体 / 比較シミュレーションの分離表示

---

## 🧮 Simulation Flow

```text
Rocket Configuration
        ↓
Environment / Wind
        ↓
Engine / Booster
        ↓
Aerodynamic Drag
        ↓
Resultant Force
        ↓
Acceleration
        ↓
Velocity
        ↓
Position
        ↓
Stage / Separation State Update
        ↓
Analysis / Recording
        ↓
Simulation Result
```

---

## 🧩 Architecture

```text
Rocket Flight Simulator
│
├── core/
│   ├── atmosphere.py
│   ├── engine.py
│   ├── gravity.py
│   ├── guidance.py
│   ├── physics_calculator.py
│   ├── rocket_simulation.py
│   └── stage_manager.py
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

## 📐 Physics Models

### Gravity

```text
g(h) = g₀ × (R / (R + h))²
```

### Aerodynamic Drag

```text
D = 1/2 × ρ × Cd × A × v²
```

風が有効な場合は、大気に対する相対速度を使用します。

### Dynamic Pressure

```text
q = 1/2 × ρ × v²
```

### Specific Impulse

```text
Isp = F / (ṁ × g₀)
```

### Thrust-to-Weight Ratio

```text
T/W = F / (m × g)
```

---

## 🛠️ Technologies

- Python
- Streamlit
- Plotly
- Matplotlib
- Pandas
- Pillow
- Dataclasses
- Git / GitHub

---

## ⚠️ Current Limitations

現在は以下を簡略化、または未実装としています。

- 地球の自転
- 地球曲率を考慮した座標系
- 揚力
- 高度・大気圧による詳細なエンジン性能変化
- 分離物体の独立飛行
- 軌道力学
- 再突入時の加熱

---

## 🗺️ Development Roadmap

### ✅ Phase 1 — Basic Flight Simulation

- 2D Flight Simulation
- Gravity / Atmosphere
- Aerodynamic Drag
- Fuel Consumption
- Mach / Max Q
- Flight Events

### ✅ Phase 2 — Analysis Dashboard

- Streamlit Dashboard
- Flight Summary
- Analysis Graphs
- Flight Replay
- CSV Export

### ✅ Phase 3 — Propulsion & Vehicle Performance

- Engine Performance Model
- Thrust Curve
- Propellant Mass Flow
- Specific Impulse
- Thrust-to-Weight Ratio
- Total Impulse
- Liftoff Detection

### ✅ Phase 4 — Wind & Environment

- Altitude-dependent Wind
- Wind Direction / Crosswind
- Gust Model
- Relative Airspeed
- Wind Effects on Aerodynamic Drag

### ✅ Phase 5 — Multi-stage Rocket

- Multi-stage Configuration
- Stage-specific Vehicle / Engine Configuration
- Stage Separation
- Booster Separation
- Fairing Separation

### ✅ Phase 6 — Guidance & Flight Control

- Time-based Attitude Change
- Pitch Program
- Gravity Turn
- Dynamic Thrust Direction
- Basic Attitude Control
- Target Pitch / Actual Pitch Visualization

### ✅ Phase 7 — Comparative Analysis

- Multiple Simulation Comparison
- Parameter Sweep
- Comparison Result Table
- Best-condition Highlight
- Trajectory Comparison
- Performance Comparison
- Comparison CSV Export

### ⬜ Phase 8 — Orbital Flight

- Earth Curvature
- Earth-centered Coordinate System
- Orbital Velocity
- Orbital Injection
- Orbital Mechanics

### ⬜ Phase 9 — High-Fidelity Vehicle Model

- Altitude-dependent Engine Performance
- Detailed Aerodynamic Coefficients
- Lift / Angle of Attack
- Vehicle Geometry / Reference Area Changes
- More Detailed Mass Properties

### ⬜ Phase 10 — Environmental Disturbances

- Improved Atmospheric Model
- Realistic Wind Profile
- Turbulence / Gust Disturbances
- Earth Rotation Effects
- Environmental Uncertainty

### ⬜ Phase 11 — Validation & Engineering Quality

- Unit Tests
- Physics Validation
- Mass / Energy Checks
- Reproducibility Checks
- Comparison with Real Rockets

### ⬜ Phase 12 — Monte Carlo Simulation

- Large-scale Repeated Simulation
- Parameter Uncertainty
- Statistical Result Analysis
- Success Probability Estimation
- Result Distribution Visualization

### ⬜ Phase 13 — Automatic Optimization

- Automatic Parameter Search
- Guidance Parameter Optimization
- Vehicle Parameter Optimization
- Objective / Constraint Evaluation
- Space / Orbit Reachability Improvement

### ⬜ Phase 14 — Mission & Failure Analysis

- Mission Success Criteria
- Failure Scenario Modeling
- Sensitivity Analysis
- Reliability Evaluation
- Mission-level Performance Analysis

### ⬜ Phase 15 — Advanced Visualization

- Improved Camera Tracking
- Launch Pad / Ground Equipment
- Separation Animation
- Orbital Visualization
- Monte Carlo / Optimization Visualization

---

## 🚀 Run Locally

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run streamlit_app.py
```

---

## 📌 Project Status

**Phase 7 Completed ✅ / Phase 8 Next ⬜**

現在は、

```text
Basic Flight Simulation
        ↓
Analysis Dashboard
        ↓
Propulsion & Vehicle Performance
        ↓
Wind & Environment
        ↓
Multi-stage Rocket
        ↓
Guidance & Flight Control
        ↓
Comparative Analysis
```

まで実装しています。

Phase 7では、複数条件の連続実行、パラメータスイープ、
軌跡・性能比較、ベスト条件の自動抽出、比較結果CSV出力まで実装しました。

次は地球曲率・軌道速度・軌道投入を扱う
**Phase 8「Orbital Flight」** に進みます。

最終的には、高精度な機体・環境モデルと検証を経て、
Monte Carlo解析・自動最適化・ミッション／故障解析まで発展させ、
多数のシミュレーションから宇宙・軌道到達条件を探索できるシステムを目指します。
