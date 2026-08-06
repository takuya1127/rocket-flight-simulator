from flight_event import FlightEvent
from dataclasses import dataclass


@dataclass
class RocketConfig:
    """
    ロケットの設定情報
    """

    dry_mass: float
    fuel_mass: float
    thrust: float
    burn_time: float
    launch_angle: float
    #空気抵抗係数　小さいほど空気抵抗を受けにくい
    drag_coefficient: float = 0.5
    #空気を正面から受ける面積
    reference_area: float = 0.1


@dataclass
class SimulationResult:
    """
    シミュレーション結果
    """

    times: list[float]
    positions_x: list[float]
    positions_y: list[float]

    velocities_x: list[float]
    velocities_y: list[float]

    accelerations_x: list[float]
    accelerations_y: list[float]

    flight_angles: list[float]

    mach_numbers: list[float]
    dynamic_pressures: list[float]

    max_altitude: float
    max_velocity: float
    flight_time: float

    max_dynamic_pressure: float
    max_q_time: float
    max_q_altitude: float
    max_q_speed: float
    max_mach_number: float
    gravities: list[float]

    total_masses: list[float]
    remaining_fuels: list[float]
    thrusts: list[float]

    # 音速を突破していない場合はNone
    sonic_boom_time: float | None
    sonic_boom_altitude: float | None
    sonic_boom_speed: float | None
    sonic_boom_mach_number: float | None

    flight_events: list[FlightEvent]
