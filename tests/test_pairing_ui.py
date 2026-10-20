import tkinter as tk
import subprocess
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from ui.app import App

def exercise(monkeypatch,tmp_path):
    root=tk.Tk();root.withdraw()
    monkeypatch.setattr('ui.app.tk.Tk',lambda:root)
    monkeypatch.setattr('ui.app.ROOT',tmp_path)
    app=App({})
    try:
        assert app.server_var.get()=='https://ga-game.codpy.org'
        assert str(app.room_entry.cget('state'))=='disabled' and app.room_var.get()==''
        app.play_var.set('PVP 雙人對決')
        assert str(app.room_entry.cget('state'))=='normal'
        app.room_entry.insert(0,'ABCDEF')
        assert app.room_var.get()==''
        app.room_entry.insert(0,'123456')
        assert app.room_var.get()=='123456'
        app.play_var.set('PVE 一命連戰')
        assert app.room_var.get()==''
        root.geometry('720x480+10000+10000');root.deiconify()
        for index,canvas in [(2,app.connection_canvas),(3,app.guide_canvas)]:
            app.tabs.select(index);root.update()
            if canvas.bbox('all')[3]>canvas.winfo_height():
                canvas.yview_moveto(1);root.update()
                assert canvas.yview()[0]>0
    finally:app.close()

def test_pve_room_is_empty_pvp_accepts_only_numeric_and_small_windows_scroll(tmp_path):
    # Each Tk interpreter gets its own process, avoiding shared Windows handles
    # between independent GUI tests while still exercising real widgets.
    result=subprocess.run([sys.executable,__file__,str(tmp_path)],capture_output=True,text=True,timeout=20)
    assert result.returncode==0,result.stdout+result.stderr

if __name__=='__main__':
    import pytest
    with pytest.MonkeyPatch.context() as patch:
        exercise(patch,Path(sys.argv[1]))
