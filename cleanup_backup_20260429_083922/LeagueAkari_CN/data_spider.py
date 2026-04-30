"""
数据爬取模块 - 集成Riot API（国服）
支持：个人信息、查询他人、英雄榜单、数据更新
"""

import json
import time
import requests
from typing import Dict, List, Optional
from riot_api_client import RiotAPIClient


class DataSpider:
    """数据爬取器（集成Riot API）"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化数据爬取器
        
        Args:
            api_key: Riot API密钥（可选）
        """
        self.api_client = RiotAPIClient(api_key)
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
    
    # ==================== 功能1：个人信息 ====================
    def get_self_info(self, game_name: str, tag_line: str = "CN") -> Dict:
        """
        获取自己的信息（功能1）
        
        Args:
            game_name: 游戏名
            tag_line: 标签（默认 "CN"）
            
        Returns:
            dict: 个人信息
        """
        print(f"[功能1] 正在查询个人信息: {game_name}#{tag_line}")
        result = self.api_client.get_player_info(game_name, tag_line)
        
        if result.get("success"):
            print(f"[功能1] 查询成功！")
            return {
                "success": True,
                "data": result
            }
        else:
            error_msg = result.get("error", "未知错误")
            print(f"[功能1] 查询失败: {error_msg}")
            return {
                "success": False,
                "error": error_msg
            }
    
    # ==================== 功能2：查询他人 ====================
    def search_player(self, game_name: str, tag_line: str = "CN") -> Dict:
        """
        查询其他玩家信息（功能2）
        
        Args:
            game_name: 游戏名
            tag_line: 标签（默认 "CN"）
            
        Returns:
            dict: 玩家信息
        """
        print(f"[功能2] 正在查询玩家: {game_name}#{tag_line}")
        result = self.api_client.get_player_info(game_name, tag_line)
        
        if result.get("success"):
            print(f"[功能2] 查询成功！")
            return {
                "success": True,
                "data": result
            }
        else:
            error_msg = result.get("error", "未知错误")
            print(f"[功能2] 查询失败: {error_msg}")
            return {
                "success": False,
                "error": error_msg
            }
    
    # ==================== 功能3：英雄榜单 ====================
    def get_champion_tier_list(self, lane: str = "ALL") -> Dict:
        """
        获取英雄榜单（功能3）- OP.GG风格
        
        Args:
            lane: 分路（TOP, JUNGLE, MID, ADC, SUPPORT, ALL）
            
        Returns:
            dict: 英雄榜单数据
        """
        print(f"[功能3] 正在获取英雄榜单（分路: {lane}）")
        
        try:
            # 从腾讯CDN获取英雄数据
            url = "https://game.gtimg.cn/images/lol/act/img/js/heroList/hero_list.js"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # 解析数据
            data = response.json()
            heroes = data.get("hero", [])
            
            # 过滤分路（如果有位置信息）
            if lane != "ALL":
                # 这里需要根据英雄位置过滤，暂时返回全部
                pass
            
            # 构建榜单数据（模拟胜率、选取率）
            tier_list = []
            for idx, hero in enumerate(heroes[:50], 1):  # 只取前50个
                tier_list.append({
                    "rank": idx,
                    "hero_id": hero.get("heroId"),
                    "hero_name": hero.get("name"),
                    "hero_title": hero.get("title"),
                    "win_rate": 50.0 + (idx % 10),  # 模拟胜率
                    "pick_rate": 10.0 - (idx % 5),   # 模拟选取率
                    "tier": "S" if idx <= 5 else ("A" if idx <= 15 else ("B" if idx <= 30 else "C"))
                })
            
            print(f"[功能3] 获取成功！共 {len(tier_list)} 个英雄")
            return {
                "success": True,
                "data": tier_list
            }
            
        except Exception as e:
            print(f"[功能3] 获取失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_champion_build(self, champion_id: int) -> Dict:
        """
        获取英雄出装和符文推荐
        
        Args:
            champion_id: 英雄ID
            
        Returns:
            dict: 出装和符文数据
        """
        print(f"[功能3] 正在获取英雄 {champion_id} 的出装和符文")
        
        try:
            # 从腾讯CDN获取出装数据
            url = f"https://game.gtimg.cn/images/lol/act/img/js/hero/{champion_id}.js"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                "success": True,
                "data": {
                    "items": data.get("items", []),
                    "runes": data.get("runes", []),
                    "skills": data.get("skills", [])
                }
            }
            
        except Exception as e:
            print(f"[功能3] 获取出装失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    # ==================== 功能4：更新数据 ====================
    def update_all_data(self) -> Dict:
        """
        更新所有数据（功能4）
        
        Returns:
            dict: 更新结果
        """
        print(f"[功能4] 开始更新数据...")
        
        result = {
            "success": True,
            "details": []
        }
        
        # 1. 更新英雄列表
        try:
            print("[功能4] 正在更新英雄列表...")
            url = "https://game.gtimg.cn/images/lol/act/img/js/heroList/hero_list.js"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            heroes = data.get("hero", [])
            
            result["details"].append({
                "name": "英雄列表",
                "status": "成功",
                "count": len(heroes)
            })
            print(f"[功能4] 英雄列表更新成功！共 {len(heroes)} 个英雄")
            
        except Exception as e:
            result["details"].append({
                "name": "英雄列表",
                "status": f"失败: {e}",
                "count": 0
            })
            print(f"[功能4] 英雄列表更新失败: {e}")
        
        # 2. 更新装备数据
        try:
            print("[功能4] 正在更新装备数据...")
            url = "https://game.gtimg.cn/images/lol/act/img/js/items/item_list.js"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            items = data.get("data", [])
            
            result["details"].append({
                "name": "装备数据",
                "status": "成功",
                "count": len(items)
            })
            print(f"[功能4] 装备数据更新成功！共 {len(items)} 件装备")
            
        except Exception as e:
            result["details"].append({
                "name": "装备数据",
                "status": f"失败: {e}",
                "count": 0
            })
            print(f"[功能4] 装备数据更新失败: {e}")
        
        # 3. 更新符文数据
        try:
            print("[功能4] 正在更新符文数据...")
            url = "https://game.gtimg.cn/images/lol/act/img/js/runes/perk_list.js"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            runes = data.get("data", [])
            
            result["details"].append({
                "name": "符文数据",
                "status": "成功",
                "count": len(runes)
            })
            print(f"[功能4] 符文数据更新成功！共 {len(runes)} 个符文")
            
        except Exception as e:
            result["details"].append({
                "name": "符文数据",
                "status": f"失败: {e}",
                "count": 0
            })
            print(f"[功能4] 符文数据更新失败: {e}")
        
        print(f"[功能4] 数据更新完成！")
        return result
    
    # ==================== 辅助功能 ====================
    def get_hero_icon_url(self, hero_id: str) -> str:
        """
        获取英雄图标URL
        
        Args:
            hero_id: 英雄ID
            
        Returns:
            str: 图标URL
        """
        return f"https://game.gtimg.cn/images/lol/act/img/champion/{hero_id}.png"
    
    def get_item_icon_url(self, item_id: str) -> str:
        """
        获取装备图标URL
        
        Args:
            item_id: 装备ID
            
        Returns:
            str: 图标URL
        """
        return f"https://game.gtimg.cn/images/lol/act/img/item/{item_id}.png"
    
    def get_rune_icon_url(self, rune_id: str) -> str:
        """
        获取符文图标URL
        
        Args:
            rune_id: 符文ID
            
        Returns:
            str: 图标URL
        """
        return f"https://game.gtimg.cn/images/lol/act/img/perk/{rune_id}.png"


# 测试代码
if __name__ == "__main__":
    spider = DataSpider()
    
    print("=" * 60)
    print("数据爬取模块测试")
    print("=" * 60)
    
    # 测试功能1：个人信息
    print("\n>>> 测试功能1：个人信息")
    result1 = spider.get_self_info("G2", "CN")
    print(json.dumps(result1, indent=2, ensure_ascii=False))
    
    # 测试功能2：查询他人
    print("\n>>> 测试功能2：查询他人")
    result2 = spider.search_player("Faker", "CN")
    print(json.dumps(result2, indent=2, ensure_ascii=False))
    
    # 测试功能3：英雄榜单
    print("\n>>> 测试功能3：英雄榜单")
    result3 = spider.get_champion_tier_list("ALL")
    print(json.dumps(result3, indent=2, ensure_ascii=False))
    
    # 测试功能4：更新数据
    print("\n>>> 测试功能4：更新数据")
    result4 = spider.update_all_data()
    print(json.dumps(result4, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
