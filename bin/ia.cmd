@echo off
rem Lenh ia (Agent 02 Anh) cho CMD/PowerShell tren Windows.
set "RT=%IMAGE_AGENT_HOME%"
if "%RT%"=="" set "RT=%USERPROFILE%\.image-agent"
if "%~1"=="setup" (
  powershell -ExecutionPolicy Bypass -File "%~dp0..\engine\setup.ps1"
  exit /b %errorlevel%
)
if not exist "%RT%\env\python.exe" (
  echo Chua cai dat. Chay: ia setup
  exit /b 1
)
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
"%RT%\env\python.exe" "%~dp0..\engine\ia.py" %*
