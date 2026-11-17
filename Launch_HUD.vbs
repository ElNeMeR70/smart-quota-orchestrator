Set WshShell = CreateObject("WScript.Shell")
strDir = WshShell.CurrentDirectory

' Launch server.py if not running
WshShell.Run "cmd /c netstat -ano | findstr :7899 || pythonw.exe """ & strDir & "\sidecars\quota_hud\server.py""", 0, True

' Launch desktop floating widget
WshShell.Run "pythonw.exe """ & strDir & "\sidecars\quota_hud\desktop_widget.py""", 0, False
