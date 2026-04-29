#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LeagueAkari 国服复刻助手 - 主程序入口
主要功能：程序启动、全局调度、主窗口初始化
"""
import sys
import os
import traceback
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("LeagueAkari")

def setup_encoding():
    """设置编码环境，解决中文乱码问题"""
    # 设置标准输出编码
    if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
        try:
            sys.stdout.reconfigure(encoding='utf-8')
        except:
            pass
    if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
        try:
            sys.stderr.reconfigure(encoding='utf-8')
        except:
            pass

def check_dependencies():
    """检查依赖包是否安装"""
    missing = []
    try:
        import PyQt6
    except ImportError:
        missing.append('PyQt6')
    try:
        import requests
    except ImportError:
        missing.append('requests')
    try:
        import psutil
    except ImportError:
        missing.append('psutil')
    try:
        import bs4
    except ImportError:
        missing.append('beautifulsoup4')
    
    if missing:
        print(f"缺少依赖包: {', '.join(missing)}")
        print("正在自动安装...")
        import subprocess
        for pkg in missing:
            pkg_name = 'beautifulsoup4' if pkg == 'bs4' else pkg
            try:
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', pkg_name, '--quiet'])
                print(f"  ✓ {pkg_name} 安装成功")
            except Exception as e:
                print(f"  ✗ {pkg_name} 安装失败: {str(e)}")
                return False
        print("所有依赖包安装完成！")
    return True

def load_config():
    """加载配置文件"""
    import configparser
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'config.ini')
    
    if os.path.exists(config_path):
        config.read(config_path, encoding='utf-8')
        logger.info(f"配置文件加载成功: {config_path}")
    else:
        # 生成默认配置
        config['UI'] = {
            'width': '400',
            'height': '600',
            'always_on_top': 'true',
            'refresh_interval': '3'
        }
        config['Data'] = {
            'cache_days': '7',
            'use_cache': 'true'
        }
        config['Game'] = {
            'auto_detect': 'true',
            'auto_connect': 'true',
            'show_notifications': 'true'
        }
        config['Window'] = {
            'position_x': '100',
            'position_y': '100',
            'opacity': '95',
            'theme': 'dark'
        }
        with open(config_path, 'w', encoding='utf-8') as f:
            config.write(f)
        logger.info("已生成默认配置文件")
    
    return config

def main():
    """程序主入口"""
    # 设置编码
    setup_encoding()
    
    try:
        # 设置工作目录为脚本所在目录
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)
        logger.info(f"工作目录: {script_dir}")
        
        # 检查依赖
        if not check_dependencies():
            input("依赖安装失败，按回车键退出...")
            sys.exit(1)
        
        # 加载配置
        config = load_config()
        
        # 导入Qt模块（在依赖检查之后）
        from PyQt6.QtWidgets import QApplication
        from PyQt6.QtCore import QTimer
        import ui_window
        import game_monitor
        import lcu_connect
        import data_spider
        
        # 创建Qt应用
        app = QApplication(sys.argv)
        app.setApplicationName("LeagueAkari 国服复刻助手")
        app.setQuitOnLastWindowClosed(False)  # 关闭窗口不退出（支持托盘）
        
        # 初始化各个模块
        monitor = game_monitor.GameMonitor()
        lcu_client = lcu_connect.LCUClient()
        spider = data_spider.DataSpider()
        
        # 创建主窗口
        window = ui_window.MainWindow(monitor, lcu_client, spider, config)
        window.show()
        
        # 启动游戏检测定时器
        refresh_interval = config.getint('UI', 'refresh_interval', fallback=3)
        game_timer = QTimer()
        game_timer.timeout.connect(lambda: monitor.check_game_status(window.update_game_status))
        game_timer.start(refresh_interval * 1000)  # 毫秒
        
        # 启动LCU连接检测
        lcu_timer = QTimer()
        lcu_timer.timeout.connect(lambda: lcu_client.auto_connect(window.update_lcu_status))
        lcu_timer.start(5000)  # 5秒检测一次
        
        # 初始立即检测一次
        monitor.check_game_status(window.update_game_status)
        lcu_client.auto_connect(window.update_lcu_status)
        
        logger.info("LeagueAkari 国服复刻助手已启动")
        logger.info("正在检测英雄联盟客户端...")
        
        # 运行应用事件循环
        sys.exit(app.exec())
        
    except ImportError as e:
        logger.error(f"模块导入失败: {str(e)}")
        logger.error("请确保已安装所有依赖包: pip install -r requirements.txt")
        input("按回车键退出...")
        sys.exit(1)
    except Exception as e:
        logger.error(f"程序启动失败: {str(e)}")
        traceback.print_exc()
        input("按回车键退出...")
        sys.exit(1)

if __name__ == "__main__":
    main()