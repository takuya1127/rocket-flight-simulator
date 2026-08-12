from dataclasses import dataclass, field


@dataclass
class SimulationRecorder:
    """
    ロケットシミュレーションの時系列データを記録する。

    各計算ステップで求めた位置・速度・加速度・
    飛行状態・機体状態・推進性能を、
    同じ時刻のデータとしてまとめて保存する。
    """

    # ========================================
    # 時刻
    # ========================================

    times: list[float] = field(default_factory=list)

    # ========================================
    # 位置
    # ========================================

    positions_x: list[float] = field(default_factory=list)
    positions_y: list[float] = field(default_factory=list)

    # ========================================
    # 速度
    # ========================================

    velocities_x: list[float] = field(default_factory=list)
    velocities_y: list[float] = field(default_factory=list)

    # ========================================
    # 加速度
    # ========================================

    accelerations_x: list[float] = field(default_factory=list)
    accelerations_y: list[float] = field(default_factory=list)

    # ========================================
    # 飛行状態
    # ========================================

    flight_angles: list[float] = field(default_factory=list)
    pitch_angles: list[float] = field(default_factory=list)

    dynamic_pressures: list[float] = field(default_factory=list)
    mach_numbers: list[float] = field(default_factory=list)
    gravities: list[float] = field(default_factory=list)

    # ========================================
    # 機体状態
    # ========================================

    total_masses: list[float] = field(default_factory=list)
    remaining_fuels: list[float] = field(default_factory=list)

    # ========================================
    # 推進性能
    # ========================================

    thrusts: list[float] = field(default_factory=list)
    mass_flow_rates: list[float] = field(default_factory=list)
    specific_impulses: list[float] = field(default_factory=list)
    thrust_to_weight_ratios: list[float] = field(
        default_factory=list
    )

    def record(
        self,
        *,
        time: float,
        position_x: float,
        position_y: float,
        velocity_x: float,
        velocity_y: float,
        acceleration_x: float,
        acceleration_y: float,
        flight_angle: float,
        pitch_angle: float,
        dynamic_pressure: float,
        mach_number: float,
        gravity: float,
        total_mass: float,
        remaining_fuel: float,
        thrust: float,
        mass_flow_rate: float,
        specific_impulse: float,
        thrust_to_weight_ratio: float,
    ) -> None:
        """
        現在のシミュレーション状態を保存する。
        """

        self.times.append(time)

        self.positions_x.append(position_x)
        self.positions_y.append(
            max(0.0, position_y)
        )

        self.velocities_x.append(velocity_x)
        self.velocities_y.append(velocity_y)

        self.accelerations_x.append(acceleration_x)
        self.accelerations_y.append(acceleration_y)

        self.flight_angles.append(flight_angle)
        self.pitch_angles.append(pitch_angle)

        self.dynamic_pressures.append(dynamic_pressure)
        self.mach_numbers.append(mach_number)
        self.gravities.append(gravity)

        self.total_masses.append(total_mass)
        self.remaining_fuels.append(remaining_fuel)

        self.thrusts.append(thrust)
        self.mass_flow_rates.append(mass_flow_rate)
        self.specific_impulses.append(specific_impulse)
        self.thrust_to_weight_ratios.append(
            thrust_to_weight_ratio
        )

    def to_result_kwargs(
        self,
    ) -> dict[str, list[float]]:
        """
        SimulationResultへ渡す時系列データを辞書で返す。
        """

        return {
            "times": self.times,
            "positions_x": self.positions_x,
            "positions_y": self.positions_y,
            "velocities_x": self.velocities_x,
            "velocities_y": self.velocities_y,
            "accelerations_x": self.accelerations_x,
            "accelerations_y": self.accelerations_y,
            "flight_angles": self.flight_angles,
            "pitch_angles": self.pitch_angles,
            "dynamic_pressures": self.dynamic_pressures,
            "mach_numbers": self.mach_numbers,
            "gravities": self.gravities,
            "total_masses": self.total_masses,
            "remaining_fuels": self.remaining_fuels,
            "thrusts": self.thrusts,
            "mass_flow_rates": self.mass_flow_rates,
            "specific_impulses": self.specific_impulses,
            "thrust_to_weight_ratios": (
                self.thrust_to_weight_ratios
            ),
        }
