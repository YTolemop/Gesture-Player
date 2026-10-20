"""The same three atomic command fields used by the current arena."""
from dataclasses import dataclass, asdict
from core.labels import LABELS

CHANNELS = ('left', 'right', 'both')
DEFAULT_CHANNELS = {
    'MOVE_LEFT': 'left', 'JUMP': 'left', 'CROUCH': 'left',
    'MOVE_RIGHT': 'right', 'NORMAL_ATTACK': 'right', 'ATTACK_SKILL': 'right',
    'CONTROL_SKILL': 'right', 'BLOCK': 'both', 'DEFENSE_SKILL': 'both', 'ULTIMATE': 'both',
}

@dataclass(frozen=True)
class Commands:
    left: str = 'NONE'
    right: str = 'NONE'
    both: str = 'NONE'

    def __post_init__(self):
        if any(value not in LABELS for value in (self.left, self.right, self.both)):
            raise ValueError('未知遊戲指令')
        if self.both != 'NONE' and (self.left != 'NONE' or self.right != 'NONE'):
            raise ValueError('雙手合成指令必須獨占輸出')

    def payload(self):
        return asdict(self)
