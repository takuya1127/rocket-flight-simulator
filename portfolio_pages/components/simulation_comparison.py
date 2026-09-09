import pandas as pd
import streamlit as st

from core.simulation_runner import SimulationRunner
from models.simulation_models import RocketConfig

def render_comparison_simulation(
    base_config: RocketConfig,
) -> None:

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
