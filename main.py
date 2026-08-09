from recording.data_exporter import SimulationDataExporter
from models.simulation_models import RocketConfig
from core.rocket_simulation import simulate_rocket
from validator import InputValidator
from visualizer import show_flight_animation, show_motion_analysis_graphs, show_vehicle_state_graphs
from visualization.console_reporter import print_flight_events


def main() -> None:
    """
    ロケットシミュレーションの開始地点。

    入力値を受け取り、
    シミュレーションを実行して、
    結果を画面へ表示する。
    """

    print("=== ロケット設定 ===")

    dry_mass = InputValidator.get_positive_float(
        "ロケット本体の質量を入力してください(kg): "
    )

    fuel_mass = InputValidator.get_positive_float(
        "燃料の質量を入力してください(kg): "
    )

    thrust = InputValidator.get_positive_float(
        "エンジン推力を入力してください(N): "
    )

    burn_time = InputValidator.get_positive_float(
        "燃焼時間を入力してください(秒): "
    )

    launch_angle = InputValidator.get_launch_angle(
        "発射角度を入力してください(度): "
    )

    print()

    # 入力された設定値を1つのオブジェクトへまとめる
    config = RocketConfig(
        dry_mass=dry_mass,
        fuel_mass=fuel_mass,
        thrust=thrust,
        burn_time=burn_time,
        launch_angle=launch_angle,
    )

    # シミュレーションを実行して結果を受け取る
    result = simulate_rocket(config)

    # 打ち上げに失敗した場合は表示処理を行わない
    if result is None:
        return

    # 発生した飛行イベントを一覧表示
    print_flight_events(
        result.flight_events
    )

    # 飛行データとイベント一覧をCSVへ出力
    flight_data_path, flight_events_path = (
        SimulationDataExporter.export_all(
            result
        )
    )

    print()
    print("=== CSV出力完了 ===")
    print(
        f"飛行データ:"
        f"{flight_data_path.resolve()}"
    )
    print(
        f"イベント一覧:"
        f"{flight_events_path.resolve()}"
    )

    # アニメーションを表示
    show_flight_animation(
        result,
        config,
    )

    # アニメーションを閉じたあとにグラフを表示
    show_motion_analysis_graphs(result)
    show_vehicle_state_graphs(result)


if __name__ == "__main__":
    main()