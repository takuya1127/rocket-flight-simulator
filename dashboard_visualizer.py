import base64
import io
import math
from functools import lru_cache
from pathlib import Path

import plotly.graph_objects as go
from PIL import Image

from models import SimulationResult


ASSET_DIRECTORY = Path(__file__).resolve().parent / "assets"
ROCKET_BODY_PATH = ASSET_DIRECTORY / "rocket_body.png"
ROCKET_FLAME_PATH = ASSET_DIRECTORY / "rocket_flame.png"
SMOKE_PATH = ASSET_DIRECTORY / "smoke.png"


def _open_rgba(path: Path) -> Image.Image:
    """
    PNG画像をRGBA形式で読み込む。
    """

    if not path.exists():
        raise FileNotFoundError(
            f"画像ファイルが見つかりません: {path}"
        )

    return Image.open(path).convert("RGBA")


def _trim_transparent_margin(
    image: Image.Image,
) -> Image.Image:
    """
    透明部分だけの余白を切り取る。
    """

    alpha = image.getchannel("A")
    bounding_box = alpha.getbbox()

    if bounding_box is None:
        return image

    return image.crop(bounding_box)


def _resize_by_width(
    image: Image.Image,
    width: int,
) -> Image.Image:
    """
    アスペクト比を保ったまま指定幅へ縮小する。
    """

    height = max(
        1,
        round(
            image.height
            * width
            / image.width
        ),
    )

    return image.resize(
        (width, height),
        Image.Resampling.LANCZOS,
    )


@lru_cache(maxsize=1)
def _load_sprite_parts() -> tuple[
    Image.Image,
    Image.Image,
    Image.Image,
]:
    """
    ロケット本体・炎・煙の画像を読み込む。
    """

    rocket_body = _trim_transparent_margin(
        _open_rgba(ROCKET_BODY_PATH)
    )

    rocket_flame = _trim_transparent_margin(
        _open_rgba(ROCKET_FLAME_PATH)
    )

    smoke = _trim_transparent_margin(
        _open_rgba(SMOKE_PATH)
    )

    return (
        rocket_body,
        rocket_flame,
        smoke,
    )


def _set_opacity(
    image: Image.Image,
    opacity: float,
) -> Image.Image:
    """
    PNG画像全体の透明度を変更する。
    """

    result = image.copy()
    alpha = result.getchannel("A")

    adjusted_alpha = alpha.point(
        lambda value: round(
            value
            * max(0.0, min(1.0, opacity))
        )
    )

    result.putalpha(adjusted_alpha)

    return result


def _image_to_data_uri(
    image: Image.Image,
) -> str:
    """
    Pillow画像をPlotlyで利用できるData URIへ変換する。
    """

    buffer = io.BytesIO()

    image.save(
        buffer,
        format="PNG",
        optimize=True,
    )

    encoded = base64.b64encode(
        buffer.getvalue()
    ).decode("ascii")

    return f"data:image/png;base64,{encoded}"


@lru_cache(maxsize=360)
def _create_rocket_sprite_data_uri(
    rounded_angle: int,
    engine_is_burning: bool,
    smoke_level: int,
) -> str:
    """
    ロケット本体・炎・煙を合成し、
    飛行角度に合わせて回転したPNGを作る。

    Parameters
    ----------
    rounded_angle:
        1度単位に丸めた飛行角度。

    engine_is_burning:
        エンジンが燃焼中かどうか。

    smoke_level:
        煙の濃さを0～10で表した値。
    """

    (
        rocket_body_source,
        rocket_flame_source,
        smoke_source,
    ) = _load_sprite_parts()

    # ブラウザへ送るデータ量を抑えるため、
    # 合成前の画像サイズを小さくする。
    body_width = 170

    rocket_body = _resize_by_width(
        rocket_body_source,
        body_width,
    )

    flame = _resize_by_width(
        rocket_flame_source,
        round(body_width * 0.82),
    )

    smoke = _resize_by_width(
        smoke_source,
        round(body_width * 0.62),
    )

    # 本体より下へ炎と煙を配置できるキャンバスを作る。
    extra_height = round(
        rocket_body.height * 0.72
    )

    canvas = Image.new(
        "RGBA",
        (
            round(body_width * 1.45),
            rocket_body.height + extra_height,
        ),
        (0, 0, 0, 0),
    )

    center_x = canvas.width // 2

    # 煙は最背面。
    if smoke_level > 0:
        smoke_opacity = smoke_level / 10

        smoke_layer = _set_opacity(
            smoke,
            smoke_opacity,
        )

        smoke_x = (
            center_x
            - smoke_layer.width // 2
        )

        smoke_y = round(
            rocket_body.height * 0.76
        )

        canvas.alpha_composite(
            smoke_layer,
            (
                smoke_x,
                smoke_y,
            ),
        )

    # 炎は煙の上、本体の後ろ。
    if engine_is_burning:
        flame_x = (
            center_x
            - flame.width // 2
        )

        flame_y = round(
            rocket_body.height * 0.70
        )

        canvas.alpha_composite(
            flame,
            (
                flame_x,
                flame_y,
            ),
        )

    # 本体を最前面へ配置する。
    body_x = (
        center_x
        - rocket_body.width // 2
    )

    canvas.alpha_composite(
        rocket_body,
        (
            body_x,
            0,
        ),
    )

    # 元画像は上向き。
    # 飛行角度90度で回転なしになる。
    rotation_degrees = (
        rounded_angle
        - 90
    )

    rotated = canvas.rotate(
        rotation_degrees,
        resample=Image.Resampling.BICUBIC,
        expand=True,
    )

    rotated = _trim_transparent_margin(
        rotated
    )

    return _image_to_data_uri(
        rotated
    )


def _calculate_smoke_level(
    current_time: float,
) -> int:
    """
    発射直後だけ煙を表示する。

    0～3秒:
        濃い煙

    3～8秒:
        徐々に薄くなる

    8秒以降:
        非表示
    """

    if current_time <= 3.0:
        return 10

    if current_time >= 8.0:
        return 0

    remaining_ratio = (
        8.0 - current_time
    ) / 5.0

    return max(
        0,
        min(
            10,
            round(
                remaining_ratio * 10
            ),
        ),
    )


def _create_sprite_layout_image(
    *,
    image_source: str,
    position_x: float,
    position_y: float,
    x_span: float,
    y_span: float,
) -> dict:
    """
    Plotlyのグラフ上へ配置する画像設定を作る。
    """

    return {
        "source": image_source,
        "xref": "x",
        "yref": "y",
        "x": position_x,
        "y": position_y,
        "sizex": max(
            x_span * 0.09,
            1.0,
        ),
        "sizey": max(
            y_span * 0.25,
            1.0,
        ),
        "xanchor": "center",
        "yanchor": "middle",
        "sizing": "contain",
        "opacity": 1.0,
        "layer": "above",
    }


def _create_status_annotation(
    *,
    current_time: float,
    current_altitude: float,
    current_speed: float,
    current_mach: float,
    compact: bool = False,
) -> dict:
    """
    現在値表示用の注釈を作る。
    """

    if compact:
        # スマホ用：1行のコンパクト表示
        status_text = (
            f"<b>T+{current_time:.1f}s</b>"
            f" | {current_altitude / 1000:.2f}km"
            f" | {current_speed:.0f}m/s"
            f" | M{current_mach:.2f}"
        )

        font_size = 10

    else:
        # PC用：従来の詳細表示
        status_text = (
            f"<b>T+{current_time:.1f}s</b><br>"
            f"高度: {current_altitude:,.1f}m<br>"
            f"速度: {current_speed:,.1f}m/s<br>"
            f"Mach: {current_mach:.2f}"
        )

        font_size = 14

    return {
        "text": status_text,
        "x": 0.02,
        "y": 0.98,
        "xref": "paper",
        "yref": "paper",
        "showarrow": False,
        "align": "left",
        "bgcolor": "rgba(0, 0, 0, 0.68)",
        "bordercolor": "#ff4b4b",
        "borderwidth": 1,
        "font": {
            "color": "white",
            "size": font_size,
        },
    }


def create_flight_animation_figure(
    result: SimulationResult,
        mobile_mode: bool = False,
) -> go.Figure:
    """
    Streamlit上で表示する飛行アニメーションを作成する。

    表示内容
    ----------
    ・PNGロケット画像
    ・燃焼中の炎
    ・発射直後の煙
    ・飛行角度に応じた機体回転
    ・飛行軌跡
    ・現在時刻、高度、速度、Mach
    ・再生、一時停止、時間スライダー
    """

    if (
        not result.times
        or not result.positions_x
        or not result.positions_y
    ):
        return go.Figure()

    data_count = min(
        len(result.times),
        len(result.positions_x),
        len(result.positions_y),
        len(result.velocities_x),
        len(result.velocities_y),
        len(result.mach_numbers),
        len(result.flight_angles),
        len(result.thrusts),
    )

    if data_count == 0:
        return go.Figure()

    # 最大120フレーム程度に抑え、
    # ブラウザへ送る画像データ量を軽くする。
    frame_step = max(
        1,
        math.ceil(
            data_count / 120
        ),
    )

    frame_indexes = list(
        range(
            0,
            data_count,
            frame_step,
        )
    )

    final_index = data_count - 1

    if frame_indexes[-1] != final_index:
        frame_indexes.append(
            final_index
        )

    valid_positions_x = (
        result.positions_x[:data_count]
    )

    valid_positions_y = (
        result.positions_y[:data_count]
    )

    max_position_x = max(
        valid_positions_x
    )

    min_position_x = min(
        valid_positions_x
    )

    max_position_y = max(
        valid_positions_y
    )

    x_range_size = max(
        max_position_x - min_position_x,
        1.0,
    )

    x_margin = max(
        x_range_size * 0.06,
        1.0,
    )

    y_margin = max(
        max_position_y * 0.12,
        1.0,
    )

    x_min = min(
        0.0,
        min_position_x,
    )

    x_max = (
        max_position_x
        + x_margin
    )

    y_max = (
        max_position_y
        + y_margin
    )

    x_span = max(
        x_max
        - (x_min - x_margin),
        1.0,
    )

    y_span = max(
        y_max,
        1.0,
    )

    first_index = (
        frame_indexes[0]
    )

    first_time = (
        result.times[first_index]
    )

    first_speed = math.hypot(
        result.velocities_x[first_index],
        result.velocities_y[first_index],
    )

    first_angle = round(
        result.flight_angles[first_index]
    )

    first_engine_is_burning = (
        result.thrusts[first_index] > 0
    )

    first_smoke_level = (
        _calculate_smoke_level(
            first_time
        )
    )

    first_sprite = (
        _create_rocket_sprite_data_uri(
            first_angle,
            first_engine_is_burning,
            first_smoke_level,
        )
    )

    figure = go.Figure(
        data=[
            go.Scatter(
                x=result.positions_x[
                    :first_index + 1
                ],
                y=result.positions_y[
                    :first_index + 1
                ],
                mode="lines",
                name="Flight Path",
                line={
                    "color": "#ff4b4b",
                    "width": 3,
                },
                hoverinfo="skip",
            ),

            # ロケットの位置へ小さな当たり判定用点を置く。
            # 実際の見た目はlayout.imagesのPNG。
            go.Scatter(
                x=[
                    result.positions_x[
                        first_index
                    ]
                ],
                y=[
                    result.positions_y[
                        first_index
                    ]
                ],
                mode="markers",
                marker={
                    "size": 8,
                    "color": "rgba(255,255,255,0.01)",
                },
                hovertemplate=(
                    f"時刻: {first_time:.1f}秒"
                    "<br>"
                    f"高度: "
                    f"{result.positions_y[first_index]:.1f}m"
                    "<br>"
                    f"速度: {first_speed:.1f}m/s"
                    "<br>"
                    f"Mach: "
                    f"{result.mach_numbers[first_index]:.2f}"
                    "<extra></extra>"
                ),
                showlegend=False,
            ),
        ]
    )

    frames = []

    for index in frame_indexes:
        current_time = (
            result.times[index]
        )

        current_x = (
            result.positions_x[index]
        )

        current_y = (
            result.positions_y[index]
        )

        current_speed = math.hypot(
            result.velocities_x[index],
            result.velocities_y[index],
        )

        current_mach = (
            result.mach_numbers[index]
        )

        rounded_angle = round(
            result.flight_angles[index]
        )

        engine_is_burning = (
            result.thrusts[index] > 0
        )

        smoke_level = (
            _calculate_smoke_level(
                current_time
            )
        )

        sprite_source = (
            _create_rocket_sprite_data_uri(
                rounded_angle,
                engine_is_burning,
                smoke_level,
            )
        )

        frame = go.Frame(
            name=str(index),
            data=[
                go.Scatter(
                    x=result.positions_x[
                        :index + 1
                    ],
                    y=result.positions_y[
                        :index + 1
                    ],
                    mode="lines",
                    line={
                        "color": "#ff4b4b",
                        "width": 3,
                    },
                    hoverinfo="skip",
                ),

                go.Scatter(
                    x=[current_x],
                    y=[current_y],
                    mode="markers",
                    marker={
                        "size": 8,
                        "color": (
                            "rgba(255,255,255,0.01)"
                        ),
                    },
                    hovertemplate=(
                        f"時刻: {current_time:.1f}秒"
                        "<br>"
                        f"X座標: {current_x:.1f}m"
                        "<br>"
                        f"高度: {current_y:.1f}m"
                        "<br>"
                        f"速度: {current_speed:.1f}m/s"
                        "<br>"
                        f"Mach: {current_mach:.2f}"
                        "<extra></extra>"
                    ),
                    showlegend=False,
                ),
            ],
            layout=go.Layout(
                images=[
                    _create_sprite_layout_image(
                        image_source=sprite_source,
                        position_x=current_x,
                        position_y=current_y,
                        x_span=x_span,
                        y_span=y_span,
                    )
                ],
                annotations=[
                    _create_status_annotation(
                        current_time=current_time,
                        current_altitude=current_y,
                        current_speed=current_speed,
                        current_mach=current_mach,
                        compact=mobile_mode,
                    )
                ],
            ),
        )

        frames.append(
            frame
        )

    figure.frames = frames

    slider_steps = []

    for index in frame_indexes:
        slider_steps.append(
            {
                "method": "animate",
                "label": (
                    f"{result.times[index]:.1f}s"
                ),
                "args": [
                    [str(index)],
                    {
                        "mode": "immediate",
                        "frame": {
                            "duration": 0,
                            "redraw": True,
                        },
                        "transition": {
                            "duration": 0,
                        },
                    },
                ],
            }
        )

    if mobile_mode:
        # スマホでは横長の動画プレイヤー風に表示する
        figure_height = 215

        figure_margin = {
            "l": 28,
            "r": 8,
            "t": 8,
            "b": 45,
        }

        slider_x = 0.48
        slider_y = -0.13
        slider_length = 0.49

        x_axis_title = None
        y_axis_title = None

        axis_font_size = 9
        axis_tick_count = 5

    else:
        # PC版は今までの表示を維持する
        figure_height = 650

        figure_margin = {
            "l": 65,
            "r": 30,
            "t": 75,
            "b": 115,
        }

        slider_x = 0.18
        slider_y = -0.11
        slider_length = 0.80

        x_axis_title = "Horizontal Position (m)"
        y_axis_title = "Altitude (m)"

        axis_font_size = 12
        axis_tick_count = None

    if mobile_mode:
        play_label = "▶ 再生"
        pause_label = "⏸"
    else:
        play_label = "▶ 再生"
        pause_label = "⏸ 一時停止"

    figure.update_layout(
        height=figure_height,
        margin=figure_margin,
        paper_bgcolor="#071426",
        plot_bgcolor="#0d2746",
        font={
            "color": "white",
        },
        xaxis={
            "title": x_axis_title,
            "range": [
                x_min - x_margin,
                x_max,
            ],
            "gridcolor": (
                "rgba(255,255,255,0.15)"
            ),
            "zeroline": False,
            "tickfont": {
                "size": axis_font_size,
            },
            "nticks": axis_tick_count,
        },
        yaxis={
            "title": y_axis_title,
            "range": [
                0,
                y_max,
            ],
            "gridcolor": (
                "rgba(255,255,255,0.15)"
            ),
            "zeroline": False,
            "tickfont": {
                "size": axis_font_size,
            },
            "nticks": axis_tick_count,
        },
        showlegend=False,

        images=[
            _create_sprite_layout_image(
                image_source=first_sprite,
                position_x=(
                    result.positions_x[
                        first_index
                    ]
                ),
                position_y=(
                    result.positions_y[
                        first_index
                    ]
                ),
                x_span=x_span,
                y_span=y_span,
            )
        ],

        shapes=[
            {
                "type": "rect",
                "x0": (
                    x_min
                    - x_margin
                ),
                "x1": x_max,
                "y0": 0,
                "y1": max(
                    y_max * 0.008,
                    0.5,
                ),
                "fillcolor": "#3c8c40",
                "line": {
                    "width": 0,
                },
                "layer": "below",
            }
        ],

        annotations=[
            _create_status_annotation(
                current_time=first_time,
                current_altitude=(
                    result.positions_y[
                        first_index
                    ]
                ),
                current_speed=first_speed,
                current_mach=(
                    result.mach_numbers[
                        first_index
                    ]
                ),
                compact=mobile_mode,
            )
        ],

        updatemenus=[
            {
                "type": "buttons",
                "direction": "left",
                "x": 0.0,
                "y": -0.13,
                "showactive": False,
                "buttons": [
                    {
                        "label": play_label,
                        "method": "animate",
                        "args": [
                            None,
                            {
                                "fromcurrent": True,
                                "frame": {
                                    "duration": 75,
                                    "redraw": True,
                                },
                                "transition": {
                                    "duration": 0,
                                },
                            },
                        ],
                    },
                    {
                        "label": pause_label,
                        "method": "animate",
                        "args": [
                            [None],
                            {
                                "mode": "immediate",
                                "frame": {
                                    "duration": 0,
                                    "redraw": False,
                                },
                                "transition": {
                                    "duration": 0,
                                },
                            },
                        ],
                    },
                ],
            }
        ],

        sliders=[
            {
                "x": slider_x,
                "y": slider_y,
                "len": slider_length,
                "currentvalue": {
                    "visible": False,
                },
                "steps": slider_steps,
            }
        ],
    )

    return figure
