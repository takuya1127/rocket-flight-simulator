import math
from dataclasses import dataclass

@dataclass(frozen=True)
class WindResult:
    """
    1ステップ分の風速データ。

    Attributes
    ----------
    wind_x:
        X方向の風速（m/s）

    wind_y:
        Y方向の風速（m/s）
    """
    wind_x: float
    wind_y: float

class WindCalculator:
    """
    風速を計算するクラス。
    高度や時間によらない一定風を扱う。
    """

    @staticmethod
    def calculate_constant_wind(
            *,
            wind_x: float,
            wind_y: float,
    ) -> WindResult:
        #指定された一定風を返す。
        return WindResult(
            wind_x=wind_x,
            wind_y=wind_y,
        )

    @staticmethod
    def calculate_altitude_wind(
            *,
            time: float,
            altitude: float,
            base_wind_speed: float,
            wind_direction_radians: float,
            gust_speed: float,
            gust_start_time: float,
            gust_duration: float,
    ) -> WindResult:
        """
        高度に応じた風速を計算する。

        現在は簡易モデルとして、
        高度1000mごとに基準風速の20%ずつ増加させる。
        """
        altitude_ratio = (
            max(0.0, altitude) / 1000.0
        )
        altitude_wind_speed = (
            base_wind_speed
            * (
                1.0 + 0.2 * altitude_ratio
            )
        )
        gust_additional_speed = (
            WindCalculator.calculate_gust(
                time=time,
                gust_start_time=gust_start_time,
                gust_duration=gust_duration,
                gust_speed=gust_speed,
            )
        )

        wind_speed = (
                altitude_wind_speed
                + gust_additional_speed
        )
        wind_x = (
            wind_speed * math.cos(wind_direction_radians)
        )
        wind_y = (
            wind_speed * math.sin(wind_direction_radians)
        )

        return WindResult(
            wind_x=wind_x,
            wind_y=wind_y,
        )

    @staticmethod
    def calculate_gust(
            time: float,
            gust_start_time: float,
            gust_duration: float,
            gust_speed: float,
    ) -> float:
        """
        指定時間だけ発生する突風の追加風速を返す。

        Parameters
        ----------
        time:現在時刻（秒）
        gust_start_time:突風開始時刻（秒）
        gust_duration:突風継続時間（秒）
        gust_speed:突風によって追加される風速（m/s）

        Returns
        -------
        float:現在時刻における追加風速（m/s）
        """
        gust_end_time = (
            gust_start_time + gust_duration
        )
        if(
            gust_start_time <= time < gust_end_time
        ):
            return gust_speed

        return 0.0

if __name__ == "__main__":
    result = (
        WindCalculator.calculate_constant_wind(
            wind_x=5.0,
            wind_y=0.0,
        )
    )

    print(
        f"X方向の風速: {result.wind_x} m/s"
    )

    print(
        f"Y方向の風速: {result.wind_y} m/s"
    )