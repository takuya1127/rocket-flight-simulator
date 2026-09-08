import math

from analysis.flight_event import FlightEventType
from models.simulation_models import SimulationResult


def calculate_smoke_level(current_time: float) -> int:
    if current_time <= 2.5:
        return 10
    if current_time >= 8.0:
        return 0
    remaining_ratio = (8.0 - current_time) / 5.5
    return max(0, min(10, round(remaining_ratio * 10)))


def first_event_time(
    result: SimulationResult,
    event_type: FlightEventType,
) -> float | None:
    matching_times = [
        event.time
        for event in result.flight_events
        if event.event_type == event_type
    ]
    if not matching_times:
        return None
    return min(matching_times)


def build_replay_data(
    result: SimulationResult,
    max_points: int = 180,
) -> list[dict]:
    data_count = min(
        len(result.times),
        len(result.positions_x),
        len(result.positions_y),
        len(result.velocities_x),
        len(result.velocities_y),
        len(result.mach_numbers),
        len(result.pitch_angles),
        len(result.flight_angles),
        len(result.thrusts),
    )

    if data_count <= 0:
        return []

    sample_step = max(1, math.ceil(data_count / max_points))
    indexes = list(range(0, data_count, sample_step))
    final_index = data_count - 1
    if indexes[-1] != final_index:
        indexes.append(final_index)

    replay_data: list[dict] = []

    for index in indexes:
        speed = math.hypot(
            result.velocities_x[index],
            result.velocities_y[index],
        )
        replay_data.append(
            {
                "t": round(result.times[index], 3),
                "x": round(result.positions_x[index], 3),
                "y": round(max(0.0, result.positions_y[index]), 3),
                "vx": round(result.velocities_x[index], 3),
                "vy": round(result.velocities_y[index], 3),
                "speed": round(speed, 3),
                "mach": round(result.mach_numbers[index], 4),
                "angle": round(result.pitch_angles[index], 2),
                "flightAngle": round(result.flight_angles[index], 2),
                "burning": bool(result.thrusts[index] > 0),
                "smoke": calculate_smoke_level(result.times[index]),
            }
        )

    return replay_data


def build_event_times(result: SimulationResult) -> dict[str, float | None]:
    return {
        "stageSeparation": first_event_time(
            result,
            FlightEventType.STAGE_SEPARATION,
        ),
        "boosterSeparation": first_event_time(
            result,
            FlightEventType.BOOSTER_SEPARATION,
        ),
        "fairingSeparation": first_event_time(
            result,
            FlightEventType.FAIRING_SEPARATION,
        ),
        "apogee": first_event_time(
            result,
            FlightEventType.APOGEE,
        ),
        "landing": first_event_time(
            result,
            FlightEventType.LANDING,
        ),
    }
