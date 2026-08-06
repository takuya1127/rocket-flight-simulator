import streamlit as st


st.title("📐 Physics & Models")

st.caption(
    "シミュレーションに使用している物理モデルと、"
    "現在の簡略化条件を整理するページです。"
)


# ========================================
# 現在のモデル
# ========================================

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
        ロケットの速度と位置を、
        一定の時間刻みで更新しています。

        現在はX方向とY方向の2次元平面で計算しています。
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


with model_tabs[1]:
    st.subheader("高度に応じた重力")

    st.markdown(
        """
        地表で固定した重力加速度ではなく、
        地球中心からの距離に応じて重力を変化させています。
        """
    )

    st.latex(
        r"g(h)=g_0\left(\frac{R}{R+h}\right)^2"
    )


with model_tabs[2]:
    st.subheader("標準大気モデル")

    st.markdown(
        """
        高度から次の値を計算しています。

        - 気温
        - 気圧
        - 空気密度
        - 音速

        現在は高度帯ごとに式を切り替える簡易モデルです。
        """
    )


with model_tabs[3]:
    st.subheader("空気抵抗と動圧")

    st.markdown(
        """
        空気抵抗は、速度の反対方向へ働く力として計算しています。
        """
    )

    st.latex(
        r"D=\frac{1}{2}\rho C_D A v^2"
    )

    st.markdown("動圧は次の式で計算しています。")

    st.latex(
        r"q=\frac{1}{2}\rho v^2"
    )


with model_tabs[4]:
    st.subheader("推力と燃料消費")

    st.markdown(
        """
        発射角度から推力をX方向・Y方向へ分解し、
        燃焼時間中は一定量ずつ燃料を減少させています。

        現在の推力は燃焼中一定で、
        スロットル制御は未実装です。
        """
    )


# ========================================
# 簡略化条件
# ========================================

st.header("Current Limitations")

st.warning(
    """
    現在のモデルは学習用の簡易シミュレーションです。

    実際のロケット飛行を完全に再現するものではありません。
    """
)

st.markdown(
    """
    現在は、主に次の要素を簡略化または未実装としています。

    - 風と突風
    - 地球の自転
    - 地球の曲率を考慮した座標系
    - 揚力
    - 姿勢制御
    - 推力の時間変化
    - エンジン性能の高度変化
    - 多段ロケット
    - ブースター・フェアリング分離
    - 軌道力学
    - 再突入時の加熱
    """
)

st.info(
    "各機能の実装に合わせて、このページも更新していきます。"
)