from __future__ import annotations
import logging
from typing import Iterator
import time
from pandas import DataFrame
from dataclasses import replace

from market_analysis_engine.commands.commands import CmdUpdateAll
from market_analysis_engine.events.events import Event, EvtProgress, EvtResult, EvtLog, EvtError
from market_analysis_engine.handlers.commandhandler import CommandHandler
from market_analysis_engine.marketdata.marketservice import MarketService
from market_analysis_engine.db.repo import MarketRepo
from market_analysis_engine.runtime.runtime import CFGMisc, CFGTickerService, MetaInfo
from market_analysis_engine.tickers.tickerservice import Ticker, TickerService
from market_analysis_engine.utils.utils import stagger_requests

logger = logging.getLogger(__name__)

class UpdateAllHandler(CommandHandler):
    def __init__(self, cmd: CmdUpdateAll, repo: MarketRepo, ts: TickerService, mkt: MarketService, cfg_ts: CFGTickerService):
        self.cmd = cmd
        self.repo = repo
        self.ts = ts
        self.mkt = mkt
        self.cfg_ts = cfg_ts


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
        logger.info("Handling CmdDisplayVersion ..")
        yield from self._update_all()

    def _update_all(self):
        """
        Handles update all situation
        """
        tickers = self.ts.update()
        logger.info("Tickermap returned ..")
        total = len(tickers)

        if total == 0:
            yield EvtLog("No tickers found")
            return

        yield EvtLog("Starting update of all tickers")
        error_tickers = []
        for i, ticker, in enumerate(tickers, start=1):
            if self.cmd.stagger_requests:
                time.sleep(stagger_requests())
            yield EvtProgress(i, total, f"{ticker.tickersymbol}")

            try:
                self._update_ticker(ticker)
            except Exception as e:
                logger.exception(f"Error updating {ticker.tickersymbol}: {e}")
                error_tickers.append(ticker.tickersymbol)
                continue

        if len(error_tickers) > 0:
            yield EvtLog(f"Following tickers failed to update: {error_tickers}")
        else:
            yield EvtLog("All tickers updated")


    def _update_ticker(self, ticker: Ticker) -> None:
        """
        Performs an update of the data for the given ticker

        Params:
        - Ticker object containing ticker symbol, update_date, 
        check_for_corporate_actions flag
        """
        df = self.mkt.get_ohlcv(ticker.tickersymbol, ticker.update_date)

        if ticker.check_corporate_actions and self._detect_corporate_action(df):
            logger.info("Detected corporate actions, re-running with default date")
            fullupdate = replace(
                    ticker,
                    update_date = self.cfg_ts.default_date,
                    check_corporate_actions = False,
            )
            return self._update_ticker(fullupdate)

        instrument_id = self.repo.ensure_instrument(ticker.tickersymbol)
        affected = self.repo.upsert_ohlcv_daily(instrument_id=instrument_id, df = df)
        count = affected if affected > 0 else len(df.index)
        logger.debug(f"Updated: {ticker.tickersymbol} , from date {ticker.update_date}, with {count} rows added")

    def _detect_corporate_action(self, df: DataFrame) -> bool:
        """
        Checks if Stocksplits or Dividends column of the given dataframe are
        different from 0.0, meaning there was a stocksplit or dividend action
        that day.

        Params:
        - df: the DataFrame to check

        Returns:
        - bool: returns True if there was a corporate action in the DataFrame
        """
        return ((df["dividends"] != 0.0).any() or (df["stocksplits"] != 0.0).any())


