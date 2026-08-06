import csv
import math

from datetime import datetime
from pathlib import Path

from flight_event import FlightEvent
from models import SimulationResult


class SimulationDataExporter:
    """
    ロケットシミュレーション結果を
    CSVファイルへ出力するクラス。

    出力内容
    ----------
    ・飛行中の時系列データ
    ・飛行イベント一覧
    """

    # CSVファイルを保存するフォルダ
    OUTPUT_DIRECTORY = Path("outputs")

    @classmethod
    def export_all(
        cls,
        result: SimulationResult,
    ) -> tuple[Path, Path]:
        """
        飛行データとイベント一覧をCSVへ出力する。

        Parameters
        ----------
        result:
            シミュレーション結果

        Returns
        -------
        tuple[Path, Path]:
            飛行データCSVとイベントCSVの保存先
        """

        # 保存先フォルダが存在しない場合は作成する
        cls.OUTPUT_DIRECTORY.mkdir(
            parents=True,
            exist_ok=True,
        )

        # ファイル名が重ならないように日時を付ける
        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S"
        )

        flight_data_path = (
            cls.OUTPUT_DIRECTORY
            / f"flight_data_{timestamp}.csv"
        )

        flight_events_path = (
            cls.OUTPUT_DIRECTORY
            / f"flight_events_{timestamp}.csv"
        )

        cls._export_flight_data(
            result=result,
            output_path=flight_data_path,
        )

        cls._export_flight_events(
            events=result.flight_events,
            output_path=flight_events_path,
        )

        return (
            flight_data_path,
            flight_events_path,
        )

    @staticmethod
    def _export_flight_data(
        result: SimulationResult,
        output_path: Path,
    ) -> None:
        """
        各時刻の飛行状態をCSVへ出力する。

        Parameters
        ----------
        result:
            シミュレーション結果

        output_path:
            CSVファイルの保存先
        """

        # 各時系列データの件数を取得
        data_lengths = {
            "times": len(result.times),
            "positions_x": len(result.positions_x),
            "positions_y": len(result.positions_y),
            "velocities_x": len(result.velocities_x),
            "velocities_y": len(result.velocities_y),
            "accelerations_x": len(
                result.accelerations_x
            ),
            "accelerations_y": len(
                result.accelerations_y
            ),
            "flight_angles": len(
                result.flight_angles
            ),
            "dynamic_pressures": len(
                result.dynamic_pressures
            ),
            "mach_numbers": len(
                result.mach_numbers
            ),
            "gravities": len(
                result.gravities
            ),
            "total_masses": len(
                result.total_masses
            ),
            "remaining_fuels": len(
                result.remaining_fuels
            ),
            "thrusts": len(
                result.thrusts
            ),
        }

        # 時系列データの件数が揃っているか確認
        if len(set(data_lengths.values())) != 1:
            raise ValueError(
                "時系列データの件数が一致していません。"
                f"件数:{data_lengths}"
            )

        # utf-8-sigを使用すると、
        # Windows版Excelでも日本語が文字化けしにくい
        with output_path.open(
            mode="w",
            newline="",
            encoding="utf-8-sig",
        ) as csv_file:
            writer = csv.writer(csv_file)

            # CSVのヘッダー
            writer.writerow(
                [
                    "time_s",
                    "position_x_m",
                    "altitude_m",
                    "velocity_x_m_s",
                    "velocity_y_m_s",
                    "total_speed_m_s",
                    "acceleration_x_m_s2",
                    "acceleration_y_m_s2",
                    "total_acceleration_m_s2",
                    "flight_angle_deg",
                    "dynamic_pressure_pa",
                    "dynamic_pressure_kpa",
                    "mach_number",
                    "gravity_m_s2",
                    "total_mass_kg",
                    "remaining_fuel_kg",
                    "thrust_n",
                ]
            )

            for index in range(
                len(result.times)
            ):
                velocity_x = (
                    result.velocities_x[index]
                )

                velocity_y = (
                    result.velocities_y[index]
                )

                acceleration_x = (
                    result.accelerations_x[index]
                )

                acceleration_y = (
                    result.accelerations_y[index]
                )

                dynamic_pressure = (
                    result.dynamic_pressures[index]
                )

                # X・Y速度から合成速度を計算
                total_speed = math.hypot(
                    velocity_x,
                    velocity_y,
                )

                # X・Y加速度から合成加速度を計算
                total_acceleration = math.hypot(
                    acceleration_x,
                    acceleration_y,
                )

                writer.writerow(
                    [
                        result.times[index],
                        result.positions_x[index],
                        result.positions_y[index],
                        velocity_x,
                        velocity_y,
                        total_speed,
                        acceleration_x,
                        acceleration_y,
                        total_acceleration,
                        result.flight_angles[index],
                        dynamic_pressure,
                        dynamic_pressure / 1000,
                        result.mach_numbers[index],
                        result.gravities[index],
                        result.total_masses[index],
                        result.remaining_fuels[index],
                        result.thrusts[index],
                    ]
                )

    @staticmethod
    def _export_flight_events(
        events: list[FlightEvent],
        output_path: Path,
    ) -> None:
        """
        飛行中に発生したイベントをCSVへ出力する。

        Parameters
        ----------
        events:
            飛行イベント一覧

        output_path:
            CSVファイルの保存先
        """

        with output_path.open(
            mode="w",
            newline="",
            encoding="utf-8-sig",
        ) as csv_file:
            writer = csv.writer(csv_file)

            writer.writerow(
                [
                    "time_s",
                    "event_type",
                    "altitude_m",
                    "description",
                ]
            )

            for event in events:
                writer.writerow(
                    [
                        event.time,
                        event.event_type.value,
                        event.altitude,
                        event.description,
                    ]
                )