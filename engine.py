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
    ・推力の方向分解
    ・燃料消費
    """

    @staticmethod
    def calculate_mass_flow_rate(
        fuel_mass: float,
        burn_time: float,
    ) -> float:
        """
        燃料質量と燃焼時間から、
        1秒あたりの推進剤流量を計算する。

        推進剤流量 = 燃料質量 / 燃焼時間
        """

        if burn_time <= 0:
            return 0.0

        return fuel_mass / burn_time

    @staticmethod
    def calculate_specific_impulse(
        thrust: float,
        mass_flow_rate: float,
    ) -> float:
        """
        推力と推進剤流量から比推力を計算する。

        Isp = F / (ṁ × g0)

        F:
            推力（N）

        ṁ:
            推進剤流量（kg/s）

        g0:
            標準重力加速度（m/s²）
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

        specific_impulse = (
            EngineCalculator.calculate_specific_impulse(
                thrust=thrust,
                mass_flow_rate=mass_flow_rate,
            )
        )

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

        thrust_x = (
            thrust
            * math.cos(launch_angle_radians)
        )

        thrust_y = (
            thrust
            * math.sin(launch_angle_radians)
        )

        consumed_fuel = (
            mass_flow_rate
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
            mass_flow_rate=mass_flow_rate,
            specific_impulse=specific_impulse,
        )