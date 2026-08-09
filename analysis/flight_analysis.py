from dataclasses import dataclass


@dataclass(frozen=True)
class MaxQRecord:
    """
    Max Qが発生した瞬間の情報。

    Attributes
    ----------
    dynamic_pressure:
        最大動圧（Pa）

    time:
        Max Q発生時刻（秒）

    altitude:
        Max Q発生高度（m）

    speed:
        Max Q発生時の速度（m/s）
    """

    dynamic_pressure: float
    time: float
    altitude: float
    speed: float


@dataclass(frozen=True)
class SonicBoomRecord:
    """
    初めて音速を突破した瞬間の情報。

    Attributes
    ----------
    time:
        音速突破時刻（秒）

    altitude:
        音速突破高度（m）

    speed:
        音速突破時の速度（m/s）

    mach_number:
        音速突破時のマッハ数
    """

    time: float
    altitude: float
    speed: float
    mach_number: float


class FlightAnalyzer:
    """
    ロケットの飛行結果を解析するクラス。

    現在は以下を担当する。

    ・動圧の計算
    ・Max Qの記録
    ・マッハ数の計算
    ・音速突破の検知と記録
    """

    def __init__(self) -> None:
        """
        飛行解析に必要な初期値を設定する。
        """

        # Max Qの初期値
        self._max_q_record = MaxQRecord(
            dynamic_pressure=0.0,
            time=0.0,
            altitude=0.0,
            speed=0.0,
        )

        # 前回計算時のマッハ数
        self._previous_mach_number = 0.0

        # 音速突破前は記録が存在しないためNone
        self._sonic_boom_record: SonicBoomRecord | None = None

    @staticmethod
    def calculate_dynamic_pressure(
        air_density: float,
        speed: float,
    ) -> float:
        """
        空気密度と速度から動圧を計算する。

        計算式

        q = 1 / 2 × 空気密度 × 速度²

        Parameters
        ----------
        air_density:
            空気密度（kg/m³）

        speed:
            ロケットの速度（m/s）

        Returns
        -------
        float:
            動圧（Pa）
        """

        return (
            0.5
            * air_density
            * speed ** 2
        )

    def update_max_q(
        self,
        dynamic_pressure: float,
        time: float,
        altitude: float,
        speed: float,
    ) -> None:
        """
        現在の動圧が過去最大の場合、
        Max Q情報を更新する。

        Parameters
        ----------
        dynamic_pressure:
            現在の動圧（Pa）

        time:
            現在時刻（秒）

        altitude:
            現在高度（m）

        speed:
            現在速度（m/s）
        """

        # 過去最大以下なら更新しない
        if (
            dynamic_pressure
            <= self._max_q_record.dynamic_pressure
        ):
            return

        self._max_q_record = MaxQRecord(
            dynamic_pressure=dynamic_pressure,
            time=time,
            altitude=altitude,
            speed=speed,
        )

    def get_max_q_record(self) -> MaxQRecord:
        """
        記録されたMax Q情報を返す。

        Returns
        -------
        MaxQRecord:
            Max Q発生時の情報
        """

        return self._max_q_record

    @staticmethod
    def calculate_mach_number(
        speed: float,
        speed_of_sound: float,
    ) -> float:
        """
        現在速度と音速からマッハ数を計算する。

        Parameters
        ----------
        speed:
            現在速度（m/s）

        speed_of_sound:
            現在高度における音速（m/s）

        Returns
        -------
        float:
            マッハ数
        """

        # 0除算を防ぐ
        if speed_of_sound <= 0:
            return 0.0

        return speed / speed_of_sound

    def update_sonic_boom(
        self,
        mach_number: float,
        time: float,
        altitude: float,
        speed: float,
    ) -> bool:
        """
        マッハ1を初めて突破した瞬間を検知して記録する。

        Parameters
        ----------
        mach_number:
            現在のマッハ数

        time:
            現在時刻（秒）

        altitude:
            現在高度（m）

        speed:
            現在速度（m/s）

        Returns
        -------
        bool:
            今回初めて音速を突破した場合はTrue。
            それ以外はFalse。
        """

        # 前回はMach 1未満で、
        # 今回Mach 1以上になったかを判定する
        crossed_mach_one = (
            self._previous_mach_number < 1.0
            and mach_number >= 1.0
        )

        # 初回の音速突破だけ記録する
        if (
            crossed_mach_one
            and self._sonic_boom_record is None
        ):
            self._sonic_boom_record = SonicBoomRecord(
                time=time,
                altitude=altitude,
                speed=speed,
                mach_number=mach_number,
            )

            # 次回判定用に現在値を保存
            self._previous_mach_number = mach_number

            return True

        # 突破しなかった場合も、
        # 次回判定用に現在値を保存する
        self._previous_mach_number = mach_number

        return False

    def get_sonic_boom_record(
        self,
    ) -> SonicBoomRecord | None:
        """
        初めて音速を突破した瞬間の情報を返す。

        Returns
        -------
        SonicBoomRecord | None:
            音速を突破済みなら記録を返す。
            未突破ならNoneを返す。
        """

        return self._sonic_boom_record