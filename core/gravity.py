class GravityCalculator:
    """
    高度に応じた地球の重力加速度を計算するクラス。

    地球を完全な球とみなし、
    地球中心からの距離に応じて重力が弱くなる
    簡易的な重力モデルを使用する。

    このモデルでは、以下は考慮しない。

    ・地球の自転
    ・緯度による重力差
    ・地球の扁平形状
    ・月や太陽など、地球以外の天体から受ける重力
    """

    #地球の平均半径(m)
    EARTH_RADIUS = 6_371_000.0
    #地表付近の標準重力加速度(m/s²)
    SURFACE_GRAVITY = 9.80665

    @staticmethod
    def calculate(
            altitude_meters: float,
    ) -> float:
        """
        高度に応じた重力加速度を計算する。

        Parameters
        ----------
        altitude_meters:
            地表からの高度(m)

        Returns
        ----------
        float:
            指定高度における重力加速度(m/s²)
        """

        #地下高度は0mとして扱う
        altitude = max(
            0.0,
            altitude_meters,
        )
        #地球中心からロケットまでの距離
        distance_from_earth_center = (
            GravityCalculator.EARTH_RADIUS
            + altitude
        )

        #高度に応じた重力加速度を計算
        #g(h) = g⁰ * (R / (R + h))²
        #g⁰: 地表の重力加速度
        #R: 地球半径
        #h: 地表からの高度
        gravity = (
            GravityCalculator.SURFACE_GRAVITY
            * (
                GravityCalculator.EARTH_RADIUS
                / distance_from_earth_center
            )
            ** 2
        )
        return gravity