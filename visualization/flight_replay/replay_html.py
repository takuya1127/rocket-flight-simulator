import json

from models.simulation_models import SimulationResult

from .replay_assets import (
    BOOSTER_PATH,
    ENGINE_FLAME_PATH,
    FAIRING_PATH,
    FIRST_STAGE_PATH,
    GROUND_BACKGROUND_PATH,
    LAUNCH_PAD_PATH,
    LAUNCH_SMOKE_PATH,
    SECOND_STAGE_PATH,
    SPACE_BACKGROUND_PATH,
    UPPER_ATMOSPHERE_BACKGROUND_PATH,
    create_canvas_asset_data_uri,
    create_canvas_background_data_uri,
    create_optional_canvas_asset_data_uri,
)
from .replay_data import build_event_times, build_replay_data
from .replay_template import REPLAY_HTML


def create_flight_replay_html(
    result: SimulationResult,
    mobile_mode: bool = False,
) -> str:
    replay_data = build_replay_data(result)
    if not replay_data:
        return "<div>飛行データがありません。</div>"

    replacements = {
        "__DATA__": json.dumps(
            replay_data,
            ensure_ascii=False,
            separators=(",", ":"),
        ),
        "__EVENT_TIMES__": json.dumps(
            build_event_times(result),
            separators=(",", ":"),
        ),
        "__FIRST_STAGE__": json.dumps(
            create_canvas_asset_data_uri(str(FIRST_STAGE_PATH), 240)
        ),
        "__SECOND_STAGE__": json.dumps(
            create_canvas_asset_data_uri(str(SECOND_STAGE_PATH), 220)
        ),
        "__BOOSTER__": json.dumps(
            create_canvas_asset_data_uri(str(BOOSTER_PATH), 180)
        ),
        "__FAIRING__": json.dumps(
            create_optional_canvas_asset_data_uri(str(FAIRING_PATH), 180)
        ),
        "__LAUNCH_PAD__": json.dumps(
            create_optional_canvas_asset_data_uri(str(LAUNCH_PAD_PATH), 420)
        ),
        "__FLAME__": json.dumps(
            create_canvas_asset_data_uri(str(ENGINE_FLAME_PATH), 150)
        ),
        "__SMOKE__": json.dumps(
            create_canvas_asset_data_uri(str(LAUNCH_SMOKE_PATH), 360)
        ),
        "__GROUND_BACKGROUND__": json.dumps(
            create_canvas_background_data_uri(str(GROUND_BACKGROUND_PATH), 1280)
        ),
        "__UPPER_BACKGROUND__": json.dumps(
            create_canvas_background_data_uri(str(UPPER_ATMOSPHERE_BACKGROUND_PATH), 1280)
        ),
        "__SPACE_BACKGROUND__": json.dumps(
            create_canvas_background_data_uri(str(SPACE_BACKGROUND_PATH), 1280)
        ),
        "__CANVAS_HEIGHT__": str(320 if mobile_mode else 540),
        "__CONTROL_HEIGHT__": str(46 if mobile_mode else 48),
        "__STATUS_FONT_SIZE__": str(11 if mobile_mode else 13),
        "__ROCKET_HEIGHT__": str(108 if mobile_mode else 158),
    }

    html = REPLAY_HTML
    for key, value in replacements.items():
        html = html.replace(key, value)
    return html
