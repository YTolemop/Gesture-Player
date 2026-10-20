from typing import TypedDict, Optional

class InputState(TypedDict):
    protocolVersion: int
    sessionId: str
    matchId: Optional[str]
    seq: int
    commands: dict[str, str]
    generation: int
