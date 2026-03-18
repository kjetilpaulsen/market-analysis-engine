from __future__ import annotations
from collections.abc import Iterator, Sequence, Callable
import logging

# FIX: change project name for imports
from market_analysis_engine.analysis.models.displaygraphhandler import DisplayGraphHandler
from market_analysis_engine.commands.commands import CmdDisplayGraph, CmdUpdateAll, Command, CmdDisplayVersion
from market_analysis_engine.events.events import Event
from market_analysis_engine.handlers.displayversionhandler import DisplayVersionHandler
from market_analysis_engine.handlers.updateallhandler import UpdateAllHandler
from market_analysis_engine.marketdata.yfclient import YFClient
from market_analysis_engine.runtime.runtime import AppPaths, CFGDataBase, CFGDev, CFGTickerService, MetaInfo

# from market_analysis_engine.cli.runtimeflags import CliFlags
# from market_analysis_engine.ui.cli.clicontroller import CLIController
# from market_analysis_engine.config.config import AppConfig, CFGTickerService, CFGDataBase
from market_analysis_engine.db.connect import connect
from market_analysis_engine.db.repo import MarketRepo
from market_analysis_engine.db.schema import create_schema
from market_analysis_engine.marketdata.yfclient import YFClient
# from market_analysis_engine.handlers.uihandlers import Handler
from market_analysis_engine.marketdata.marketservice import MarketService
from market_analysis_engine.tickers.tickerclient import TickerClient
from market_analysis_engine.tickers.tickerservice import Ticker, TickerService
# from market_analysis_engine.commands.uicommands import (
#     CmdNotAnOption, 
#     CmdQuit, 
#     CmdUpdateAll,
#     Command, 
# )
# from market_analysis_engine.events.uievents import (
#     EvtExit,
#     EvtStartUp,
#     EvtStatus, 
#     EvtProgress,
#     Event, 
# )


logger = logging.getLogger(__name__)

class App:
    """
    Core application engine responsible for executing commands.

    The `App` class acts as the central coordinator for the application.
    It owns the runtime configuration and services required to execute
    commands and produce events.

    Commands passed into the application are resolved to handler objects
    which perform the actual work. Handlers emit `Event` objects that
    describe progress, results, or errors. These events are yielded back
    to the caller, allowing different frontends (CLI, API, etc.) to decide
    how to present the results.

    Attributes:
        meta: Application metadata such as name, version, and description.
        dev: Development-related runtime flags.
        db: Database configuration.
        paths: Resolved application filesystem paths.
    """
    def __init__(self, meta: MetaInfo, dev: CFGDev, db: CFGDataBase, paths: AppPaths, cfg_ts: CFGTickerService) -> None:
        """
        Initialize the application runtime.

        The constructor stores the runtime configuration and prepares any
        services required by the application. Service initialization such
        as database connections, caches, or external clients may also be
        performed here.

        Args:
            meta: Application metadata.
            dev: Development configuration flags.
            db: Database configuration settings.
            paths: Resolved filesystem paths used by the application.
        """
        logger.info("--INITIALIZING APP--")
        self.meta = meta
        self.dev = dev
        self.db = db
        self.paths = paths
        self.cfg_ts = cfg_ts

        # DB wiring
        self._conn = connect(self.db)
        logger.info("DB connection created")
        create_schema(self._conn)
        repo = MarketRepo(self._conn)

        # Market wiring
        yfclient = YFClient()
        mkt = MarketService(client=yfclient)

        # Ticker wiring
        tickerclient = TickerClient()
        ts = TickerService(repo=repo, tickerclient=tickerclient, cfg_ts=self.cfg_ts, cfg_dev= self.dev)

        # Create handlers
        self._handlers: dict[type[Command], Callable] = {
            CmdDisplayVersion: lambda cmd: DisplayVersionHandler(cmd, self.meta).handle(),
            CmdUpdateAll: lambda cmd: UpdateAllHandler(cmd, repo, ts, mkt, self.cfg_ts).handle(),
            CmdDisplayGraph: lambda cmd: DisplayGraphHandler(cmd, repo, self.paths).handle(),
        }

    def run(self, cmds: Sequence[Command]) -> Iterator[Event]:
        """
        Execute a sequence of commands and yield resulting events.

        Each command is dispatched to its corresponding handler via
        `_handle_command`. Handlers produce a stream of `Event` objects
        describing the execution results.

        This generator-based design allows frontends to process events
        incrementally instead of waiting for the entire command pipeline
        to complete.

        Args:
            cmds: A sequence of command objects to execute.

        Yields:
            Event: Events produced during command execution.
        """
        logger.debug("Starting run(cmd) ..")
        for cmd in cmds:
            yield from self._handle_command(cmd)

    def _handle_command(self, cmd: Command) -> Iterator[Event]:
        """
        Resolve and execute the handler corresponding to a command.

        The method maps command types to their handler implementations.
        If a matching handler exists, it is invoked and its resulting
        event stream is yielded back to the caller.

        Args:
            cmd: A command instance representing an application action.

        Yields:
            Event: Events produced by the command handler.

        Raises:
            ValueError: If no handler is registered for the given command
                type.
        """
        handler = self._handlers.get(type(cmd)) 
        if handler is None:
            raise ValueError(f"Command not found in _handlers: {type(cmd).__name__}")
        yield from handler(cmd)
