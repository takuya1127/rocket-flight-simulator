import streamlit as st
import streamlit.components.v1 as components

from analysis.flight_event import FlightEventType
from visualization.dashboard_visualizer import create_flight_replay_html


def render_simulation_results(
    result,
    config,
    flight_dataframe,
    event_dataframe,
    mobile_mode: bool,
) -> None:
    chart_dataframe = flight_dataframe.set_index("時刻（秒）")

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
    analysis_view = st.radio(
        "表示する解析カテゴリ",
        ["運動解析", "空力・環境", "機体状態", "推進性能"],
        horizontal=True,
        label_visibility="collapsed",
    )


    # ========================================
    # 運動解析
    # ========================================

    if analysis_view == "運動解析":
        st.subheader("高度")
        st.line_chart(
            chart_dataframe[
                [
                    "高度（m）",
                ]
            ],
            height=320,
        )

        st.subheader("速度")
        st.line_chart(
            chart_dataframe[
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
            chart_dataframe[
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
            chart_dataframe[
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

    if analysis_view == "空力・環境":
        st.subheader("動圧")
        st.line_chart(
            chart_dataframe[
                [
                    "動圧（kPa）",
                ]
            ],
            height=320,
        )

        st.subheader("マッハ数")
        st.line_chart(
            chart_dataframe[
                [
                    "マッハ数",
                ]
            ],
            height=320,
        )

        st.subheader("重力加速度")
        st.line_chart(
            chart_dataframe[
                [
                    "重力加速度（m/s²）",
                ]
            ],
            height=320,
        )


    # ========================================
    # 機体状態
    # ========================================

    if analysis_view == "機体状態":
        st.subheader("燃料残量・総質量")
        st.line_chart(
            chart_dataframe[
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

    if analysis_view == "推進性能":

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
            chart_dataframe[
                [
                    "推力（N）",
                ]
            ],
            height=320,
        )

        st.subheader("推進剤流量")
        st.line_chart(
            chart_dataframe[
                [
                    "推進剤流量（kg/s）",
                ]
            ],
            height=320,
        )

        st.subheader("比推力")
        st.line_chart(
            chart_dataframe[
                [
                    "比推力（s）",
                ]
            ],
            height=320,
        )

        st.subheader("推力重量比")
        st.line_chart(
            chart_dataframe[
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
