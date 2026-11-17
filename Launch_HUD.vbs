Set WshShell = CreateObject("WScript.Shell")
WshShell.Run "pythonw.exe """ & WshShell.CurrentDirectory & "\sidecars\quota_hud\desktop_widget.py""", 0, False
