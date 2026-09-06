from dataclasses import dataclass


@dataclass(frozen=True)
class GuidanceResult:
    """
    1ステップ分の誘導計算結果。
    """

    pitch_angle: float
    target_pitch_angle: float

class GuidanceController:
    """
    ロケットの姿勢角を計算するクラス。

    Phase 6では、
    ・初期姿勢維持
    ・Pitch Program
    ・簡易Gravity Turn
    を担当する。
    """

    @staticmethod
    def calculate_pitch_angle(
        *,
        time: float,
        initial_pitch_angle: float,
        flight_angle: float,
        previous_pitch_angle: float,
        has_launched: bool,
        engine_is_burning: bool,
        time_step: float,
    ) -> GuidanceResult:
        """
        現在の飛行状態から姿勢角を計算する。
        """

        # ========================================
        # 発射前
        # ========================================

        if not has_launched:
            return GuidanceResult(
                pitch_angle=initial_pitch_angle,
                target_pitch_angle=initial_pitch_angle,
            )

        # ========================================
        # 初期上昇
        # 0～5秒
        # ========================================

        if time < 5.0:
            return GuidanceResult(
                pitch_angle=initial_pitch_angle,
                target_pitch_angle=initial_pitch_angle,
            )

        # ========================================
        # Pitch Program
        # 5～15秒
        # ========================================

        if time < 15.0:
            progress = (
                (time - 5.0)
                / 10.0
            )

            target_pitch_angle = 65.0

            pitch_angle = (
                initial_pitch_angle
                + (
                    target_pitch_angle
                    - initial_pitch_angle
                )
                * progress
            )

            return GuidanceResult(
                pitch_angle=pitch_angle,
                target_pitch_angle=pitch_angle,
            )

        # ========================================
        # エンジン停止後
        # ========================================

        if not engine_is_burning:
            # 燃焼終了後は誘導による姿勢変更を行わない
            return GuidanceResult(
                pitch_angle=previous_pitch_angle,
                target_pitch_angle=previous_pitch_angle,
            )

        # ========================================
        # Gravity Turn
        # ========================================

        # 上昇中のGravity Turnでは、
        # 0～90度の範囲だけを目標とする。
        target_pitch_angle = max(
            0.0,
            min(
                90.0,
                flight_angle,
            ),
        )

        max_pitch_rate = 3.0

        max_pitch_change = (max_pitch_rate * time_step)
        pitch_error = (target_pitch_angle - previous_pitch_angle)
        pitch_change = max(-max_pitch_change, min(max_pitch_change, pitch_error))
        pitch_angle = (previous_pitch_angle + pitch_change)

        # 数値誤差などで範囲外へ出ないようにする
        pitch_angle = max(
            0.0,
            min(
                90.0,
                pitch_angle,
            ),
        )

        return GuidanceResult(
            pitch_angle=pitch_angle,
            target_pitch_angle=target_pitch_angle,
        )