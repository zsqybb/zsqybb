#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API连接测试脚本 - 验证您注册的API Key是否有效
使用方法:
1. 先注册API并获取API Key
2. 将API Key填入 api_config.json
3. 运行此脚本: python test_api_connection.py
"""

import sys
import json
import requests

# 添加当前目录到路径
sys.path.insert(0, sys.path[0])

from data_spider import DataSpider

def test_riot_api(api_key, region="na1"):
    """测试Riot API连接"""
    print("\n" + "="*60)
    print("测试1: Riot Games官方API")
    print("="*60)
    
    # 测试获取版本信息
    url = f"https://{region}.api.riotgames.com/lol/status/v4/platform-data"
    headers = {"X-Riot-Token": api_key}
    
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            print(f"✅ Riot API连接成功!")
            print(f"   服务器: {data.get('name', 'Unknown')}")
            print(f"   状态: {data.get('status', {}).get('name', 'Unknown')}")
            return True
        elif resp.status_code == 403:
            print(f"❌ API Key无效或已过期 (403 Forbidden)")
            print(f"   请检查api_config.json中的riot_api.api_key是否正确")
            return False
        elif resp.status_code == 429:
            print(f"⚠️  请求次数超限 (429 Too Many Requests)")
            print(f"   免费版限制: 100 requests/24小时")
            return False
        else:
            print(f"❌ 请求失败 (状态码: {resp.status_code})")
            print(f"   响应: {resp.text[:200]}")
            return False
            
    except Exception as e:
        print(f"❌ 连接失败: {e}")
        return False

def test_opgg_api(api_key):
    """测试OP.GG API连接"""
    print("\n" + "="*60)
    print("测试2: OP.GG API")
    print("="*60)
    
    # OP.GG API端点可能因版本而异
    url = "https://opgg-api.com/api/v1/champions"
    headers = {"Authorization": f"Bearer {api_key}"}
    
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        
        if resp.status_code == 200:
            print(f"✅ OP.GG API连接成功!")
            data = resp.json()
            print(f"   返回数据量: {len(data) if isinstance(data, list) else 'N/A'}")
            return True
        elif resp.status_code == 401:
            print(f"❌ API Key无效 (401 Unauthorized)")
            return False
        else:
            print(f"⚠️  OP.GG API可能不可用 (状态码: {resp.status_code})")
            print(f"   注: OP.GG API可能需要特殊权限")
            return False
            
    except Exception as e:
        print(f"⚠️  OP.GG API连接失败: {e}")
        print(f"   注: OP.GG可能不对外提供公开API")
        return False

def test_champion_gg_api(api_key):
    """测试Champion.gg API连接"""
    print("\n" + "="*60)
    print("测试3: Champion.gg API")
    print("="*60)
    
    url = "https://champion.gg/api/champions"
    headers = {"X-API-Key": api_key}
    
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        
        if resp.status_code == 200:
            print(f"✅ Champion.gg API连接成功!")
            return True
        else:
            print(f"⚠️  Champion.gg API可能不可用 (状态码: {resp.status_code})")
            return False
            
    except Exception as e:
        print(f"⚠️  Champion.gg API连接失败: {e}")
        return False

def test_tencent_cdn():
    """测试腾讯CDN公开数据"""
    print("\n" + "="*60)
    print("测试4: 腾讯官方CDN (无需API Key)")
    print("="*60)
    
    url = "https://game.gtimg.cn/images/lol/act/img/js/heroList/hero_list.js"
    
    try:
        resp = requests.get(url, timeout=10)
        
        if resp.status_code == 200:
            data = resp.json()
            hero_count = len(data.get('hero', []))
            print(f"✅ 腾讯CDN连接成功!")
            print(f"   英雄数量: {hero_count}")
            return True
        else:
            print(f"❌ 腾讯CDN连接失败 (状态码: {resp.status_code})")
            return False
            
    except Exception as e:
        print(f"❌ 腾讯CDN连接失败: {e}")
        return False

def test_data_spider():
    """测试DataSpider类"""
    print("\n" + "="*60)
    print("测试5: DataSpider类集成测试")
    print("="*60)
    
    try:
        spider = DataSpider()
        
        # 加载API配置
        config_loaded = spider.load_api_config()
        if config_loaded:
            print(f"✅ API配置加载成功")
            print(f"   Riot API: {'启用' if spider.riot_api_enabled else '禁用'}")
            print(f"   OP.GG API: {'启用' if spider.opgg_api_enabled else '禁用'}")
        else:
            print(f"⚠️  API配置加载失败，将使用默认数据源")
        
        # 测试获取英雄列表
        print(f"\n   测试获取英雄列表...")
        heroes = spider.get_all_hero_names()
        if heroes:
            print(f"✅ 成功获取 {len(heroes)} 个英雄")
            print(f"   示例: {heroes[:3]}")
        else:
            print(f"❌ 获取英雄列表失败")
        
        # 测试获取英雄详情
        print(f"\n   测试获取英雄详情 (亚索)...")
        detail = spider.get_champ_detail("亚索")
        if detail:
            print(f"✅ 成功获取英雄详情")
            print(f"   数据源: {detail.get('source', 'unknown')}")
        else:
            print(f"❌ 获取英雄详情失败")
        
        return True
        
    except Exception as e:
        print(f"❌ DataSpider测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主测试流程"""
    print("\n" + "="*60)
    print("  LOL数据API连接测试工具")
    print("  版本: 2026-04-28")
    print("="*60)
    
    # 读取配置
    config = {}
    config_path = "api_config.json"
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        print(f"\n✅ 配置文件加载成功: {config_path}")
    except Exception as e:
        print(f"\n⚠️  配置文件加载失败: {e}")
        print(f"   将仅测试公开数据源")
    
    # 测试各项API
    results = {}
    
    # 测试Riot API
    riot_config = config.get("riot_api", {})
    if riot_config.get("enabled", False):
        api_key = riot_config.get("api_key", "")
        if api_key and api_key != "YOUR_RIOT_API_KEY_HERE":
            results["riot"] = test_riot_api(api_key, riot_config.get("region", "na1"))
        else:
            print(f"\n⚠️  Riot API已启用但未配置API Key")
            results["riot"] = False
    else:
        print(f"\n⚠️  Riot API未启用，跳过测试")
        results["riot"] = None
    
    # 测试OP.GG API
    opgg_config = config.get("opgg_api", {})
    if opgg_config.get("enabled", False):
        api_key = opgg_config.get("api_key", "")
        if api_key and api_key != "YOUR_OPGG_API_KEY_HERE":
            results["opgg"] = test_opgg_api(api_key)
        else:
            print(f"\n⚠️  OP.GG API已启用但未配置API Key")
            results["opgg"] = False
    else:
        print(f"\n⚠️  OP.GG API未启用，跳过测试")
        results["opgg"] = None
    
    # 测试Champion.gg API
    cgg_config = config.get("champion_gg", {})
    if cgg_config.get("enabled", False):
        api_key = cgg_config.get("api_key", "")
        if api_key and api_key != "YOUR_CHAMPIONGG_API_KEY_HERE":
            results["champion_gg"] = test_champion_gg_api(api_key)
        else:
            print(f"\n⚠️  Champion.gg API已启用但未配置API Key")
            results["champion_gg"] = False
    else:
        print(f"\n⚠️  Champion.gg API未启用，跳过测试")
        results["champion_gg"] = None
    
    # 测试腾讯CDN (总是测试)
    results["tencent"] = test_tencent_cdn()
    
    # 测试DataSpider集成
    results["spider"] = test_data_spider()
    
    # 输出测试报告
    print("\n" + "="*60)
    print("  测试报告")
    print("="*60)
    
    for name, result in results.items():
        if result is None:
            status = "⚠️  未启用"
        elif result:
            status = "✅ 成功"
        else:
            status = "❌ 失败"
        print(f"  {name.upper():15s}: {status}")
    
    print("\n" + "="*60)
    print("  下一步操作建议")
    print("="*60)
    
    if not any(results.values()):
        print("\n❌ 所有API测试均失败！")
        print("\n建议操作:")
        print("  1. 检查网络连接")
        print("  2. 检查API Key是否正确")
        print("  3. 查看 'API注册流程指南.md' 重新注册")
        print("  4. 尝试使用腾讯CDN公开数据 (无需注册)")
    else:
        print("\n✅ 部分API测试成功！")
        print("\n建议操作:")
        if not results.get("riot"):
            print("  1. 注册Riot API: https://developer.riotgames.com/")
        if not results.get("tencent"):
            print("  2. 检查腾讯CDN是否被防火墙拦截")
        print("  3. 修改 api_config.json 启用成功的API")
        print("  4. 运行主程序测试: python main.py")
    
    print("\n" + "="*60)
    print("测试完成！")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
