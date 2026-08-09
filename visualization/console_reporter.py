from analysis.flight_event import FlightEvent

def print_simulation_start(
    dry_mass: float,
    fuel_mass: float,
    thrust: float,
    launch_angle: float,
    thrust_to_weight_ratio: float,
    vertical_thrust_to_weight_ratio: float,
) -> None:
    """
    シミュレーション開始時の情報を表示する。
    """

    print("=== ロケットシミュレーション開始 ===")

    print(
        f"機体重量:{dry_mass:.1f}kg / "
        f"燃料重量:{fuel_mass:.1f}kg / "
        f"推力:{thrust:.1f}N / "
        f"発射角度:{launch_angle:.1f}°"
    )

    print(f"全体の推力重量比:{thrust_to_weight_ratio:.2f}")
    print(f"垂直方向の推力重量比:{vertical_thrust_to_weight_ratio:.2f}")

    if vertical_thrust_to_weight_ratio > 1:
        print("打ち上げ可能です。")
    else:
        print("垂直方向の推力不足により打ち上げできません。")

    print()


def print_status(
    time: float,
    position_y: float,
    velocity_y: float,
    acceleration_y: float,
    current_fuel: float,
    engine_is_burning: bool,
    flight_angle: float,
) -> None:
    """
    飛行中の状態を表示する。
    """

    engine_status = "燃焼中" if engine_is_burning else "停止"

    print(
        f"{time:5.1f}秒 | "
        f"高度:{position_y:8.1f}m | "
        f"速度:{velocity_y:7.1f}m/s | "
        f"加速度:{acceleration_y:7.1f}m/s² | "
        f"燃料:{current_fuel:6.1f}kg | "
        f"角度:{flight_angle:6.1f}° | "
        f"エンジン:{engine_status}"
    )


def print_simulation_result(
    max_altitude: float,
    max_velocity: float,
    flight_time: float,
    max_dynamic_pressure: float,
    max_q_time: float,
    max_q_altitude: float,
    max_q_speed: float,
    max_mach_number: float,
) -> None:
    """
    シミュレーション終了時の結果を表示する。
    """

    # PaからkPaへ変換
    max_dynamic_pressure_kpa = (
        max_dynamic_pressure / 1000
    )

    print()
    print("=== シミュレーション終了 ===")
    print(f"最高高度:{max_altitude:.1f}m")
    print(f"最高速度:{max_velocity:.1f}m/s")
    print(f"飛行時間:{flight_time:.1f}秒")

    print()
    print("=== Max Q解析 ===")
    print(
        f"最大動圧:"
        f"{max_dynamic_pressure_kpa:.2f}kPa"
    )
    print(
        f"発生時刻:"
        f"{max_q_time:.1f}秒"
    )
    print(
        f"発生高度:"
        f"{max_q_altitude:.1f}m"
    )
    print(
        f"発生時速度:"
        f"{max_q_speed:.1f}m/s"
    )

    print()
    print("=== Mach解析 ===")
    print(
        f"最高マッハ数:"
        f"Mach {max_mach_number:.2f}"
    )

def print_flight_events(
    events: list[FlightEvent],
) -> None:
    """
    飛行中に発生したイベントを時刻順に表示する。

    Parameters
    ----------
    events:
        飛行イベント一覧
    """

    print()
    print("=== 飛行イベント一覧 ===")

    if not events:
        print("飛行イベントは記録されませんでした。")
        return

    for event in events:
        print(
            f"T+{event.time:7.1f}s | "
            f"{event.event_type.value:8s} | "
            f"高度:{event.altitude:10.1f}m"
        )

        print(
            f"    {event.description}"
        )