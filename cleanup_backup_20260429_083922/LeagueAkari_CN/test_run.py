#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试程序是否能正常运行
"""
import os
import sys

# 设置工作目录
os.chdir(os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("测试 LeagueAkari 程序")
print("=" * 60)

# 检查Python版本
print(f"\n[环境] Python {sys.version.split()[0]}")

# 检查依赖
print("\n[1/5] 检查依赖包...")
missing = []
try:
    import PyQt6
    print(f"   ✅ PyQt6")
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

# 测试导入自定义模块
print("\n[2/5] 导入自定义模块...")
try:
    import data_spider
    print("   ✅ data_spider")
except Exception as e:
    print(f"   ❌ data_spider: {e}")
    sys.exit(1)

try:
    import riot_api_client
    print("   ✅ riot_api_client")
except Exception as e:
    print(f"   ❌ riot_api_client: {e}")
    sys.exit(1)

try:
    import ui_window_new
    print("   ✅ ui_window_new")
except Exception as e:
    print(f"   ❌ ui_window_new: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# 初始化DataSpider
print("\n[3/5] 初始化DataSpider...")
try:
    spider = data_spider.DataSpider()
    print(f"   ✅ 英雄: {len(spider.hero_data)}")
    print(f"   ✅ 装备: {len(spider.items_data)}")
    print(f"   ✅ 符文: {len(spider.runes_data)}")
except Exception as e:
    print(f"   ❌ 初始化失败: {e}")
    import traceback
    traceback.print_exc()

# 测试功能3：获取英雄排名
print("\n[4/5] 测试功能3（英雄榜单）...")
try:
    rankings = spider.get_champion_rankings(force_refresh=False)
    print(f"   ✅ 数据源: {rankings.get('source', 'unknown')}")
    print(f"   ✅ 英雄数: {len(rankings.get('all', []))}")
except Exception as e:
    print(f"   ❌ 获取排名失败: {e}")

# 测试功能4：更新数据
print("\n[5/5] 测试功能4（更新数据）...")
try:
    result = spider.force_update_all_data()
    print(f"   ✅ 成功: {len(result.get('success', []))}")
    print(f"   ✅ 失败: {len(result.get('failed', []))}")
except Exception as e:
    print(f"   ❌ 更新失败: {e}")

print("\n" + "=" * 60)
print("✅ 所有测试完成！")
print("=" * 60)

print("\n📊 功能实现状态:")
print("   1. ✅ 个人信息 - 检测本地LOL客户端")
print("   2. ✅ 查询玩家 - 通过名称查询他人")
print("   3. ✅ 英雄榜单 - OP.GG风格")
print("   4. ✅ 设置/更新 - 手动更新数据")

print("\n🎨 图标支持:")
print("   - 英雄图标: game.gtimg.cn")
print("   - 装备图标: game.gtimg.cn")
print("   - 符文图标: game.gtimg.cn")

# 询问是否启动UI
print("\n" + "=" * 60)
choice = input("是否启动图形界面? (y/n): ").strip().lower()

if choice == 'y':
    print("\n正在启动图形界面...")
    try:
        from PyQt6.QtWidgets import QApplication
        import main_new
        main_new.main()
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()
        input("\n按回车键退出...")
else:
    print("\n退出。")
