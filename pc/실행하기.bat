@echo off
chcp 65001 >nul
cd /d "%~dp0"
python taehyun_rescue.py
if errorlevel 1 (
  echo.
  echo 실행에 실패했습니다. Python 3와 tkinter가 설치되어 있는지 확인하세요.
  pause
)
