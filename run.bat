@echo off
chcp 65001 > nul
cd /d "C:\agy"
echo 공부 시간 기록 프로그램을 실행합니다...
"C:\Users\82109\AppData\Local\Programs\Python\Python312\python.exe" main.py
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [실행 오류] 아래 오류 내용을 확인해주세요:
    python main.py
    pause
)
