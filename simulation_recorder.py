from dataclasses import dataclass, field

@dataclass
class SimulationRecorder:
    """
    ロケットシミュレーションの時系列データを記録する。
    書く計算ステップで求めた位置・速度・加速度・機体状態などを、
    同じ時刻のデータとしてまとめて保存する。
    """

    #時刻
    times: list[float] = field(default_factory=list)
    #位置
    positions_x: list[float] = field(default_factory=list)
    positions_y: list[float] = field(default_factory=list)
    #速度
    velocities_x: list[float] = field(default_factory=list)
    velocities_y: list[float] = field(default_factory=list)
    #加速度
    accelerations_x: list[float] = field(default_factory=list)
    accelerations_y: list[float] = field(default_factory=list)
    #飛行状態
    flight_angles: list[float] = field(default_factory=list)
    dynamic_pressures: list[float] = field(default_factory=list)
    mach_numbers: list[float] = field(default_factory=list)
    gravities: list[float] = field(default_factory=list)
    #機体状態
    total_masses: list[float] = field(default_factory=list)
    remaining_fuels: list[float] = field(default_factory=list)
    thrusts: list[float] = field(default_factory=list)

    def record(
        self,
        *,
        time:float,
        position_x:float,
        position_y:float,
        velocity_x:float,
        velocity_y:float,
        acceleration_x:float,
        acceleration_y:float,
        flight_angle:float,
        dynamic_pressure:list[float],
        mach_number:float,
        gravity:list[float],
        total_mass:list[float],
        remaining_fuel:list[float],
        thrust:list[float],
    ) -> None:
        """
        現在のシミュレーション状態を保存する。

        Parameters
        ----------
        time: 現在時刻（秒）
        position_x: 水平方向の位置（m）
        position_y: 高度（m）
        velocity_x: X方向速度（m/s）
        velocity_y: Y方向速度（m/s）
        acceleration_x: X方向加速度（m/s²）
        acceleration_y: Y方向加速度（m/s²）
        flight_angle: 進行方向の角度（度）
        dynamic_pressure: 動圧（Pa）
        mach_number: マッハ数
        gravity: 重力加速度（m/s²）
        total_mass: ロケットの総質量（kg）
        remaining_fuel: 燃料残量（kg）
        thrust: 現在の推力（N）
        """

        self.times.append(time)
        self.positions_x.append(position_x)
        #地面より下の高度は0mとして保存
        self.positions_y.append(
            max(0.0, position_y)
        )
        self.velocities_x.append(velocity_x)
        self.velocities_y.append(velocity_y)
        self.accelerations_x.append(acceleration_x)
        self.accelerations_y.append(acceleration_y)
        self.flight_angles.append(flight_angle)
        self.dynamic_pressures.append(dynamic_pressure)
        self.mach_numbers.append(mach_number)
        self.gravities.append(gravity)
        self.total_masses.append(total_mass)
        self.remaining_fuels.append(remaining_fuel)
        self.thrusts.append(thrust)

    def to_result_kwargs(
        self,
    ) -> dict[str, list[float]]:
        """
       SimulationResultへ渡す時系列データを辞書で返す。

       Returns
       -----------
       dict[str, list[float]]:
           SimulationResultの初期化に使用できるデータ
       """
        return{
            "times": self.times,
            "positions_x": self.positions_x,
            "positions_y": self.positions_y,
            "velocities_x": self.velocities_x,
            "velocities_y": self.velocities_y,
            "accelerations_x": self.accelerations_x,
            "accelerations_y": self.accelerations_y,
            "flight_angles": self.flight_angles,
            "dynamic_pressures": self.dynamic_pressures,
            "mach_numbers": self.mach_numbers,
            "gravities": self.gravities,
            "total_masses": self.total_masses,
            "remaining_fuels": self.remaining_fuels,
            "thrusts": self.thrusts,
        }