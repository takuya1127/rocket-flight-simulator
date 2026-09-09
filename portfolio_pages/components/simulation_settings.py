import streamlit as st

from models.simulation_models import (
    BoosterConfig,
    RocketConfig,
    StageConfig,
)

def render_simulation_settings() -> RocketConfig:

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

    return config