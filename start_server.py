import subprocess
import sys

proc = subprocess.Popen(
    ['F:\\andconda\\envs\\pyxx_cuda\\python.exe', 'web_server.py'],
    cwd='f:\\code-tengxun',
    stdout=open('server.log', 'w'),
    stderr=subprocess.STDOUT,
    text=True
)
print(f"Server started, PID={proc.pid}")
print("Check server.log for output...")
