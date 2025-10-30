@echo off
echo ========================================
echo 启动 PaddleOCRVL 持久化服务
echo ========================================
echo.
echo 注意: 模型初始化需要 10-15 分钟
echo       服务启动后会一直运行，直到手动关闭
echo.
echo 按 Ctrl+C 可以停止服务
echo.

:: 激活 conda 环境
call conda activate paddle

:: 启动OCR服务
python ocr_server.py

echo.
echo OCR服务已停止
pause