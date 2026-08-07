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

    # 現在時刻
    time = 0.0

    # 現在位置
    position_x = 0.0
    position_y = 0.0

    # 現在速度
    velocity_x = 0.0
    velocity_y = 0.0

    # 入力された角度をラジアンへ変換
    angle_radians = math.radians(launch_angle)

    # 現在の燃料量
    current_fuel = fuel_mass

    # 1秒あたりに消費する燃料
    fuel_consumption_per_second = fuel_mass / burn_time

    # 最高高度
    max_altitude = 0.0

    # 最高速度
    max_velocity = 0.0

    max_mach_number = 0.0

    #動圧やMax Qを解析
    flight_analyzer = FlightAnalyzer()

    #飛行中に発生したイベントを管理する
    event_manager = FlightEventManager()

    # 一度でも地面から離れたか
    has_launched = False

    # イベントを一度だけ表示するためのフラグ
    burnout_displayed = False
    apogee_displayed = False

    # ==========================
    # シミュレーション結果
    # ==========================

    times: list[float] = []
    positions_x: list[float] = []
    altitudes: list[float] = []
    velocities_x: list[float] = []
    velocities_y: list[float] = []
    flight_angles: list[float] = []
    dynamic_pressures: list[float] = []
    mach_numbers: list[float] = []
    gravities: list[float] = []
    accelerations_x: list[float] = []
    accelerations_y: list[float] = []
    total_masses: list[float] = []
    remaining_fuels: list[float] = []
    thrusts: list[float] = []

    # ==========================
    # 打ち上げ前の計算
    # ==========================

    # 打ち上げ開始時の総質量
    initial_total_mass = dry_mass + fuel_mass

    #発射地点における重力加速度
    initial_gravity = (
        GravityCalculator.calculate(
            altitude_meters = 0.0
        )
    )
    #打ち上げ開始時にかかる重力
    initial_weight_force = (
        initial_total_mass
        * initial_gravity
    )

    # 推力重量比
    thrust_to_weight_ratio = (
        thrust / initial_weight_force
    )

    # 初期状態におけるY方向の推力
    initial_thrust_y = (
        thrust * math.sin(angle_radians)
    )

    # 垂直方向の推力重量比
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

    # ==========================
    # シミュレーション開始
    # ==========================

    while True:
        # 現在のロケット全体の質量
        total_mass = dry_mass + current_fuel

        # エンジンが燃焼中か判定
        engine_is_burning = (
            time < burn_time
            and current_fuel > 0
        )

        # ==========================
        # 推力と燃料消費
        # ==========================

        if engine_is_burning:
            # 推力をX方向とY方向へ分解
            thrust_x = (
                thrust
                * math.cos(angle_radians)
            )

            thrust_y = (
                thrust
                * math.sin(angle_radians)
            )

            # TIME_STEP秒間に消費する燃料
            consumed_fuel = (
                fuel_consumption_per_second
                * TIME_STEP
            )

            # 燃料がマイナスにならないようにする
            current_fuel = max(
                0.0,
                current_fuel - consumed_fuel,
            )

        else:
            # 燃焼終了後は推力が0
            thrust_x = 0.0
            thrust_y = 0.0

            # 燃焼終了を一度だけ表示
            if (
                has_launched
                and not burnout_displayed
            ):
                print()
                print(
                    f"--- 燃焼終了:"
                    f"{time:.1f}秒 / "
                    f"高度{position_y:.1f}m / "
                    f"Y方向速度{velocity_y:.1f}m/s ---"
                )
                print()

                burnout_displayed = True

        #現在の推力の大きさ
        current_thrust_magnitude = math.hypot(
            thrust_x,
            thrust_y,
        )

        # ==========================
        # 重力
        # ==========================

        # 現在高度における重力加速度を計算
        current_gravity = (
            GravityCalculator.calculate(
                altitude_meters=position_y,
            )
        )

        # 現在のロケットに働く重力
        weight_force = (
                total_mass
                * current_gravity
        )

        # ==========================
        # 空気抵抗
        # ==========================

        #現在高度における大気状態を取得
        atmosphere = AtmosphereCalculator.calculate(
            position_y
        )
        #現在高度の空気密度
        air_density = atmosphere.density

        # 速度の大きさ
        speed_before_update = math.hypot(
            velocity_x,
            velocity_y,
        )

        # 現在の動圧
        dynamic_pressure = (
            FlightAnalyzer.calculate_dynamic_pressure(
                air_density=air_density,
                speed=speed_before_update,
            )
        )

        # 上昇中だけMax Qを更新する
        if velocity_y > 0:
            flight_analyzer.update_max_q(
                dynamic_pressure=dynamic_pressure,
                time=time,
                altitude=max(0.0, position_y),
                speed=speed_before_update,
            )

        # 停止中は空気抵抗0
        drag_force_x = 0.0
        drag_force_y = 0.0

        if speed_before_update > 0:
            # 空気抵抗の大きさ
            drag_force = (
                0.5
                * air_density
                * drag_coefficient
                * reference_area
                * speed_before_update ** 2
            )

            # X方向の空気抵抗
            # 進行方向と逆向きになる
            drag_force_x = (
                -drag_force
                * velocity_x
                / speed_before_update
            )

            # Y方向の空気抵抗
            # 上昇中は下向き、下降中は上向きになる
            drag_force_y = (
                -drag_force
                * velocity_y
                / speed_before_update
            )

        # ==========================
        # 合力
        # ==========================

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

        # ==========================
        # 加速度
        # ==========================

        acceleration_x = (
            net_force_x / total_mass
        )

        acceleration_y = (
            net_force_y / total_mass
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

        # 高度が0より大きければ打ち上がったと判定
        if position_y > 0:
            has_launched = True

        # 最高高度を更新
        if position_y > max_altitude:
            max_altitude = position_y

        # ==========================
        # 速度と進行角度
        # ==========================

        # X・Y方向を合わせた速度
        current_speed = math.hypot(
            velocity_x,
            velocity_y,
        )

        current_mach = (
            FlightAnalyzer.calculate_mach_number(
                speed = current_speed,
                speed_of_sound = atmosphere.speed_of_sound,
            )
        )
        #マッハ1を初めて突破した瞬間か判定
        sonic_boom_detected = (
            flight_analyzer.update_sonic_boom(
                mach_number = current_mach,
                time = time,
                altitude = max(0.0, position_y),
                speed = current_speed,
            )
        )
        #初めて音速を突破した瞬間だけ表示
        if sonic_boom_detected:
            print()
            print("=== 音速突破 ===")
            print(f"時刻:{time:.1f}秒")
            print(f"高度:{max(0.0, position_y):.1f}m")
            print(f"速度:{current_speed:.1f}m/s")
            print(f"マッハ数:Mach {current_mach:.2f}")
            print()

        # 進行方向の角度を計算
        flight_angle_radians = math.atan2(
            velocity_y,
            velocity_x,
        )

        flight_angle = math.degrees(
            flight_angle_radians
        )

        # 最高速度を更新
        if current_speed > max_velocity:
            max_velocity = current_speed

        if current_mach > max_mach_number:
            max_mach_number = current_mach

        # ==========================
        # 現在の状態を保存
        # ==========================

        times.append(time)
        positions_x.append(position_x)
        altitudes.append(
            max(0.0, position_y)
        )
        velocities_x.append(velocity_x)
        velocities_y.append(velocity_y)
        accelerations_x.append(acceleration_x)
        accelerations_y.append(acceleration_y)
        flight_angles.append(flight_angle)
        dynamic_pressures.append(dynamic_pressure)
        mach_numbers.append(current_mach)
        gravities.append(current_gravity)

        #現在の機体状態を保存
        total_masses.append(total_mass)
        remaining_fuels.append(current_fuel)
        thrusts.append(current_thrust_magnitude)

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
            landing_velocity = velocity_y
            position_y = 0.0

            print()
            print(
                f"--- 着地:"
                f"{time:.1f}秒 / "
                f"着地速度"
                f"{abs(landing_velocity):.1f}m/s ---"
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

        # 時間を進める
        time = time + TIME_STEP

    # ==========================
    # 最終結果
    # ==========================

    #記録されたMax Q情報を取得
    max_q_record = (
        flight_analyzer.get_max_q_record()
    )
    # 音速突破時の情報を取得
    sonic_boom_record = (
        flight_analyzer.get_sonic_boom_record()
    )

    print_simulation_result (
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

    # シミュレーション結果を返す
    return SimulationResult (
        times = times,
        positions_x = positions_x,
        positions_y = altitudes,
        velocities_x = velocities_x,
        velocities_y = velocities_y,
        accelerations_x = accelerations_x,
        accelerations_y = accelerations_y,
        flight_angles = flight_angles,
        dynamic_pressures = dynamic_pressures,
        mach_numbers = mach_numbers,
        gravities = gravities,
        total_masses = total_masses,
        remaining_fuels = remaining_fuels,
        thrusts = thrusts,
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
        sonic_boom_altitude=(
            sonic_boom_record.altitude
            if sonic_boom_record is not None
            else None
        ),
        sonic_boom_speed=(
            sonic_boom_record.speed
            if sonic_boom_record is not None
            else None
        ),
        sonic_boom_mach_number=(
            sonic_boom_record.mach_number
            if sonic_boom_record is not None
            else None
        ),
    )