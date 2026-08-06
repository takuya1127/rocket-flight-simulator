import streamlit as st


# ========================================
# アプリ全体の設定
# ========================================

st.set_page_config(
    page_title="Rocket Flight Simulator",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ========================================
# ページ定義
# ========================================

home_page = st.Page(
    "portfolio_pages/home.py",
    title="Home",
    icon="🏠",
    default=True,
)

simulation_page = st.Page(
    "portfolio_pages/simulation.py",
    title="Simulation",
    icon="🚀",
)

physics_page = st.Page(
    "portfolio_pages/physics.py",
    title="Physics & Models",
    icon="📐",
)

architecture_page = st.Page(
    "portfolio_pages/architecture.py",
    title="Architecture",
    icon="🧩",
)

roadmap_page = st.Page(
    "portfolio_pages/roadmap.py",
    title="Roadmap",
    icon="🗺️",
)


# ========================================
# ナビゲーション
# ========================================

current_page = st.navigation(
    {
        "Rocket Flight Simulator": [
            home_page,
            simulation_page,
        ],
        "Technical Information": [
            physics_page,
            architecture_page,
        ],
        "Project": [
            roadmap_page,
        ],
    }
)


# 選択されたページを実行する
current_page.run()