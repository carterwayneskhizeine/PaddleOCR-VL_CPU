@echo off
chcp 65001 >nul
echo ====================================
echo 批量 OCR 处理
echo ====================================
echo.

REM 激活 conda 环境
echo 正在激活 paddle 环境...

REM 获取 conda 安装路径
for /f "tokens=*" %%i in ('conda info --base') do set CONDA_PATH=%%i

REM 激活环境
call "%CONDA_PATH%\Scripts\activate.bat" paddle

REM 检查激活是否成功
if errorlevel 1 (
    echo.
    echo 错误: 无法激活 paddle 环境
    echo 请确保已安装 conda 并且存在 paddle 环境
    echo.
    echo 按任意键退出...
    pause >nul
    exit /b 1
)

echo paddle 环境已激活
echo.

python batch_ocr.py

echo.
echo 按任意键退出...
pause >nul

