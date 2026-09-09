import altair as alt
import pandas as pd
import streamlit as st

def render_comparison_results() -> None:

    if "comparison_dataframe" in st.session_state:

        comparison_dataframe = st.session_state[
            "comparison_dataframe"
        ]

        comparison_parameter_label = st.session_state.get(
            "comparison_parameter_label",
            "比較値",
        )

        st.subheader("比較結果")

        st.caption(
            "比較項目："
            + comparison_parameter_label
        )

        st.dataframe(
            comparison_dataframe,
            use_container_width=True,
            hide_index=True,
        )

        # ========================================
        # 比較ハイライト
        # ========================================
        successful_dataframe = comparison_dataframe[
            comparison_dataframe["状態"] == "成功"
            ].copy()

        if not successful_dataframe.empty:
            st.subheader("比較ハイライト")

            st.markdown(
                """
                <style>
                [data-testid="stMetricDelta"] svg {
                    display: none;
                }
                </style>
                """,
                unsafe_allow_html=True,
            )

            successful_dataframe = successful_dataframe.set_index("比較値")

            best_altitude_value = (
                successful_dataframe[
                    "最高高度（km）"
                ].idxmax()
            )
            best_altitude = (
                successful_dataframe.loc[
                    best_altitude_value,
                    "最高高度（km）",
                ]
            )

            best_velocity_value = (
                successful_dataframe[
                    "最高速度（m/s）"
                ].idxmax()
            )
            best_velocity = (
                successful_dataframe.loc[
                    best_velocity_value,
                    "最高速度（m/s）",
                ]
            )

            best_mach_value = (
                successful_dataframe[
                    "最大マッハ数"
                ].idxmax()
            )
            best_mach = (
                successful_dataframe.loc[
                    best_mach_value,
                    "最大マッハ数",
                ]
            )

            best_flight_time_value = (
                successful_dataframe[
                    "飛行時間（秒）"
                ].idxmax()
            )
            best_flight_time = (
                successful_dataframe.loc[
                    best_flight_time_value,
                    "飛行時間（秒）",
                ]
            )

            highlight_columns = st.columns(4)

            highlight_columns[0].metric(
                label="最高高度",
                value=f"{best_altitude:.2f} km",
                delta=(
                    f"{best_altitude_value:g}"
                    f" {comparison_parameter_label}"
                ),
            )

            highlight_columns[1].metric(
                label="最高速度",
                value=f"{best_velocity:.1f} m/s",
                delta=(
                    f"{best_velocity_value:g}"
                    f" {comparison_parameter_label}"
                ),
            )

            highlight_columns[2].metric(
                label="最大マッハ数",
                value=f"{best_mach:.2f}",
                delta=(
                    f"{best_mach_value:g}"
                    f" {comparison_parameter_label}"
                ),
            )

            highlight_columns[3].metric(
                label="最長飛行時間",
                value=f"{best_flight_time:.1f} 秒",
                delta=(
                    f"{best_flight_time_value:g}"
                    f" {comparison_parameter_label}"
                ),
            )

        # ========================================
        # 比較結果CSVダウンロード
        # ========================================
        comparison_csv = comparison_dataframe.to_csv(
            index=False,
        ).encode("utf-8-sig")

        st.download_button(
            label="比較結果CSVをダウンロード",
            data=comparison_csv,
            file_name="comparison_result.csv",
            mime="text/csv",
            use_container_width=True,
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

        performance_dataframe = comparison_dataframe[
            comparison_dataframe["状態"] == "成功"
            ].copy()

        if performance_dataframe.empty:

            st.warning(
                "比較できる成功データがありません。"
            )

        else:

            performance_col1, performance_col2 = (
                st.columns(2)
            )

            with performance_col1:

                st.markdown("#### 最高高度")

                altitude_chart = (
                    alt.Chart(performance_dataframe)
                    .mark_line(point=True)
                    .encode(
                        x=alt.X(
                            "比較値:O",
                            title=comparison_parameter_label,
                            sort=None,
                        ),
                        y=alt.Y(
                            "最高高度（km）:Q",
                            title="最高高度（km）",
                        ),
                        tooltip=[
                            alt.Tooltip(
                                "比較値:O",
                                title=comparison_parameter_label,
                            ),
                            alt.Tooltip(
                                "最高高度（km）:Q",
                                title="最高高度（km）",
                                format=".2f",
                            ),
                        ],
                    )
                )

                st.altair_chart(
                    altitude_chart,
                    use_container_width=True,
                )

            with performance_col2:

                st.markdown("#### 最高速度")

                velocity_chart = (
                    alt.Chart(performance_dataframe)
                    .mark_line(point=True)
                    .encode(
                        x=alt.X(
                            "比較値:O",
                            title=comparison_parameter_label,
                            sort=None,
                        ),
                        y=alt.Y(
                            "最高速度（m/s）:Q",
                            title="最高速度（m/s）",
                        ),
                        tooltip=[
                            alt.Tooltip(
                                "比較値:O",
                                title=comparison_parameter_label,
                            ),
                            alt.Tooltip(
                                "最高速度（m/s）:Q",
                                title="最高速度（m/s）",
                                format=".1f",
                            ),
                        ],
                    )
                )

                st.altair_chart(
                    velocity_chart,
                    use_container_width=True,
                )

            performance_col3, performance_col4 = (
                st.columns(2)
            )

            with performance_col3:

                st.markdown("#### 最大マッハ数")

                mach_chart = (
                    alt.Chart(performance_dataframe)
                    .mark_line(point=True)
                    .encode(
                        x=alt.X(
                            "比較値:O",
                            title=comparison_parameter_label,
                            sort=None,
                        ),
                        y=alt.Y(
                            "最大マッハ数:Q",
                            title="最大マッハ数",
                        ),
                        tooltip=[
                            alt.Tooltip(
                                "比較値:O",
                                title=comparison_parameter_label,
                            ),
                            alt.Tooltip(
                                "最大マッハ数:Q",
                                title="最大マッハ数",
                                format=".2f",
                            ),
                        ],
                    )
                )

                st.altair_chart(
                    mach_chart,
                    use_container_width=True,
                )

            with performance_col4:

                st.markdown("#### 飛行時間")

                flight_time_chart = (
                    alt.Chart(performance_dataframe)
                    .mark_line(point=True)
                    .encode(
                        x=alt.X(
                            "比較値:O",
                            title=comparison_parameter_label,
                            sort=None,
                        ),
                        y=alt.Y(
                            "飛行時間（秒）:Q",
                            title="飛行時間（秒）",
                        ),
                        tooltip=[
                            alt.Tooltip(
                                "比較値:O",
                                title=comparison_parameter_label,
                            ),
                            alt.Tooltip(
                                "飛行時間（秒）:Q",
                                title="飛行時間（秒）",
                                format=".1f",
                            ),
                        ],
                    )
                )

                st.altair_chart(
                    flight_time_chart,
                    use_container_width=True,
                )