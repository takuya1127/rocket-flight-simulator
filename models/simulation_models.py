from analysis.flight_event import FlightEvent
from dataclasses import dataclass, field

@dataclass(frozen=True)
class StageConfig:
    """
    ロケット1段分の設定を保持するデータモデル。

    Attributes
    ----------
    name:ステージ名
    structure_mass:ステージ構造質量（kg）
    engine_mass:エンジン質量（kg）
    fuel_mass:推進剤質量（kg）
    thrust:最大推力（N）
    burn_time:燃焼時間（s）
    """
    name: str
    structure_mass: float
    engine_mass: float
    fuel_mass: float
    thrust: float
    burn_time: float

    @property
    def dry_mass(self) -> float:
        """
        ステージの乾燥質量を返す。
        乾燥質量 = 構造質量 + エンジン質量
        """

        return (
            self.structure_mass + self.engine_mass
        )

    @property
    def initial_total_mass(self) -> float:
        """
        燃料を含むステージ初期質量を返す。
        """

        return (
            self.dry_mass + self.fuel_mass
        )

@dataclass(frozen=True)
class BoosterConfig:
    """
    補助ブースター１種類分の設定。

    countを使って、同じ性能のブースターを複数本搭載できる。
    """

    name:str
    count:int

    #ブースター１本あたりの質量
    structure_mass:float
    engine_mass:float
    fuel_mass:float

    #ブースター１本あたりの性能
    thrust:float
    burn_time:float

    @property
    def dry_mass_per_booster(self) -> float:
        """
        ブースター１本あたりの乾燥質量。
        """
        return (self.structure_mass + self.engine_mass)

    @property
    def initial_mass_per_booster(self) -> float:
        """
        ブースター１本あたりの初期質量。
        """
        return (self.dry_mass_per_booster + self.fuel_mass)

    @property
    def total_dry_mass(self) -> float:
        """
        全ブースターの乾燥質量。
        """

        return(self.dry_mass_per_booster * self.count)

    @property
    def total_fuel_mass(self) -> float:
        """
        全ブースターを含めた初期質量。
        """
        return(self.fuel_mass * self.count)

    @property
    def total_initial_mass(self) -> float:
        return(self.initial_mass_per_booster * self.count)

    @property
    def total_thrust(self) -> float:
        """
        全ブースターが発生する合計推力。
        """
        return(self.thrust * self.count)

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
    #風設定
    wind_speed: float
    wind_direction_deg: float
    gust_speed: float
    gust_start_time: float
    gust_duration: float
    #空気抵抗係数 小さいほど空気抵抗を受けにくい
    drag_coefficient: float = 0.5
    #空気を正面から受ける面積(m²)
    reference_area: float = 0.1
    #フェアリング質量
    fairing_mass: float = 0.0
    #フェアリング分離高度（m）
    fairing_separation_altitude: float = 0.0

    #補助ブースター
    booster: BoosterConfig | None = None


    stages:list[StageConfig] = field(default_factory=list)


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

    @property
    def has_multiple_stages(self) -> bool:
        """
        複数ステージ設定を持っているかを返す。
        """
        return len(self.stages) > 0

    @property
    def stage_count(self) -> int:
        """
        登録されているステージ数を返す。
        """
        return len(self.stages)

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
    pitch_angles: list[float]

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
    mass_flow_rates: list[float]
    specific_impulses: list[float]
    thrust_to_weight_ratios: list[float]

    # 音速を突破していない場合はNone
    sonic_boom_time: float | None
    sonic_boom_altitude: float | None
    sonic_boom_speed: float | None
    sonic_boom_mach_number: float | None

    flight_events: list[FlightEvent]