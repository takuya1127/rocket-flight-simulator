from dataclasses import replace

from models.simulation_models import (
    RocketConfig,
    SimulationResult,
)

from core.rocket_simulation import simulate_rocket

class SimulationRunner:
    """
    複数のロケット設定を連続してシミュレーションするクラス
    """

    def run(
            self,
            configs: list[RocketConfig],
    ) -> list[SimulationResult | None]:

        results = []

        for config in configs:
            result = simulate_rocket(config)
            results.append(result)

        return results

    def run_parameter_sweep(
            self,
            base_config: RocketConfig,
            parameter_name: str,
            values: list[float],
    ) -> list[SimulationResult | None]:
        """
        １つのパラメータだけを変更ながら
        複数回シミュレーションする
        """

        configs = []

        for value in values:
            config = replace(
                base_config,
                ** {parameter_name: value}
            )

            configs.append(config)

        return self.run(configs)