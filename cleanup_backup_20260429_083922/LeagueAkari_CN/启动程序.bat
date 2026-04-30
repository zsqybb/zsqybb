@echo off
chcp 65001 >nul
echo ==================================================
echo LOL数据助手 - 启动程序
echo ==================================================
echo.

REM 检查Python是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未检测到Python，请先安装Python 3.8或更高版本！
    pause
    exit /b 1
)

echo ✅ Python已安装
echo.

REM 检查依赖库
echo 正在检查依赖库...
python -c "import PyQt6" 2>nul
if errorlevel 1 (
    echo ⚠️ 未检测到PyQt6，正在安装...
    pip install PyQt6 requests
)

echo ✅ 依赖库检查完成
echo.

REM 启动程序
echo 正在启动程序...
echo ==================================================
echo.

python main_new.py

if errorlevel 1 (
    echo.
    echo ❌ 程序启动失败！
    pause
    exit /b 1
)

exit /b 0
