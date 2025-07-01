@echo off
call activate_environment.bat
call pyinstaller --name MinimalisticPomodoroTimer --onefile --windowed main.py
xcopy settings.ini dist /Y
xcopy serif_led_board-7.ttf dist /Y