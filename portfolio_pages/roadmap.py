import streamlit as st


st.title("🗺️ Development Roadmap")

st.caption(
    "基本飛行モデル・解析ダッシュボード・推進性能モデルまで実装済みです。"
)

st.header("Development Status")

st.progress(
    55,
    text="全体構想に対する現在の進捗イメージ：55%",
)

st.info(
    "Phase 3「Propulsion & Vehicle Performance」まで完了。"
    "次はPhase 4「Wind & Environment」を開発予定です。"
)

with st.expander("✅ Phase 1 — Basic Flight Simulation"):
    st.markdown(
        """
        - ✅ 2次元飛行
        - ✅ 推力
        - ✅ 燃料消費
        - ✅ 空気抵抗
        - ✅ 可変重力
        - ✅ 標準大気
        - ✅ Mach数
        - ✅ Max Q
        - ✅ 飛行イベント
        """
    )

with st.expander("✅ Phase 2 — Analysis Dashboard"):
    st.markdown(
        """
        - ✅ Streamlit
        - ✅ 飛行サマリー
        - ✅ 解析グラフ
        - ✅ 飛行リプレイ
        - ✅ イベント一覧
        - ✅ CSV出力
        - ✅ PC・スマホ対応
        """
    )

with st.expander("✅ Phase 3 — Propulsion & Vehicle Performance", expanded=True):
    st.markdown(
        """
        - ✅ EngineCalculator分離
        - ✅ 推進剤流量
        - ✅ 比推力（Isp）
        - ✅ 推力重量比（T/W）
        - ✅ 推力曲線
        - ✅ 推力立ち上がり
        - ✅ 定常燃焼
        - ✅ 推力減衰
        - ✅ Ignitionイベント
        - ✅ 発射台保持
        - ✅ Liftoff判定
        - ✅ 総力積
        - ✅ エンジン性能サマリー
        - ✅ 推進性能ダッシュボード
        """
    )

with st.expander("🚧 Phase 4 — Wind & Environment"):
    st.markdown(
        """
        - ⬜ 一定風
        - ⬜ 高度別風速
        - ⬜ 横風
        - ⬜ 突風
        - ⬜ 相対風速を考慮した空気抵抗
        - ⬜ 風あり・なし比較
        """
    )

with st.expander("⬜ Phase 5 — Multi-stage Rocket"):
    st.markdown(
        """
        - ⬜ 多段ロケット
        - ⬜ ステージごとの質量・燃料・エンジン
        - ⬜ ブースター分離
        - ⬜ ステージ分離
        - ⬜ フェアリング分離
        """
    )

with st.expander("⬜ Phase 6 — Guidance & Flight Control"):
    st.markdown(
        """
        - ⬜ 時間による姿勢変更
        - ⬜ ピッチプログラム
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
        - ⬜ 最高高度比較
        - ⬜ Max Q比較
        - ⬜ パラメータ探索
        """
    )

with st.expander("⬜ Phase 8 — Orbital Flight"):
    st.markdown(
        """
        - ⬜ 地球曲率
        - ⬜ 地球中心座標系
        - ⬜ 軌道速度
        - ⬜ 軌道投入判定
        - ⬜ 近地点・遠地点
        - ⬜ 衛星軌道
        """
    )

with st.expander("🚧 Phase 9 — Visualization & Presentation"):
    st.markdown(
        """
        **実装済み**
        - ✅ Canvas飛行アニメーション
        - ✅ ロケット画像
        - ✅ 機体回転
        - ✅ 炎・煙
        - ✅ 雲
        - ✅ 高度による空の色変化
        - ✅ 再生・一時停止
        - ✅ タイムライン

        **今後**
        - ⬜ カメラ追従の高度化
        - ⬜ 発射台・地上設備
        - ⬜ ステージ分離アニメーション
        - ⬜ 軌道飛行用の地球表示
        """
    )

with st.expander("⬜ Phase 10 — Validation & Engineering Quality"):
    st.markdown(
        """
        - ⬜ 単体テスト
        - ⬜ 物理計算の検証
        - ⬜ 質量・エネルギー収支チェック
        - ⬜ 異常入力テスト
        - ⬜ 再現性確認
        - ⬜ 実在ロケットとの簡易比較
        """
    )
