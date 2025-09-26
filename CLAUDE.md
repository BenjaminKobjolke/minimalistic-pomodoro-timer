# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a minimalistic Pomodoro timer application built with Python and Tkinter. It features a transparent, borderless window with LED-style display in green that can be moved around the screen. The application uses PIL (Pillow) for custom font rendering and maintains user preferences in a settings.ini file.

## Key Commands

### Development
- **Run timer**: `run.bat` or `run.vbs` (runs without console window)
- **Install dependencies**: `install.bat` (creates venv and installs from requirements.txt)
- **Activate virtual environment**: `activate_environment.bat` or `venv\Scripts\activate`
- **Build executable**: `compile_exe.bat` (uses PyInstaller to create standalone .exe)

### Python Environment
- Virtual environment located in `venv/` directory
- Main dependencies: Pillow for image processing, PyInstaller for building executables
- Entry point: `main.py`

## Architecture

The application follows a simple modular structure:

- **main.py**: Entry point that initializes the logger and timer
- **timer.py**: Core PomodoroTimer class containing all timer logic, UI rendering, and window management
  - Uses system clock for accurate timing (target_end_time approach)
  - Renders time display using PIL/Pillow with custom font support
  - Handles keyboard shortcuts and window movement
  - Persists window position and custom duration in settings.ini
- **logger.py**: Simple logging utility that writes to pomodoro.log

### Key Implementation Details

- **Transparent Window**: Uses `overrideredirect(True)` with alpha transparency for borderless, semi-transparent appearance
- **Timer Accuracy**: Uses `target_end_time` with system clock rather than decrementing counter to maintain accuracy
- **Font Rendering**: PIL/Pillow creates timer display as image with custom TrueType font support
- **Settings Persistence**: ConfigParser saves/loads window position and custom timer duration
- **Window in Alt+Tab**: Uses Windows-specific ctypes to ensure window appears in Alt+Tab despite being borderless

### Keyboard Controls
- `s` - Start/Pause timer
- `r` - Reset timer to default duration
- `e` - Set custom timer duration
- Arrow keys - Move window (fast)
- Shift + Arrow keys - Move window (slow/fine control)

## Settings Configuration

The `settings.ini` file stores:
- `[Window]` section: x, y position
- `[Display]` section: font_size, font_path (optional)
- `[Timer]` section: custom_duration_minutes (persisted custom duration)