@echo off
chcp 65001 > nul
echo ===================================
echo LeagueAkari - LOL数据助手
echo ===================================
echo.

REM 检查Python
python --version > nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

REM 检查依赖
echo [1/3] 检查依赖包...
python -c "import PyQt6, requests, psutil" 2> nul
if errorlevel 1 (
    echo 正在安装依赖包...
    pip install -r requirements.txt -q
)

REM 启动程序
echo [2/3] 启动程序...
echo.

python main_new.py

if errorlevel 1 (
    echo.
    echo [错误] 程序异常退出
    pause
)

exit /b 0
