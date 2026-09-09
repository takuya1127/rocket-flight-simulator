import streamlit as st


st.title("🗺️ Development Roadmap")

st.caption(
    "Phase 7「Comparative Analysis」まで実装済み。"
    "次はPhase 8「Orbital Flight」です。"
)

st.header("Development Status")

st.progress(
    47,
    text="全15フェーズ中、Phase 7まで完了：47%",
)

st.info(
    "Phase 7「Comparative Analysis」まで完了。"
    "次は地球曲率・軌道速度・軌道投入を扱う"
    "Phase 8「Orbital Flight」に進みます。"
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


with st.expander("✅ Phase 5 — Multi-stage Rocket"):
    st.markdown(
        """
        - ✅ 多段ロケット
        - ✅ ステージごとの機体・エンジン設定
        - ✅ ステージ分離
        - ✅ ブースター分離
        - ✅ フェアリング分離
        """
    )


with st.expander("✅ Phase 6 — Guidance & Flight Control"):
    st.markdown(
        """
        - ✅ 時間による姿勢変更
        - ✅ ピッチプログラム
        - ✅ 重力ターン
        - ✅ 推力方向の動的変更
        - ✅ Pitch Rate制限による簡易姿勢制御
        - ✅ 目標姿勢角・姿勢角の可視化
        """
    )


with st.expander("✅ Phase 7 — Comparative Analysis", expanded=True):
    st.markdown(
        """
        - ✅ 複数条件の連続実行
        - ✅ パラメータスイープ
        - ✅ 比較結果テーブル
        - ✅ ベスト条件の自動ハイライト
        - ✅ 軌跡比較
        - ✅ 性能比較
        - ✅ 比較結果CSV出力
        """
    )


with st.expander("⬜ Phase 8 — Orbital Flight", expanded=True):
    st.markdown(
        """
        - ⬜ 地球曲率
        - ⬜ 地球中心座標系
        - ⬜ 軌道速度
        - ⬜ 軌道投入
        - ⬜ 軌道力学
        """
    )


with st.expander("⬜ Phase 9 — High-Fidelity Vehicle Model"):
    st.markdown(
        """
        - ⬜ 高度・大気圧によるエンジン性能変化
        - ⬜ 詳細な空力係数
        - ⬜ 揚力・迎角
        - ⬜ 機体形状・基準断面積の変化
        - ⬜ より詳細な質量特性
        """
    )


with st.expander("⬜ Phase 10 — Environmental Disturbances"):
    st.markdown(
        """
        - ⬜ 大気モデルの高精度化
        - ⬜ 現実的な風速プロファイル
        - ⬜ 乱気流・突風外乱
        - ⬜ 地球自転の影響
        - ⬜ 環境条件の不確実性
        """
    )


with st.expander("⬜ Phase 11 — Validation & Engineering Quality"):
    st.markdown(
        """
        - ⬜ 単体テスト
        - ⬜ 物理計算の検証
        - ⬜ 質量・エネルギー収支
        - ⬜ 再現性確認
        - ⬜ 実在ロケットとの比較
        """
    )


with st.expander("⬜ Phase 12 — Monte Carlo Simulation"):
    st.markdown(
        """
        - ⬜ 大量反復シミュレーション
        - ⬜ パラメータ不確実性
        - ⬜ 統計解析
        - ⬜ 成功確率の推定
        - ⬜ 結果分布の可視化
        """
    )


with st.expander("⬜ Phase 13 — Automatic Optimization"):
    st.markdown(
        """
        - ⬜ パラメータ自動探索
        - ⬜ 誘導パラメータ最適化
        - ⬜ 機体パラメータ最適化
        - ⬜ 目的関数・制約条件評価
        - ⬜ 宇宙・軌道到達性能の改善
        """
    )


with st.expander("⬜ Phase 14 — Mission & Failure Analysis"):
    st.markdown(
        """
        - ⬜ ミッション成功条件
        - ⬜ 故障シナリオ
        - ⬜ 感度解析
        - ⬜ 信頼性評価
        - ⬜ ミッション単位の性能解析
        """
    )


with st.expander("⬜ Phase 15 — Advanced Visualization"):
    st.markdown(
        """
        - ⬜ カメラ追従の高度化
        - ⬜ 発射台・地上設備
        - ⬜ 分離アニメーション
        - ⬜ 軌道飛行の可視化
        - ⬜ Monte Carlo・最適化結果の可視化
        """
    )
