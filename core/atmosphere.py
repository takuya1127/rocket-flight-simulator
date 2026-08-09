import math

from dataclasses import dataclass


@dataclass(frozen=True)
class AtmosphereState:
    """
    指定高度における大気状態を保持するクラス。

    Attributes
    ----------
    temperature_celsius:
        気温（℃）

    pressure_kpa:
        気圧（kPa）

    density:
        空気密度（kg/m³）

    speed_of_sound:
        現在の気温における音速(m/s)
    """

    temperature_celsius: float
    pressure_kpa: float
    density: float
    speed_of_sound: float


class AtmosphereCalculator:
    """
    高度から地球の大気状態を計算するクラス。

    高度に応じて、
    ・気温
    ・気圧
    ・空気密度
    ・音速
    を計算する。
    """

    @staticmethod
    def calculate(
        altitude_meters: float,
    ) -> AtmosphereState:
        """
        指定高度の大気状態を計算する。

        Parameters
        ----------
        altitude_meters:
            海抜高度（m）

        Returns
        -------
        AtmosphereState:
            指定高度の気温・気圧・空気密度・音速
        """

        # 高度がマイナスの場合は0mとして扱う
        altitude = max(
            0.0,
            altitude_meters,
        )

        # 高度から気温を計算
        temperature_celsius = (
            AtmosphereCalculator._calculate_temperature(
                altitude
            )
        )

        # 高度と気温から気圧を計算
        pressure_kpa = (
            AtmosphereCalculator._calculate_pressure(
                altitude,
                temperature_celsius,
            )
        )

        # 気温と気圧から空気密度を計算
        density = (
            AtmosphereCalculator._calculate_density(
                temperature_celsius,
                pressure_kpa,
            )
        )

        #気温から現在高度における音速を計算
        speed_of_sound = (
            AtmosphereCalculator._calculate_speed_of_sound(
                temperature_celsius
            )
        )

        return AtmosphereState(
            temperature_celsius=temperature_celsius,
            pressure_kpa=pressure_kpa,
            density=density,
            speed_of_sound=speed_of_sound,
        )

    @staticmethod
    def _calculate_temperature(
        altitude_meters: float,
    ) -> float:
        """
        高度に応じた気温を計算する。

        Returns
        -------
        float:
            気温（℃）
        """

        # 対流圏
        # 0m以上11,000m未満
        if altitude_meters < 11_000:
            return (
                15.04
                - 0.00649 * altitude_meters
            )

        # 下部成層圏
        # 11,000m以上25,000m未満
        if altitude_meters < 25_000:
            return -56.46

        # 上部成層圏
        # 25,000m以上
        return (
            -131.21
            + 0.00299 * altitude_meters
        )

    @staticmethod
    def _calculate_pressure(
        altitude_meters: float,
        temperature_celsius: float,
    ) -> float:
        """
        高度と気温から気圧を計算する。

        Returns
        -------
        float:
            気圧（kPa）
        """

        # 対流圏
        if altitude_meters < 11_000:
            return (
                101.29
                * (
                    (
                        temperature_celsius
                        + 273.1
                    )
                    / 288.08
                )
                ** 5.256
            )

        # 下部成層圏
        if altitude_meters < 25_000:
            return (
                22.65
                * math.exp(
                    1.73
                    - 0.000157
                    * altitude_meters
                )
            )

        # 上部成層圏
        return (
            2.488
            * (
                (
                    temperature_celsius
                    + 273.1
                )
                / 216.6
            )
            ** -11.388
        )

    @staticmethod
    def _calculate_density(
        temperature_celsius: float,
        pressure_kpa: float,
    ) -> float:
        """
        気温と気圧から空気密度を計算する。

        Returns
        -------
        float:
            空気密度（kg/m³）
        """

        temperature_kelvin = (
            temperature_celsius
            + 273.1
        )

        return (
            pressure_kpa
            / (
                0.2869
                * temperature_kelvin
            )
        )

    @staticmethod
    def _calculate_speed_of_sound(
            temperature_celsius: float,
    ) -> float:
        """
        気温から音速を計算する。

        空気中の音速は気温によって変化する。
        気温を絶対温度(K)へ変換し、
        空気の比熱比と気体定数を使用して求める。

        Parameters
        ----------
        temperature_celsius:
            気温(℃)

        Return
        ----------
        float:
            音速(m/s)
        """

        #摂氏から絶対温度(K)へ変換
        temperature_kelvin = (
            temperature_celsius
            + 273.15
        )
        #空気の比熱比
        specific_heat_ratio = 1.4
        #乾燥空気の気体定数(J/(kg・K))
        specific_gas_constant = 287.05
        #音速を計算
        return math.sqrt(
            specific_heat_ratio
            * specific_gas_constant
            * temperature_kelvin
        )