from __future__ import annotations

from pathlib import Path
from importlib import metadata
from typing import Any
from datetime import date, timedelta
import random
import logging
from typing import Optional, Tuple

# FIX: change project name for imports
from market_analysis_engine.identity import IDENTITY

#Helper functions

logger = logging.getLogger(__name__)

def stagger_requests(mintime: float = 0.1, maxtime: float = 0.3) -> float:
    """
    Creats a float in the range between the two numbers. 
    """
    if mintime >= maxtime:
        mintime, maxtime = maxtime, mintime
    return random.uniform(mintime, maxtime)


def period_to_date(period: str, *, end_date: date) -> Tuple[Optional[date], date]:
    """
    Converts a period like '12d', '12w', '12m', '12y' 'max' into start_date
    and end_date

    Params:
    - period, string
    - end_date, comes in as a python date(provided by caller)
    """
    p = period.strip().lower()
    if p in {"max", "all"}:
        return None, end_date
    
    m, p = p[-1:], p[:-1]
    try:
        p = int(p)
    except ValueError:
        logger.warning(f"Cannot convert {p} to integer, defaulting to 30")
        p = 30

    if m == "d":
        return end_date - timedelta(days=p), end_date
    if m == "w":
        return end_date - timedelta(weeks=p), end_date
    if m == "m":
        return end_date - timedelta(days=30*p), end_date
    if m == "y":
        return end_date - timedelta(days=365*p), end_date

    logger.warning(f"Unhandled period unit: {p}{m}. Defaulting to 30d")
    return end_date - timedelta(days=30), end_date


def load_dotenv_if_present() -> bool:
    """
    Load a repository-root `.env` file if one exists and `python-dotenv` is
    installed.

    This is intended as a development convenience. In production and container
    environments, real environment variables should be preferred.

    The function walks upward from the current file location until it finds a
    directory containing `pyproject.toml`, treats that directory as the project
    root, and then looks for a `.env` file there. If found, it loads the file
    without overriding existing environment variables.

    Returns:
        int: Returns `1` if a `.env` file was found and loaded, otherwise `0`.
    """
    try:
        from dotenv import load_dotenv #type: ignore[import-not-found]
    except ImportError:
        return False

    here = Path(__file__).resolve()
    for rootpath in (here.parent, *here.parents):
        if (rootpath / "pyproject.toml").exists():
            envfile = rootpath / ".env"
            if envfile.exists():
                load_dotenv(dotenv_path = envfile, override=False)
                return True
            break
    return False

def resolve_version() -> str:
    """
    Resolve the installed package version from project metadata.

    The version is looked up using the package distribution name defined in
    `IDENTITY.dist_name`. If the installed package metadata cannot be found,
    a fallback string is returned instead.

    Returns:
        str: The resolved package version, or `"Cannot resolve version"` if
        package metadata is unavailable.
    """
    try:
        return metadata.version(IDENTITY.dist_name)
    except metadata.PackageNotFoundError:
        return "Cannot resolve version"

def compact_dict(context: dict[str, Any]) -> dict[str, Any]:
    """
    Remove keys whose values that are `None`.

    Args:
        context: A mapping of keys to values.

    Returns:
        dict[str, Any]: A new dictionary containing only keys whose values
        are not `None`.
    """
    return {k: v for k, v in context.items() if v is not None}
