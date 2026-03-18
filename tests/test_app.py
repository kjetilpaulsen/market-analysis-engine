# tests/test_app.py

from __future__ import annotations

from pathlib import Path

import pytest

from market_analysis_engine.app import App
from market_analysis_engine.commands.commands import CmdDisplayVersion, Command
from market_analysis_engine.events.events import EvtResult
from market_analysis_engine.runtime.runtime import AppPaths, CFGDataBase, CFGDev, CFGTickerService, MetaInfo


def _make_app(tmp_path: Path) -> App:
    return App(
        meta=MetaInfo(
            app_name="market-analysis-engine",
            app_version="1.2.3",
            app_description="test app",
        ),
        dev=CFGDev(dev_mode=False, dry_run=False),
        db=CFGDataBase(
            db_name="market_analysis_engine",
            db_host="/run/postgresql",
        ),
        paths=AppPaths(
            data_dir=tmp_path / "data",
            state_dir=tmp_path / "state",
            cache_dir=tmp_path / "cache",
            tmp_dir=tmp_path / "cache" / "tmp",
            config_dir=tmp_path / "config",
        ),
        cfg_ts=CFGTickerService(),
    )


def test_app_run_executes_registered_command(tmp_path: Path):
    app = _make_app(tmp_path)

    events = list(app.run([CmdDisplayVersion(uppercase=True)]))

    assert events == [
        EvtResult(
            command_name="DisplayVersion",
            payload={"version": "V1.2.3"},
        )
    ]


def test_app_run_preserves_command_order(tmp_path: Path):
    app = _make_app(tmp_path)

    events = list(
        app.run(
            [
                CmdDisplayVersion(uppercase=False),
                CmdDisplayVersion(uppercase=True),
            ]
        )
    )

    assert events == [
        EvtResult(
            command_name="DisplayVersion",
            payload={"version": "v1.2.3"},
        ),
        EvtResult(
            command_name="DisplayVersion",
            payload={"version": "V1.2.3"},
        ),
    ]


def test_handle_command_raises_for_unknown_command(tmp_path: Path):
    app = _make_app(tmp_path)

    class UnknownCommand(Command):
        pass

    with pytest.raises(ValueError, match="Command not found in _handlers: UnknownCommand"):
        list(app._handle_command(UnknownCommand()))
