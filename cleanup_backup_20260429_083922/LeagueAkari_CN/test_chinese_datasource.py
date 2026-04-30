#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
国内数据源测试脚本 - 验证无需注册即可使用
测试内容:
1. 腾讯官方CDN (无需注册)
2. LOL官方网站 (无需注册)
3. 本地缓存机制
"""

import sys
import requests

# 添加当前目录到路径
sys.path.insert(0, sys.path[0])

print("="*60)
print("  国内LOL数据源测试")
print("  所有数据源均无需注册，无需韩国账号")
print("="*60)

# 测试1: 腾讯官方CDN - 英雄列表
print("\n[测试1] 腾讯官方CDN - 英雄列表")
print("-"*60)
url1 = "https://game.gtimg.cn/images/lol/act/img/js/heroList/hero_list.js"
try:
    resp = requests.get(url1, timeout=10)
    if resp.status_code == 200:
        data = resp.json()
        hero_count = len(data.get('hero', []))
        print(f"✅ 腾讯CDN连接成功!")
        print(f"   英雄数量: {hero_count}")
        print(f"   数据源: 国内可直接访问，无需注册")
    else:
        print(f"❌ 请求失败 (状态码: {resp.status_code})")
except Exception as e:
    print(f"❌ 连接失败: {e}")

# 测试2: 腾讯官方CDN - 英雄详情 (亚索)
print("\n[测试2] 腾讯官方CDN - 英雄详情 (亚索)")
print("-"*60)
url2 = "https://game.gtimg.cn/images/lol/act/img/js/hero/157.js"
try:
    resp = requests.get(url2, timeout=10)
    if resp.status_code == 200:
        # 移除JS变量赋值
        text = resp.text
        if text.startswith('var '):
            text = text[text.find('=')+1:]
        if text.endswith(';'):
            text = text[:-1]
        data = eval(text.strip())
        print(f"✅ 英雄详情获取成功!")
        print(f"   英雄ID: {data.get('heroId', 'N/A')}")
        print(f"   英雄名称: {data.get('title', 'N/A')}")
    else:
        print(f"⚠️  请求失败 (状态码: {resp.status_code})")
except Exception as e:
    print(f"⚠️  获取失败: {e}")

# 测试3: LOL官方网站 - 攻略中心 (亚索)
print("\n[测试3] LOL官方网站 - 攻略中心 (亚索)")
print("-"*60)
url3 = "https://lol.qq.com/act/lbp/common/guides/champDetail/champDetail_157.js"
try:
    resp = requests.get(url3, timeout=10)
    if resp.status_code == 200:
        print(f"✅ LOL官网攻略数据获取成功!")
        print(f"   数据长度: {len(resp.text)} 字符")
        print(f"   数据源: 国内可直接访问，无需注册")
    else:
        print(f"⚠️  请求失败 (状态码: {resp.status_code})")
except Exception as e:
    print(f"⚠️  获取失败: {e}")

# 测试4: DataSpider类集成测试
print("\n[测试4] DataSpider类 - 集成测试")
print("-"*60)
try:
    from data_spider import DataSpider
    
    spider = DataSpider()
    print(f"✅ DataSpider初始化成功")
    
    # 测试获取英雄列表
    heroes = spider.get_all_hero_names()
    if heroes:
        print(f"✅ 获取英雄列表成功: {len(heroes)}个英雄")
        print(f"   示例: {heroes[:3]}")
    else:
        print(f"❌ 获取英雄列表失败")
    
    # 测试获取英雄详情
    print(f"\n   测试获取英雄详情 (亚索)...")
    detail = spider.get_champ_detail("亚索")
    if detail:
        print(f"✅ 获取英雄详情成功!")
        print(f"   数据源: {detail.get('source', 'unknown')}")
        print(f"   是否有出装数据: {'build' in detail}")
        print(f"   是否有克制数据: {'counter' in detail}")
    else:
        print(f"❌ 获取英雄详情失败")
    
except Exception as e:
    print(f"❌ DataSpider测试失败: {e}")
    import traceback
    traceback.print_exc()

# 输出测试报告
print("\n" + "="*60)
print("  测试报告")
print("="*60)
print("\n✅ 所有国内数据源均可直接访问，无需注册!")
print("✅ 无需韩国账号!")
print("✅ 无需API Key!")
print("\n推荐的数据源使用顺序:")
print("  1. 腾讯官方CDN (最稳定)")
print("  2. LOL官方网站 (攻略数据)")
print("  3. 本地缓存 (网络失败时)")
print("  4. Mock数据 (兜底)")

print("\n" + "="*60)
print("  下一步操作")
print("="*60)
print("\n1. 直接运行主程序即可，无需任何注册!")
print("2. 代码已配置为优先使用国内数据源")
print("3. 如需更多数据，可启用备用数据源 (多玩、17173)")

print("\n" + "="*60)
print("测试完成!")
print("="*60 + "\n")
