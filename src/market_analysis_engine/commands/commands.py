from dataclasses import dataclass

class Command:
    """
    Base class for one-shot app commands.
    """

@dataclass(frozen=True)
class CmdDisplayVersion(Command):
    uppercase: bool = False

@dataclass(frozen=True)
class CmdUpdateAll(Command):
    stagger_requests: bool = True
    stagger_start: float = 0.1
    stagger_amount: float = 0.2

@dataclass(frozen=True)
class CmdDisplayGraph(Command):
    top_n: int = 20
    n_factors: int = 20
    #Using period instead
    #min_days: int = 1260
    lookback: int = 60
    horizon: int = 1
    epochs: int = 10
    period: str = "3y"
    ticker: str = "AAPL"
