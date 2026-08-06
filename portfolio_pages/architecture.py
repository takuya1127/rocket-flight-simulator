import streamlit as st


st.title("🧩 System Architecture")

st.caption(
    "シミュレーション計算・解析・表示を、"
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
    ├── PhysicsCalculator
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
    ├── Plotly Flight Replay
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
        "role": "機体質量・燃料・推力・発射角度などの入力条件を保持",
    },
    {
        "name": "PhysicsCalculator",
        "role": "重力・大気・空気抵抗・合力・加速度を計算",
    },
    {
        "name": "AtmosphereCalculator",
        "role": "高度から気温・気圧・密度・音速を計算",
    },
    {
        "name": "GravityCalculator",
        "role": "高度に応じた重力加速度を計算",
    },
    {
        "name": "FlightAnalyzer",
        "role": "Mach数・Max Q・音速突破などを解析",
    },
    {
        "name": "FlightEventManager",
        "role": "Launch・Burnout・Apogee・Landingなどを管理",
    },
    {
        "name": "SimulationRecorder",
        "role": "各時刻の位置・速度・加速度・機体状態を保存",
    },
    {
        "name": "SimulationResult",
        "role": "計算結果をダッシュボードやCSVへ渡す",
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
# 設計方針
# ========================================

st.header("Design Policy")

design_columns = st.columns(3)

with design_columns[0]:
    st.subheader("責務分離")

    st.write(
        "計算・解析・記録・表示を"
        "別のクラスやモジュールへ分離。"
    )

with design_columns[1]:
    st.subheader("再利用性")

    st.write(
        "同じSimulationResultを、"
        "グラフ・CSV・Web画面で利用。"
    )

with design_columns[2]:
    st.subheader("拡張性")

    st.write(
        "風・多段化・軌道計算を、"
        "既存処理へ追加しやすい構成を目指す。"
    )