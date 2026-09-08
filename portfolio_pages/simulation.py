import math

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from visualization.dashboard_visualizer import (
    create_flight_replay_html,
)
from models.simulation_models import (
    BoosterConfig,
    RocketConfig,
    StageConfig,
)
from core.rocket_simulation import simulate_rocket
from core.simulation_runner import SimulationRunner
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
            "姿勢角度（度）": result.pitch_angles,
            "目標姿勢角度（度）": result.target_pitch_angles,
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
# ロケット設定
# ========================================

st.header("⚙️ ロケット設定")

st.caption(
    "シミュレーションに使用するロケット・飛行条件・"
    "環境条件を設定します。"
)

stages = []
booster = None

with st.container(border=True):

    use_multi_stage = st.toggle(
        "多段ロケットを使用",
        value=False,
    )

    # ========================================
    # 単段ロケット
    # ========================================

    if not use_multi_stage:

        vehicle_col, propulsion_col, flight_col = st.columns(3)

        with vehicle_col:
            st.subheader("🚀 機体")

            structure_mass = st.number_input(
                "機体構造質量（kg）",
                min_value=0.1,
                value=70.0,
                step=5.0,
            )

            engine_mass = st.number_input(
                "エンジン質量（kg）",
                min_value=0.1,
                value=20.0,
                step=5.0,
            )

            payload_mass = st.number_input(
                "ペイロード質量（kg）",
                min_value=0.0,
                value=10.0,
                step=5.0,
            )

        with propulsion_col:
            st.subheader("🔥 推進系")

            fuel_mass = st.number_input(
                "燃料質量（kg）",
                min_value=0.1,
                value=50.0,
                step=5.0,
            )

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

        with flight_col:
            st.subheader("🛫 飛行・空力")

            launch_angle = st.slider(
                "発射角度（度）",
                min_value=1.0,
                max_value=90.0,
                value=75.0,
                step=1.0,
            )

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

        dry_mass = (
            structure_mass
            + engine_mass
            + payload_mass
        )

        initial_total_mass = (
            dry_mass
            + fuel_mass
        )

    # ========================================
    # 多段ロケット
    # ========================================

    else:

        vehicle_col, flight_col, aero_col = st.columns(3)

        with vehicle_col:
            st.subheader("🚀 機体")

            payload_mass = st.number_input(
                "ペイロード質量（kg）",
                min_value=0.0,
                value=10.0,
                step=5.0,
            )

            stage_count = st.number_input(
                "段数",
                min_value=2,
                max_value=4,
                value=2,
                step=1,
            )

        with flight_col:
            st.subheader("🛫 飛行")

            launch_angle = st.slider(
                "発射角度（度）",
                min_value=1.0,
                max_value=90.0,
                value=75.0,
                step=1.0,
            )

        with aero_col:
            st.subheader("🌍 空力")

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

        st.markdown("#### 📦 ステージ構成")

        for stage_index in range(stage_count):

            stage_number = stage_index + 1

            with st.expander(
                f"{stage_number}段目",
                expanded=(stage_number == 1),
            ):

                default_structure_mass = (
                    60.0 if stage_number == 1 else 20.0
                )
                default_engine_mass = (
                    20.0 if stage_number == 1 else 10.0
                )
                default_fuel_mass = (
                    50.0 if stage_number == 1 else 20.0
                )
                default_thrust = (
                    7000.0 if stage_number == 1 else 3000.0
                )
                default_burn_time = (
                    20.0 if stage_number == 1 else 15.0
                )

                stage_columns = st.columns(5)

                with stage_columns[0]:
                    stage_structure_mass = st.number_input(
                        "構造質量（kg）",
                        min_value=0.1,
                        value=default_structure_mass,
                        step=5.0,
                        key=f"stage_{stage_number}_structure_mass",
                    )

                with stage_columns[1]:
                    stage_engine_mass = st.number_input(
                        "エンジン質量（kg）",
                        min_value=0.1,
                        value=default_engine_mass,
                        step=5.0,
                        key=f"stage_{stage_number}_engine_mass",
                    )

                with stage_columns[2]:
                    stage_fuel_mass = st.number_input(
                        "燃料質量（kg）",
                        min_value=0.1,
                        value=default_fuel_mass,
                        step=5.0,
                        key=f"stage_{stage_number}_fuel_mass",
                    )

                with stage_columns[3]:
                    stage_thrust = st.number_input(
                        "最大推力（N）",
                        min_value=0.1,
                        value=default_thrust,
                        step=500.0,
                        key=f"stage_{stage_number}_thrust",
                    )

                with stage_columns[4]:
                    stage_burn_time = st.number_input(
                        "燃焼時間（秒）",
                        min_value=0.1,
                        value=default_burn_time,
                        step=1.0,
                        key=f"stage_{stage_number}_burn_time",
                    )

                stages.append(
                    StageConfig(
                        name=f"Stage {stage_number}",
                        structure_mass=stage_structure_mass,
                        engine_mass=stage_engine_mass,
                        fuel_mass=stage_fuel_mass,
                        thrust=stage_thrust,
                        burn_time=stage_burn_time,
                    )
                )

        dry_mass = (
            sum(stage.dry_mass for stage in stages)
            + payload_mass
        )

        fuel_mass = sum(
            stage.fuel_mass
            for stage in stages
        )

        initial_total_mass = (
            dry_mass
            + fuel_mass
        )

        structure_mass = sum(
            stage.structure_mass
            for stage in stages
        )

        engine_mass = sum(
            stage.engine_mass
            for stage in stages
        )

        thrust = stages[0].thrust
        burn_time = sum(
            stage.burn_time
            for stage in stages
        )

    # ========================================
    # 質量サマリー
    # ========================================

    st.divider()

    mass_columns = st.columns(3)

    mass_columns[0].metric(
        "乾燥質量",
        f"{dry_mass:.1f} kg",
    )

    mass_columns[1].metric(
        "燃料質量",
        f"{fuel_mass:.1f} kg",
    )

    mass_columns[2].metric(
        "初期総質量",
        f"{initial_total_mass:.1f} kg",
    )

    # ========================================
    # 環境設定
    # ========================================

    with st.expander(
        "🌬️ 環境設定",
        expanded=False,
    ):

        wind_col, direction_col = st.columns(2)

        with wind_col:
            wind_speed = st.number_input(
                "風速（m/s）",
                min_value=0.0,
                max_value=100.0,
                value=5.0,
                step=1.0,
            )

        with direction_col:
            wind_direction_deg = st.slider(
                "風向（度）",
                min_value=0,
                max_value=359,
                value=0,
                step=1,
            )

        st.markdown("#### 突風")

        gust_columns = st.columns(3)

        with gust_columns[0]:
            gust_speed = st.number_input(
                "追加風速（m/s）",
                min_value=0.0,
                max_value=100.0,
                value=0.0,
                step=1.0,
            )

        with gust_columns[1]:
            gust_start_time = st.number_input(
                "開始時刻（秒）",
                min_value=0.0,
                max_value=300.0,
                value=15.0,
                step=1.0,
            )

        with gust_columns[2]:
            gust_duration = st.number_input(
                "継続時間（秒）",
                min_value=0.0,
                max_value=60.0,
                value=5.0,
                step=1.0,
            )

    # ========================================
    # 分離・ブースター設定
    # ========================================

    with st.expander(
        "⚙️ 分離・ブースター設定",
        expanded=False,
    ):

        fairing_col1, fairing_col2 = st.columns(2)

        with fairing_col1:
            fairing_mass = st.number_input(
                "フェアリング質量（kg）",
                min_value=0.0,
                value=0.0,
                step=1.0,
            )

        with fairing_col2:
            fairing_separation_altitude = st.number_input(
                "フェアリング分離高度（m）",
                min_value=0.0,
                value=3000.0,
                step=100.0,
            )

        st.divider()

        use_booster = st.checkbox(
            "補助ブースターを使用",
            value=False,
        )

        if use_booster:

            booster_top_columns = st.columns(3)

            with booster_top_columns[0]:
                booster_count = st.number_input(
                    "ブースター本数",
                    min_value=1,
                    max_value=8,
                    value=2,
                    step=1,
                )

            with booster_top_columns[1]:
                booster_structure_mass = st.number_input(
                    "構造質量 / 1本（kg）",
                    min_value=0.1,
                    value=10.0,
                    step=1.0,
                )

            with booster_top_columns[2]:
                booster_engine_mass = st.number_input(
                    "エンジン質量 / 1本（kg）",
                    min_value=0.1,
                    value=5.0,
                    step=1.0,
                )

            booster_bottom_columns = st.columns(3)

            with booster_bottom_columns[0]:
                booster_fuel_mass = st.number_input(
                    "燃料質量 / 1本（kg）",
                    min_value=0.1,
                    value=20.0,
                    step=1.0,
                )

            with booster_bottom_columns[1]:
                booster_thrust = st.number_input(
                    "推力 / 1本（N）",
                    min_value=0.1,
                    value=3000.0,
                    step=500.0,
                )

            with booster_bottom_columns[2]:
                booster_burn_time = st.number_input(
                    "燃焼時間（秒）",
                    min_value=0.1,
                    value=10.0,
                    step=1.0,
                )

            booster = BoosterConfig(
                name="Side Booster",
                count=booster_count,
                structure_mass=booster_structure_mass,
                engine_mass=booster_engine_mass,
                fuel_mass=booster_fuel_mass,
                thrust=booster_thrust,
                burn_time=booster_burn_time,
            )


# ========================================
# 共通RocketConfig
# ========================================

base_config = RocketConfig(
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
    fairing_mass=fairing_mass,
    fairing_separation_altitude=fairing_separation_altitude,
    booster=booster,
    stages=stages,
)


# ========================================
# シミュレーションモード
# ========================================

st.header("2. シミュレーション実行")

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


with comparison_tab:

    st.write(
        "現在の設定を基準に、"
        "1つの条件だけを変化させて結果を比較します。"
    )

    parameter_options = {
        "発射角度（度）": {
            "name": "launch_angle",
            "min": 60.0,
            "max": 90.0,
            "step": 5.0,
        },
        "風速（m/s）": {
            "name": "wind_speed",
            "min": 0.0,
            "max": 20.0,
            "step": 5.0,
        },
        "抗力係数": {
            "name": "drag_coefficient",
            "min": 0.30,
            "max": 0.70,
            "step": 0.10,
        },
        "基準断面積（m²）": {
            "name": "reference_area",
            "min": 0.10,
            "max": 0.50,
            "step": 0.10,
        },
    }

    parameter_label = st.selectbox(
        "比較する項目",
        options=list(parameter_options.keys()),
    )

    parameter_setting = parameter_options[
        parameter_label
    ]

    comparison_columns = st.columns(3)

    with comparison_columns[0]:
        comparison_min = st.number_input(
            "最小値",
            value=float(parameter_setting["min"]),
            key=f"comparison_min_{parameter_setting['name']}",
        )

    with comparison_columns[1]:
        comparison_max = st.number_input(
            "最大値",
            value=float(parameter_setting["max"]),
            key=f"comparison_max_{parameter_setting['name']}",
        )

    with comparison_columns[2]:
        comparison_step = st.number_input(
            "刻み",
            min_value=0.001,
            value=float(parameter_setting["step"]),
            key=f"comparison_step_{parameter_setting['name']}",
        )

    comparison_values = []

    if comparison_max >= comparison_min:

        current_value = comparison_min

        while (
            current_value
            <= comparison_max + 1e-9
            and len(comparison_values) < 20
        ):
            comparison_values.append(
                round(current_value, 6)
            )
            current_value += comparison_step

    if not comparison_values:
        st.warning(
            "最大値は最小値以上になるように設定してください。"
        )

    elif len(comparison_values) >= 20:
        st.warning(
            "一度に実行できる比較条件は最大20件です。"
        )

    else:
        preview = " / ".join(
            f"{value:g}"
            for value in comparison_values
        )

        st.info(
            f"比較予定：{preview} "
            f"（{len(comparison_values)}パターン）"
        )

    run_comparison = st.button(
        "📊 比較シミュレーションを実行",
        type="primary",
        use_container_width=True,
        disabled=not comparison_values,
        key="run_comparison_simulation",
    )

    if run_comparison:

        runner = SimulationRunner()

        with st.spinner(
            "比較シミュレーションを実行しています..."
        ):
            comparison_results = (
                runner.run_parameter_sweep(
                    base_config=base_config,
                    parameter_name=parameter_setting["name"],
                    values=comparison_values,
                )
            )

        comparison_rows = []

        for value, comparison_result in zip(
            comparison_values,
            comparison_results,
        ):

            if comparison_result is None:
                comparison_rows.append(
                    {
                        "比較値": value,
                        "状態": "失敗",
                        "最高高度（km）": None,
                        "最高速度（m/s）": None,
                        "最大マッハ数": None,
                        "飛行時間（秒）": None,
                    }
                )
                continue

            comparison_rows.append(
                {
                    "比較値": value,
                    "状態": "成功",
                    "最高高度（km）": (
                        comparison_result.max_altitude
                        / 1000
                    ),
                    "最高速度（m/s）": (
                        comparison_result.max_velocity
                    ),
                    "最大マッハ数": (
                        comparison_result.max_mach_number
                    ),
                    "飛行時間（秒）": (
                        comparison_result.flight_time
                    ),
                }
            )

        comparison_dataframe = pd.DataFrame(
            comparison_rows
        )

        st.session_state[
            "comparison_dataframe"
        ] = comparison_dataframe

        st.session_state[
            "comparison_results"
        ] = comparison_results

        st.session_state[
            "comparison_values"
        ] = comparison_values

        st.session_state[
            "comparison_parameter_label"
        ] = parameter_label

        st.success(
            "比較シミュレーションが完了しました。"
        )

    if "comparison_dataframe" in st.session_state:

        st.subheader("比較結果")

        st.caption(
            "比較項目："
            + st.session_state.get(
                "comparison_parameter_label",
                "",
            )
        )

        st.dataframe(
            st.session_state[
                "comparison_dataframe"
            ],
            use_container_width=True,
            hide_index=True,
        )

        # ========================================
        # 各性能比較
        # ========================================

        comparison_results = st.session_state.get(
            "comparison_results",
            [],
        )

        comparison_values = st.session_state.get(
            "comparison_values",
            [],
        )

        trajectory_rows = []

        for value, comparison_result in zip(
            comparison_values,
            comparison_results,
        ):

            if comparison_result is None:
                continue

            # 点数が多すぎると画面表示が重くなるため、
            # 最大800点程度になるように間引く
            point_count = len(
                comparison_result.positions_x
            )

            sample_step = max(
                1,
                point_count // 800,
            )

            for position_x, position_y in zip(
                comparison_result.positions_x[
                    ::sample_step
                ],
                comparison_result.positions_y[
                    ::sample_step
                ],
            ):

                trajectory_rows.append(
                    {
                        "水平距離（km）": (
                            position_x / 1000
                        ),
                        "高度（km）": (
                            position_y / 1000
                        ),
                        "条件": f"{value:g}",
                    }
                )


        # ========================================
        # 飛行軌跡比較
        # ========================================

        if trajectory_rows:

            st.subheader("飛行軌跡比較")

            trajectory_dataframe = pd.DataFrame(
                trajectory_rows
            )

            st.line_chart(
                trajectory_dataframe,
                x="水平距離（km）",
                y="高度（km）",
                color="条件",
                height=500,
            )


        # ========================================
        # 性能比較
        # ========================================

        st.subheader("性能比較")

        comparison_dataframe = st.session_state[
            "comparison_dataframe"
        ]

        successful_dataframe = (
            comparison_dataframe[
                comparison_dataframe["状態"] == "成功"
            ]
            .copy()
            .set_index("比較値")
        )

        if successful_dataframe.empty:

            st.warning(
                "比較できる成功データがありません。"
            )

        else:

            performance_col1, performance_col2 = (
                st.columns(2)
            )

            with performance_col1:

                st.markdown("#### 最高高度")

                st.line_chart(
                    successful_dataframe[
                        "最高高度（km）"
                    ],
                    height=300,
                )

            with performance_col2:

                st.markdown("#### 最高速度")

                st.line_chart(
                    successful_dataframe[
                        "最高速度（m/s）"
                    ],
                    height=300,
                )

            performance_col3, performance_col4 = (
                st.columns(2)
            )

            with performance_col3:

                st.markdown("#### 最大マッハ数")

                st.line_chart(
                    successful_dataframe[
                        "最大マッハ数"
                    ],
                    height=300,
                )

            with performance_col4:

                st.markdown("#### 飛行時間")

                st.line_chart(
                    successful_dataframe[
                        "飛行時間（秒）"
                    ],
                    height=300,
                )


# ========================================
# シミュレーション実行
# ========================================
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

has_single_result = (
    "simulation_result"
    in st.session_state
)

has_comparison_result = (
    "comparison_dataframe"
    in st.session_state
)

if(
    not has_single_result
    and not has_comparison_result
):
    st.info(
        "上のロケット設定を入力し"
        "単体または比較シミュレーションを実行してください"
    )

    st.stop()

if has_single_result:

    result = st.session_state["simulation_result"]
    config = st.session_state["rocket_config"]

    flight_dataframe = (
        create_flight_dataframe(result)
    )

    event_dataframe = (
        create_event_dataframe(result)
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
        label="最大マッハ数",
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
            f"{result.total_masses[0]:.1f} kg"
            if result.total_masses
            else "-"
        ),
    )

    display_burn_time = (
        sum(
            stage.burn_time
            for stage in config.stages
        )
        if config.stages
        else config.burn_time
    )

    summary_columns[3].metric(
        label="総燃焼時間" if config.stages else "燃焼時間",
        value=f"{display_burn_time:.1f} 秒",
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

        st.subheader("飛行角度・姿勢制御")
        st.line_chart(
            flight_dataframe.set_index(
                "時刻（秒）"
            )[
                [
                    "飛行角度（度）",
                    "目標姿勢角度（度）",
                    "姿勢角度（度）",
                ]
            ],
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
                "動圧（kPa）"
            ],
            height=320,
        )

        st.subheader("マッハ数")
        st.line_chart(
            flight_dataframe.set_index(
                "時刻（秒）"
            )[
                "マッハ数"
            ],
            height=320,
        )

        st.subheader("重力加速度")
        st.line_chart(
            flight_dataframe.set_index(
                "時刻（秒）"
            )[
                "重力加速度（m/s²）"
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
                    "推力（N）"
                ]
            ],
            height=320,
        )

        st.subheader("推進剤流量")
        st.line_chart(
            flight_dataframe.set_index(
                "時刻（秒）"
            )[
                "推進剤流量（kg/s）"
            ],
            height=320,
        )

        st.subheader("比推力")
        st.line_chart(
            flight_dataframe.set_index(
                "時刻（秒）"
            )[
                "比推力（s）"
            ],
            height=320,
        )

        st.subheader("推力重量比")
        st.line_chart(
            flight_dataframe.set_index(
                "時刻（秒）"
            )[
                "推力重量比"
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