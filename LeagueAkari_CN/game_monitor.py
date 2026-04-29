#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
游戏进程检测模块 - 自动判断LOL客户端启停状态
核心功能：检测LeagueClient.exe和League of Legends.exe进程
"""
import psutil
import time
import threading

class GameMonitor:
    """游戏进程监控类"""
    
    def __init__(self):
        self.client_running = False
        self.game_running = False
        self.last_check = 0
        self.callbacks = []
        
    def check_game_status(self, callback=None):
        """检查游戏进程状态"""
        # 防止频繁检查
        current_time = time.time()
        if current_time - self.last_check < 2:  # 至少2秒间隔
            return
        
        self.last_check = current_time
        
        # 检查LeagueClient.exe（客户端）
        client_found = False
        game_found = False
        
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                try:
                    name = proc.info['name'].lower()
                    if 'leagueclient.exe' in name:
                        client_found = True
                    elif 'league of legends.exe' in name:
                        game_found = True
                    
                    # 如果两个都找到了就提前退出
                    if client_found and game_found:
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            print(f"进程检查异常: {str(e)}")
        
        # 更新状态
        status_changed = False
        if client_found != self.client_running:
            self.client_running = client_found
            status_changed = True
        
        if game_found != self.game_running:
            self.game_running = game_found
            status_changed = True
        
        # 生成状态描述
        status_text = self._get_status_text()
        
        # 调用回调函数
        if callback:
            callback(self.client_running, self.game_running, status_text)
        
        # 调用注册的回调
        if status_changed:
            for cb in self.callbacks:
                cb(self.client_running, self.game_running, status_text)
        
        return self.client_running, self.game_running, status_text
    
    def _get_status_text(self):
        """获取状态描述文本"""
        if self.client_running and self.game_running:
            return "游戏运行中"
        elif self.client_running and not self.game_running:
            return "客户端运行中（大厅）"
        elif not self.client_running and self.game_running:
            return "游戏进程运行中（异常状态）"
        else:
            return "游戏未运行"
    
    def register_callback(self, callback):
        """注册状态变更回调函数"""
        if callback not in self.callbacks:
            self.callbacks.append(callback)
    
    def unregister_callback(self, callback):
        """取消注册回调函数"""
        if callback in self.callbacks:
            self.callbacks.remove(callback)
    
    def is_client_running(self):
        """客户端是否运行"""
        return self.client_running
    
    def is_game_running(self):
        """游戏是否运行"""
        return self.game_running
    
    def get_detailed_process_info(self):
        """获取详细的进程信息"""
        processes = []
        try:
            for proc in psutil.process_iter(['pid', 'name', 'exe', 'cpu_percent', 'memory_info']):
                try:
                    name = proc.info['name'].lower()
                    if 'league' in name:
                        processes.append({
                            'pid': proc.info['pid'],
                            'name': proc.info['name'],
                            'exe': proc.info['exe'] if proc.info['exe'] else '未知',
                            'cpu_percent': proc.info['cpu_percent'],
                            'memory_mb': proc.info['memory_info'].rss / (1024 * 1024) if proc.info['memory_info'] else 0
                        })
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
        except Exception as e:
            print(f"获取进程详细信息异常: {str(e)}")
        
        return processes
    
    def start_background_monitoring(self, interval=3):
        """启动后台监控线程"""
        def monitor_loop():
            while True:
                self.check_game_status()
                time.sleep(interval)
        
        thread = threading.Thread(target=monitor_loop, daemon=True)
        thread.start()
        return thread