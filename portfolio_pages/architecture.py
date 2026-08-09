import streamlit as st


st.title("🧩 System Architecture")

st.caption(
    "シミュレーション計算・推進・解析・記録・表示を、"
    "役割ごとに分離して実装しています。"
)


# ========================================
# 処理の流れ
# ========================================

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


# ========================================
# 主なクラス
# ========================================

st.header("Main Components")

components = [
    {
        "name": "RocketConfig",
        "role": (
            "機体構造質量・エンジン質量・ペイロード・"
            "燃料・最大推力・燃焼時間・発射角度などの入力条件を保持"
        ),
    },
    {
        "name": "EngineCalculator",
        "role": (
            "燃焼状態・推力曲線・推進剤流量・比推力・"
            "推力方向・燃料消費などの推進系計算を担当"
        ),
    },
    {
        "name": "PhysicsCalculator",
        "role": (
            "機体質量・重力・空気抵抗・合力・"
            "X/Y方向加速度を計算"
        ),
    },
    {
        "name": "AtmosphereCalculator",
        "role": (
            "高度から気温・気圧・空気密度・音速を計算"
        ),
    },
    {
        "name": "GravityCalculator",
        "role": (
            "高度に応じた重力加速度を計算"
        ),
    },
    {
        "name": "FlightAnalyzer",
        "role": (
            "Mach数・Max Q・音速突破などの飛行状態を解析"
        ),
    },
    {
        "name": "FlightEventManager",
        "role": (
            "Launch・Burnout・Mach 1・Max Q・"
            "Apogee・Landingなどのイベントを管理"
        ),
    },
    {
        "name": "SimulationRecorder",
        "role": (
            "各時刻の位置・速度・加速度・機体状態・"
            "推進性能を時系列データとして保存"
        ),
    },
    {
        "name": "SimulationResult",
        "role": (
            "シミュレーション結果をDashboard・"
            "Replay・CSVなどへ渡すデータモデル"
        ),
    },
    {
        "name": "Dashboard Visualizer",
        "role": (
            "Canvasを使用した軽量飛行リプレイと、"
            "ロケット・炎・煙・雲などの描画を担当"
        ),
    },
]

for component in components:
    with st.expander(
        component["name"]
    ):
        st.write(
            component["role"]
        )


# ========================================
# 責務の分離
# ========================================

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


# ========================================
# 設計方針
# ========================================

st.header("Design Policy")

design_columns = st.columns(3)

with design_columns[0]:
    st.subheader("責務分離")

    st.write(
        "推進・物理・環境・解析・記録・表示を"
        "別のクラスやモジュールへ分離しています。"
    )


with design_columns[1]:
    st.subheader("再利用性")

    st.write(
        "同じSimulationResultを、"
        "Dashboard・Replay・CSVなどから利用します。"
    )


with design_columns[2]:
    st.subheader("拡張性")

    st.write(
        "風・多段化・姿勢制御・軌道計算を、"
        "既存の責務を崩さず追加できる構成を目指しています。"
    )


# ========================================
# 今後の拡張イメージ
# ========================================

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