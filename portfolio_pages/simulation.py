import math

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from visualization.dashboard_visualizer import (
    create_flight_replay_html,
)
from models.simulation_models import RocketConfig
from core.rocket_simulation import simulate_rocket
from analysis.flight_event import FlightEventType


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



def create_flight_dataframe(
    result,
) -> pd.DataFrame:
    """
    SimulationResultから、
    表示・グラフ・CSV出力に使用するDataFrameを作成する。
    """

    total_speeds = [
        math.hypot(
            velocity_x,
            velocity_y,
        )
        for velocity_x, velocity_y in zip(
            result.velocities_x,
            result.velocities_y,
        )
    ]

    total_accelerations = [
        math.hypot(
            acceleration_x,
            acceleration_y,
        )
        for acceleration_x, acceleration_y in zip(
            result.accelerations_x,
            result.accelerations_y,
        )
    ]

    return pd.DataFrame(
        {
            "時刻（秒）": result.times,
            "X座標（m）": result.positions_x,
            "高度（m）": result.positions_y,
            "X方向速度（m/s）": result.velocities_x,
            "Y方向速度（m/s）": result.velocities_y,
            "合成速度（m/s）": total_speeds,
            "X方向加速度（m/s²）": result.accelerations_x,
            "Y方向加速度（m/s²）": result.accelerations_y,
            "合成加速度（m/s²）": total_accelerations,
            "飛行角度（度）": result.flight_angles,
            "動圧（kPa）": [
                pressure / 1000
                for pressure in result.dynamic_pressures
            ],
            "マッハ数": result.mach_numbers,
            "重力加速度（m/s²）": result.gravities,
            "総質量（kg）": result.total_masses,
            "燃料残量（kg）": result.remaining_fuels,
            "推力（N）": result.thrusts,
            "推進剤流量（kg/s）": result.mass_flow_rates,
            "比推力（s）": result.specific_impulses,
            "推力重量比": result.thrust_to_weight_ratios,
        }
    )


def create_event_dataframe(
    result,
) -> pd.DataFrame:
    """
    飛行イベントを表形式へ変換する。
    """

    return pd.DataFrame(
        [
            {
                "時刻（秒）": event.time,
                "イベント": event.event_type.value,
                "高度（m）": event.altitude,
                "説明": event.description,
            }
            for event in result.flight_events
        ]
    )


# ========================================
# タイトル
# ========================================

st.title("🚀 Rocket Flight Simulator")

st.caption(
    "ロケットの2次元飛行を計算し、"
    "高度・速度・Mach・Max Q・燃料・推力などを解析します。"
)


# ========================================
# サイドバー：入力設定
# ========================================

with st.sidebar:
    st.header("ロケット設定")

    st.markdown("### 🚀 機体設定")
    structure_mass = st.number_input(
        "機体構造質量(kg)",
        min_value=0.1,
        value=70.0,
        step=5.0,
    )

    engine_mass = st.number_input(
        "エンジン質量(kg)",
        min_value=0.1,
        value=20.0,
        step=5.0,
    )

    payload_mass = st.number_input(
        "ペイロード質量(kg)",
        min_value=0.0,
        value=10.0,
        step=5.0,
    )

    fuel_mass = st.number_input(
        "燃料質量(kg)",
        min_value=0.1,
        value=50.0,
        step=5.0,
    )

    dry_mass  = (
        structure_mass + engine_mass + payload_mass
    )

    initial_total_mass = (
        dry_mass + fuel_mass
    )

    st.caption(f"乾燥質量:{dry_mass:.1f}kg")
    st.caption(f"初期総質量:{initial_total_mass:.1f}kg")

    st.markdown("### 🔥 エンジン設定")
    thrust = st.number_input(
        "エンジン推力（N）",
        min_value=0.1,
        value=5000.0,
        step=500.0,
    )

    burn_time = st.number_input(
        "燃焼時間（秒）",
        min_value=0.1,
        value=25.0,
        step=1.0,
    )

    launch_angle = st.slider(
        "発射角度（度）",
        min_value=1.0,
        max_value=90.0,
        value=75.0,
        step=1.0,
    )

    st.markdown("### 🌍 空力設定")
    drag_coefficient = st.number_input(
        "抗力係数",
        min_value=0.01,
        value=0.50,
        step=0.05,
    )

    reference_area = st.number_input(
        "基準断面積（m²）",
        min_value=0.001,
        value=0.20,
        step=0.01,
        format="%.3f",
    )

    st.markdown("### 🌬️ 風設定")
    wind_speed = st.number_input(
        "風速（m/s）",
        min_value=0.0,
        max_value=100.0,
        value=5.0,
        step=1.0,
    )

    wind_direction_deg = st.slider(
        "風向（度）",
        min_value=0,
        max_value=359,
        value=0,
        step=1,
    )

    with st.expander(
        "⚙️ 詳細設定",
        expanded=False,
    ):
        gust_speed = st.number_input(
            "突風追加風速（m/s）",
            min_value=0.0,
            max_value=100.0,
            value=0.0,
            step=1.0,
        )

        gust_start_time = st.number_input(
            "突風開始時刻（秒）",
            min_value=0.0,
            max_value=300.0,
            value=15.0,
            step=1.0,
        )

        gust_duration = st.number_input(
            "突風継続時間（秒）",
            min_value=0.0,
            max_value=60.0,
            value=5.0,
            step=1.0,
        )

    run_simulation = st.button(
        "シミュレーション実行",
        type="primary",
        use_container_width=True,
    )


# ========================================
# シミュレーション実行
# ========================================

if run_simulation:
    config = RocketConfig(
        structure_mass=structure_mass,
        engine_mass=engine_mass,
        payload_mass=payload_mass,
        fuel_mass=fuel_mass,
        thrust=thrust,
        burn_time=burn_time,
        launch_angle=launch_angle,
        drag_coefficient=drag_coefficient,
        reference_area=reference_area,
        wind_speed=wind_speed,
        wind_direction_deg=wind_direction_deg,
        gust_speed=gust_speed,
        gust_start_time=gust_start_time,
        gust_duration=gust_duration,
    )

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
        # Streamlitは操作ごとにプログラムを再実行するため、
        # 結果をsession_stateへ保存する
        st.session_state["simulation_result"] = result
        st.session_state["rocket_config"] = config

        # 新しいシミュレーション結果ではスマホリプレイを先頭へ戻す
        st.session_state["mobile_replay_index"] = 0
        st.session_state["mobile_replay_slider"] = 0
        st.session_state["mobile_replay_playing"] = False

        st.success(
            "シミュレーションが完了しました。"
        )


# ========================================
# 結果表示
# ========================================

if "simulation_result" not in st.session_state:
    st.info(
        "左側でロケットの条件を入力し、"
        "「シミュレーション実行」を押してください。"
    )

    st.stop()


result = st.session_state["simulation_result"]
config = st.session_state["rocket_config"]

flight_dataframe = create_flight_dataframe(
    result
)

event_dataframe = create_event_dataframe(
    result
)


# ========================================
# 飛行サマリー
# ========================================

st.header("飛行サマリー")

summary_columns = st.columns(4)

summary_columns[0].metric(
    label="最高高度",
    value=f"{result.max_altitude / 1000:.2f} km",
)

summary_columns[1].metric(
    label="最高速度",
    value=f"{result.max_velocity:.1f} m/s",
)

summary_columns[2].metric(
    label="最大Mach",
    value=f"Mach {result.max_mach_number:.2f}",
)

summary_columns[3].metric(
    label="Max Q",
    value=(
        f"{result.max_dynamic_pressure / 1000:.2f} kPa"
    ),
)

summary_columns = st.columns(4)

summary_columns[0].metric(
    label="飛行時間",
    value=f"{result.flight_time:.1f} 秒",
)

summary_columns[1].metric(
    label="水平到達距離",
    value=(
        f"{max(result.positions_x) / 1000:.2f} km"
    ),
)

summary_columns[2].metric(
    label="初期総質量",
    value=(
        f"{config.initial_total_mass:.1f} kg"
    ),
)

summary_columns[3].metric(
    label="燃焼時間",
    value=f"{config.burn_time:.1f} 秒",
)


# ========================================
# 飛行軌跡とイベント
# ========================================

st.header("飛行概要")
trajectory_column, event_column = st.columns(
    [2, 1]
)

with trajectory_column:
    st.subheader("飛行リプレイ")

    # PC / スマホとも同じCanvasエンジンを使用する。
    # Plotlyの大量フレームをブラウザへ送らないため、
    # MessageSizeErrorと再生負荷を大幅に抑えられる。
    mobile_mode = is_mobile_device()

    replay_html = create_flight_replay_html(
        result,
        mobile_mode=mobile_mode,
    )

    components.html(
        replay_html,
        height=390 if mobile_mode else 610,
        scrolling=False,
    )

with event_column:
    st.subheader("イベントタイムライン")

    if event_dataframe.empty:
        st.info(
            "イベントは記録されていません。"
        )
    else:
        for event in result.flight_events:
            st.markdown(
                f"""
                **T+{event.time:.1f}s — {event.event_type.value}**

                高度：{event.altitude:.1f}m

                {event.description}
                """
            )

            st.divider()


# ========================================
# 解析グラフ
# ========================================

st.header("詳細解析")
tab_motion, tab_aero, tab_vehicle, tab_propulsion = st.tabs(
    [
        "運動解析",
        "空力・環境",
        "機体状態",
        "推進性能",
    ]
)


# ========================================
# 運動解析
# ========================================

with tab_motion:
    st.subheader("高度")
    st.line_chart(
        flight_dataframe.set_index(
            "時刻（秒）"
        )[
            [
                "高度（m）",
            ]
        ],
        height=320,
    )

    st.subheader("速度")
    st.line_chart(
        flight_dataframe.set_index(
            "時刻（秒）"
        )[
            [
                "X方向速度（m/s）",
                "Y方向速度（m/s）",
                "合成速度（m/s）",
            ]
        ],
        height=320,
    )

    st.subheader("加速度")
    st.line_chart(
        flight_dataframe.set_index(
            "時刻（秒）"
        )[
            [
                "X方向加速度（m/s²）",
                "Y方向加速度（m/s²）",
                "合成加速度（m/s²）",
            ]
        ],
        height=320,
    )


# ========================================
# 空力・環境解析
# ========================================

with tab_aero:
    st.subheader("動圧")
    st.line_chart(
        flight_dataframe.set_index(
            "時刻（秒）"
        )[
            [
                "動圧（kPa）",
            ]
        ],
        height=320,
    )

    st.subheader("マッハ数")
    st.line_chart(
        flight_dataframe.set_index(
            "時刻（秒）"
        )[
            [
                "マッハ数",
            ]
        ],
        height=320,
    )

    st.subheader("重力加速度")
    st.line_chart(
        flight_dataframe.set_index(
            "時刻（秒）"
        )[
            [
                "重力加速度（m/s²）",
            ]
        ],
        height=320,
    )


# ========================================
# 機体状態
# ========================================

with tab_vehicle:
    st.subheader("燃料残量・総質量")
    st.line_chart(
        flight_dataframe.set_index(
            "時刻（秒）"
        )[
            [
                "総質量（kg）",
                "燃料残量（kg）",
            ]
        ],
        height=320,
    )

# ========================================
# 推進性能
# ========================================

with tab_propulsion:

    # ========================================
    # エンジン性能サマリー
    # ========================================

    st.subheader("エンジン性能サマリー")

    max_thrust = max(
        result.thrusts,
        default=0.0,
    )

    max_mass_flow_rate = max(
        result.mass_flow_rates,
        default=0.0,
    )

    max_specific_impulse = max(
        result.specific_impulses,
        default=0.0,
    )

    max_thrust_to_weight_ratio = max(
        result.thrust_to_weight_ratios,
        default=0.0,
    )

    # 推力を時間積分して総力積を求める
    total_impulse = 0.0

    for index in range(
        len(result.times) - 1
    ):
        time_interval = (
            result.times[index + 1]
            - result.times[index]
        )

        average_thrust = (
            result.thrusts[index]
            + result.thrusts[index + 1]
        ) / 2

        total_impulse += (
            average_thrust
            * time_interval
        )

    # Launchイベントから実際のリフトオフ時刻を取得
    launch_event = next(
        (
            event
            for event in result.flight_events
            if event.event_type
            == FlightEventType.LAUNCH
        ),
        None,
    )

    liftoff_time = (
        launch_event.time
        if launch_event is not None
        else None
    )

    performance_columns = st.columns(3)

    performance_columns[0].metric(
        label="最大推力",
        value=f"{max_thrust:,.0f} N",
    )

    performance_columns[1].metric(
        label="最大推進剤流量",
        value=f"{max_mass_flow_rate:.2f} kg/s",
    )

    performance_columns[2].metric(
        label="比推力",
        value=f"{max_specific_impulse:.1f} s",
    )

    performance_columns = st.columns(3)

    performance_columns[0].metric(
        label="最大推力重量比",
        value=f"{max_thrust_to_weight_ratio:.2f}",
    )

    performance_columns[1].metric(
        label="総力積",
        value=f"{total_impulse / 1000:.1f} kN·s",
    )

    performance_columns[2].metric(
        label="リフトオフ時刻",
        value=(
            f"T+{liftoff_time:.1f} s"
            if liftoff_time is not None
            else "Not launched"
        ),
    )

    st.divider()

    # ========================================
    # 推進性能グラフ
    # ========================================

    st.subheader("推力")
    st.line_chart(
        flight_dataframe.set_index(
            "時刻（秒）"
        )[
            [
                "推力（N）",
            ]
        ],
        height=320,
    )

    st.subheader("推進剤流量")
    st.line_chart(
        flight_dataframe.set_index(
            "時刻（秒）"
        )[
            [
                "推進剤流量（kg/s）",
            ]
        ],
        height=320,
    )

    st.subheader("比推力")
    st.line_chart(
        flight_dataframe.set_index(
            "時刻（秒）"
        )[
            [
                "比推力（s）",
            ]
        ],
        height=320,
    )

    st.subheader("推力重量比")
    st.line_chart(
        flight_dataframe.set_index(
            "時刻（秒）"
        )[
            [
                "推力重量比",
            ]
        ],
        height=320,
    )


# ========================================
# データ一覧・ダウンロード
# ========================================

st.header("データ")

data_tab, event_tab = st.tabs(
    [
        "飛行時系列データ",
        "イベントデータ",
    ]
)

with data_tab:
    st.dataframe(
        flight_dataframe,
        use_container_width=True,
        hide_index=True,
    )

    flight_csv = flight_dataframe.to_csv(
        index=False,
    ).encode(
        "utf-8-sig"
    )

    st.download_button(
        label="飛行データCSVをダウンロード",
        data=flight_csv,
        file_name="flight_data.csv",
        mime="text/csv",
        use_container_width=True,
    )

with event_tab:
    st.dataframe(
        event_dataframe,
        use_container_width=True,
        hide_index=True,
    )

    event_csv = event_dataframe.to_csv(
        index=False,
    ).encode(
        "utf-8-sig"
    )

    st.download_button(
        label="イベントCSVをダウンロード",
        data=event_csv,
        file_name="flight_events.csv",
        mime="text/csv",
        use_container_width=True,
    )