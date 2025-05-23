@echo off
call activate_environment.bat
call pyinstaller --name MinimalisticPomodoroTimer --onefile --windowed main.py
xcopy settings.ini dist /E /Y
xcopy serif_led_board-7.ttf dist /E /Y