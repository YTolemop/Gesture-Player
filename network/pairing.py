"""Validate UI entries while preserving six-digit codes as strings."""
import re
from urllib.parse import urlsplit

SERVER = 'https://ga-game.codpy.org'
REASONS = {'READY': '可接收指令', 'NOT_PLAYING': '等待網站準備、選技或恢復',
    'NEUTRAL_REQUIRED': '請先放下雙手回到中立', 'RELEASE_REQUIRED': '請離開手勢至少 0.1 秒後再做一次',
    'ACTION_LOCKED': '空中、受擊或收招中', 'OPPOSITE_DIRECTIONS': '左右移動同時輸入，互相抵銷',
    'OK': '已執行', 'COOLDOWN': '技能冷卻中', 'INSUFFICIENT_QI': '氣量不足',
    'ULTIMATE_LOCKED': '大招尚未解鎖', 'IMBALANCE': '失衡中', 'ROOTED': '定身中',
    'PROJECTILE_ACTIVE': '上一發仍在場上', 'INVALID_ACTION': '未設定該技能'}

def server_url(value):
    value = value.strip().rstrip('/')
    parts = urlsplit(value)
    if parts.scheme not in ('http', 'https') or not parts.hostname or parts.path or parts.query or parts.fragment or parts.username or parts.password:
        raise ValueError('主機網址請填網站首頁，例如 https://ga-game.codpy.org，不要加 /controller')
    return value

def pairing_values(server, room, code):
    server, room, code = server_url(server), room.strip(), code.strip()
    if room and not re.fullmatch(r'[0-9]{6}', room):
        raise ValueError('PVP 房號為六位數字，例如 123456；PVE 與練習請留空')
    if not re.fullmatch(r'[0-9]{6}', code):
        raise ValueError('請填入自己網頁剛產生的六位數配對碼，保留開頭的 0')
    return server, room, code
