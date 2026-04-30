#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""简化测试"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("简化测试")
print("=" * 60)

# 测试1: 导入
print("\n[1] 导入data_spider...")
try:
    from data_spider import DataSpider
    print("OK")
except Exception as e:
    print(f"Failed: {e}")
    sys.exit(1)

# 测试2: 初始化
print("\n[2] 初始化DataSpider...")
try:
    spider = DataSpider()
    print(f"OK - Hero: {len(spider.hero_data)}, Items: {len(spider.items_data)}")
except Exception as e:
    print(f"Failed: {e}")

# 测试3: 获取排名
print("\n[3] 获取英雄排名...")
try:
    rankings = spider.get_champion_rankings(force_refresh=False)
    print(f"OK - Source: {rankings.get('source')}, Count: {len(rankings.get('all', []))}")
except Exception as e:
    print(f"Failed: {e}")

# 测试4: 获取出装
print("\n[4] 获取英雄出装...")
try:
    builds = spider.get_champion_builds("Ahri", "MIDDLE")
    print(f"OK - Champion: {builds.get('champion_name')}, Source: {builds.get('source')}")
except Exception as e:
    print(f"Failed: {e}")

# 测试5: 更新数据
print("\n[5] 测试更新功能...")
try:
    result = spider.force_update_all_data()
    print(f"OK - Success: {len(result.get('success', []))}, Failed: {len(result.get('failed', []))}")
except Exception as e:
    print(f"Failed: {e}")

print("\n" + "=" * 60)
print("测试完成")
print("=" * 60)
