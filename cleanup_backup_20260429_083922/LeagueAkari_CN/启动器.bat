@echo off
chcp 65001 >nul 2>nul
title LeagueAkari 国服复刻助手
color 0A

echo.
echo ========================================
echo    LeagueAkari 国服复刻助手启动器
echo    版本: 1.0.0
echo ========================================
echo.

REM 切换到脚本所在目录
cd /d "%~dp0"

REM 查找Python路径
set PYTHON_CMD=

REM 1. 尝试系统PATH中的python
where python >nul 2>nul
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
    goto :found_python
)

REM 2. 尝试常见安装路径
for %%P in (
    "C:\Users\Lenovo\AppData\Local\Programs\Python\Python312\python.exe"
    "C:\Users\Lenovo\AppData\Local\Programs\Python\Python311\python.exe"
    "C:\Users\Lenovo\AppData\Local\Programs\Python\Python310\python.exe"
    "C:\Python312\python.exe"
    "C:\Python311\python.exe"
    "C:\Python310\python.exe"
    "D:\Python312\python.exe"
) do (
    if exist %%P (
        set PYTHON_CMD=%%P
        goto :found_python
    )
)

REM 3. 尝试py启动器
where py >nul 2>nul
if %errorlevel% equ 0 (
    set PYTHON_CMD=py -3
    goto :found_python
)

echo [错误] 未检测到Python环境！
echo.
echo 请安装Python 3.10或更高版本：
echo   下载地址: https://www.python.org/downloads/
echo   安装时请勾选 "Add Python to PATH"
echo.
echo 或使用winget安装：
echo   winget install Python.Python.3.12
echo.
pause
exit /b 1

:found_python
echo [信息] 使用Python: %PYTHON_CMD%
echo.

REM 显示Python版本
%PYTHON_CMD% --version 2>nul
echo.

REM 安装依赖包
echo 正在检查/安装依赖包...
%PYTHON_CMD% -m pip install --quiet --upgrade pip 2>nul
%PYTHON_CMD% -m pip install --quiet PyQt6 requests psutil beautifulsoup4 2>nul

if %errorlevel% neq 0 (
    echo [警告] 部分依赖安装可能失败，尝试继续运行...
    echo.
)

echo.
echo ========================================
echo   所有依赖检查完成！
echo ========================================
echo.
echo 正在启动 LeagueAkari 国服复刻助手...
echo.
echo 使用提示：
echo   1. 请确保英雄联盟客户端已启动
echo   2. 程序会自动检测游戏状态
echo   3. 关闭窗口会最小化到系统托盘
echo   4. 右键托盘图标可退出程序
echo   5. 按 Ctrl+C 可强制停止
echo.

REM 启动主程序
%PYTHON_CMD% main.py

if %errorlevel% neq 0 (
    echo.
    echo [错误] 程序异常退出 (代码: %errorlevel%)
    echo.
    pause
    exit /b 1
)

echo.
echo 程序已正常退出
pause