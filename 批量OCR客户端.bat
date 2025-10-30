@echo off
echo ========================================
echo 批量 OCR 处理 (客户端模式)
echo ========================================
echo.
echo 注意: 请确保 OCR 服务已启动
echo       运行 'start_ocr_service.bat' 启动服务
echo.

:: 激活 conda 环境
call conda activate paddle

:: 执行批量OCR
python batch_ocr_client.py

echo.
echo 批量处理完成
pause