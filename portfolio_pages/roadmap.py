import streamlit as st


st.title("🗺️ Development Roadmap")

st.caption(
    "現在は基本飛行モデルと解析ダッシュボードまで実装済みです。"
)


# ========================================
# 開発状況
# ========================================

st.header("Development Status")

st.progress(
    35,
    text="全体構想に対する現在の進捗イメージ：35%",
)


# ========================================
# フェーズ
# ========================================

with st.expander(
    "✅ Phase 1 — Basic Flight Simulation",
    expanded=True,
):
    st.markdown(
        """
        - 2次元飛行
        - 推力
        - 燃料消費
        - 空気抵抗
        - 可変重力
        - 標準大気
        - Mach数
        - Max Q
        - 飛行イベント
        """
    )


with st.expander(
    "✅ Phase 2 — Analysis Dashboard",
    expanded=True,
):
    st.markdown(
        """
        - Streamlit
        - 飛行サマリー
        - Plotlyグラフ
        - 飛行リプレイ
        - イベント一覧
        - CSV出力
        """
    )


with st.expander(
    "⬜ Phase 3 — Vehicle Performance",
):
    st.markdown(
        """
        - 比推力
        - 推進剤流量
        - 推力曲線
        - エンジン性能
        - 推力重量比の時系列解析
        """
    )


with st.expander(
    "⬜ Phase 4 — Wind Model",
):
    st.markdown(
        """
        - 一定風
        - 高度別風速
        - 横風
        - 突風
        - 風あり・なし比較
        """
    )


with st.expander(
    "⬜ Phase 5 — Multi-stage Rocket",
):
    st.markdown(
        """
        - 多段ロケット
        - ブースター分離
        - ステージ分離
        - フェアリング分離
        - 分離イベント
        """
    )


with st.expander(
    "⬜ Phase 6 — Comparative Analysis",
):
    st.markdown(
        """
        - 複数条件の同時実行
        - 軌跡比較
        - 最高高度比較
        - Max Q比較
        - パラメータ探索
        """
    )


with st.expander(
    "⬜ Phase 7 — Orbital Flight",
):
    st.markdown(
        """
        - 地球曲率
        - 重力ターン
        - 軌道投入
        - 軌道速度
        - 衛星軌道
        """
    )


with st.expander(
    "⬜ Phase 8 — Presentation Quality",
):
    st.markdown(
        """
        - Canvas飛行アニメーション
        - カメラ追従
        - 高度別背景
        - 炎・煙エフェクト
        - 完成版ポートフォリオページ
        """
    )

st.info(
    "機能の優先順位は、開発状況に応じて変更する可能性があります。"
)