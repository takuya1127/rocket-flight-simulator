from flight_event import FlightEvent
from dataclasses import dataclass


@dataclass
class RocketConfig:
    """
    ロケットの設定情報
    """

    #ロケット本体・タンク・外装などの構造質量(kg)
    structure_mass: float
    #エンジン本体の質量(kg)
    engine_mass: float
    #衛星・貨物などの搭載物質量(kg)
    payload_mass: float
    #初期燃料質量(kg)
    fuel_mass: float
    #エンジン推力(N)
    thrust: float
    #燃焼時間(秒)
    burn_time: float
    #発射角度(度)
    launch_angle: float
    #空気抵抗係数 小さいほど空気抵抗を受けにくい
    drag_coefficient: float = 0.5
    #空気を正面から受ける面積(m²)
    reference_area: float = 0.1

    @property
    def dry_mass(self) -> float:
        """
        燃料を除いたロケット質量を返す。
        """
        return (
            self.structure_mass
            + self.engine_mass
            + self.payload_mass
        )

    @property
    def initial_total_mass(self) -> float:
        """
        発射時点のロケット総質量を返す。
        """

        return (
            self.dry_mass
            + self.fuel_mass
        )


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
