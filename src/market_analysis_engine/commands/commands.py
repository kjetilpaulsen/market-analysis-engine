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
