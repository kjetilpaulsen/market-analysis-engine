from __future__ import annotations

import argparse
import logging

# FIX: change project name for imports
from market_analysis_engine.commands.frontendcommandinput import FrontendCommandInput
from market_analysis_engine.runtime.runtimeoverrides import RuntimeOverrides
from market_analysis_engine.identity import IDENTITY


logger = logging.getLogger(__name__)

def cli_parser(argv: list[str] | None = None) -> tuple[tuple[FrontendCommandInput, ...], RuntimeOverrides]:
    """
    Parse CLI arguments and convert them into structured runtime inputs.

    This function resolves command-line arguments using `argparse` and
    converts them into two structured components used by the application:

        1. `RuntimeOverrides` – optional runtime configuration overrides
           supplied by the CLI.
        2. `FrontendCommandInput` objects – normalized representations of
           commands requested by the user.

    The parser defines both global runtime flags (for configuration such
    as logging or database settings) and command-specific options using
    subparsers.

    To add a new CLI command:

        1. Define a new subparser using `parser.add_subparsers()`.
        2. Add command-specific arguments to that subparser.
        3. Convert the parsed arguments into a `FrontendCommandInput`
           instance in the command resolution section.

    Args:
        argv: Optional list of CLI arguments. If `None`, `argparse`
            reads arguments from `sys.argv`. Passing an explicit list
            is primarily useful for testing or programmatic invocation.

    Returns:
        CliParsedInput: A structured container containing:

            - `overrides`: Runtime configuration overrides provided via CLI.
            - `commands`: A tuple of normalized frontend command inputs
              representing the requested CLI commands.
    """

    logger.info("Parsing argv ..")

    parser = argparse.ArgumentParser(prog = IDENTITY.app_name)

    parser.add_argument("--dev-mode", action=argparse.BooleanOptionalAction, default=None, help="Enable developer conviniences")
    parser.add_argument("--dry-run", action=argparse.BooleanOptionalAction, default=None, help="Do not write to DB")
    parser.add_argument("--build-config", action=argparse.BooleanOptionalAction, default=None, help="Build a .conf file at XDG config path")

    parser.add_argument("--log-level", type=str, default=None, help="Set the general logging level for the app")
    parser.add_argument("--console-level", type=str, default=None, help="Set the logging level consolelogging")
    parser.add_argument("--stderr-level", type=str, default=None, help="Set the logging level stderrlogging")
    parser.add_argument("--file-log", action=argparse.BooleanOptionalAction, default=None, help="Enable logging to files")
    parser.add_argument("--console-log", action=argparse.BooleanOptionalAction, default=None, help="Enable logging to console")
    parser.add_argument("--stderr-log", action=argparse.BooleanOptionalAction, default=None, help="Enable logging to stder")

    parser.add_argument("--db-host", default=None)
    parser.add_argument("--db-name", default=None)
    parser.add_argument("--db-user", default=None)
    parser.add_argument("--db-password", default=None)
    parser.add_argument("--db-port", type=int, default=None)

    parser.add_argument("--default_date", type=str, default=None, help="Default start date to get data")
    parser.add_argument("--default_timedelta", type=int, default=1, help="Default start date to get data")


    # Subparsers
    subparses = parser.add_subparsers(dest="command")

    # Version
    version_parser = subparses.add_parser("version", help="Display the current version")
    version_parser.add_argument("--uppercase", action="store_true", default=False, help="Displays the version in uppercase letters")

    # Updateall
    updateall_parser = subparses.add_parser("updateall", help="Updates all tickers, dev mode reduces to small selection")
    updateall_parser.add_argument("--stagger-requests", action="store_true", default=False, help="Waits a random amount of time between requests")
    updateall_parser.add_argument("--stagger-start", type=float, default=0.1, help="Minimum wait time if staggerting")
    updateall_parser.add_argument("--stagger-amount", type=float, default=0.2, help="The max amount of stagger")

    # Updateall
    displaygraph_parser = subparses.add_parser("display-graph", help="Displays a graph of the given ticker for the given period")
    displaygraph_parser.add_argument("--stagger-requests", action="store_true", default=False, help="Waits a random amount of time between requests")
    displaygraph_parser.add_argument("--ticker", type=str, default="AAPL", help="The ticker to check, defaults to AAPL")
    displaygraph_parser.add_argument("--period", type=str, default="3y", help="The period to check, y, m, w, d")

    # Parse them

    args = parser.parse_args(argv)

    overrides = RuntimeOverrides(
        dev_mode=args.dev_mode,
        dry_run=args.dry_run,
        build_config=args.build_config,
        log_level=args.log_level,
        console_level=args.console_level,
        stderr_level=args.stderr_level,
        file_log=args.file_log,
        console_log=args.console_log,
        stderr_log=args.stderr_log,
        db_host=args.db_host,
        db_name=args.db_name,
        db_user=args.db_user,
        db_password=args.db_password,
        db_port=args.db_port,
        default_date=args.default_date,
        default_timedelta=args.default_timedelta,
    )

    commands: list[FrontendCommandInput] = []
    if args.command == "version":
        commands.append(
            FrontendCommandInput(
                name="version",
                options={
                    "uppercase": args.uppercase,
                },
            )
        )
    if args.command == "updateall":
        commands.append(
            FrontendCommandInput(
                name="updateall",
                options={
                    "stagger_requests": args.stagger_requests,
                    "stagger_start": args.stagger_start,
                    "stagger_amount": args.stagger_amount,
                },
            )
        )
    if args.command == "display-graph":
        commands.append(
            FrontendCommandInput(
                name="display_graph",
                options={
                    "ticker": args.ticker,
                    "period": args.period,
                },
            )
        )
    return (tuple(commands), overrides)
