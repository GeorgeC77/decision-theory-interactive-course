@echo off
setlocal
cd /d "%~dp0"
set "COURSE_PYTHON=C:\Users\admin\.conda\envs\env_Online_Lecture\python.exe"
if not exist "%COURSE_PYTHON%" (
  echo The env_Online_Lecture Python environment was not found.
  echo Open course-site\dist\index.html directly instead.
  pause
  exit /b 1
)
echo Course portal: http://127.0.0.1:8765/
echo Keep this window open while using the course. Press Ctrl+C to stop.
"%COURSE_PYTHON%" -m http.server 8765 --bind 127.0.0.1 --directory "%~dp0course-site\dist"
if errorlevel 1 pause
