from enum import Enum
from dataclasses import dataclass

from models.simulation_models import StageConfig

class StageStatus(Enum):
    """
    ステージの現在状態。
    """

    READY = "Ready"
    BURNING = "Burning"
    BURNOUT = "Burnout"
    SEPARATED = "Separated"

@dataclass(frozen=True)
class StageState:
    """
    現在のステージ状態を表す。

    Attributes
    ----------
    stage_index:現在のステージ番号。 Pythonのlistに合わせて0始まり。
    stage:現在使用中のStageConfig。
    has_next_stage:次のステージが存在するか。
    """

    stage_index: int
    stage: StageConfig
    has_next_stage: bool

class StageManager:
    """
    多段ロケットのステージ状態を管理するクラス。
    """
    def __init__(
        self,
        *,
        stages: list[StageConfig],
    ) -> None:

        if not stages:
            raise ValueError(
                "少なくとも１つのステージが必要です。"
            )

        self._stages = stages
        self._current_stage_index = 0
        self._current_status = StageStatus.READY

    @property
    def current_stage_index(self) -> int:
        """
        現在のステージ番号を返す。
        """
        return self._current_stage_index

    @property
    def current_stage(self) -> StageConfig:
        """
        現在使用中のStageConfigを返す。
        """

        return self._stages[self._current_stage_index]

    @property
    def stage_count(self) -> int:
        """
        全ステージ数を返す。
        """

        return len(self._stages)

    @property
    def has_next_stage(self) -> bool:
        """
        次のステージが存在するかを返す。
        """
        return (self._current_stage_index
                < len(self._stages) -1
                )

    @property
    def remaining_stages(self) -> list[StageConfig]:
        """
        現在のステージ以降に残っている
        ステージ一覧を返す。
        """

        return self._stages[self._current_stage_index:]

    @property
    def remaining_dry_mass(self) -> float:
        """現在残っている全ステージの
        乾燥質量合計を返す。
        """

        return sum(
            stage.dry_mass
            for stage in self.remaining_stages
        )

    @property
    def remaining_initial_mass(self) -> float:
        """
        現在残っている全ステージの
        燃料込み処置室量合計を返す。
        """

        return sum(
            stage.initial_total_mass
            for stage in self.remaining_stages
        )

    def get_state(self)->StageState:
        """
        現在のステージ状態をまとめて返す。
        """

        return StageState(
            stage_index=self._current_stage_index,
            stage=self.current_stage,
            has_next_stage=self.has_next_stage,
        )

    def separate_stage(self) -> bool:
        """
        現在のステージを分離し、次のステージへ切り替える。
        """

        if self._current_status != StageStatus.BURNOUT:
            return False

        if not self.has_next_stage:
            return False

        self._current_status = StageStatus.SEPARATED

        self._current_stage_index += 1

        self._current_status = StageStatus.READY

        return True

    @property
    def current_status(self) -> StageStatus:
        """
        現在のステージ状態を返す。
        """
        return self._current_status

    def ignite_current_stage(self) -> bool:
        """
        現在のステージ点火状態へ切り替える・
        """

        if self._current_status != StageStatus.READY:
            return False

        self._current_status = StageStatus.BURNING

        return True

    def burnout_current_stage(self) -> bool:
        """
        現在のステージを燃焼終了状態へ切り替える。
        """

        if self._current_status != StageStatus.BURNING:
            return False

        self._current_status = StageStatus.BURNOUT

        return True