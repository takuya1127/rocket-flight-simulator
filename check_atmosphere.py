from core.gravity import GravityCalculator


test_altitudes = [
    0,
    10_000,
    100_000,
    300_000,
    1_000_000,
]

for altitude in test_altitudes:
    gravity = GravityCalculator.calculate(
        altitude_meters=altitude,
    )

    print(
        f"高度:{altitude:10.0f}m | "
        f"重力加速度:{gravity:.5f}m/s²"
    )