import base64
import io
import json
import math
from functools import lru_cache
from pathlib import Path

import plotly.graph_objects as go
from PIL import Image

from models.simulation_models import SimulationResult

PROJECT_ROOT = Path(__file__).resolve().parent.parent
ASSET_DIRECTORY = PROJECT_ROOT / "assets"
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
        "x": 0.01,
        "y": 0.99,
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
                    ""
                    if mobile_mode
                    else f"{result.times[index]:.1f}s"
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
        # コントロール行はできるだけ薄くして、
        # グラフの表示領域を最大化する。
        figure_height = 230

        figure_margin = {
            "l": 2,
            "r": 2,
            "t": 4,
            "b": 34,
        }

        # ボタンとスライダーを同じ高さ（同じy）に揃えて
        # 細い一列に並べる。
        controls_y = 0.14

        button_x = 0.02
        button_y = controls_y

        slider_x = 0.17
        slider_y = controls_y
        slider_length = 0.81

        x_axis_title = None
        y_axis_title = None

        axis_font_size = 9
        axis_tick_count = 4

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

        button_x = 0.01
        button_y = -0.05

        x_axis_title = "Horizontal Position (m)"
        y_axis_title = "Altitude (m)"

        axis_font_size = 12
        axis_tick_count = None

    if mobile_mode:
        x_domain = [0.00, 1.00]

        # 以前はグラフ下側に大きな余白（0.30）を
        # 確保していたが、ロケットが画面下端付近に
        # いる時間はごく短いため、必要最小限まで縮めて
        # チャート自体の表示を大きくする。
        y_domain = [0.04, 1.00]

        # スマホでは横幅が限られるため、
        # アイコンのみのコンパクトなラベルにする。
        # 注意: "⏸"（U+23F8）はiOS等でフォントサイズを
        # 無視した大きな絵文字として描画されることがあり、
        # それがボタンを不自然に大きくしていた原因。
        # 絵文字化されない記号に置き換える。
        play_label = "▶"
        pause_label = "‖‖"

        # ボタンを左→右の順で並べ、
        # スライダーと同じダーク系の見た目に揃える。
        # pad/fontを極力小さくし、細いコントロール行に収める。
        button_style = {
            "direction": "right",
            "pad": {
                "l": 2,
                "r": 2,
                "t": 0,
                "b": 0,
            },
            "font": {
                "size": 11,
                "color": "white",
            },
            "bgcolor": "#132a4a",
            "bordercolor": "#ff4b4b",
            "borderwidth": 1,
        }

        slider_style = {
            "pad": {
                "t": 4,
                "b": 0,
            },
            "ticklen": 0,
            "tickcolor": "rgba(0,0,0,0)",
            "bgcolor": "rgba(255,255,255,0.25)",
            "activebgcolor": "#ff4b4b",
            "bordercolor": "rgba(0,0,0,0)",
            "borderwidth": 0,
        }
    else:
        x_domain = [0.00, 1.00]
        y_domain = [0.00, 1.00]
        play_label = "▶ 再生"
        pause_label = "‖‖ 一時停止"

        # PC版は元のPlotly標準スタイルのまま。
        button_style = {
            "direction": "left",
        }

        slider_style = {}

    figure.update_layout(
        autosize=True,
        height=figure_height,
        margin=figure_margin,
        paper_bgcolor="#071426",
        plot_bgcolor="#0d2746",
        font={
            "color": "white",
        },
        xaxis={
            "title": x_axis_title,
            "domain": x_domain,
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
            "domain": y_domain,
            "visible": not mobile_mode,
            "range": [
                0,
                y_max,
            ],
            "gridcolor": (
                "rgba(255,255,255,0.15)"
            ),
            "zeroline": False,

            # スマホでは縦軸文字を消して
            # 飛行画面を横いっぱい使う
            "showticklabels": not mobile_mode,

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
                "x": button_x,
                "y": button_y,
                "showactive": False,
                **button_style,
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
                **slider_style,
                "steps": slider_steps,
            }
        ],
    )

    return figure


def create_mobile_flight_replay_figure(
    result: SimulationResult,
    frame_index: int,
) -> go.Figure:
    """
    スマホ用の飛行リプレイを1フレームだけ描画する。

    Plotly内部には再生ボタンやスライダーを置かない。
    操作UIをStreamlit側へ分離することで、
    グラフ領域をスマホの横幅いっぱいまで利用する。
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

    index = max(
        0,
        min(
            int(frame_index),
            data_count - 1,
        ),
    )

    valid_positions_x = result.positions_x[:data_count]
    valid_positions_y = result.positions_y[:data_count]

    min_position_x = min(valid_positions_x)
    max_position_x = max(valid_positions_x)
    max_position_y = max(valid_positions_y)

    x_range_size = max(
        max_position_x - min_position_x,
        1.0,
    )

    # スマホでは左右余白を小さくし、軌道をできるだけ大きく見せる。
    x_margin = max(
        x_range_size * 0.025,
        1.0,
    )

    y_margin = max(
        max_position_y * 0.08,
        1.0,
    )

    x_min = min(
        0.0,
        min_position_x,
    )

    x_max = max_position_x + x_margin
    y_max = max_position_y + y_margin

    x_span = max(
        x_max - (x_min - x_margin),
        1.0,
    )

    y_span = max(
        y_max,
        1.0,
    )

    current_time = result.times[index]
    current_x = result.positions_x[index]
    current_y = result.positions_y[index]

    current_speed = math.hypot(
        result.velocities_x[index],
        result.velocities_y[index],
    )

    current_mach = result.mach_numbers[index]
    rounded_angle = round(result.flight_angles[index])
    engine_is_burning = result.thrusts[index] > 0

    smoke_level = _calculate_smoke_level(
        current_time
    )

    sprite_source = _create_rocket_sprite_data_uri(
        rounded_angle,
        engine_is_burning,
        smoke_level,
    )

    figure = go.Figure(
        data=[
            go.Scatter(
                x=result.positions_x[: index + 1],
                y=result.positions_y[: index + 1],
                mode="lines",
                line={
                    "color": "#ff5a52",
                    "width": 3,
                },
                hoverinfo="skip",
                showlegend=False,
            ),
            go.Scatter(
                x=[current_x],
                y=[current_y],
                mode="markers",
                marker={
                    "size": 8,
                    "color": "rgba(255,255,255,0.01)",
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
        ]
    )

    figure.update_layout(
        autosize=True,
        height=230,
        margin={
            "l": 2,
            "r": 2,
            "t": 4,
            "b": 24,
        },
        paper_bgcolor="#071426",
        plot_bgcolor="#0d2746",
        font={
            "color": "white",
        },
        xaxis={
            "title": None,
            "range": [
                x_min - x_margin,
                x_max,
            ],
            "domain": [0.0, 1.0],
            "gridcolor": "rgba(255,255,255,0.15)",
            "zeroline": False,
            "showticklabels": True,
            "tickfont": {
                "size": 9,
            },
            "nticks": 4,
            "ticks": "",
            "automargin": False,
            "fixedrange": True,
        },
        yaxis={
            "title": None,
            "range": [
                0,
                y_max,
            ],
            "domain": [0.0, 1.0],
            "gridcolor": "rgba(255,255,255,0.15)",
            "zeroline": False,
            "showgrid": True,
            "showticklabels": False,
            "ticks": "",
            "automargin": False,
            "fixedrange": True,
        },
        showlegend=False,
        images=[
            _create_sprite_layout_image(
                image_source=sprite_source,
                position_x=current_x,
                position_y=current_y,
                x_span=x_span,
                y_span=y_span,
            )
        ],
        shapes=[
            {
                "type": "rect",
                "x0": x_min - x_margin,
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
                current_time=current_time,
                current_altitude=current_y,
                current_speed=current_speed,
                current_mach=current_mach,
                compact=True,
            )
        ],
    )

    return figure



def create_mobile_flight_replay_html(
    result: SimulationResult,
) -> str:
    """
    スマホ用の軽量飛行リプレイHTMLを作る。

    初回に飛行データとPNGをブラウザへ渡し、
    再生中はCanvas + requestAnimationFrameだけで動かす。
    Streamlit/Pythonの連続再実行は行わない。
    """

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

    if data_count <= 0:
        return "<div>飛行データがありません。</div>"

    max_points = 180
    sample_step = max(
        1,
        math.ceil(data_count / max_points),
    )

    indexes = list(range(0, data_count, sample_step))
    final_index = data_count - 1

    if indexes[-1] != final_index:
        indexes.append(final_index)

    replay_data = []

    for index in indexes:
        speed = math.hypot(
            result.velocities_x[index],
            result.velocities_y[index],
        )

        replay_data.append(
            {
                "t": round(result.times[index], 3),
                "x": round(result.positions_x[index], 3),
                "y": round(result.positions_y[index], 3),
                "speed": round(speed, 3),
                "mach": round(result.mach_numbers[index], 4),
                "angle": round(result.flight_angles[index], 2),
                "burning": bool(result.thrusts[index] > 0),
                "smoke": _calculate_smoke_level(result.times[index]),
            }
        )

    rocket_body, rocket_flame, smoke = _load_sprite_parts()

    data_json = json.dumps(
        replay_data,
        ensure_ascii=False,
        separators=(",", ":"),
    )

    body_json = json.dumps(_image_to_data_uri(rocket_body))
    flame_json = json.dumps(_image_to_data_uri(rocket_flame))
    smoke_json = json.dumps(_image_to_data_uri(smoke))

    html = r'''<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<style>
  * { box-sizing: border-box; }
  html, body { margin: 0; padding: 0; background: transparent; font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }
  .replay-wrap { width: 100%; }
  .replay-card {
    width: 100%;
    background: #071426;
    border-radius: 8px;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,.10);
  }
  .canvas-wrap {
    position: relative;
    width: 100%;
    height: 250px;
    background: linear-gradient(180deg, #0b1d35 0%, #102c4f 62%, #15365b 100%);
  }
  canvas { display: block; width: 100%; height: 100%; }
  .timeline-row {
    height: 42px;
    display: flex;
    align-items: center;
    padding: 0 12px 4px 12px;
    background: #071426;
  }
  input[type="range"] { width: 100%; accent-color: #ff5a52; }
  .external-controls {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-top: 10px;
  }
  .control-btn {
    height: 44px;
    border-radius: 9px;
    border: 1px solid #bcc4d0;
    background: #ffffff;
    color: #202735;
    font-size: 16px;
    font-weight: 600;
  }
  .control-btn:active { transform: scale(.98); }
</style>
</head>
<body>
<div class="replay-wrap">
  <div class="replay-card">
    <div class="canvas-wrap">
      <canvas id="flightCanvas"></canvas>
    </div>
    <div class="timeline-row">
      <input id="timeline" type="range" min="0" max="1000" value="0" step="1" aria-label="再生位置" />
    </div>
  </div>

  <div class="external-controls">
    <button id="playBtn" class="control-btn">▶ 再生</button>
    <button id="pauseBtn" class="control-btn">Ⅱ 一時停止</button>
  </div>
</div>

<script>
const DATA = __DATA__;
const PLAYBACK_DURATION = 10000;

const canvas = document.getElementById('flightCanvas');
const ctx = canvas.getContext('2d');
const timeline = document.getElementById('timeline');
const playBtn = document.getElementById('playBtn');
const pauseBtn = document.getElementById('pauseBtn');

const bodyImg = new Image();
const flameImg = new Image();
const smokeImg = new Image();
bodyImg.src = __BODY__;
flameImg.src = __FLAME__;
smokeImg.src = __SMOKE__;

const xMax = Math.max(...DATA.map(p => p.x), 1);
const yMaxRaw = Math.max(...DATA.map(p => p.y), 1);
const yMax = yMaxRaw * 1.08;

let playing = false;
let progress = 0;
let lastTimestamp = null;
let rafId = null;

function resizeCanvas() {
  const rect = canvas.getBoundingClientRect();
  const dpr = Math.min(window.devicePixelRatio || 1, 2);
  canvas.width = Math.round(rect.width * dpr);
  canvas.height = Math.round(rect.height * dpr);
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  draw();
}

function formatAltitude(value) {
  if (value >= 1000) return (value / 1000).toFixed(value >= 5000 ? 0 : 1) + 'km';
  return Math.round(value) + 'm';
}

function getInterpolatedState(p) {
  const scaled = p * (DATA.length - 1);
  const i0 = Math.floor(scaled);
  const i1 = Math.min(i0 + 1, DATA.length - 1);
  const f = scaled - i0;
  const a = DATA[i0];
  const b = DATA[i1];
  const lerp = (v0, v1) => v0 + (v1 - v0) * f;

  return {
    index: i0,
    t: lerp(a.t, b.t),
    x: lerp(a.x, b.x),
    y: lerp(a.y, b.y),
    speed: lerp(a.speed, b.speed),
    mach: lerp(a.mach, b.mach),
    angle: lerp(a.angle, b.angle),
    burning: f < .5 ? a.burning : b.burning,
    smoke: lerp(a.smoke, b.smoke),
  };
}

function drawRocket(px, py, state) {
  const rocketHeight = 46;
  const bodyAspect = bodyImg.naturalWidth && bodyImg.naturalHeight
    ? bodyImg.naturalWidth / bodyImg.naturalHeight
    : 0.32;
  const rocketWidth = rocketHeight * bodyAspect;

  ctx.save();
  ctx.translate(px, py);
  ctx.rotate((90 - state.angle) * Math.PI / 180);

  if (state.smoke > 0.3 && smokeImg.complete) {
    ctx.globalAlpha = Math.min(.55, state.smoke / 10 * .55);
    const sh = rocketHeight * 1.15;
    const sw = sh * (smokeImg.naturalWidth / Math.max(smokeImg.naturalHeight, 1));
    ctx.drawImage(smokeImg, -sw / 2, rocketHeight * .25, sw, sh);
    ctx.globalAlpha = 1;
  }

  if (state.burning && flameImg.complete) {
    const fh = rocketHeight * .72;
    const fw = fh * (flameImg.naturalWidth / Math.max(flameImg.naturalHeight, 1));
    ctx.drawImage(flameImg, -fw / 2, rocketHeight * .22, fw, fh);
  }

  if (bodyImg.complete) {
    ctx.drawImage(bodyImg, -rocketWidth / 2, -rocketHeight / 2, rocketWidth, rocketHeight);
  } else {
    ctx.fillStyle = '#fff';
    ctx.fillRect(-4, -18, 8, 36);
  }

  ctx.restore();
}

function draw() {
  const w = canvas.clientWidth;
  const h = canvas.clientHeight;
  if (!w || !h) return;

  ctx.clearRect(0, 0, w, h);

  const left = 46;
  const right = 10;
  const top = 34;
  const bottom = 27;
  const plotW = Math.max(1, w - left - right);
  const plotH = Math.max(1, h - top - bottom);

  const mapX = x => left + (x / xMax) * plotW;
  const mapY = y => top + plotH - (y / yMax) * plotH;

  ctx.lineWidth = 1;
  ctx.font = '11px system-ui, -apple-system, sans-serif';
  ctx.textAlign = 'right';
  ctx.textBaseline = 'middle';

  for (let i = 0; i <= 4; i++) {
    const ratio = i / 4;
    const yValue = yMax * ratio;
    const py = mapY(yValue);
    ctx.strokeStyle = 'rgba(255,255,255,.18)';
    ctx.beginPath();
    ctx.moveTo(left, py);
    ctx.lineTo(w - right, py);
    ctx.stroke();
    ctx.fillStyle = 'rgba(255,255,255,.85)';
    ctx.fillText(formatAltitude(yValue), left - 6, py);
  }

  ctx.textAlign = 'center';
  ctx.textBaseline = 'top';
  for (let i = 0; i <= 4; i++) {
    const ratio = i / 4;
    const xValue = xMax * ratio;
    const px = mapX(xValue);
    ctx.strokeStyle = 'rgba(255,255,255,.13)';
    ctx.beginPath();
    ctx.moveTo(px, top);
    ctx.lineTo(px, top + plotH);
    ctx.stroke();
    if (i === 0 || i === 2 || i === 4) {
      ctx.fillStyle = 'rgba(255,255,255,.80)';
      ctx.fillText(Math.round(xValue) + 'm', px, top + plotH + 5);
    }
  }

  ctx.strokeStyle = '#4ea057';
  ctx.lineWidth = 3;
  ctx.beginPath();
  ctx.moveTo(left, mapY(0));
  ctx.lineTo(w - right, mapY(0));
  ctx.stroke();

  const state = getInterpolatedState(progress);

  ctx.strokeStyle = '#ff5a52';
  ctx.lineWidth = 3;
  ctx.beginPath();
  let started = false;
  const endFloat = progress * (DATA.length - 1);
  const endIndex = Math.floor(endFloat);
  for (let i = 0; i <= endIndex; i++) {
    const p = DATA[i];
    const px = mapX(p.x);
    const py = mapY(p.y);
    if (!started) { ctx.moveTo(px, py); started = true; }
    else ctx.lineTo(px, py);
  }
  ctx.lineTo(mapX(state.x), mapY(state.y));
  ctx.stroke();

  drawRocket(mapX(state.x), mapY(state.y), state);

  const status = `T+${state.t.toFixed(1)}s | ${(state.y / 1000).toFixed(2)}km | ${Math.round(state.speed)}m/s | M${state.mach.toFixed(2)}`;
  ctx.font = '600 12px system-ui, -apple-system, sans-serif';
  const tw = ctx.measureText(status).width;
  ctx.fillStyle = 'rgba(4,10,19,.82)';
  ctx.fillRect(left + 4, 5, tw + 12, 24);
  ctx.strokeStyle = '#ff5a52';
  ctx.lineWidth = 1;
  ctx.strokeRect(left + 4, 5, tw + 12, 24);
  ctx.fillStyle = '#fff';
  ctx.textAlign = 'left';
  ctx.textBaseline = 'middle';
  ctx.fillText(status, left + 10, 17);
}

function animate(timestamp) {
  if (!playing) return;
  if (lastTimestamp === null) lastTimestamp = timestamp;
  const delta = timestamp - lastTimestamp;
  lastTimestamp = timestamp;

  progress += delta / PLAYBACK_DURATION;
  if (progress >= 1) {
    progress = 1;
    playing = false;
  }

  timeline.value = Math.round(progress * 1000);
  draw();

  if (playing) rafId = requestAnimationFrame(animate);
}

playBtn.addEventListener('click', () => {
  if (progress >= 1) progress = 0;
  if (!playing) {
    playing = true;
    lastTimestamp = null;
    rafId = requestAnimationFrame(animate);
  }
});

pauseBtn.addEventListener('click', () => {
  playing = false;
  lastTimestamp = null;
  if (rafId) cancelAnimationFrame(rafId);
});

timeline.addEventListener('input', () => {
  progress = Number(timeline.value) / 1000;
  lastTimestamp = null;
  draw();
});

window.addEventListener('resize', resizeCanvas);
[bodyImg, flameImg, smokeImg].forEach(img => img.addEventListener('load', draw));
resizeCanvas();
</script>
</body>
</html>'''

    return (
        html
        .replace("__DATA__", data_json)
        .replace("__BODY__", body_json)
        .replace("__FLAME__", flame_json)
        .replace("__SMOKE__", smoke_json)
    )

# ========================================
# PC / スマホ共通 軽量Canvasリプレイ
# ========================================

@lru_cache(maxsize=16)
def _create_canvas_asset_data_uri(
    path_text: str,
    target_width: int,
) -> str:
    """
    Canvasへ渡すPNGを必要サイズまで縮小してData URI化する。
    元画像をそのままHTMLへ埋め込まないことで、
    初回通信量とブラウザのメモリ使用量を抑える。
    """
    image = _open_rgba(Path(path_text))

    # 生成PNGには端にごく薄い半透明ノイズが残ることがある。
    # 通常のgetbbox()だとそのノイズまで画像領域と判定されるため、
    # 一定以上のアルファだけで実体領域を求めて切り抜く。
    alpha = image.getchannel("A")
    meaningful_alpha = alpha.point(
        lambda value: 255 if value >= 18 else 0
    )
    bounding_box = meaningful_alpha.getbbox()
    if bounding_box is not None:
        image = image.crop(bounding_box)

    if image.width > target_width:
        image = _resize_by_width(
            image,
            target_width,
        )
    return _image_to_data_uri(image)


def create_flight_replay_html(
    result: SimulationResult,
    mobile_mode: bool = False,
) -> str:
    """
    PC / スマホ共通の軽量飛行リプレイHTMLを作る。

    ・Pythonからブラウザへ飛行データと画像を1回だけ送る
    ・再生中はCanvas + requestAnimationFrameのみで描画する
    ・Plotlyのフレームを大量生成しないためMessageSizeErrorを避ける
    ・高度に応じて空色、雲、星空を連続的に変化させる
    """
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
    if data_count <= 0:
        return "<div>飛行データがありません。</div>"

    max_points = 150
    sample_step = max(
        1,
        math.ceil(data_count / max_points),
    )
    indexes = list(range(0, data_count, sample_step))
    final_index = data_count - 1
    if indexes[-1] != final_index:
        indexes.append(final_index)

    replay_data = []
    for index in indexes:
        speed = math.hypot(
            result.velocities_x[index],
            result.velocities_y[index],
        )
        replay_data.append(
            {
                "t": round(result.times[index], 3),
                "x": round(result.positions_x[index], 3),
                "y": round(result.positions_y[index], 3),
                "speed": round(speed, 3),
                "mach": round(result.mach_numbers[index], 4),
                "angle": round(result.flight_angles[index], 2),
                "burning": bool(result.thrusts[index] > 0),
                "smoke": _calculate_smoke_level(result.times[index]),
            }
        )

    data_json = json.dumps(
        replay_data,
        ensure_ascii=False,
        separators=(",", ":"),
    )

    body_json = json.dumps(
        _create_canvas_asset_data_uri(str(ROCKET_BODY_PATH), 150)
    )
    flame_json = json.dumps(
        _create_canvas_asset_data_uri(str(ROCKET_FLAME_PATH), 130)
    )
    smoke_json = json.dumps(
        _create_canvas_asset_data_uri(str(SMOKE_PATH), 120)
    )
    cloud_01_json = json.dumps(
        _create_canvas_asset_data_uri(
            str(ASSET_DIRECTORY / "cloud_01.png"), 520
        )
    )
    cloud_02_json = json.dumps(
        _create_canvas_asset_data_uri(
            str(ASSET_DIRECTORY / "cloud_02.png"), 620
        )
    )
    cloud_03_json = json.dumps(
        _create_canvas_asset_data_uri(
            str(ASSET_DIRECTORY / "cloud_03.png"), 390
        )
    )

    canvas_height = 285 if mobile_mode else 500
    control_height = 46 if mobile_mode else 48
    status_font_size = 11 if mobile_mode else 13
    axis_font_size = 10 if mobile_mode else 12
    rocket_height = 48 if mobile_mode else 66

    html = r'''<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<style>
  * { box-sizing: border-box; }
  html, body {
    margin: 0;
    padding: 0;
    background: transparent;
    font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  }
  .replay-wrap { width: 100%; }
  .replay-card {
    width: 100%;
    background: #071426;
    border-radius: 10px;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,.12);
    box-shadow: 0 8px 24px rgba(2,10,22,.10);
  }
  .canvas-wrap {
    position: relative;
    width: 100%;
    height: __CANVAS_HEIGHT__px;
    background: #0b1d35;
  }
  canvas { display: block; width: 100%; height: 100%; }
  .timeline-row {
    height: 46px;
    display: flex;
    align-items: center;
    padding: 2px 14px 6px 14px;
    background: #071426;
    border-top: 1px solid rgba(255,255,255,.08);
  }
  input[type="range"] {
    width: 100%;
    accent-color: #ff5a52;
    cursor: pointer;
  }
  .external-controls {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
    margin-top: 10px;
  }
  .control-btn {
    height: __CONTROL_HEIGHT__px;
    border-radius: 9px;
    border: 1px solid #bcc4d0;
    background: #ffffff;
    color: #202735;
    font-size: 15px;
    font-weight: 650;
    cursor: pointer;
  }
  .control-btn:hover { background: #f6f8fb; }
  .control-btn:active { transform: scale(.985); }
</style>
</head>
<body>
<div class="replay-wrap">
  <div class="replay-card">
    <div class="canvas-wrap">
      <canvas id="flightCanvas"></canvas>
    </div>
    <div class="timeline-row">
      <input id="timeline" type="range" min="0" max="1000" value="0" step="1" aria-label="再生位置" />
    </div>
  </div>

  <div class="external-controls">
    <button id="playBtn" class="control-btn">▶ 再生</button>
    <button id="pauseBtn" class="control-btn">Ⅱ 一時停止</button>
  </div>
</div>

<script>
const DATA = __DATA__;
const PLAYBACK_DURATION = 12000;
const STATUS_FONT_SIZE = __STATUS_FONT_SIZE__;
const AXIS_FONT_SIZE = __AXIS_FONT_SIZE__;
const ROCKET_HEIGHT = __ROCKET_HEIGHT__;

const canvas = document.getElementById('flightCanvas');
const ctx = canvas.getContext('2d', { alpha: false });
const timeline = document.getElementById('timeline');
const playBtn = document.getElementById('playBtn');
const pauseBtn = document.getElementById('pauseBtn');

const bodyImg = new Image();
const flameImg = new Image();
const smokeImg = new Image();
const cloud01 = new Image();
const cloud02 = new Image();
const cloud03 = new Image();
bodyImg.src = __BODY__;
flameImg.src = __FLAME__;
smokeImg.src = __SMOKE__;
cloud01.src = __CLOUD_01__;
cloud02.src = __CLOUD_02__;
cloud03.src = __CLOUD_03__;

const xMaxRaw = Math.max(...DATA.map(p => p.x), 1);
const yMaxRaw = Math.max(...DATA.map(p => p.y), 1);
const xMax = xMaxRaw * 1.04;
const yMax = yMaxRaw * 1.08;

let playing = false;
let progress = 0;
let lastTimestamp = null;
let rafId = null;

function clamp(v, lo, hi) {
  return Math.max(lo, Math.min(hi, v));
}

function mixColor(a, b, t) {
  const c = [];
  for (let i = 0; i < 3; i++) {
    c.push(Math.round(a[i] + (b[i] - a[i]) * t));
  }
  return `rgb(${c[0]},${c[1]},${c[2]})`;
}

function skyColors(altitude) {
  const lowTop = [67, 145, 214];
  const lowBottom = [167, 219, 246];
  const midTop = [19, 65, 122];
  const midBottom = [65, 135, 190];
  const highTop = [5, 17, 45];
  const highBottom = [20, 55, 105];
  const spaceTop = [1, 4, 13];
  const spaceBottom = [5, 12, 30];

  if (altitude <= 12000) {
    const t = clamp(altitude / 12000, 0, 1);
    return [mixColor(lowTop, midTop, t), mixColor(lowBottom, midBottom, t)];
  }
  if (altitude <= 35000) {
    const t = (altitude - 12000) / 23000;
    return [mixColor(midTop, highTop, t), mixColor(midBottom, highBottom, t)];
  }
  const t = clamp((altitude - 35000) / 45000, 0, 1);
  return [mixColor(highTop, spaceTop, t), mixColor(highBottom, spaceBottom, t)];
}

function drawSky(w, h, altitude) {
  const [topColor, bottomColor] = skyColors(altitude);
  const gradient = ctx.createLinearGradient(0, 0, 0, h);
  gradient.addColorStop(0, topColor);
  gradient.addColorStop(1, bottomColor);
  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, w, h);

  const starAlpha = clamp((altitude - 18000) / 40000, 0, .85);
  if (starAlpha > 0) {
    ctx.save();
    ctx.fillStyle = `rgba(255,255,255,${starAlpha})`;
    for (let i = 0; i < 64; i++) {
      const sx = ((i * 83 + 31) % 997) / 997 * w;
      const sy = ((i * 157 + 47) % 991) / 991 * h * .82;
      const size = (i % 7 === 0) ? 1.7 : 1.0;
      ctx.fillRect(sx, sy, size, size);
    }
    ctx.restore();
  }
}

function formatAltitude(value) {
  if (value >= 1000) {
    const km = value / 1000;
    return (km >= 10 ? km.toFixed(0) : km.toFixed(1)) + 'km';
  }
  return Math.round(value) + 'm';
}

function formatDistance(value) {
  if (value >= 1000) {
    return (value / 1000).toFixed(value >= 5000 ? 0 : 1) + 'km';
  }
  return Math.round(value) + 'm';
}

function getInterpolatedState(p) {
  const scaled = p * (DATA.length - 1);
  const i0 = Math.floor(scaled);
  const i1 = Math.min(i0 + 1, DATA.length - 1);
  const f = scaled - i0;
  const a = DATA[i0];
  const b = DATA[i1];
  const lerp = (v0, v1) => v0 + (v1 - v0) * f;
  return {
    index: i0,
    t: lerp(a.t, b.t),
    x: lerp(a.x, b.x),
    y: lerp(a.y, b.y),
    speed: lerp(a.speed, b.speed),
    mach: lerp(a.mach, b.mach),
    angle: lerp(a.angle, b.angle),
    burning: f < .5 ? a.burning : b.burning,
    smoke: lerp(a.smoke, b.smoke),
  };
}

function drawCloud(img, cx, cy, width, opacity) {
  if (!img.complete || !img.naturalWidth || opacity <= .01) return;
  const aspect = img.naturalHeight / img.naturalWidth;
  const height = width * aspect;
  ctx.save();
  ctx.globalAlpha = opacity;
  ctx.drawImage(img, cx - width / 2, cy - height / 2, width, height);
  ctx.restore();
}

function drawCloudLayer(mapX, mapY, plotW, currentAltitude) {
  const opacity = clamp(.92 - currentAltitude / 11000, .12, .92);
  const clouds = [
    [cloud03, xMax * .12, 850,  plotW * .18, .72],
    [cloud02, xMax * .35, 1650, plotW * .30, .62],
    [cloud01, xMax * .62, 2800, plotW * .22, .72],
    [cloud03, xMax * .81, 3900, plotW * .15, .52],
    [cloud02, xMax * .92, 5200, plotW * .25, .38],
  ];

  for (const [img, x, y, width, layerOpacity] of clouds) {
    if (y <= yMax * 1.05) {
      drawCloud(img, mapX(x), mapY(y), width, opacity * layerOpacity);
    }
  }
}

function drawRocket(px, py, state) {
  const rocketHeight = ROCKET_HEIGHT;
  const bodyAspect = bodyImg.naturalWidth && bodyImg.naturalHeight
    ? bodyImg.naturalWidth / bodyImg.naturalHeight
    : 0.32;
  const rocketWidth = rocketHeight * bodyAspect;

  ctx.save();
  ctx.translate(px, py);
  ctx.rotate((90 - state.angle) * Math.PI / 180);

  if (state.smoke > .3 && smokeImg.complete) {
    ctx.globalAlpha = Math.min(.48, state.smoke / 10 * .48);
    const sh = rocketHeight * 1.05;
    const sw = sh * (smokeImg.naturalWidth / Math.max(smokeImg.naturalHeight, 1));
    ctx.drawImage(smokeImg, -sw / 2, rocketHeight * .22, sw, sh);
    ctx.globalAlpha = 1;
  }

  if (state.burning && flameImg.complete) {
    const pulse = 1 + Math.sin(performance.now() / 75) * .08;
    const fh = rocketHeight * .70 * pulse;
    const fw = fh * (flameImg.naturalWidth / Math.max(flameImg.naturalHeight, 1));
    ctx.drawImage(flameImg, -fw / 2, rocketHeight * .20, fw, fh);
  }

  if (bodyImg.complete) {
    ctx.drawImage(bodyImg, -rocketWidth / 2, -rocketHeight / 2, rocketWidth, rocketHeight);
  }
  ctx.restore();
}

function resizeCanvas() {
  const rect = canvas.getBoundingClientRect();
  const dpr = Math.min(window.devicePixelRatio || 1, 1.6);
  canvas.width = Math.max(1, Math.round(rect.width * dpr));
  canvas.height = Math.max(1, Math.round(rect.height * dpr));
  ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  draw();
}

function draw() {
  const w = canvas.clientWidth;
  const h = canvas.clientHeight;
  if (!w || !h) return;

  const state = getInterpolatedState(progress);
  drawSky(w, h, state.y);

  const mobile = w < 600;
  const left = mobile ? 44 : 62;
  const right = mobile ? 9 : 18;
  const top = mobile ? 34 : 44;
  const bottom = mobile ? 28 : 34;
  const plotW = Math.max(1, w - left - right);
  const plotH = Math.max(1, h - top - bottom);

  const mapX = x => left + (x / xMax) * plotW;
  const mapY = y => top + plotH - (y / yMax) * plotH;

  drawCloudLayer(mapX, mapY, plotW, state.y);

  const earthCurve = clamp(state.y / 80000, 0, 1);
  const groundY = mapY(0);
  ctx.save();
  if (earthCurve < .25) {
    const groundGradient = ctx.createLinearGradient(0, groundY, 0, h);
    groundGradient.addColorStop(0, '#4b9b55');
    groundGradient.addColorStop(.18, '#285d38');
    groundGradient.addColorStop(1, '#183525');
    ctx.fillStyle = groundGradient;
    ctx.fillRect(left, groundY, plotW, Math.max(0, h - groundY));
  } else {
    ctx.fillStyle = '#174c73';
    ctx.beginPath();
    const radiusX = plotW * 1.25;
    const radiusY = 70 + earthCurve * 50;
    ctx.ellipse(left + plotW / 2, groundY + radiusY - 4, radiusX, radiusY, 0, Math.PI, Math.PI * 2);
    ctx.fill();
  }
  ctx.restore();

  ctx.lineWidth = 1;
  ctx.font = `${AXIS_FONT_SIZE}px system-ui, -apple-system, sans-serif`;
  ctx.textAlign = 'right';
  ctx.textBaseline = 'middle';

  for (let i = 0; i <= 4; i++) {
    const ratio = i / 4;
    const yValue = yMax * ratio;
    const py = mapY(yValue);
    ctx.strokeStyle = 'rgba(255,255,255,.20)';
    ctx.beginPath();
    ctx.moveTo(left, py);
    ctx.lineTo(w - right, py);
    ctx.stroke();
    ctx.fillStyle = 'rgba(255,255,255,.92)';
    ctx.fillText(formatAltitude(yValue), left - 6, py);
  }

  ctx.textAlign = 'center';
  ctx.textBaseline = 'top';
  for (let i = 0; i <= 4; i++) {
    const ratio = i / 4;
    const xValue = xMax * ratio;
    const px = mapX(xValue);
    ctx.strokeStyle = 'rgba(255,255,255,.14)';
    ctx.beginPath();
    ctx.moveTo(px, top);
    ctx.lineTo(px, top + plotH);
    ctx.stroke();
    if (i === 0 || i === 2 || i === 4) {
      ctx.fillStyle = 'rgba(255,255,255,.90)';
      ctx.fillText(formatDistance(xValue), px, top + plotH + 5);
    }
  }

  ctx.strokeStyle = '#65ba68';
  ctx.lineWidth = 2.5;
  ctx.beginPath();
  ctx.moveTo(left, groundY);
  ctx.lineTo(w - right, groundY);
  ctx.stroke();

  ctx.strokeStyle = '#ff5a52';
  ctx.lineWidth = mobile ? 2.6 : 3.3;
  ctx.beginPath();
  let started = false;
  const endFloat = progress * (DATA.length - 1);
  const endIndex = Math.floor(endFloat);
  for (let i = 0; i <= endIndex; i++) {
    const p = DATA[i];
    const px = mapX(p.x);
    const py = mapY(p.y);
    if (!started) {
      ctx.moveTo(px, py);
      started = true;
    } else {
      ctx.lineTo(px, py);
    }
  }
  ctx.lineTo(mapX(state.x), mapY(state.y));
  ctx.stroke();

  drawRocket(mapX(state.x), mapY(state.y), state);

  const status = `T+${state.t.toFixed(1)}s | ${(state.y / 1000).toFixed(2)}km | ${Math.round(state.speed)}m/s | M${state.mach.toFixed(2)}`;
  ctx.font = `650 ${STATUS_FONT_SIZE}px system-ui, -apple-system, sans-serif`;
  const tw = ctx.measureText(status).width;
  const statusX = left + 4;
  const statusY = 6;
  const statusH = mobile ? 24 : 28;
  ctx.fillStyle = 'rgba(4,10,19,.76)';
  ctx.fillRect(statusX, statusY, tw + 14, statusH);
  ctx.strokeStyle = '#ff5a52';
  ctx.lineWidth = 1;
  ctx.strokeRect(statusX, statusY, tw + 14, statusH);
  ctx.fillStyle = '#fff';
  ctx.textAlign = 'left';
  ctx.textBaseline = 'middle';
  ctx.fillText(status, statusX + 7, statusY + statusH / 2);
}

function animate(timestamp) {
  if (!playing) return;
  if (lastTimestamp === null) lastTimestamp = timestamp;
  const delta = timestamp - lastTimestamp;
  lastTimestamp = timestamp;
  progress += delta / PLAYBACK_DURATION;
  if (progress >= 1) {
    progress = 1;
    playing = false;
  }
  timeline.value = Math.round(progress * 1000);
  draw();
  if (playing) rafId = requestAnimationFrame(animate);
}

playBtn.addEventListener('click', () => {
  if (progress >= 1) progress = 0;
  if (!playing) {
    playing = true;
    lastTimestamp = null;
    rafId = requestAnimationFrame(animate);
  }
});

pauseBtn.addEventListener('click', () => {
  playing = false;
  lastTimestamp = null;
  if (rafId) cancelAnimationFrame(rafId);
});

timeline.addEventListener('input', () => {
  progress = Number(timeline.value) / 1000;
  lastTimestamp = null;
  draw();
});

window.addEventListener('resize', resizeCanvas);
[bodyImg, flameImg, smokeImg, cloud01, cloud02, cloud03]
  .forEach(img => img.addEventListener('load', draw));
resizeCanvas();
</script>
</body>
</html>'''

    return (
        html
        .replace("__DATA__", data_json)
        .replace("__BODY__", body_json)
        .replace("__FLAME__", flame_json)
        .replace("__SMOKE__", smoke_json)
        .replace("__CLOUD_01__", cloud_01_json)
        .replace("__CLOUD_02__", cloud_02_json)
        .replace("__CLOUD_03__", cloud_03_json)
        .replace("__CANVAS_HEIGHT__", str(canvas_height))
        .replace("__CONTROL_HEIGHT__", str(control_height))
        .replace("__STATUS_FONT_SIZE__", str(status_font_size))
        .replace("__AXIS_FONT_SIZE__", str(axis_font_size))
        .replace("__ROCKET_HEIGHT__", str(rocket_height))
    )
