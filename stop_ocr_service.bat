@echo off
chcp 65001 >nul
echo ========================================
echo Stop PaddleOCRVL Persistent Service
echo ========================================
echo.

REM Activate conda environment
echo Activating paddle environment...

REM Get conda installation path
for /f "tokens=*" %%i in ('conda info --base') do set CONDA_PATH=%%i

REM Activate environment
call "%CONDA_PATH%\Scripts\activate.bat" paddle

REM Check if activation was successful
if errorlevel 1 (
    echo.
    echo ERROR: Failed to activate paddle environment
    echo Please make sure conda is installed and paddle environment exists
    echo.
    echo Press any key to exit...
    pause >nul
    exit /b 1
)

echo paddle environment activated
echo.

python ocr_client.py --shutdown

echo.
echo Service stopped
echo Press any key to exit...
pause >nul