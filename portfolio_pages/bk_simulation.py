import streamlit as st
from models.simulation_models import (
    BoosterConfig,
    RocketConfig,
    StageConfig,
)
from core.rocket_simulation import simulate_rocket
from portfolio_pages.components.simulation_data import (
    create_event_dataframe,
    create_flight_dataframe,
)
from portfolio_pages.components.simulation_results import (
    render_simulation_results,
)

from core.simulation_runner import SimulationRunner


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


# ========================================
# ロケット設定
# ========================================

st.header("１．ロケット設定")
st.caption(
    "シミュレーションに使用するロケットと"
    "飛行環境の基本条件を設定します。"
)

with st.container(border=True):

    use_multi_stage = st.toggle(
        "多段ロケットを使用",
        value=False,
    )

    stages = []
    booster = None

    if not use_multi_stage:

        vehicle_col, propulsion_col, flight_col = st.columns(3)

        # ========================================
        # 機体設定
        # ========================================
        with vehicle_col:

            st.subheader("### ⛽ 機体")

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


        # ========================================
        # 推進系
        # ========================================
        with propulsion_col:
            st.subheader("###🔥 推進系")

            fuel_mass = st.number_input(
                "燃料質量(kg)",
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

        # ========================================
        # 飛行・空力
        # ========================================

        with flight_col:
            st.subheader("###🛬 飛行・空力")

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

        dry_mass = structure_mass + engine_mass + payload_mass
        initial_total_mass = dry_mass + fuel_mass

        st.caption(f"乾燥質量:{dry_mass:.1f}kg")
        st.caption(f"初期総質量:{initial_total_mass:.1f}kg")

        st.markdown("### 🔥 エンジン設定")


    else:
        st.markdown("### ⛽ 機体設定")

        payload_mass = st.number_input(
            "ペイロード質量(kg)",
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

        st.markdown("### 📦 ロケット構成")

        for stage_index in range(stage_count):
            stage_number = stage_index + 1

            with st.expander(
                f"{stage_number}段目",
                expanded=True,
            ):
                default_structure_mass = 60.0 if stage_number == 1 else 20.0
                default_engine_mass = 20.0 if stage_number == 1 else 10.0
                default_fuel_mass = 50.0 if stage_number == 1 else 20.0
                default_thrust = 7000.0 if stage_number == 1 else 3000.0
                default_burn_time = 20.0 if stage_number == 1 else 15.0

                stage_structure_mass = st.number_input(
                    "構造質量（kg）",
                    min_value=0.1,
                    value=default_structure_mass,
                    step=5.0,
                    key=f"stage_{stage_number}_structure_mass",
                )

                stage_engine_mass = st.number_input(
                    "エンジン質量（kg）",
                    min_value=0.1,
                    value=default_engine_mass,
                    step=5.0,
                    key=f"stage_{stage_number}_engine_mass",
                )

                stage_fuel_mass = st.number_input(
                    "燃料質量（kg）",
                    min_value=0.1,
                    value=default_fuel_mass,
                    step=5.0,
                    key=f"stage_{stage_number}_fuel_mass",
                )

                stage_thrust = st.number_input(
                    "最大推力（N）",
                    min_value=0.1,
                    value=default_thrust,
                    step=500.0,
                    key=f"stage_{stage_number}_thrust",
                )

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

        dry_mass = sum(stage.dry_mass for stage in stages) + payload_mass
        fuel_mass = sum(stage.fuel_mass for stage in stages)
        initial_total_mass = dry_mass + fuel_mass

        st.caption(f"全段乾燥質量:{dry_mass:.1f}kg")
        st.caption(f"全段燃料質量:{fuel_mass:.1f}kg")
        st.caption(f"初期総質量:{initial_total_mass:.1f}kg")

        structure_mass = sum(stage.structure_mass for stage in stages)
        engine_mass = sum(stage.engine_mass for stage in stages)
        thrust = stages[0].thrust
        burn_time = sum(stage.burn_time for stage in stages)

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
        st.markdown("#### 突風")

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

        st.divider()

        st.markdown("#### フェアリング")

        fairing_mass = st.number_input(
            "フェアリング質量（kg）",
            min_value=0.0,
            value=0.0,
            step=1.0,
        )

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

            booster_count = st.number_input(
                "ブースター本数",
                min_value=1,
                max_value=8,
                value=2,
                step=1,
            )

            st.caption(
                "以下の値はブースター１本あたりの設定です。"
            )

            booster_structure_mass = st.number_input(
                "ブースター構造質量（kg）",
                min_value=0.1,
                value=10.0,
                step=1.0,
            )

            booster_engine_mass = st.number_input(
                "ブースターエンジン質量（kg）",
                min_value=0.1,
                value=5.0,
                step=1.0,
            )

            booster_fuel_mass = st.number_input(
                "ブースター燃料質量（kg）",
                min_value=0.1,
                value=20.0,
                step=1.0,
            )

            booster_thrust = st.number_input(
                "ブースター推力（N）",
                min_value=0.1,
                value=3000.0,
                step=500.0,
            )

            booster_burn_time = st.number_input(
                "ブースター燃焼時間（秒）",
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
# 比較シミュレーション
# ========================================
st.subheader("比較シミュレーション")

compare_parameter = st.selectbox(
    "比較するパラメータ",
    [
        "launch_angle",
        "wind_speed",
        "drag_coefficient",
    ],
)

compare_values_text = st.text_input(
    "比較する値（カンマ区切り）",
    value="70,75,80",
)

run_comparison = st.button(
    "比較シミュレーションを実行"
)

if run_comparison:

    values = [
        float(value.strip())
        for value in compare_values_text.split(",")
    ]

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

    runner =SimulationRunner()

    results = runner.run_parameter_sweep(
        base_config=base_config,
        parameter_name=compare_parameter,
        values=values,
    )

# ========================================
# シミュレーションモード
# ========================================
st.header("２．シミュレーション実行")
st.caption(
    "実行するシミュレーションの種類を選択してください。"
)

single_tab, comparison_tab = st.tabs(
    [
        "🚀 単体シミュレーション",
        "📊 比較シミュレーション",
    ]
)

with single_tab:

    st.subheader("単体シミュレーション")
    st.caption(
        "設定している条件で"
        "１回の飛行シミュレーションを実行します。"
    )

    run_simulation = st.button(
        "🚀 シミュレーションを実行",
        type="primary",
        use_container_width=True,
        key="run_single_simulation",
    )

with comparison_tab:
    st.subheader("比較シミュレーション")
    st.caption(
        "ロケットの設定を基準に、"
        "１つの条件を変化させて性能を比較します。"
    )

    st.info(
        "比較条件の設定画面をここに追加していきます。"
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
        fairing_mass=fairing_mass,
        fairing_separation_altitude=fairing_separation_altitude,
        booster=booster,
        stages=stages,
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



render_simulation_results(
    result=result,
    config=config,
    flight_dataframe=flight_dataframe,
    event_dataframe=event_dataframe,
    mobile_mode=is_mobile_device(),
)
