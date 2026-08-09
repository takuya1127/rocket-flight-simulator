import math

from dataclasses import dataclass

from gravity import GravityCalculator


@dataclass(frozen=True)
class EngineResult:
    """
    1ステップ分のエンジン計算結果。

    Attributes
    ----------
    engine_is_burning:
        エンジンが燃焼中かどうか

    thrust_x:
        X方向の推力（N）

    thrust_y:
        Y方向の推力（N）

    thrust_magnitude:
        現在の推力の大きさ（N）

    remaining_fuel:
        計算後の燃料残量（kg）

    mass_flow_rate:
        推進剤流量（kg/s）

    specific_impulse:
        比推力（秒）
    """

    engine_is_burning: bool

    thrust_x: float
    thrust_y: float
    thrust_magnitude: float

    remaining_fuel: float

    mass_flow_rate: float
    specific_impulse: float


class EngineCalculator:
    """
    ロケットエンジンの性能と燃料消費を計算するクラス。

    現在は以下を担当する。

    ・燃焼状態
    ・推進剤流量
    ・比推力
    ・推力曲線
    ・推力の方向分解
    ・燃料消費
    """

    @staticmethod
    def calculate_mass_flow_rate(
        fuel_mass: float,
        burn_time: float,
    ) -> float:
        """
        推力曲線を考慮した、
        最大推進剤流量を計算する。

        推力の立ち上がり・減衰中は流量も減るため、
        燃焼終了時に燃料を使い切るよう補正する。
        """

        if burn_time <= 0:
            return 0.0

        rise_time = min(
            2.0,
            burn_time * 0.2,
        )

        fall_time = min(
            3.0,
            burn_time * 0.2,
        )

        effective_burn_time = (
            burn_time
            - rise_time / 2
            - fall_time / 2
        )

        if effective_burn_time <= 0:
            return 0.0

        return (
            fuel_mass
            / effective_burn_time
        )

    @staticmethod
    def calculate_specific_impulse(
        thrust: float,
        mass_flow_rate: float,
    ) -> float:
        """
        推力と推進剤流量から比推力を計算する。

        Isp = F / (ṁ × g0)
        """

        if mass_flow_rate <= 0:
            return 0.0

        return (
            thrust
            / (
                mass_flow_rate
                * GravityCalculator.SURFACE_GRAVITY
            )
        )

    @staticmethod
    def calculate_thrust_ratio(
        time: float,
        burn_time: float,
    ) -> float:
        """
        燃焼時間中の推力割合を0.0～1.0で返す。

        ・点火直後：徐々に推力上昇
        ・定常燃焼：100%
        ・燃焼終了直前：徐々に推力低下
        """

        if time < 0 or time >= burn_time:
            return 0.0

        rise_time = min(
            2.0,
            burn_time * 0.2,
        )

        fall_time = min(
            3.0,
            burn_time * 0.2,
        )

        fall_start_time = (
            burn_time
            - fall_time
        )

        # 推力立ち上がり
        if time < rise_time:
            return (
                time
                / rise_time
            )

        # 推力減衰
        if time >= fall_start_time:
            return (
                burn_time - time
            ) / fall_time

        # 定常燃焼
        return 1.0

    @staticmethod
    def calculate(
        *,
        time: float,
        burn_time: float,
        thrust: float,
        launch_angle_radians: float,
        current_fuel: float,
        mass_flow_rate: float,
        time_step: float,
    ) -> EngineResult:
        """
        1ステップ分のエンジン状態を計算する。
        """

        engine_is_burning = (
            time < burn_time
            and current_fuel > 0
        )

        if not engine_is_burning:
            return EngineResult(
                engine_is_burning=False,
                thrust_x=0.0,
                thrust_y=0.0,
                thrust_magnitude=0.0,
                remaining_fuel=current_fuel,
                mass_flow_rate=0.0,
                specific_impulse=0.0,
            )

        # 現在時刻の推力割合
        thrust_ratio = (
            EngineCalculator.calculate_thrust_ratio(
                time=time,
                burn_time=burn_time,
            )
        )

        # 現在推力
        current_thrust = (
            thrust
            * thrust_ratio
        )

        # 現在の推進剤流量
        current_mass_flow_rate = (
            mass_flow_rate
            * thrust_ratio
        )

        # 現在の比推力
        specific_impulse = (
            EngineCalculator.calculate_specific_impulse(
                thrust=current_thrust,
                mass_flow_rate=current_mass_flow_rate,
            )
        )

        # 推力をX・Y方向へ分解
        thrust_x = (
            current_thrust
            * math.cos(launch_angle_radians)
        )

        thrust_y = (
            current_thrust
            * math.sin(launch_angle_radians)
        )

        # 今回の時間ステップで消費する燃料
        consumed_fuel = (
            current_mass_flow_rate
            * time_step
        )

        remaining_fuel = max(
            0.0,
            current_fuel - consumed_fuel,
        )

        thrust_magnitude = math.hypot(
            thrust_x,
            thrust_y,
        )

        return EngineResult(
            engine_is_burning=True,
            thrust_x=thrust_x,
            thrust_y=thrust_y,
            thrust_magnitude=thrust_magnitude,
            remaining_fuel=remaining_fuel,
            mass_flow_rate=current_mass_flow_rate,
            specific_impulse=specific_impulse,
        )