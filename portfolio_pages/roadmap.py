import streamlit as st


st.title("🗺️ Development Roadmap")

st.caption(
    "基本飛行・解析・推進性能・風モデル・多段ロケットまで実装済みです。"
)

st.header("Development Status")

st.progress(
    70,
    text="全体構想に対する現在の進捗イメージ：70%",
)

st.info(
    "Phase 5「Multi-stage Rocket」まで完了。"
    "次はPhase 6「Guidance & Flight Control」を開発予定です。"
)


with st.expander("✅ Phase 1 — Basic Flight Simulation"):
    st.markdown(
        """
        - ✅ 2次元飛行
        - ✅ 重力・標準大気
        - ✅ 空気抵抗
        - ✅ 燃料消費
        - ✅ Mach数・Max Q
        - ✅ 飛行イベント
        """
    )


with st.expander("✅ Phase 2 — Analysis Dashboard"):
    st.markdown(
        """
        - ✅ Streamlit Dashboard
        - ✅ 飛行サマリー
        - ✅ 解析グラフ
        - ✅ Flight Replay
        - ✅ CSV出力
        """
    )


with st.expander("✅ Phase 3 — Propulsion & Vehicle Performance"):
    st.markdown(
        """
        - ✅ エンジン性能モデル
        - ✅ 推力曲線
        - ✅ 推進剤流量
        - ✅ 比推力（Isp）
        - ✅ 推力重量比（T/W）
        - ✅ 総力積
        - ✅ Liftoff判定
        """
    )


with st.expander("✅ Phase 4 — Wind & Environment"):
    st.markdown(
        """
        - ✅ 高度別風速
        - ✅ 風向・横風
        - ✅ 突風
        - ✅ 相対風速
        - ✅ 風を考慮した空気抵抗
        """
    )


with st.expander("✅ Phase 5 — Multi-stage Rocket", expanded=True):
    st.markdown(
        """
        - ✅ 多段ロケット
        - ✅ ステージごとの機体・エンジン設定
        - ✅ ステージ分離
        - ✅ ブースター分離
        - ✅ フェアリング分離
        """
    )


with st.expander("🚧 Phase 6 — Guidance & Flight Control"):
    st.markdown(
        """
        - ✅ 時間による姿勢変更
        - ✅ ピッチプログラム
        - ⬜ 重力ターン
        - ⬜ 推力方向の動的変更
        - ⬜ 簡易姿勢制御
        """
    )


with st.expander("⬜ Phase 7 — Comparative Analysis"):
    st.markdown(
        """
        - ⬜ 複数条件の同時実行
        - ⬜ 軌跡比較
        - ⬜ 性能比較
        - ⬜ パラメータ探索
        """
    )


with st.expander("⬜ Phase 8 — Orbital Flight"):
    st.markdown(
        """
        - ⬜ 地球曲率
        - ⬜ 地球中心座標系
        - ⬜ 軌道速度
        - ⬜ 軌道投入
        - ⬜ 軌道力学
        """
    )


with st.expander("🚧 Phase 9 — Visualization & Presentation"):
    st.markdown(
        """
        **実装済み**
        - ✅ Flight Replay
        - ✅ ロケットアニメーション
        - ✅ 炎・煙
        - ✅ 高度による背景変化

        **今後**
        - ⬜ カメラ追従の高度化
        - ⬜ 発射台・地上設備
        - ⬜ 分離アニメーション
        - ⬜ 軌道飛行用の地球表示
        """
    )


with st.expander("⬜ Phase 10 — Validation & Engineering Quality"):
    st.markdown(
        """
        - ⬜ 単体テスト
        - ⬜ 物理計算の検証
        - ⬜ 質量・エネルギー収支
        - ⬜ 再現性確認
        - ⬜ 実在ロケットとの比較
        """
    )
