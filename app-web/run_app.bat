@echo off
start py wsgi.py
timeout /t 2
start http://localhost:8000
pause
