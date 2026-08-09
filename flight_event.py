from dataclasses import dataclass
from enum import Enum


class FlightEventType(Enum):
    """
    飛行イベントの種類。
    """

    IGNITION = "Ignition"
    LAUNCH = "Launch"
    MACH_ONE = "Mach 1"
    MAX_Q = "Max Q"
    BURNOUT = "Burnout"
    APOGEE = "Apogee"
    LANDING = "Landing"


@dataclass(frozen=True)
class FlightEvent:
    """
    飛行中に発生したイベント。

    Attributes
    ----------
    event_type:
        イベントの種類

    time:
        イベント発生時刻（秒）

    altitude:
        イベント発生高度（m）

    description:
        イベントの説明
    """

    event_type: FlightEventType
    time: float
    altitude: float
    description: str


class FlightEventManager:
    """
    飛行中に発生したイベントを管理するクラス。
    """

    def __init__(self) -> None:
        """
        空のイベント一覧を作成する。
        """

        self._events: list[FlightEvent] = []

    def add_event(
        self,
        event: FlightEvent,
    ) -> None:
        """
        飛行イベントを追加する。

        Parameters
        ----------
        event:
            追加する飛行イベント
        """

        self._events.append(event)

    def get_events(
        self,
    ) -> list[FlightEvent]:
        """
        イベントを発生時刻順に並べて返す。

        Returns
        -------
        list[FlightEvent]:
            時刻順に並んだイベント一覧
        """

        return sorted(
            self._events,
            key=lambda event: event.time,
        )