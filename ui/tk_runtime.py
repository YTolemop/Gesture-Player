"""Use an installed Xft-capable Tk when a Linux Python bundles core-font Tk."""

import ctypes.util
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
_LIBRARY_DIRS = ('/usr/lib', '/usr/lib64', '/lib', '/lib64')
_PROBE = """
import json
from pathlib import Path
import tkinter as tk
from tkinter import font
from ui.fonts import FONT_FAMILIES
root = tk.Tk()
root.withdraw()
families = {f.casefold() for f in font.families(root)}
libraries = [line.split()[-1] for line in Path('/proc/self/maps').read_text().splitlines() if '/' in line]
tcl = next((p for p in libraries if Path(p).name.startswith('libtcl') and 'tk' not in Path(p).name), '')
print(json.dumps({'version': str(tk.TkVersion), 'tcl': tcl,
                  'cjk': any(f.casefold() in families for f in FONT_FAMILIES)}))
root.destroy()
"""


def _probe(environment):
    try:
        result = subprocess.run([sys.executable, '-c', _PROBE], cwd=ROOT,
                                env=environment, capture_output=True, text=True, timeout=10)
        return json.loads(result.stdout) if result.returncode == 0 else None
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return None


def _system_library(names):
    for name in names:
        library = ctypes.util.find_library(name)
        if not library:
            continue
        if Path(library).is_absolute() and Path(library).is_file():
            return str(Path(library).resolve())
        for base in _LIBRARY_DIRS:
            directory = Path(base)
            for path in (directory / library, *directory.glob(f'*/{library}')):
                if path.is_file():
                    return str(path.resolve())
    return None


def ensure_linux_tk():
    if not sys.platform.startswith('linux') or os.environ.get('GESTURE_PLAYER_SYSTEM_TK'):
        return
    environment = os.environ.copy()
    current = _probe(environment)
    # Leave a working Tk, a missing display, or a missing tkinter module alone.
    if not current or current['cjk']:
        return
    version = current['version']
    names = (f'tcl9tk{version}', f'tk{version}') if version.startswith('9.') else (f'tk{version}',)
    # An unqualified soname can resolve to uv's bundled Tk again via RPATH.
    library = _system_library(names)
    scripts = next((path for base in ('/usr/lib', '/usr/share/tcltk', '/usr/share')
                    if (path := Path(base) / f'tk{version}').joinpath('tk.tcl').is_file()), None)
    if library and scripts and current['tcl']:
        # Keep Python's Tcl: replacing it with distro Tcl can break TclBN symbols.
        environment['LD_PRELOAD'] = ':'.join(filter(None, (
            current['tcl'], library, environment.get('LD_PRELOAD'))))
        environment['TK_LIBRARY'] = str(scripts)
        candidate = _probe(environment)
        # Verify in a separate process before changing the GUI's native libraries.
        if candidate and candidate['version'] == version and candidate['cjk']:
            environment['GESTURE_PLAYER_SYSTEM_TK'] = '1'
            os.execve(sys.executable, [sys.executable, *sys.argv], environment)
    print(f'Linux 字型提示：目前 Tk 無法使用中文字型。Ubuntu／Debian 請安裝 '
          f'fonts-noto-cjk、fontconfig 和 tk{version}，再重開 GUI。'
          '其他發行版請安裝對應的中文字型與 Tk；也可改用系統 Python。', file=sys.stderr)
