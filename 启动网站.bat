@echo off
chcp 65001 >nul
title LOL数据助手 - 国服版

echo ============================================
echo    LOL 数据助手 - 国服版 v2.0
echo ============================================
echo.

:: 设置Python路径
set PYTHON=C:\Users\Lenovo\AppData\Local\Programs\Python\Python312\python.exe

if not exist "%PYTHON%" (
    echo [错误] 未找到Python，请安装Python 3.12+
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/3] 检查依赖...
"%PYTHON%" -m pip install flask flask-cors requests -q 2>nul

echo [2/3] 检查资源文件...
if not exist "static\img\champion" (
    echo [警告] 英雄图标未找到，请先解压dragontail数据
)

echo [3/3] 启动服务器...
echo.
echo 访问地址: http://127.0.0.1:5000
echo 按 Ctrl+C 停止服务器
echo.

"%PYTHON%" web_server.py
pause
