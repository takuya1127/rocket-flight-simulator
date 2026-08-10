import math

from dataclasses import dataclass

from core.atmosphere import AtmosphereCalculator
from analysis.flight_analysis import FlightAnalyzer
from core.gravity import GravityCalculator

@dataclass(frozen=True)
class PhysicsResult:
    """
    1ステップ分の物理計算結果。

    Attributes
    ----------
    total_mass: 現在のロケット総質量（kg）
    gravity: 現在高度の重力加速度（m/s²）
    air_density: 現在高度の空気密度（kg/m³）
    speed: 計算前の合成速度（m/s）
    dynamic_pressure: 動圧（Pa）
    drag_force_x: X方向の空気抵抗（N）
    drag_force_y: Y方向の空気抵抗（N）
    acceleration_x: X方向の加速度（m/s²）
    acceleration_y: Y方向の加速度（m/s²）
    """

    total_mass: float
    gravity: float
    air_density: float
    speed: float
    dynamic_pressure: float
    speed_of_sound: float
    drag_force_x: float
    drag_force_y: float
    acceleration_x: float
    acceleration_y: float

class PhysicsCalculator:
    """
    ロケットへ働く力と加速度を計算するクラス。
    以下の計算を担当する。

    ・現在の総質量
    ・高度に応じた重力
    ・高度に応じた大気状態
    ・動圧
    ・空気抵抗
    ・X方向、Y方向の合力
    ・X方向、Y方向の加速度
    """

    @staticmethod
    def calculate(
        *,
        dry_mass: float,
        current_fuel: float,
        position_y: float,
        velocity_x: float,
        velocity_y: float,
        wind_x: float,
        wind_y: float,
        thrust_x: float,
        thrust_y: float,
        drag_coefficient: float,
        reference_area: float,
    ) -> PhysicsResult:
        """
        現在の状態から1ステップ分の物理量を計算する。

        Parameters
        ----------
        dry_mass: 燃料を除いた機体質量（kg）
        current_fuel: 現在の燃料残量（kg）
        position_y: 現在高度（m）
        velocity_x: 現在のX方向速度（m/s）
        velocity_y: 現在のY方向速度（m/s）
        wind_x: X方向の風速（m/s）
        wind_y: Y方向の風速（m/s）
        thrust_x: X方向の推力（N）
        thrust_y: Y方向の推力（N）
        drag_coefficient: 抗力係数
        reference_area: 基準断面積（m²）

        Returns
        -------
        PhysicsResult: 現在の物理計算結果
        """

        # 現在のロケット総質量
        total_mass = (
            dry_mass
            + current_fuel
        )

        # 現在高度における重力加速度
        gravity = GravityCalculator.calculate(
            altitude_meters=position_y,
        )

        # 現在のロケットへ働く重力
        weight_force = (
            total_mass
            * gravity
        )

        # 現在高度における大気状態
        atmosphere = AtmosphereCalculator.calculate(
            position_y
        )

        air_density = atmosphere.density

        # X・Y方向を合わせた現在速度
        relative_velocity_x= (
            velocity_x - wind_x
        )

        relative_velocity_y= (
            velocity_y - wind_y
        )

        relative_speed = math.hypot(relative_velocity_x, relative_velocity_y)

        # 現在の動圧
        dynamic_pressure = (
            FlightAnalyzer.calculate_dynamic_pressure(
                air_density=air_density,
                speed=relative_speed,
            )
        )

        # 空気抵抗の初期値
        drag_force_x = 0.0
        drag_force_y = 0.0

        # 相対風速がある場合のみ空気抵抗を計算する
        if relative_speed > 0:
            # 空気抵抗の大きさ
            drag_force = (
                dynamic_pressure
                * drag_coefficient
                * reference_area
            )

            # 空気抵抗は進行方向と反対向き
            drag_force_x = (
                -drag_force
                * relative_velocity_x
                / relative_speed
            )

            drag_force_y = (
                -drag_force
                * relative_velocity_y
                / relative_speed
            )

        # X方向の合力
        net_force_x = (
            thrust_x
            + drag_force_x
        )

        # Y方向の合力
        net_force_y = (
            thrust_y
            - weight_force
            + drag_force_y
        )

        # X方向の加速度
        acceleration_x = (
            net_force_x
            / total_mass
        )

        # Y方向の加速度
        acceleration_y = (
            net_force_y
            / total_mass
        )

        return PhysicsResult(
            total_mass=total_mass,
            gravity=gravity,
            air_density=air_density,
            speed=relative_speed,
            dynamic_pressure=dynamic_pressure,
            drag_force_x=drag_force_x,
            drag_force_y=drag_force_y,
            acceleration_x=acceleration_x,
            acceleration_y=acceleration_y,
            speed_of_sound=atmosphere.speed_of_sound,
        )