import streamlit as st


st.title("🚀 Rocket Flight Simulator")

st.subheader(
    "Pythonによる2次元ロケット飛行・解析シミュレーター"
)

st.markdown(
    """
    重力・大気・空気抵抗・推力・燃料消費に加えて、
    エンジン性能や推力曲線も考慮しながら、
    ロケットの飛行を時間ステップごとに計算する
    シミュレーションアプリケーションです。
    """
)

st.markdown(
    """
    `Python`　`Streamlit`　`Pandas`　`Dataclass`　
    `Canvas`　`Physics Simulation`
    """
)

st.divider()

st.header("Project Overview")

overview_left, overview_right = st.columns([3, 2])

with overview_left:
    st.markdown(
        """
        ### このプロジェクトについて

        「ロケットはどのような力を受け、
        エンジン性能や機体状態の変化によって
        飛行結果がどう変わるのか」を、

        物理モデルとプログラムの両面から理解するために
        個人開発しています。

        現在は次の要素を考慮しています。

        - 2次元飛行
        - エンジン推力
        - 推力の時間変化
        - 推進剤流量
        - 比推力
        - 推力重量比
        - 燃料消費と機体質量の変化
        - 高度に応じた重力
        - 標準大気モデル
        - 空気抵抗
        - 動圧とMax Q
        - 音速とMach数
        - 発射から着地までの飛行イベント
        """
    )

with overview_right:
    st.info(
        """
        **現在の開発段階**

        Phase 1：
        Basic Flight Simulation ✅

        Phase 2：
        Analysis Dashboard ✅

        Phase 3：
        Propulsion & Vehicle Performance ✅

        次は Phase 4：
        Wind & Environment を開発予定です。
        """
    )

st.divider()

st.header("Current Features")

column_1, column_2, column_3, column_4 = st.columns(4)

with column_1:
    st.subheader("Flight Simulation")
    st.markdown(
        """
        - 2次元飛行
        - 推力の方向分解
        - 燃料消費
        - 質量変化
        - 速度・位置更新
        """
    )

with column_2:
    st.subheader("Propulsion")
    st.markdown(
        """
        - 推力曲線
        - 推進剤流量
        - 比推力
        - 推力重量比
        - Ignition / Liftoff
        """
    )

with column_3:
    st.subheader("Flight Analysis")
    st.markdown(
        """
        - 最高高度
        - 最高速度
        - Mach数
        - Max Q
        - 飛行時間
        - 水平到達距離
        """
    )

with column_4:
    st.subheader("Visualization")
    st.markdown(
        """
        - Webダッシュボード
        - Canvas飛行リプレイ
        - 解析グラフ
        - イベントログ
        - CSV出力
        """
    )

st.divider()

st.header("Project Highlights")

highlight_1, highlight_2, highlight_3 = st.columns(3)

with highlight_1:
    st.markdown(
        """
        ### 📐 Physics Modeling

        重力・大気・抗力・推進を
        個別の計算モデルとして実装しています。
        """
    )

with highlight_2:
    st.markdown(
        """
        ### 🧩 Modular Architecture

        推進・物理・環境・解析・記録・表示を
        モジュールごとに分離しています。
        """
    )

with highlight_3:
    st.markdown(
        """
        ### 📊 Engineering Analysis

        飛行性能・機体状態・推進性能を
        時系列データとして解析できます。
        """
    )

st.divider()

st.header("Explore the Project")

navigation_columns = st.columns(4)

with navigation_columns[0]:
    st.markdown("### 🚀 Simulation\n飛行計算・リプレイ・解析を実行します。")

with navigation_columns[1]:
    st.markdown("### 📐 Physics & Models\n使用している物理モデルを説明します。")

with navigation_columns[2]:
    st.markdown("### 🧩 Architecture\nクラス構成と責務分割を説明します。")

with navigation_columns[3]:
    st.markdown("### 🗺️ Roadmap\n実装済み機能と今後の計画を整理しています。")

st.divider()

st.caption(
    "個人開発・学習・転職ポートフォリオとして継続開発中"
)
