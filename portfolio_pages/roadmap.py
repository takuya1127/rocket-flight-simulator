import streamlit as st


st.title("🗺️ Development Roadmap")

st.caption(
    "基本飛行モデル・解析ダッシュボードを基盤として、"
    "現在は推進性能モデルの高度化を進めています。"
)


# ========================================
# 開発状況
# ========================================

st.header("Development Status")

st.progress(
    48,
    text="全体構想に対する現在の進捗イメージ：48%",
)

st.info(
    "現在は Phase 3「Propulsion & Vehicle Performance」を開発中です。"
)


# ========================================
# フェーズ
# ========================================

with st.expander(
    "✅ Phase 1 — Basic Flight Simulation",
):
    st.markdown(
        """
        - ✅ 2次元飛行
        - ✅ 推力の方向分解
        - ✅ 燃料消費・質量変化
        - ✅ 空気抵抗
        - ✅ 高度に応じた重力
        - ✅ 標準大気モデル
        - ✅ Mach数
        - ✅ Max Q
        - ✅ 飛行イベント
        - ✅ 発射から着地までのシミュレーション
        """
    )


with st.expander(
    "✅ Phase 2 — Analysis Dashboard",
):
    st.markdown(
        """
        - ✅ Streamlit Web UI
        - ✅ 飛行サマリー
        - ✅ 運動解析グラフ
        - ✅ 空力・環境解析
        - ✅ 機体状態解析
        - ✅ イベントタイムライン
        - ✅ CSV出力
        - ✅ PC・スマホ対応
        - ✅ 軽量Canvas飛行リプレイ
        """
    )


with st.expander(
    "🚧 Phase 3 — Propulsion & Vehicle Performance",
    expanded=True,
):
    st.markdown(
        """
        **実装済み**

        - ✅ エンジン計算を `EngineCalculator` へ分離
        - ✅ 推進剤流量
        - ✅ 比推力（Isp）
        - ✅ 推力重量比（T/W）の時系列解析
        - ✅ 推進性能専用ダッシュボード
        - ✅ 推力立ち上がり
        - ✅ 定常燃焼
        - ✅ 燃焼終了時の推力減衰
        - ✅ 推力に連動した推進剤流量

        **現在開発中 / 次に実装**

        - 🚧 点火とリフトオフの分離
        - ⬜ 発射台保持モデル
        - ⬜ T/W > 1による実リフトオフ判定
        - ⬜ Ignitionイベント
        - ⬜ エンジン性能サマリー

        **将来拡張**

        - ⬜ スロットル制御
        - ⬜ 高度によるエンジン性能変化
        - ⬜ 真空比推力・海面上比推力
        """
    )


with st.expander(
    "⬜ Phase 4 — Wind & Environment",
):
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


with st.expander(
    "⬜ Phase 5 — Multi-stage Rocket",
):
    st.markdown(
        """
        - ⬜ 多段ロケット
        - ⬜ ステージごとの質量・燃料・エンジン
        - ⬜ ブースター分離
        - ⬜ ステージ分離
        - ⬜ フェアリング分離
        - ⬜ 分離による質量変化
        - ⬜ 分離イベント
        """
    )


with st.expander(
    "⬜ Phase 6 — Guidance & Flight Control",
):
    st.markdown(
        """
        - ⬜ 時間による姿勢変更
        - ⬜ ピッチプログラム
        - ⬜ 重力ターン
        - ⬜ 推力方向の動的変更
        - ⬜ 簡易姿勢制御
        - ⬜ 飛行プロファイル設定
        """
    )


with st.expander(
    "⬜ Phase 7 — Comparative Analysis",
):
    st.markdown(
        """
        - ⬜ 複数条件の同時実行
        - ⬜ 軌跡比較
        - ⬜ 最高高度比較
        - ⬜ 最大速度比較
        - ⬜ Max Q比較
        - ⬜ 燃料効率比較
        - ⬜ エンジン性能比較
        - ⬜ パラメータ探索
        """
    )


with st.expander(
    "⬜ Phase 8 — Orbital Flight",
):
    st.markdown(
        """
        - ⬜ 地球曲率
        - ⬜ 地球中心座標系
        - ⬜ 水平速度による軌道飛行
        - ⬜ 軌道速度
        - ⬜ 軌道投入判定
        - ⬜ 近地点・遠地点
        - ⬜ 衛星軌道
        """
    )


with st.expander(
    "🚧 Phase 9 — Visualization & Presentation",
):
    st.markdown(
        """
        **実装済み**

        - ✅ Canvas飛行アニメーション
        - ✅ ロケット画像表示
        - ✅ 機体角度に応じた回転
        - ✅ 炎エフェクト
        - ✅ 煙エフェクト
        - ✅ 雲レイヤー
        - ✅ 高度に応じた空の色変化
        - ✅ 再生・一時停止
        - ✅ タイムライン操作
        - ✅ PC・スマホ対応

        **今後**

        - ⬜ カメラ追従の高度化
        - ⬜ 発射台・地上設備
        - ⬜ ステージ分離アニメーション
        - ⬜ 軌道飛行用の地球表示
        - ⬜ 完成版ポートフォリオUI
        """
    )


with st.expander(
    "⬜ Phase 10 — Validation & Engineering Quality",
):
    st.markdown(
        """
        - ⬜ 単体テスト
        - ⬜ 物理計算の検証
        - ⬜ エネルギー・質量収支チェック
        - ⬜ 異常入力テスト
        - ⬜ シミュレーション結果の再現性確認
        - ⬜ 実在ロケットとの簡易比較
        - ⬜ 計算モデル・制約条件の文書化
        """
    )


st.info(
    "ロードマップは、シミュレーション精度・設計品質・"
    "ポートフォリオとしての完成度をバランスよく高める方針で更新しています。"
)