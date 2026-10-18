@echo off
chcp 65001 >nul
cd /d "%~dp0"
python -c "import pygame" 2>nul
if errorlevel 1 (
  echo Pygame이 설치되어 있지 않습니다.
  echo 다음 명령으로 설치하세요: python -m pip install -r requirements-pygame.txt
  pause
  exit /b 1
)
python chunsang_raising.py
if errorlevel 1 (
  echo.
  echo 실행에 실패했습니다. Python 3와 Pygame 설치를 확인하세요.
  pause
)
