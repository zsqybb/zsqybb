#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Riot Data Dragon API 测试脚本
无需API密钥，免费访问所有静态游戏数据
"""

import requests
import json
import time

class RiotDataDragonTester:
    """测试Riot Data Dragon API访问"""
    
    def __init__(self):
        self.base_url = "https://ddragon.leagueoflegends.com"
        self.cdn_base = "https://cdn.communitydragon.org"
        self.version = None
        
    def test_version_api(self):
        """测试1: 获取游戏版本列表"""
        print("=" * 60)
        print("测试1: 获取游戏版本列表")
        print("=" * 60)
        
        try:
            url = f"{self.base_url}/api/versions.json"
            print(f"请求URL: {url}")
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            versions = response.json()
            self.version = versions[0]  # 最新版本
            
            print(f"✅ 成功！")
            print(f"最新版本: {self.version}")
            print(f"前5个版本: {versions[:5]}")
            print(f"总计版本数: {len(versions)}")
            
            return True
            
        except Exception as e:
            print(f"❌ 失败: {e}")
            return False
    
    def test_champions_api(self):
        """测试2: 获取英雄列表"""
        print("\n" + "=" * 60)
        print("测试2: 获取英雄列表 (Data Dragon)")
        print("=" * 60)
        
        if not self.version:
            print("⚠️ 请先运行 test_version_api()")
            return False
        
        try:
            url = f"{self.base_url}/cdn/{self.version}/data/en_US/champion.json"
            print(f"请求URL: {url}")
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            champions = data['data']
            
            print(f"✅ 成功！")
            print(f"英雄总数: {len(champions)}")
            print(f"\n前5个英雄:")
            
            count = 0
            for champ_key, champ_data in champions.items():
                if count < 5:
                    print(f"  - {champ_data['name']} ({champ_data['id']})")
                    count += 1
            
            return True
            
        except Exception as e:
            print(f"❌ 失败: {e}")
            return False
    
    def test_champion_detail_api(self, champion_id="Aatrox"):
        """测试3: 获取英雄详情"""
        print("\n" + "=" * 60)
        print(f"测试3: 获取英雄详情 ({champ_id})")
        print("=" * 60)
        
        if not self.version:
            print("⚠️ 请先运行 test_version_api()")
            return False
        
        try:
            url = f"{self.base_url}/cdn/{self.version}/data/en_US/champion/{champion_id}.json"
            print(f"请求URL: {url}")
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            champ = data['data'][champion_id]
            
            print(f"✅ 成功！")
            print(f"英雄名称: {champ['name']}")
            print(f"称号: {champ['title']}")
            print(f"英雄类型: {champ['tags']}")
            print(f"基础生命值: {champ['stats']['hp']}")
            print(f"基础法力值: {champ['stats']['mp']}")
            print(f"技能数量: {len(champ['spells']) + 1}")  # +1 for passive
            
            return True
            
        except Exception as e:
            print(f"❌ 失败: {e}")
            return False
    
    def test_items_api(self):
        """测试4: 获取装备列表"""
        print("\n" + "=" * 60)
        print("测试4: 获取装备列表")
        print("=" * 60)
        
        if not self.version:
            print("⚠️ 请先运行 test_version_api()")
            return False
        
        try:
            url = f"{self.base_url}/cdn/{self.version}/data/en_US/item.json"
            print(f"请求URL: {url}")
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            items = data['data']
            
            print(f"✅ 成功！")
            print(f"装备总数: {len(items)}")
            print(f"\n前5个装备:")
            
            count = 0
            for item_id, item_data in items.items():
                if count < 5:
                    print(f"  - {item_data['name']} (ID: {item_id})")
                    count += 1
            
            return True
            
        except Exception as e:
            print(f"❌ 失败: {e}")
            return False
    
    def test_runes_api(self):
        """测试5: 获取符文数据"""
        print("\n" + "=" * 60)
        print("测试5: 获取符文数据")
        print("=" * 60)
        
        if not self.version:
            print("⚠️ 请先运行 test_version_api()")
            return False
        
        try:
            url = f"{self.cdn_base}/{self.version}/cdragon/lolpony/plugin/rcp-be-lol-game-data/global/default/v1/perks.json"
            print(f"请求URL: {url}")
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            runes = response.json()
            
            print(f"✅ 成功！")
            print(f"符文总数: {len(runes)}")
            print(f"\n前5个符文:")
            
            for i, rune in enumerate(runes[:5]):
                print(f"  - {rune.get('name', 'Unknown')} (ID: {rune.get('id', 'Unknown')})")
            
            return True
            
        except Exception as e:
            print(f"❌ 失败: {e}")
            return False
    
    def test_champion_icon(self, champion_id="Aatrox"):
        """测试6: 获取英雄头像"""
        print("\n" + "=" * 60)
        print(f"测试6: 获取英雄头像 ({champion_id})")
        print("=" * 60)
        
        if not self.version:
            print("⚠️ 请先运行 test_version_api()")
            return False
        
        try:
            url = f"{self.base_url}/cdn/{self.version}/img/champion/{champion_id}.png"
            print(f"请求URL: {url}")
            
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            print(f"✅ 成功！")
            print(f"图片大小: {len(response.content)} bytes")
            print(f"Content-Type: {response.headers.get('Content-Type')}")
            
            # 保存图片
            filename = f"champion_{champion_id}.png"
            with open(filename, 'wb') as f:
                f.write(response.content)
            print(f"已保存到: {filename}")
            
            return True
            
        except Exception as e:
            print(f"❌ 失败: {e}")
            return False
    
    def run_all_tests(self):
        """运行所有测试"""
        print("\n" + "🚀" * 30)
        print("Riot Data Dragon API 测试开始")
        print("🚀" * 30 + "\n")
        
        results = []
        
        # 测试1: 版本API
        results.append(("版本列表", self.test_version_api()))
        time.sleep(1)
        
        # 测试2: 英雄列表
        results.append(("英雄列表", self.test_champions_api()))
        time.sleep(1)
        
        # 测试3: 英雄详情
        results.append(("英雄详情", self.test_champion_detail_api()))
        time.sleep(1)
        
        # 测试4: 装备列表
        results.append(("装备列表", self.test_items_api()))
        time.sleep(1)
        
        # 测试5: 符文数据
        results.append(("符文数据", self.test_runes_api()))
        time.sleep(1)
        
        # 测试6: 英雄头像
        results.append(("英雄头像", self.test_champion_icon()))
        
        # 汇总结果
        print("\n" + "=" * 60)
        print("测试汇总")
        print("=" * 60)
        
        success_count = 0
        for test_name, result in results:
            status = "✅ 成功" if result else "❌ 失败"
            print(f"{test_name}: {status}")
            if result:
                success_count += 1
        
        print(f"\n总计: {success_count}/{len(results)} 个测试通过")
        
        if success_count == len(results):
            print("\n🎉 所有测试通过！你可以使用 Data Dragon API 获取数据")
            print("📝 无需API密钥，完全免费！")
        else:
            print("\n⚠️ 部分测试失败，请检查网络连接")

def main():
    tester = RiotDataDragonTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()
