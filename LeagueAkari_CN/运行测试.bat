@echo off
chcp 65001 > nul
echo 正在测试LeagueAkari程序...
echo.

python test_run.py > test_output.txt 2>&1

echo 测试完成！
echo 正在显示结果...
echo.
type test_output.txt
echo.
pause
