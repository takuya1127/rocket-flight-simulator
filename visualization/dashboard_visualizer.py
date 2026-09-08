"""
Visualization compatibility layer.

Flight Replayの実装本体は
visualization.flight_replay パッケージへ分離しています。
"""

from visualization.flight_replay import (
    create_flight_replay_html,
)

__all__ = [
    "create_flight_replay_html",
]
