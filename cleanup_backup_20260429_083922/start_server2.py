import subprocess, sys, os

# 先编译检查
result = subprocess.run(
    [sys.executable, '-m', 'py_compile', r'f:\code-tengxun\LeagueAkari_CN\data_spider.py'],
    capture_output=True, text=True
)
if result.returncode != 0:
    print("Syntax error:")
    print(result.stderr)
    sys.exit(1)
print("Syntax OK!")

# 启动服务器
proc = subprocess.Popen(
    [sys.executable, 'web_server.py'],
    cwd=r'f:\code-tengxun',
    stdout=open('server.log', 'w', encoding='utf-8'),
    stderr=subprocess.STDOUT
)
print(f"Server started, PID={proc.pid}")
print("Check server.log for output...")
