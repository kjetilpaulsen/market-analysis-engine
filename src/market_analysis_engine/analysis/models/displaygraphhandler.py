from __future__ import annotations
import os
import logging
from typing import Iterator
from market_analysis_engine.commands.commands import CmdDisplayGraph
from market_analysis_engine.db.repo import MarketRepo
from market_analysis_engine.events.events import Event, EvtLog
from market_analysis_engine.handlers.commandhandler import CommandHandler
from market_analysis_engine.runtime.runtime import AppPaths
from market_analysis_engine.utils.utils import period_to_date
import matplotlib.pyplot as plt
import subprocess
import numpy as np


logger = logging.getLogger(__name__)

class DisplayGraphHandler(CommandHandler):
    def __init__(self, cmd: CmdDisplayGraph, repo: MarketRepo, paths: AppPaths):
        self.cmd = cmd
        self.repo = repo
        self.paths = paths

    def handle(self) -> Iterator[Event]:
        """
        Execute the command and produce events describing the result.

        This method acts as the standard entrypoint for all command
        handlers. It coordinates the execution flow and delegates the
        actual work to helper methods that produce events.

        Handlers emit events using Python generators. This allows the
        application to stream progress updates, intermediate results,
        and final outputs to the frontend.

        Examples of typical event patterns:

            Producing a single result:

                yield EvtResult(...)

            Producing progress updates followed by a result:

                for i in range(total):
                    yield EvtProgress(...)
                yield EvtResult(...)

        Returns:
            Iterator[Event]: A generator yielding events produced during
            command execution.
        """
        logger.info("Handling CmdDisplayGraph ..")
        yield from self._handle_display_graph_of_period()

    def _handle_display_graph_of_period(self):
        """
        Handles the request for graph display of a single ticker
        """
        df = self.repo.fetch_adjclose_series(self.cmd.ticker, self.cmd.period)
        #create plot here for now

        x = np.arange(len(df))
        adjclose = df["adjclose"].to_numpy()

        coef = np.polyfit(x, adjclose, deg = 1)
        trend = np.poly1d(coef)(x)

        out_dir = self.paths.data_dir
        filename = f"{self.cmd.ticker}_{self.cmd.period}.png"
        out_path = out_dir / filename

        #set colors:
        plt.rcParams.update({
        "figure.facecolor": "#0f172a",
        "axes.facecolor": "#0f172a",
        "axes.edgecolor": "white",
        "axes.labelcolor": "white",
        "text.color": "white",
        "xtick.color": "white",
        "ytick.color": "white",
        "grid.color": "#e5e7eb",
        "grid.alpha": 0.25,
        })

        #plt.style.use("seaborn-v0_8-darkgrid")
        fig, ax = plt.subplots(figsize=(10,5))
        #ax.plot(df["date"], df["adjclose"], linewidth=2)
        ax.plot(df["date"], adjclose, label="Adj Close", linewidth=2, color="#38bdf8")
        ax.plot(df["date"], trend, label="Linear trend", linestyle="--", linewidth=2, color="#fbbf24")
        ax.set_title(f"{self.cmd.ticker} - Adjusted close ({self.cmd.period})")
        ax.set_xlabel("Date")
        ax.set_ylabel("Adjusted Close")
        ax.grid(True)
        ax.legend()
        fig.autofmt_xdate()
        fig.tight_layout()
        fig.savefig(out_path, dpi=150)
        plt.close(fig)
        #display in kitty if using kitty
        term = os.environ.get("TERM", "")
        if "kitty" not in term.lower():
            yield EvtLog("Not using kitty terminal, open plot manually")
        try:
            subprocess.run(["kitty", "+kitten", "icat", str(out_path)],
                            check=False)
        except FileNotFoundError:
            logger.error("Cannot find file, open plot manually")
            pass


