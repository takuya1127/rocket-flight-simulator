import math

import pandas as pd


def create_flight_dataframe(
    result,
) -> pd.DataFrame:
    """
    SimulationResultから、
    表示・グラフ・CSV出力に使用するDataFrameを作成する。
    """

    total_speeds = [
        math.hypot(
            velocity_x,
            velocity_y,
        )
        for velocity_x, velocity_y in zip(
            result.velocities_x,
            result.velocities_y,
        )
    ]

    total_accelerations = [
        math.hypot(
            acceleration_x,
            acceleration_y,
        )
        for acceleration_x, acceleration_y in zip(
            result.accelerations_x,
            result.accelerations_y,
        )
    ]

    return pd.DataFrame(
        {
            "時刻（秒）": result.times,
            "X座標（m）": result.positions_x,
            "高度（m）": result.positions_y,
            "X方向速度（m/s）": result.velocities_x,
            "Y方向速度（m/s）": result.velocities_y,
            "合成速度（m/s）": total_speeds,
            "X方向加速度（m/s²）": result.accelerations_x,
            "Y方向加速度（m/s²）": result.accelerations_y,
            "合成加速度（m/s²）": total_accelerations,
            "飛行角度（度）": result.flight_angles,
            "目標姿勢角度（度）": result.target_pitch_angles,
            "姿勢角度（度）": result.pitch_angles,
            "動圧（kPa）": [
                pressure / 1000
                for pressure in result.dynamic_pressures
            ],
            "マッハ数": result.mach_numbers,
            "重力加速度（m/s²）": result.gravities,
            "総質量（kg）": result.total_masses,
            "燃料残量（kg）": result.remaining_fuels,
            "推力（N）": result.thrusts,
            "推進剤流量（kg/s）": result.mass_flow_rates,
            "比推力（s）": result.specific_impulses,
            "推力重量比": result.thrust_to_weight_ratios,
        }
    )


def create_event_dataframe(
    result,
) -> pd.DataFrame:
    """
    飛行イベントを表形式へ変換する。
    """

    return pd.DataFrame(
        [
            {
                "時刻（秒）": event.time,
                "イベント": event.event_type.value,
                "高度（m）": event.altitude,
                "説明": event.description,
            }
            for event in result.flight_events
        ]
    )
