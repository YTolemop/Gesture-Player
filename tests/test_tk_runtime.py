import pytest

from ui import tk_runtime


@pytest.mark.parametrize('platform', ['win32', 'darwin'])
def test_native_platforms_do_not_probe_or_replace_tk(monkeypatch, platform):
    monkeypatch.setattr(tk_runtime.sys, 'platform', platform)
    monkeypatch.setattr(tk_runtime, '_probe', lambda _: pytest.fail('Linux-only probe'))
    tk_runtime.ensure_linux_tk()


def linux(monkeypatch):
    monkeypatch.setattr(tk_runtime.sys, 'platform', 'linux')
    monkeypatch.delenv('GESTURE_PLAYER_SYSTEM_TK', raising=False)


def test_working_fonts_leave_runtime_unchanged(monkeypatch):
    linux(monkeypatch)
    monkeypatch.setattr(tk_runtime, '_probe', lambda _: {'cjk': True})
    monkeypatch.setattr(tk_runtime.os, 'execve', lambda *_: pytest.fail('Already working'))
    tk_runtime.ensure_linux_tk()


@pytest.mark.parametrize('candidate', [None, {'version': '8.6', 'cjk': True},
                                       {'version': '9.0', 'cjk': False}])
def test_incompatible_or_broken_system_tk_is_never_used(monkeypatch, candidate):
    linux(monkeypatch)
    responses = iter([{'version': '9.0', 'cjk': False, 'tcl': '/python/libtcl9.0.so'}, candidate])
    monkeypatch.setattr(tk_runtime, '_probe', lambda _: next(responses))
    monkeypatch.setattr(tk_runtime, '_system_library', lambda _: '/usr/lib/libtcl9tk9.0.so')
    monkeypatch.setattr(tk_runtime.Path, 'is_file', lambda _: True)
    monkeypatch.setattr(tk_runtime.os, 'execve', lambda *_: pytest.fail('Unsafe replacement'))
    tk_runtime.ensure_linux_tk()


def test_verified_replacement_keeps_pythons_tcl_and_original_arguments(monkeypatch):
    linux(monkeypatch)
    monkeypatch.delenv('LD_PRELOAD', raising=False)
    monkeypatch.delenv('TCL_LIBRARY', raising=False)
    responses = iter([{'version': '9.0', 'cjk': False, 'tcl': '/python/libtcl9.0.so'},
                      {'version': '9.0', 'cjk': True}])
    monkeypatch.setattr(tk_runtime, '_probe', lambda _: next(responses))
    monkeypatch.setattr(tk_runtime, '_system_library', lambda _: '/usr/lib/libtcl9tk9.0.so')
    monkeypatch.setattr(tk_runtime.Path, 'is_file', lambda _: True)
    monkeypatch.setattr(tk_runtime.sys, 'argv', ['main.py', 'record'])
    called = []
    monkeypatch.setattr(tk_runtime.os, 'execve', lambda *args: called.append(args))
    tk_runtime.ensure_linux_tk()
    executable, arguments, environment = called[0]
    assert arguments == [executable, 'main.py', 'record']
    assert environment['LD_PRELOAD'] == '/python/libtcl9.0.so:/usr/lib/libtcl9tk9.0.so'
    assert environment['GESTURE_PLAYER_SYSTEM_TK'] == '1'
    assert 'TCL_LIBRARY' not in environment


def test_system_library_is_resolved_to_an_absolute_multiarch_path(monkeypatch, tmp_path):
    library = tmp_path / 'x86_64-linux-gnu' / 'libtcl9tk9.0.so'
    library.parent.mkdir()
    library.touch()
    monkeypatch.setattr(tk_runtime, '_LIBRARY_DIRS', (str(tmp_path),))
    monkeypatch.setattr(tk_runtime.ctypes.util, 'find_library', lambda _: library.name)
    assert tk_runtime._system_library(('tcl9tk9.0',)) == str(library.resolve())
