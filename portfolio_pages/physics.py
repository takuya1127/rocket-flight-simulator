import streamlit as st


st.title("📐 Physics & Models")

st.caption(
    "シミュレーションに使用している物理モデルと、"
    "現在の簡略化条件を整理するページです。"
)

st.header("Implemented Models")

model_tabs = st.tabs(
    [
        "運動",
        "重力",
        "大気",
        "空気抵抗",
        "推進",
    ]
)

with model_tabs[0]:
    st.subheader("2次元運動")
    st.markdown(
        """
        ロケットの位置と速度を一定の時間刻みで更新します。
        現在はX方向・Y方向の2次元平面で飛行を計算します。
        """
    )
    st.code(
        """
velocity_x += acceleration_x * time_step
velocity_y += acceleration_y * time_step

position_x += velocity_x * time_step
position_y += velocity_y * time_step
        """,
        language="python",
    )
    st.latex(r"\theta=\mathrm{atan2}(v_y,v_x)")

with model_tabs[1]:
    st.subheader("高度に応じた重力")
    st.latex(r"g(h)=g_0\left(\frac{R}{R+h}\right)^2")

with model_tabs[2]:
    st.subheader("標準大気モデル")
    st.markdown(
        """
        高度から気温・気圧・空気密度・音速を計算し、
        空気抵抗やMach数の計算へ利用しています。
        """
    )

with model_tabs[3]:
    st.subheader("空気抵抗と動圧")
    st.markdown("### 空気抵抗")
    st.latex(r"D=\frac{1}{2}\rho C_D A v^2")
    st.markdown("### 動圧")
    st.latex(r"q=\frac{1}{2}\rho v^2")

with model_tabs[4]:
    st.subheader("エンジン・推進モデル")
    st.markdown(
        """
        推進系の計算は `EngineCalculator` が担当します。

        - エンジン燃焼状態
        - 推進剤流量
        - 比推力
        - 推力重量比
        - 推力曲線
        - 燃料消費
        - Ignition / Liftoff
        """
    )

    st.markdown("### 比推力")
    st.latex(r"I_{sp}=\frac{F}{\dot{m}g_0}")

    st.markdown("### 推力重量比")
    st.latex(r"\frac{T}{W}=\frac{F}{mg}")

    st.markdown(
        """
        エンジン点火後、垂直方向の推力重量比が1を超えるまでは
        発射台上に保持し、条件を満たした時点でLiftoffと判定します。
        """
    )

st.header("Current Limitations")

st.warning(
    """
    現在のモデルは学習・ポートフォリオ用途の
    簡易ロケットシミュレーションです。
    """
)

st.markdown(
    """
    - 風・横風・突風
    - 揚力
    - 地球の自転
    - 地球曲率を考慮した座標系
    - 動的な姿勢制御
    - ピッチプログラム
    - 重力ターン
    - 高度によるエンジン性能変化
    - 海面上・真空中の比推力差
    - 多段ロケット
    - 軌道力学
    - 再突入時の加熱
    """
)
