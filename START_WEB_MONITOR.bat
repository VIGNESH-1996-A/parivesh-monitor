@echo off
cd /d v:\PARIVESH
echo Starting PARIVESH web monitor - open http://localhost:5000 on this PC
echo On your phone (same WiFi): use your PC IP, e.g. http://192.168.1.x:5000
echo.
python web_monitor.py
pause
