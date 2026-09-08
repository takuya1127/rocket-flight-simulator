import base64
import io
from functools import lru_cache
from pathlib import Path

from PIL import Image


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ASSET_DIRECTORY = PROJECT_ROOT / "assets"

FIRST_STAGE_PATH = ASSET_DIRECTORY / "rocket_first_stage.png"
SECOND_STAGE_PATH = ASSET_DIRECTORY / "rocket_second_stage.png"
BOOSTER_PATH = ASSET_DIRECTORY / "rocket_booster.png"
FAIRING_PATH = ASSET_DIRECTORY / "rocket_fairing.png"
LAUNCH_PAD_PATH = ASSET_DIRECTORY / "launch_pad.png"

ENGINE_FLAME_PATH = ASSET_DIRECTORY / "engine_flame.png"
LAUNCH_SMOKE_PATH = ASSET_DIRECTORY / "launch_smoke.png"

GROUND_BACKGROUND_PATH = ASSET_DIRECTORY / "background_ground.png"
UPPER_ATMOSPHERE_BACKGROUND_PATH = ASSET_DIRECTORY / "background_upper_atmosphere.png"
SPACE_BACKGROUND_PATH = ASSET_DIRECTORY / "background_space.png"


def _open_rgba(path: Path) -> Image.Image:
    if not path.exists():
        raise FileNotFoundError(f"画像ファイルが見つかりません: {path}")
    return Image.open(path).convert("RGBA")


def _resize_by_width(image: Image.Image, width: int) -> Image.Image:
    height = max(1, round(image.height * width / image.width))
    return image.resize((width, height), Image.Resampling.LANCZOS)


def _image_to_data_uri(
    image: Image.Image,
    format_name: str = "PNG",
    **save_kwargs,
) -> str:
    buffer = io.BytesIO()
    image.save(buffer, format=format_name, **save_kwargs)
    encoded = base64.b64encode(buffer.getvalue()).decode("ascii")
    mime = "image/jpeg" if format_name.upper() == "JPEG" else "image/png"
    return f"data:{mime};base64,{encoded}"


@lru_cache(maxsize=24)
def create_canvas_asset_data_uri(path_text: str, target_width: int) -> str:
    image = _open_rgba(Path(path_text))
    alpha = image.getchannel("A")
    meaningful_alpha = alpha.point(lambda value: 255 if value >= 18 else 0)
    bounding_box = meaningful_alpha.getbbox()
    if bounding_box is not None:
        image = image.crop(bounding_box)
    if image.width > target_width:
        image = _resize_by_width(image, target_width)
    return _image_to_data_uri(image)


@lru_cache(maxsize=12)
def create_optional_canvas_asset_data_uri(path_text: str, target_width: int) -> str:
    path = Path(path_text)
    if not path.exists():
        image = Image.new("RGBA", (1, 1), (0, 0, 0, 0))
        return _image_to_data_uri(image)
    return create_canvas_asset_data_uri(path_text, target_width)


@lru_cache(maxsize=12)
def create_canvas_background_data_uri(path_text: str, target_width: int) -> str:
    path = Path(path_text)
    if not path.exists():
        raise FileNotFoundError(f"背景画像が見つかりません: {path}")
    image = Image.open(path).convert("RGB")
    if image.width > target_width:
        image = _resize_by_width(image, target_width)
    return _image_to_data_uri(
        image,
        "JPEG",
        quality=80,
        optimize=True,
        progressive=True,
    )
