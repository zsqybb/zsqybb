@echo off
chcp 65001 >nul 2>nul
title LeagueAkari 打包工具
color 0E

echo.
echo ========================================
echo    LeagueAkari 国服复刻助手 - 打包工具
echo ========================================
echo.

REM 切换到脚本所在目录
cd /d "%~dp0"

REM 查找Python
set PYTHON_CMD=
where python >nul 2>nul
if %errorlevel% equ 0 (
    set PYTHON_CMD=python
) else (
    for %%P in (
        "C:\Users\Lenovo\AppData\Local\Programs\Python\Python312\python.exe"
        "C:\Users\Lenovo\AppData\Local\Programs\Python\Python311\python.exe"
        "C:\Users\Lenovo\AppData\Local\Programs\Python\Python310\python.exe"
    ) do (
        if exist %%P (
            set PYTHON_CMD=%%P
            goto :found_py
        )
    )
    echo [错误] 未找到Python！
    pause
    exit /b 1
)
:found_py

echo [信息] 使用Python: %PYTHON_CMD%

REM 安装PyInstaller
echo.
echo [步骤1] 安装PyInstaller...
%PYTHON_CMD% -m pip install pyinstaller --quiet 2>nul
if %errorlevel% neq 0 (
    echo [警告] PyInstaller安装可能失败，尝试继续...
)

REM 清理旧构建
echo.
echo [步骤2] 清理旧构建...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist
if exist "*.spec" del /q *.spec

REM 执行打包
echo.
echo [步骤3] 开始打包（这可能需要几分钟）...
echo.

%PYTHON_CMD% -m PyInstaller ^
    --onefile ^
    --windowed ^
    --name="LeagueAkari国服助手" ^
    --add-data="static_data;static_data" ^
    --add-data="config.ini;." ^
    --hidden-import=PyQt6.sip ^
    --hidden-import=PyQt6.QtCore ^
    --hidden-import=PyQt6.QtWidgets ^
    --hidden-import=PyQt6.QtGui ^
    --noupx ^
    --clean ^
    main.py

if %errorlevel% neq 0 (
    echo.
    echo [错误] 打包失败！
    echo 请检查以上错误信息
    pause
    exit /b 1
)

echo.
echo ========================================
echo    打包成功！
echo ========================================
echo.
echo 输出文件: dist\LeagueAkari国服助手.exe
echo.

REM 复制必要文件到dist目录
echo [步骤4] 复制资源文件...
if not exist "dist\static_data" mkdir "dist\static_data"
xcopy /y /q "static_data\*.json" "dist\static_data\" >nul
copy /y "config.ini" "dist\" >nul
copy /y "启动器.bat" "dist\" >nul

echo.
echo 所有文件已复制到 dist\ 目录
echo.
echo 使用方式：
echo   1. 双击 dist\LeagueAkari国服助手.exe 运行
echo   2. 或双击 dist\启动器.bat 运行
echo.
echo 注意：首次运行较慢，请耐心等待
echo.

REM 清理构建临时文件
echo [步骤5] 清理临时文件...
if exist "build" rmdir /s /q build
if exist "*.spec" del /q *.spec

echo.
pause