@echo off
echo ========================================
echo 停止 PaddleOCRVL 持久化服务
echo ========================================
echo.

:: 激活 conda 环境
call conda activate paddle

:: 发送关闭请求
python ocr_client.py --shutdown

echo.
echo 服务已关闭
pause