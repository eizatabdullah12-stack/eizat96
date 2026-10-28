import os
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))


@unittest.skipUnless(sys.platform=='win32' or os.environ.get('DISPLAY'),'Needs a graphical display; also exercised inside the Windows EXE')
class PersonalUITests(unittest.TestCase):
    def test_localized_editor_reopen_approval_and_stale_online_results(self):
        import tkinter as tk
        from app import App
        from personal_selftest import exercise
        root=tk.Tk(); root.withdraw()
        app=App(root)
        try: exercise(app)
        finally:
            app.text_worker.close(); root.destroy()
