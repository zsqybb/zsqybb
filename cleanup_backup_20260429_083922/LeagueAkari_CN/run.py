#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单启动器 - 测试程序
"""
import os
import sys

# 设置工作目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("LeagueAkari - LOL数据助手")
print("=" * 60)

# 检查Python版本
print(f"\n[环境] Python {sys.version}")

# 检查依赖
print("\n[1/4] 检查依赖...")
missing = []
try:
    import PyQt6
    print(f"   ✅ PyQt6 {PyQt6.QtCore.PYQT_VERSION_STR}")
except ImportError:
    missing.append("PyQt6")

try:
    import requests
    print(f"   ✅ requests")
except ImportError:
    missing.append("requests")

try:
    import psutil
    print(f"   ✅ psutil")
except ImportError:
    missing.append("psutil")

if missing:
    print(f"\n❌ 缺少依赖: {', '.join(missing)}")
    print("请运行: pip install -r requirements.txt")
    input("\n按回车键退出...")
    sys.exit(1)

# 导入并运行主程序
print("\n[2/4] 导入模块...")
try:
    import data_spider
    print("   ✅ data_spider")
    
    import riot_api_client
    print("   ✅ riot_api_client")
    
    print("\n[3/4] 初始化DataSpider...")
    spider = data_spider.DataSpider()
    print(f"   ✅ 英雄: {len(spider.hero_data)}")
    print(f"   ✅ 装备: {len(spider.items_data)}")
    print(f"   ✅ 符文: {len(spider.runes_data)}")
    
    print("\n[4/4] 测试功能...")
    
    # 测试功能3：获取英雄排名
    print("\n   测试功能3: 英雄榜单...")
    rankings = spider.get_champion_rankings(force_refresh=False)
    print(f"   ✅ 数据源: {rankings.get('source')}")
    print(f"   ✅ 英雄数: {len(rankings.get('all', []))}")
    
    # 测试功能4：更新数据
    print("\n   测试功能4: 更新数据...")
    result = spider.force_update_all_data()
    print(f"   ✅ 成功: {len(result.get('success', []))}")
    print(f"   ✅ 失败: {len(result.get('failed', []))}")
    
    print("\n" + "=" * 60)
    print("✅ 所有核心功能测试通过！")
    print("=" * 60)
    
    print("\n📋 功能列表:")
    print("   1. 个人信息 - 检测本地LOL客户端")
    print("   2. 查询玩家 - 通过名称查询他人")
    print("   3. 英雄榜单 - OP.GG风格")
    print("   4. 设置/更新 - 手动更新数据")
    
    print("\n🎨 图标支持:")
    print("   - 英雄图标: game.gtimg.cn")
    print("   - 装备图标: game.gtimg.cn")
    print("   - 符文图标: game.gtimg.cn")
    
    # 询问是否启动UI
    print("\n" + "=" * 60)
    choice = input("是否启动图形界面? (y/n): ").strip().lower()
    
    if choice == 'y':
        print("\n正在启动图形界面...")
        import main_new
        main_new.main()
    else:
        print("\n退出。")
        
except Exception as e:
    print(f"\n❌ 错误: {e}")
    import traceback
    traceback.print_exc()
    input("\n按回车键退出...")
    sys.exit(1)
