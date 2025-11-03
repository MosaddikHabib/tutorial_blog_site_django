@echo off
echo ============================================
echo Blog Site - Virtual Environment Setup
echo ============================================
echo.

REM Check if venv_blog exists
if exist "venv_blog\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv_blog\Scripts\activate.bat
    echo.
    echo Virtual environment activated!
    echo.
    echo Installing dependencies...
    pip install -r requirements.txt
    echo.
    echo ============================================
    echo Setup complete!
    echo.
    echo Next steps:
    echo 1. Run: python manage.py migrate
    echo 2. Run: python manage.py runserver
    echo.
    echo Access your site at: http://127.0.0.1:8000/
    echo ============================================
) else (
    echo Virtual environment not found!
    echo Creating virtual environment...
    python -m venv venv_blog
    echo.
    echo Activating virtual environment...
    call venv_blog\Scripts\activate.bat
    echo.
    echo Installing dependencies...
    pip install -r requirements.txt
    echo.
    echo ============================================
    echo Setup complete!
    echo ============================================
)

pause
