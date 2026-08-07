import math

from atmosphere import AtmosphereCalculator
from console_reporter import (
    print_simulation_result,
    print_simulation_start,
    print_status,
)
from flight_analysis import FlightAnalyzer
from flight_event import (
    FlightEvent,
    FlightEventManager,
    FlightEventType,
)
from gravity import GravityCalculator
from models import RocketConfig, SimulationResult
from simulation_recorder import SimulationRecorder
from physics_calculator import PhysicsCalculator

# シミュレーションを何秒刻みで計算するか
TIME_STEP = 0.1


def simulate_rocket(
    config: RocketConfig,
) -> SimulationResult | None:
    """
    ロケットの2次元飛行を簡易シミュレーションする。

    Parameters
    ----------
    config:
        ロケットの質量、推力、燃焼時間、発射角度、
        空気抵抗などの設定情報。

    Returns
    -------
    SimulationResult | None:
        打ち上げに成功した場合はシミュレーション結果を返す。
        打ち上げられなかった場合はNoneを返す。
    """

    # ==========================
    # 設定値の取り出し
    # ==========================

    dry_mass = config.dry_mass
    fuel_mass = config.fuel_mass
    thrust = config.thrust
    burn_time = config.burn_time
    launch_angle = config.launch_angle
    drag_coefficient = config.drag_coefficient
    reference_area = config.reference_area

    # ==========================
    # 現在の状態
    # ==========================

    time = 0.0

    position_x = 0.0
    position_y = 0.0

    velocity_x = 0.0
    velocity_y = 0.0

    current_fuel = fuel_mass

    angle_radians = math.radians(launch_angle)

    fuel_consumption_per_second = fuel_mass / burn_time

    max_altitude = 0.0
    max_velocity = 0.0
    max_mach_number = 0.0

    # 動圧・Max Q・マッハ数などを解析する
    flight_analyzer = FlightAnalyzer()

    # 発射・燃焼終了・最高高度・着地などを管理する
    event_manager = FlightEventManager()

    has_launched = False

    burnout_displayed = False
    apogee_displayed = False

    # ==========================
    # シミュレーション結果
    # ==========================

    # 位置・速度・加速度・機体状態を記録する
    recorder = SimulationRecorder()

    # ==========================
    # 打ち上げ前の計算
    # ==========================

    initial_total_mass = dry_mass + fuel_mass

    initial_gravity = GravityCalculator.calculate(
        altitude_meters=0.0,
    )

    initial_weight_force = (
        initial_total_mass
        * initial_gravity
    )

    thrust_to_weight_ratio = (
        thrust
        / initial_weight_force
    )

    initial_thrust_y = (
        thrust
        * math.sin(angle_radians)
    )

    vertical_thrust_to_weight_ratio = (
        initial_thrust_y
        / initial_weight_force
    )

    print_simulation_start(
        dry_mass,
        fuel_mass,
        thrust,
        launch_angle,
        thrust_to_weight_ratio,
        vertical_thrust_to_weight_ratio,
    )

    if vertical_thrust_to_weight_ratio > 1.0:
        print("打ち上げ可能です。")

        event_manager.add_event(
            FlightEvent(
                event_type=FlightEventType.LAUNCH,
                time=0.0,
                altitude=0.0,
                description="ロケットが発射されました。",
            )
        )
    else:
        print("推力不足のため、打ち上げできません。")

    print()

    # ==========================
    # シミュレーション開始
    # ==========================

    while True:

        engine_is_burning = (
            time < burn_time
            and current_fuel > 0
        )

        # ==========================
        # 推力と燃料消費
        # ==========================

        if engine_is_burning:
            thrust_x = (
                thrust
                * math.cos(angle_radians)
            )

            thrust_y = (
                thrust
                * math.sin(angle_radians)
            )

            consumed_fuel = (
                fuel_consumption_per_second
                * TIME_STEP
            )

            current_fuel = max(
                0.0,
                current_fuel - consumed_fuel,
            )

        else:
            thrust_x = 0.0
            thrust_y = 0.0

            if (
                has_launched
                and not burnout_displayed
            ):
                burnout_speed = math.hypot(
                    velocity_x,
                    velocity_y,
                )

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

        current_thrust_magnitude = math.hypot(
            thrust_x,
            thrust_y,
        )
        # ==========================
        # 物理計算
        # ==========================

        physics_result = PhysicsCalculator.calculate(
            dry_mass=dry_mass,
            current_fuel=current_fuel,
            position_y=position_y,
            velocity_x=velocity_x,
            velocity_y=velocity_y,
            thrust_x=thrust_x,
            thrust_y=thrust_y,
            drag_coefficient=drag_coefficient,
            reference_area=reference_area,
        )

        total_mass = physics_result.total_mass

        current_gravity = physics_result.gravity
        air_density = physics_result.air_density

        speed_before_update = physics_result.speed
        dynamic_pressure = physics_result.dynamic_pressure

        drag_force_x = physics_result.drag_force_x
        drag_force_y = physics_result.drag_force_y

        acceleration_x = physics_result.acceleration_x
        acceleration_y = physics_result.acceleration_y

        # 打ち上げ時のMax Qとして、上昇中だけ更新する
        if velocity_y > 0:
            flight_analyzer.update_max_q(
                dynamic_pressure=dynamic_pressure,
                time=time,
                altitude=max(0.0, position_y),
                speed=speed_before_update,
            )

        # ==========================
        # 速度を更新
        # ==========================

        velocity_x = (
                velocity_x
                + acceleration_x * TIME_STEP
        )
        # ==========================
        # 速度を更新
        # ==========================

        velocity_x = (
            velocity_x
            + acceleration_x * TIME_STEP
        )

        velocity_y = (
            velocity_y
            + acceleration_y * TIME_STEP
        )

        # ==========================
        # 位置を更新
        # ==========================

        position_x = (
            position_x
            + velocity_x * TIME_STEP
        )

        position_y = (
            position_y
            + velocity_y * TIME_STEP
        )

        if position_y > 0:
            has_launched = True

        if position_y > max_altitude:
            max_altitude = position_y

        # ==========================
        # 速度・マッハ数・進行角度
        # ==========================

        current_speed = math.hypot(
            velocity_x,
            velocity_y,
        )

        current_mach = (
            FlightAnalyzer.calculate_mach_number(
                speed=current_speed,
                speed_of_sound=atmosphere.speed_of_sound,
            )
        )

        sonic_boom_detected = (
            flight_analyzer.update_sonic_boom(
                mach_number=current_mach,
                time=time,
                altitude=max(0.0, position_y),
                speed=current_speed,
            )
        )

        if sonic_boom_detected:
            sonic_boom_altitude = max(
                0.0,
                position_y,
            )

            print()
            print("=== 音速突破 ===")
            print(f"時刻:{time:.1f}秒")
            print(
                f"高度:"
                f"{sonic_boom_altitude:.1f}m"
            )
            print(f"速度:{current_speed:.1f}m/s")
            print(
                f"マッハ数:"
                f"Mach {current_mach:.2f}"
            )
            print()

            # 音速突破イベントを登録
            event_manager.add_event(
                FlightEvent(
                    event_type=FlightEventType.MACH_ONE,
                    time=time,
                    altitude=sonic_boom_altitude,
                    description=(
                        "ロケットが音速を突破しました。"
                        f"速度は{current_speed:.1f}m/s、"
                        f"Mach {current_mach:.2f}です。"
                    ),
                )
            )

        flight_angle_radians = math.atan2(
            velocity_y,
            velocity_x,
        )

        flight_angle = math.degrees(
            flight_angle_radians
        )

        if current_speed > max_velocity:
            max_velocity = current_speed

        if current_mach > max_mach_number:
            max_mach_number = current_mach

        # 現在の飛行状態と機体状態をまとめて保存
        recorder.record(
            time=time,
            position_x=position_x,
            position_y=position_y,
            velocity_x=velocity_x,
            velocity_y=velocity_y,
            acceleration_x=acceleration_x,
            acceleration_y=acceleration_y,
            flight_angle=flight_angle,
            dynamic_pressure=dynamic_pressure,
            mach_number=current_mach,
            gravity=current_gravity,
            total_mass=total_mass,
            remaining_fuel=current_fuel,
            thrust=current_thrust_magnitude,
        )

        # ==========================
        # 最高高度到達
        # ==========================

        if (
            has_launched
            and velocity_y <= 0
            and not apogee_displayed
        ):
            print()
            print(
                f"--- 最高高度到達:"
                f"{time:.1f}秒 / "
                f"高度{max_altitude:.1f}m ---"
            )
            print()

            event_manager.add_event(
                FlightEvent(
                    event_type = FlightEventType.APOGEE,
                    time = time,
                    altitude = max_altitude,
                    description = (
                        f"最高高度{max_altitude:.1f}mへ到達しました。"
                    ),
                )
            )

            apogee_displayed = True

        # ==========================
        # 1秒ごとの状態表示
        # ==========================

        step_number = round(
            time / TIME_STEP
        )

        if step_number % 10 == 0:
            print_status(
                time,
                position_y,
                velocity_y,
                acceleration_y,
                current_fuel,
                engine_is_burning,
                flight_angle,
            )

        # ==========================
        # 着地判定
        # ==========================

        if (
            has_launched
            and position_y <= 0
        ):
            landing_speed = math.hypot(
                velocity_x,
                velocity_y,
            )

            position_y = 0.0

            print()
            print(
                f"--- 着地:"
                f"{time:.1f}秒 / "
                f"着地速度{landing_speed:.1f}m/s ---"
            )

            event_manager.add_event(
                FlightEvent(
                    event_type = FlightEventType.LANDING,
                    time = time,
                    altitude = 0.0,
                    description = (
                        "ロケットが着地しました。"
                        f"着地速度は{landing_speed:.1f}m/sです。"
                    ),
                )
            )

            break

        # ==========================
        # 打ち上げ失敗
        # ==========================

        if (
            not has_launched
            and time > burn_time
        ):
            print()
            print(
                "推力が不足しているため、"
                "ロケットは打ち上がりませんでした。"
            )

            return None

        # ==========================
        # 安全対策
        # ==========================

        if time > 1000:
            print(
                "シミュレーション時間が"
                "長すぎるため終了しました。"
            )

            return None

        time = time + TIME_STEP

    # ==========================
    # 最終結果
    # ==========================

    max_q_record = (
        flight_analyzer.get_max_q_record()
    )

    sonic_boom_record = (
        flight_analyzer.get_sonic_boom_record()
    )

    # Max Qが記録されている場合、
    # 飛行イベントとして追加する
    if max_q_record.dynamic_pressure > 0:
        max_q_kpa = (
                max_q_record.dynamic_pressure
                / 1000
        )

        event_manager.add_event(
            FlightEvent(
                event_type=FlightEventType.MAX_Q,
                time=max_q_record.time,
                altitude=max_q_record.altitude,
                description=(
                    "上昇中の最大動圧へ到達しました。"
                    f"動圧は{max_q_kpa:.2f}kPa、"
                    f"速度は{max_q_record.speed:.1f}m/sです。"
                ),
            )
        )

    # 全イベントを時刻順で取得
    flight_events = (
        event_manager.get_events()
    )

    print_simulation_result(
        max_altitude = max_altitude,
        max_velocity = max_velocity,
        flight_time = time,
        max_dynamic_pressure = (
            max_q_record.dynamic_pressure
        ),
        max_q_time = max_q_record.time,
        max_q_altitude = max_q_record.altitude,
        max_q_speed = max_q_record.speed,
        max_mach_number = max_mach_number,
    )

    return SimulationResult(
        **recorder.to_result_kwargs(),

        max_altitude = max_altitude,
        max_velocity = max_velocity,
        flight_time = time,

        max_dynamic_pressure = (
            max_q_record.dynamic_pressure
        ),
        max_q_time = max_q_record.time,
        max_q_altitude = max_q_record.altitude,
        max_q_speed = max_q_record.speed,

        max_mach_number = max_mach_number,

        sonic_boom_time=(
            sonic_boom_record.time
            if sonic_boom_record is not None
            else None
        ),
        sonic_boom_altitude = (
            sonic_boom_record.altitude
            if sonic_boom_record is not None
            else None
        ),
        sonic_boom_speed = (
            sonic_boom_record.speed
            if sonic_boom_record is not None
            else None
        ),
        sonic_boom_mach_number = (
            sonic_boom_record.mach_number
            if sonic_boom_record is not None
            else None
        ),

        flight_events = flight_events,
    )
