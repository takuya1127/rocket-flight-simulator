import streamlit as st


st.title("🚀 Rocket Flight Simulator")

st.subheader(
    "Pythonによる2次元ロケット飛行・解析ツール"
)

st.markdown(
    """
    重力・大気・空気抵抗・推力・燃料消費を考慮し、
    ロケットの飛行を時間ステップごとに計算する
    シミュレーションアプリケーションです。
    """
)


# ========================================
# 技術タグ
# ========================================

st.markdown(
    """
    `Python`　`Streamlit`　`Plotly`　`Pandas`　
    `Dataclass`　`Physics Simulation`
    """
)

st.divider()


# ========================================
# プロジェクト概要
# ========================================

st.header("Project Overview")

overview_left, overview_right = st.columns(
    [3, 2]
)

with overview_left:
    st.markdown(
        """
        ### このプロジェクトについて

        「ロケットはどのような力を受けて飛行するのか」を、
        物理モデルとプログラムの両面から理解するために制作しています。

        単純な放物運動ではなく、現在は次の要素を考慮しています。

        - エンジン推力
        - 燃料消費と機体質量の変化
        - 高度に応じた重力
        - 標準大気モデル
        - 空気抵抗
        - 動圧とMax Q
        - 音速とMach数
        - 発射から着地までのイベント
        """
    )

with overview_right:
    st.info(
        """
        **現在の開発段階**

        基本的な2次元飛行計算と、
        解析ダッシュボードまで実装済みです。

        今後、風・多段ロケット・機体分離・
        比較解析などを追加予定です。
        """
    )

st.divider()


# ========================================
# 現在実装済みの機能
# ========================================

st.header("Current Features")

column_1, column_2, column_3 = st.columns(3)

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

with column_3:
    st.subheader("Visualization")

    st.markdown(
        """
        - Webダッシュボード
        - 飛行リプレイ
        - 解析グラフ
        - イベントログ
        - CSV出力
        """
    )

st.divider()


# ========================================
# ページ案内
# ========================================

st.header("Explore the Project")

navigation_columns = st.columns(4)

with navigation_columns[0]:
    st.markdown(
        """
        ### 🚀 Simulation

        ロケット条件を入力し、
        飛行計算と解析を実行します。
        """
    )

with navigation_columns[1]:
    st.markdown(
        """
        ### 📐 Physics

        使用している物理モデルや
        計算の前提を説明します。
        """
    )

with navigation_columns[2]:
    st.markdown(
        """
        ### 🧩 Architecture

        ファイル構成やクラスの
        責務分割を説明します。
        """
    )

with navigation_columns[3]:
    st.markdown(
        """
        ### 🗺️ Roadmap

        今後追加する機能と
        開発段階を整理します。
        """
    )

st.divider()

st.caption(
    "個人開発・学習・転職ポートフォリオとして開発中"
)