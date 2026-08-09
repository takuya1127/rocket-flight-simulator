import streamlit as st


st.title("🧩 System Architecture")

st.caption(
    "シミュレーション計算・推進・解析・記録・表示を、"
    "役割ごとに分離して実装しています。"
)

st.header("Processing Flow")

st.code(
    """
RocketConfig
    │
    ▼
rocket_simulation.py
    │
    ├── EngineCalculator
    │       ├── Thrust Curve
    │       ├── Mass Flow Rate
    │       ├── Specific Impulse
    │       └── Fuel Consumption
    │
    ├── PhysicsCalculator
    │       ├── Forces
    │       ├── Drag
    │       └── Acceleration
    │
    ├── AtmosphereCalculator
    ├── GravityCalculator
    ├── FlightAnalyzer
    ├── FlightEventManager
    └── SimulationRecorder
            │
            ▼
      SimulationResult
            │
            ├── Streamlit Dashboard
            ├── Canvas Flight Replay
            ├── Analysis Graphs
            └── CSV Export
    """,
    language="text",
)

st.header("Main Components")

components = [
    ("RocketConfig", "機体・燃料・最大推力・燃焼時間・発射角度などの入力条件を保持"),
    ("EngineCalculator", "燃焼状態・推力曲線・推進剤流量・比推力・燃料消費を担当"),
    ("PhysicsCalculator", "機体質量・重力・空気抵抗・合力・加速度を計算"),
    ("AtmosphereCalculator", "高度から気温・気圧・空気密度・音速を計算"),
    ("GravityCalculator", "高度に応じた重力加速度を計算"),
    ("FlightAnalyzer", "Mach数・Max Q・音速突破などを解析"),
    ("FlightEventManager", "Ignition・Launch・Burnout・Apogeeなどのイベントを管理"),
    ("SimulationRecorder", "位置・速度・加速度・機体状態・推進性能を時系列保存"),
    ("SimulationResult", "シミュレーション結果を各表示・出力へ渡す"),
    ("Dashboard Visualizer", "Canvas飛行リプレイと描画を担当"),
]

for name, role in components:
    with st.expander(name):
        st.write(role)

st.header("Responsibility Separation")

st.code(
    """
Input / Configuration
    RocketConfig

Propulsion
    EngineCalculator

Environment
    AtmosphereCalculator
    GravityCalculator

Flight Physics
    PhysicsCalculator

Analysis
    FlightAnalyzer
    FlightEventManager

Recording
    SimulationRecorder
    SimulationResult

Presentation
    Streamlit
    Dashboard Visualizer
    CSV Exporter
    """,
    language="text",
)

st.header("Future Extensions")

st.code(
    """
Current
    EngineCalculator
    PhysicsCalculator
    AtmosphereCalculator
    GravityCalculator

        │
        ▼

Future
    WindCalculator
    GuidanceController
    StageManager
    OrbitalCalculator
    Validation / Test Layer
    """,
    language="text",
)

st.info(
    "新機能をrocket_simulation.pyへ直接詰め込まず、"
    "役割ごとのモジュールとして追加する方針です。"
)
