import math
from dataclasses import dataclass

from analysis.flight_event import (
    FlightEvent,
    FlightEventManager,
    FlightEventType,
)
from core.engine import EngineCalculator
from core.stage_manager import StageManager
from models.simulation_models import RocketConfig


@dataclass(frozen=True)
class BurnoutTransitionResult:
    """燃焼終了・段切り替え後にシミュレーション本体へ戻す状態。"""

    dry_mass: float
    current_fuel: float
    thrust: float
    burn_time: float
    mass_flow_rate: float
    stage_start_time: float
    last_burnout_stage_index: int
    burnout_displayed: bool


@dataclass(frozen=True)
class BoosterSeparationResult:
    """ブースター分離後の機体状態。"""

    dry_mass: float
    booster_fuel_mass: float
    booster_attached: bool
    booster_separated: bool


@dataclass(frozen=True)
class FairingSeparationResult:
    """フェアリング分離後の機体状態。"""

    dry_mass: float
    current_fairing_mass: float
    fairing_separated: bool


class SeparationManager:
    """
    燃焼終了・ステージ切り替え・分離イベントをまとめて扱う。

    rocket_simulation.py は飛行計算の流れに集中し、
    機体構成が変わる処理はこのクラスへ集約する。
    """

    @staticmethod
    def handle_engine_burnout(
        *,
        engine_is_burning: bool,
        has_launched: bool,
        stage_manager: StageManager | None,
        stage_fuels: list[float],
        config: RocketConfig,
        current_fairing_mass: float,
        booster_attached: bool,
        booster_separated: bool,
        time: float,
        position_y: float,
        velocity_x: float,
        velocity_y: float,
        dry_mass: float,
        current_fuel: float,
        thrust: float,
        burn_time: float,
        mass_flow_rate: float,
        stage_start_time: float,
        last_burnout_stage_index: int,
        burnout_displayed: bool,
        event_manager: FlightEventManager,
    ) -> BurnoutTransitionResult:
        result = BurnoutTransitionResult(
            dry_mass=dry_mass,
            current_fuel=current_fuel,
            thrust=thrust,
            burn_time=burn_time,
            mass_flow_rate=mass_flow_rate,
            stage_start_time=stage_start_time,
            last_burnout_stage_index=last_burnout_stage_index,
            burnout_displayed=burnout_displayed,
        )

        if engine_is_burning or not has_launched:
            return result

        if stage_manager is not None:
            current_stage_index = stage_manager.current_stage_index

            # 同じステージのBurnoutを何度も処理しない。
            if current_stage_index == last_burnout_stage_index:
                return result

            burned_stage = stage_manager.current_stage
            burnout_speed = math.hypot(velocity_x, velocity_y)

            stage_manager.burnout_current_stage()
            last_burnout_stage_index = current_stage_index

            print()
            print(
                f"--- {burned_stage.name} 燃焼終了:"
                f"{time:.1f}秒 / "
                f"高度{position_y:.1f}m / "
                f"速度{burnout_speed:.1f}m/s ---"
            )
            print()

            event_manager.add_event(
                FlightEvent(
                    event_type=FlightEventType.BURNOUT,
                    time=time,
                    altitude=max(0.0, position_y),
                    description=(
                        f"{burned_stage.name} エンジン燃焼終了。"
                        f"速度は{burnout_speed:.1f}m/s。"
                    ),
                )
            )

            if stage_manager.has_next_stage:
                separated_stage_name = burned_stage.name
                stage_manager.separate_stage()

                event_manager.add_event(
                    FlightEvent(
                        event_type=FlightEventType.STAGE_SEPARATION,
                        time=time,
                        altitude=max(0.0, position_y),
                        description=f"{separated_stage_name} を分離しました。",
                    )
                )

                current_stage = stage_manager.current_stage

                dry_mass = (
                    stage_manager.remaining_dry_mass
                    + config.payload_mass
                    + current_fairing_mass
                )

                if (
                    booster_attached
                    and not booster_separated
                    and config.booster is not None
                ):
                    dry_mass += config.booster.total_dry_mass

                current_fuel = stage_fuels[
                    stage_manager.current_stage_index
                ]
                thrust = current_stage.thrust
                burn_time = current_stage.burn_time
                mass_flow_rate = EngineCalculator.calculate_mass_flow_rate(
                    fuel_mass=current_fuel,
                    burn_time=burn_time,
                )
                stage_start_time = time
                stage_manager.ignite_current_stage()

                print()
                print(f"--- {separated_stage_name} 分離 ---")
                print(
                    f"--- {current_stage.name} 点火:"
                    f"{time:.1f}秒 ---"
                )
                print()

                event_manager.add_event(
                    FlightEvent(
                        event_type=FlightEventType.IGNITION,
                        time=time,
                        altitude=max(0.0, position_y),
                        description=(
                            f"{current_stage.name} エンジンに点火しました。"
                        ),
                    )
                )

            return BurnoutTransitionResult(
                dry_mass=dry_mass,
                current_fuel=current_fuel,
                thrust=thrust,
                burn_time=burn_time,
                mass_flow_rate=mass_flow_rate,
                stage_start_time=stage_start_time,
                last_burnout_stage_index=last_burnout_stage_index,
                burnout_displayed=burnout_displayed,
            )

        if not burnout_displayed:
            burnout_speed = math.hypot(velocity_x, velocity_y)

            print()
            print(
                f"--- 燃焼終了:"
                f"{time:.1f}秒 / "
                f"高度{position_y:.1f}m / "
                f"速度{burnout_speed:.1f}m/s ---"
            )
            print()

            event_manager.add_event(
                FlightEvent(
                    event_type=FlightEventType.BURNOUT,
                    time=time,
                    altitude=max(0.0, position_y),
                    description=(
                        "エンジン燃焼終了。"
                        f"速度は{burnout_speed:.1f}m/s。"
                    ),
                )
            )
            burnout_displayed = True

        return BurnoutTransitionResult(
            dry_mass=dry_mass,
            current_fuel=current_fuel,
            thrust=thrust,
            burn_time=burn_time,
            mass_flow_rate=mass_flow_rate,
            stage_start_time=stage_start_time,
            last_burnout_stage_index=last_burnout_stage_index,
            burnout_displayed=burnout_displayed,
        )

    @staticmethod
    def handle_booster_separation(
        *,
        config: RocketConfig,
        booster_result,
        booster_attached: bool,
        booster_separated: bool,
        dry_mass: float,
        booster_fuel_mass: float,
        time: float,
        position_y: float,
        event_manager: FlightEventManager,
    ) -> BoosterSeparationResult:
        if not (
            booster_attached
            and not booster_separated
            and config.booster is not None
            and booster_result is not None
            and not booster_result.engine_is_burning
        ):
            return BoosterSeparationResult(
                dry_mass=dry_mass,
                booster_fuel_mass=booster_fuel_mass,
                booster_attached=booster_attached,
                booster_separated=booster_separated,
            )

        booster_separated = True
        booster_attached = False
        dry_mass = max(0.0, dry_mass - config.booster.total_dry_mass)

        # ブースターに残った燃料も機体から離れる。
        booster_fuel_mass = 0.0

        print()
        print(
            f"--- ブースター分離:"
            f"{time:.1f}秒 / "
            f"高度{position_y:.1f}m ---"
        )
        print()

        event_manager.add_event(
            FlightEvent(
                event_type=FlightEventType.BOOSTER_SEPARATION,
                time=time,
                altitude=max(0.0, position_y),
                description=(
                    f"{config.booster.count}本の補助ブースターを分離しました。"
                ),
            )
        )

        return BoosterSeparationResult(
            dry_mass=dry_mass,
            booster_fuel_mass=booster_fuel_mass,
            booster_attached=booster_attached,
            booster_separated=booster_separated,
        )

    @staticmethod
    def handle_fairing_separation(
        *,
        config: RocketConfig,
        has_launched: bool,
        fairing_separated: bool,
        current_fairing_mass: float,
        dry_mass: float,
        time: float,
        position_y: float,
        event_manager: FlightEventManager,
    ) -> FairingSeparationResult:
        if not (
            has_launched
            and not fairing_separated
            and config.fairing_mass > 0.0
            and config.fairing_separation_altitude > 0.0
            and position_y >= config.fairing_separation_altitude
        ):
            return FairingSeparationResult(
                dry_mass=dry_mass,
                current_fairing_mass=current_fairing_mass,
                fairing_separated=fairing_separated,
            )

        fairing_separated = True
        current_fairing_mass = 0.0
        dry_mass = max(0.0, dry_mass - config.fairing_mass)

        print()
        print(
            f"--- フェアリング分離:"
            f"{time:.1f}秒 / "
            f"高度{position_y:.1f}m ---"
        )
        print()

        event_manager.add_event(
            FlightEvent(
                event_type=FlightEventType.FAIRING_SEPARATION,
                time=time,
                altitude=max(0.0, position_y),
                description=(
                    "フェアリングを分離しました。"
                    f"機体質量が{config.fairing_mass:.1f}kg減少しました。"
                ),
            )
        )

        return FairingSeparationResult(
            dry_mass=dry_mass,
            current_fairing_mass=current_fairing_mass,
            fairing_separated=fairing_separated,
        )
