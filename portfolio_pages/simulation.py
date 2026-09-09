import streamlit as st

from portfolio_pages.components.simulation_settings import(
    render_simulation_settings,
)
from portfolio_pages.components.simulation_comparison import (
    render_comparison_simulation,
)
from portfolio_pages.components.simulation_results import (
    render_simulation_results,
)
from portfolio_pages.components.simulation_data import (
    create_event_dataframe,
    create_flight_dataframe,
)
from portfolio_pages.components.simulation_comparison_results import (
    render_comparison_results,
)

from core.rocket_simulation import simulate_rocket

# ========================================
# 補助関数
# ========================================

def is_mobile_device() -> bool:
    """
    ブラウザのUser-Agentからスマートフォンを簡易判定する。
    """

    user_agent = st.context.headers.get(
        "User-Agent",
        "",
    ).lower()

    mobile_keywords = (
        "iphone",
        "android",
        "mobile",
    )

    return any(
        keyword in user_agent
        for keyword in mobile_keywords
    )

# ========================================
# タイトル
# ========================================

st.title("🚀 Rocket Flight Simulator")

st.caption(
    "ロケットの2次元飛行を計算し、"
    "高度・速度・Mach・Max Q・燃料・推力などを解析します。"
)

#ロケット設定
base_config = render_simulation_settings()

# ========================================
# シミュレーションモード
# ========================================

st.header("🎯 シミュレーション")

st.caption(
    "現在のロケット設定を使って、"
    "単体または比較シミュレーションを実行します。"
)

single_tab, comparison_tab = st.tabs(
    [
        "▶️ 単体シミュレーション",
        "📊 比較シミュレーション",
    ]
)


with single_tab:

    st.write(
        "現在設定している条件で、"
        "1回の飛行シミュレーションを実行します。"
    )

    run_simulation = st.button(
        "🚀 シミュレーションを実行",
        type="primary",
        use_container_width=True,
        key="run_single_simulation",
    )

    if run_simulation:

        config = base_config

        with st.spinner(
            "シミュレーションを実行しています..."
        ):
            result = simulate_rocket(config)

        if result is None:

            st.error(
                "ロケットを打ち上げられませんでした。"
                "推力や発射角度を見直してください。"
            )

        else:

            st.session_state[
                "simulation_result"
            ] = result

            st.session_state[
                "rocket_config"
            ] = config

            st.session_state[
                "mobile_replay_index"
            ] = 0

            st.session_state[
                "mobile_replay_slider"
            ] = 0

            st.session_state[
                "mobile_replay_playing"
            ] = False

            st.success(
                "シミュレーションが完了しました。"
            )

    if "simulation_result" in st.session_state:

        result = st.session_state[
            "simulation_result"
        ]

        config = st.session_state[
            "rocket_config"
        ]

        flight_dataframe = (
            create_flight_dataframe(
                result
            )
        )

        event_dataframe = (
            create_event_dataframe(
                result
            )
        )

        mobile_mode = is_mobile_device()

        st.divider()

        render_simulation_results(
            result=result,
            config=config,
            flight_dataframe=flight_dataframe,
            event_dataframe=event_dataframe,
            mobile_mode=mobile_mode,
        )


with comparison_tab:

    render_comparison_simulation(
        base_config
    )

    if (
        "comparison_dataframe"
        in st.session_state
    ):

        st.divider()

        render_comparison_results()