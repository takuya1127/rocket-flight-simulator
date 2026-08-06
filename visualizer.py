import math

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from matplotlib.offsetbox import AnnotationBbox, DrawingArea
from matplotlib.patches import Circle, Polygon

from models import RocketConfig, SimulationResult


def rotate_point(
    x: float,
    y: float,
    angle_degrees: float,
    center_x: float,
    center_y: float,
) -> tuple[float, float]:
    """
    1つの座標を、指定した中心点の周りに回転させる。

    Parameters
    ----------
    x:
        回転前のX座標

    y:
        回転前のY座標

    angle_degrees:
        回転角度（度）

    center_x:
        回転中心のX座標

    center_y:
        回転中心のY座標

    Returns
    -------
    tuple[float, float]:
        回転後のX座標とY座標
    """

    # 度数法をラジアンへ変換
    angle_radians = math.radians(angle_degrees)

    # 回転中心を原点として扱えるように座標を移動
    translated_x = x - center_x
    translated_y = y - center_y

    # 回転行列を使って座標を回転
    rotated_x = (
        translated_x * math.cos(angle_radians)
        - translated_y * math.sin(angle_radians)
    )

    rotated_y = (
        translated_x * math.sin(angle_radians)
        + translated_y * math.cos(angle_radians)
    )

    # 回転中心を元の位置へ戻す
    result_x = rotated_x + center_x
    result_y = rotated_y + center_y

    return result_x, result_y


def rotate_points(
    points: list[list[float]],
    angle_degrees: float,
    center_x: float,
    center_y: float,
) -> list[list[float]]:
    """
    複数の座標をまとめて回転させる。

    Parameters
    ----------
    points:
        回転前の座標一覧

    angle_degrees:
        回転角度（度）

    center_x:
        回転中心のX座標

    center_y:
        回転中心のY座標

    Returns
    -------
    list[list[float]]:
        回転後の座標一覧
    """

    rotated_points: list[list[float]] = []

    for point in points:
        rotated_x, rotated_y = rotate_point(
            x=point[0],
            y=point[1],
            angle_degrees=angle_degrees,
            center_x=center_x,
            center_y=center_y,
        )

        rotated_points.append(
            [
                rotated_x,
                rotated_y,
            ]
        )

    return rotated_points

def show_motion_analysis_graphs(
    result: SimulationResult,
) -> None:
    """
    ロケットの位置・速度・加速度を表示する。

    表示内容
    ----------
    ・高度
    ・X方向、Y方向、合成速度
    ・X方向、Y方向、合成加速度
    """

    fig, axes = plt.subplots(
        3,
        1,
        figsize=(10, 10),
    )

    # ==========================
    # 1段目：高度
    # ==========================

    axes[0].plot(
        result.times,
        result.positions_y,
        label="Altitude",
    )

    axes[0].set_title(
        "Altitude"
    )

    axes[0].set_ylabel(
        "Altitude (m)"
    )

    axes[0].grid()
    axes[0].legend()

    # ==========================
    # 2段目：速度
    # ==========================

    # X方向とY方向の速度から合成速度を計算
    speeds = [
        math.hypot(
            velocity_x,
            velocity_y,
        )
        for velocity_x, velocity_y
        in zip(
            result.velocities_x,
            result.velocities_y,
        )
    ]

    axes[1].plot(
        result.times,
        result.velocities_x,
        label="Velocity X",
    )

    axes[1].plot(
        result.times,
        result.velocities_y,
        label="Velocity Y",
    )

    axes[1].plot(
        result.times,
        speeds,
        label="Total Speed",
        linestyle="--",
    )

    axes[1].set_title(
        "Velocity"
    )

    axes[1].set_ylabel(
        "Velocity (m/s)"
    )

    axes[1].grid()
    axes[1].legend()

    # ==========================
    # 3段目：加速度
    # ==========================

    # X方向とY方向の加速度から合成加速度を計算
    accelerations = [
        math.hypot(
            acceleration_x,
            acceleration_y,
        )
        for acceleration_x, acceleration_y
        in zip(
            result.accelerations_x,
            result.accelerations_y,
        )
    ]

    axes[2].plot(
        result.times,
        result.accelerations_x,
        label="Acceleration X",
    )

    axes[2].plot(
        result.times,
        result.accelerations_y,
        label="Acceleration Y",
    )

    axes[2].plot(
        result.times,
        accelerations,
        label="Total Acceleration",
        linestyle="--",
    )

    axes[2].set_title(
        "Acceleration"
    )

    axes[2].set_xlabel(
        "Time (seconds)"
    )

    axes[2].set_ylabel(
        "Acceleration (m/s²)"
    )

    axes[2].grid()
    axes[2].legend()

    # グラフ同士が重ならないように調整
    plt.tight_layout(
        h_pad=3.0,
        pad=2.0,
    )

    plt.show()

def show_flight_animation(
    result: SimulationResult,
    config: RocketConfig,
) -> None:
    """
    ロケットの2次元飛行をアニメーションで表示する。

    ロケットの本体・窓・翼・炎を、
    現在の進行方向に合わせてまとめて回転させる。
    """

    if (
        not result.times
        or not result.positions_x
        or not result.positions_y
    ):
        print("アニメーションに必要なデータがありません。")
        return

    fig, axis = plt.subplots(
        figsize=(10, 8),
    )

    # ==========================
    # 表示範囲
    # ==========================

    max_position_x = max(result.positions_x)
    max_position_y = max(result.positions_y)

    x_limit = max(
        1.0,
        max_position_x * 1.1,
    )

    y_limit = max(
        1.0,
        max_position_y * 1.1,
    )

    axis.set_xlim(
        0,
        x_limit,
    )

    axis.set_ylim(
        0,
        y_limit,
    )

    axis.set_title("Rocket Flight Animation")
    axis.set_xlabel("Horizontal Position (meters)")
    axis.set_ylabel("Altitude (meters)")
    axis.grid()

    # 地面
    axis.axhline(
        y=0,
        linewidth=3,
    )

    # ==========================
    # ロケットの描画領域
    # ==========================

    # 回転しても図形が切れないように、
    # 縦横120の広めの領域を用意する
    rocket_drawing = DrawingArea(
        120,
        120,
        0,
        0,
    )

    # ロケット全体の回転中心
    rocket_center_x = 60.0
    rocket_center_y = 60.0

    # ==========================
    # 回転前の座標
    # ==========================

    # ロケット本体
    rocket_body_points = [
        [50, 38],
        [70, 38],
        [70, 82],
        [60, 108],
        [50, 82],
    ]

    # 左翼
    left_fin_points = [
        [50, 42],
        [34, 24],
        [50, 30],
    ]

    # 右翼
    right_fin_points = [
        [70, 42],
        [86, 24],
        [70, 30],
    ]

    # 炎
    rocket_flame_points = [
        [53, 38],
        [60, 8],
        [67, 38],
    ]

    # 窓の中心
    rocket_window_center = (
        60.0,
        72.0,
    )

    # ==========================
    # ロケットの各パーツを作成
    # ==========================

    rocket_body = Polygon(
        rocket_body_points,
        closed=True,
    )

    rocket_drawing.add_artist(
        rocket_body
    )

    rocket_window = Circle(
        rocket_window_center,
        radius=6,
    )

    rocket_drawing.add_artist(
        rocket_window
    )

    left_fin = Polygon(
        left_fin_points,
        closed=True,
    )

    rocket_drawing.add_artist(
        left_fin
    )

    right_fin = Polygon(
        right_fin_points,
        closed=True,
    )

    rocket_drawing.add_artist(
        right_fin
    )

    rocket_flame = Polygon(
        rocket_flame_points,
        closed=True,
    )

    rocket_drawing.add_artist(
        rocket_flame
    )

    # ==========================
    # ロケットをグラフへ配置
    # ==========================

    rocket_box = AnnotationBbox(
        rocket_drawing,
        (
            result.positions_x[0],
            result.positions_y[0],
        ),
        xybox=(
            result.positions_x[0],
            result.positions_y[0],
        ),
        xycoords="data",
        boxcoords="data",
        frameon=False,
        box_alignment=(0.5, 0.5),
    )

    axis.add_artist(
        rocket_box
    )

    # 飛行軌跡
    flight_path, = axis.plot(
        [],
        [],
        linestyle="--",
    )

    # 現在の状態を表示するテキスト
    status_text = axis.text(
        0.02,
        0.96,
        "",
        transform=axis.transAxes,
        verticalalignment="top",
    )

    def update(frame: int):
        """
        フレームごとにロケットの位置・角度・炎・軌跡を更新する。
        """

        current_time = result.times[frame]
        current_x = result.positions_x[frame]
        current_y = result.positions_y[frame]

        # 角度データが不足していてもエラーにならないようにする
        if frame < len(result.flight_angles):
            current_angle = result.flight_angles[frame]
        else:
            current_angle = 90.0

        # 元のロケットは上向き、つまり90度を向いている。
        # そのため進行角度との差分だけ回転させる。
        rotation_angle = current_angle - 90.0

        # ==========================
        # 本体を回転
        # ==========================

        rotated_body_points = rotate_points(
            points=rocket_body_points,
            angle_degrees=rotation_angle,
            center_x=rocket_center_x,
            center_y=rocket_center_y,
        )

        rocket_body.set_xy(
            rotated_body_points
        )

        # ==========================
        # 左翼を回転
        # ==========================

        rotated_left_fin_points = rotate_points(
            points=left_fin_points,
            angle_degrees=rotation_angle,
            center_x=rocket_center_x,
            center_y=rocket_center_y,
        )

        left_fin.set_xy(
            rotated_left_fin_points
        )

        # ==========================
        # 右翼を回転
        # ==========================

        rotated_right_fin_points = rotate_points(
            points=right_fin_points,
            angle_degrees=rotation_angle,
            center_x=rocket_center_x,
            center_y=rocket_center_y,
        )

        right_fin.set_xy(
            rotated_right_fin_points
        )

        # ==========================
        # 炎を回転
        # ==========================

        rotated_flame_points = rotate_points(
            points=rocket_flame_points,
            angle_degrees=rotation_angle,
            center_x=rocket_center_x,
            center_y=rocket_center_y,
        )

        rocket_flame.set_xy(
            rotated_flame_points
        )

        # ==========================
        # 窓を回転
        # ==========================

        rotated_window_x, rotated_window_y = rotate_point(
            x=rocket_window_center[0],
            y=rocket_window_center[1],
            angle_degrees=rotation_angle,
            center_x=rocket_center_x,
            center_y=rocket_center_y,
        )

        rocket_window.center = (
            rotated_window_x,
            rotated_window_y,
        )

        # ==========================
        # ロケット全体の位置を更新
        # ==========================

        rocket_box.xy = (
            current_x,
            current_y,
        )

        rocket_box.xybox = (
            current_x,
            current_y,
        )

        rocket_box.stale = True

        # 燃焼中だけ炎を表示
        rocket_flame.set_visible(
            current_time < config.burn_time
        )

        # ==========================
        # 軌跡を更新
        # ==========================

        flight_path.set_data(
            result.positions_x[:frame + 1],
            result.positions_y[:frame + 1],
        )

        # ==========================
        # 状態表示を更新
        # ==========================

        status_text.set_text(
            f"Time: {current_time:.1f} s\n"
            f"X Position: {current_x:.1f} m\n"
            f"Altitude: {current_y:.1f} m\n"
            f"Flight Angle: {current_angle:.1f}°"
        )

        return (
            rocket_box,
            rocket_body,
            rocket_window,
            left_fin,
            right_fin,
            rocket_flame,
            flight_path,
            status_text,
        )

    # 0.1秒刻みのデータから10個ごとに表示するため、
    # シミュレーション上では約1秒ごとの動きになる
    frame_indexes = range(
        0,
        len(result.times),
        10,
    )

    animation = FuncAnimation(
        fig,
        update,
        frames=frame_indexes,
        interval=30,
        repeat=False,
        blit=False,
    )

    plt.tight_layout()
    plt.show()

def show_vehicle_state_graphs(
        result: SimulationResult,
) -> None:
    """
    ロケット機体状態の推移を表示する。
    """

    import math

    fig, axes = plt.subplots(
        2,
        2,
        figsize=(13, 8)
    )
    fig.suptitle(
        "Vehicle State Analysis",
        fontsize=18,
    )
    # ==========================
    # 燃料残量
    # ==========================
    axes[0][0].plot(
        result.times,
        result.remaining_fuels,
        color="green",
    )
    axes[0][0].set_title("Remaining Fuels")
    axes[0][0].set_xlabel("Time(s)")
    axes[0][0].set_ylabel("Fuel(kg)")
    axes[0][0].grid()

    # ==========================
    # 総質量
    # ==========================

    axes[0][1].plot(
        result.times,
        result.total_masses,
        color="blue",
    )
    axes[0][1].set_title("Rocket Mass")
    axes[0][1].set_xlabel("Time (s)")
    axes[0][1].set_ylabel("Mass (kg)")
    axes[0][1].grid()

    # ==========================
    # 推力
    # ==========================

    axes[1][0].plot(
        result.times,
        result.thrusts,
        color="red",
    )
    axes[1][0].set_title("Engine Thrust")
    axes[1][0].set_xlabel("Time (s)")
    axes[1][0].set_ylabel("Thrust (N)")
    axes[1][0].grid()

    # ==========================
    # 合成加速度
    # ==========================

    total_acceleration = []

    for ax, ay in zip(
            result.accelerations_x,
            result.accelerations_y,
    ):
        total_acceleration.append(
            math.hypot(
                ax,
                ay,
            )
        )

    axes[1][1].plot(
        result.times,
        total_acceleration,
        color="purple",
    )
    axes[1][1].set_title("Total Acceleration")
    axes[1][1].set_xlabel("Time (s)")
    axes[1][1].set_ylabel("Acceleration (m/s²)")
    axes[1][1].grid()

    plt.tight_layout()
    plt.show()