from dataclasses import dataclass
from datetime import time


@dataclass(frozen=True)
class GuidanceResult:
    """
    1ステップ分の誘導計算結果。
    """

    pitch_angle: float

class GuidanceController:
    """
    ロケットの姿勢角を計算するクラス。

    Phase 6では、
    時間に応じてピッチ角を変化させる
    簡易Pitch Programから実装する。
    """

    @staticmethod
    def calculate_pitch_angle(
            *,
            time: float,
            initial_pitch_angle: float,
    ) -> GuidanceResult:
        """
            ロケットの姿勢角を計算するクラス。
            現段階では簡易Pitch Programとして、

            0〜5秒:初期姿勢を維持
            5〜25秒:徐々に水平方向へ傾ける
            25秒以降:45度を維持

            とする。
            """

        if time < 5.0:
            pitch_angle = initial_pitch_angle

        elif time < 25.0:
            progress = (time - 5.0) / 20.0

            target_pitch_angle = 45.0

            pitch_angle = (
                initial_pitch_angle
                + (
                target_pitch_angle - initial_pitch_angle
                )
                * progress
            )

        else:
            pitch_angle = 45.0

        return GuidanceResult(
            pitch_angle=pitch_angle,
        )