"""Headless sweep orchestrator: iterate (roof x date x time) -> capture -> rows.

Requires Isaac Sim + RTX GPU (headless SimulationApp) and depends on capture.py.
Adds checkpoint/resume and per-site/year sharding for the observation campaign.

Planned API
-----------
    run_sweep(config) -> None       # set sun (ephemeris) -> capture -> sample -> append Parquet
    resume(config) -> None          # idempotent restart from checkpoint

Stub: superseded by the GUI runner (scripts/production_sweep_gui.py).
"""
from __future__ import annotations

_BLOCKED = "solar_twin.sweep is superseded by the GUI runner (scripts/production_sweep_gui.py); see README."


def run_sweep(config) -> None:
    raise NotImplementedError(_BLOCKED)


def resume(config) -> None:
    raise NotImplementedError(_BLOCKED)
