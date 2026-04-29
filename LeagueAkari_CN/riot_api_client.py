"""
Riot API 客户端 - 国服专用
支持：Account-V1, Summoner-V4, Champion-Mastery-V4, Match-V5
API密钥：RGAPI-3e6004c5-1943-4264-8a14-417f66ce6e48
"""

import requests
import json
import time
from typing import Optional, Dict, List

class RiotAPIClient:
    """Riot API 客户端（国服专用）"""
    
    # API密钥（国服可用）
    API_KEY = "RGAPI-3e6004c5-1943-4264-8a14-417f66ce6e48"
    
    # API端点
    ASIA_API = "https://asia.api.riotgames.com"  # Account-V1, Match-V5
    CN_API = "https://cn.api.riotgames.com"      # Summoner-V4, Champion-Mastery-V4
    
    def __init__(self, api_key: Optional[str] = None):
        """
        初始化API客户端
        
        Args:
            api_key: Riot API密钥（可选，默认使用内置密钥）
        """
        self.api_key = api_key or self.API_KEY
        self.session = requests.Session()
        self.session.headers.update({
            "X-Riot-Token": self.api_key,
            "User-Agent": "LeagueAkari_CN/1.0"
        })
    
    def _request(self, url: str, params: Optional[Dict] = None) -> Dict:
        """
        发送API请求
        
        Args:
            url: API URL
            params: 查询参数
            
        Returns:
            dict: 响应数据
        """
        if params is None:
            params = {}
        
        # 添加API密钥
        params["api_key"] = self.api_key
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API请求失败: {e}")
            return {"error": str(e)}
    
    # ==================== 1. Account-V1 ====================
    def get_account_by_riot_id(self, game_name: str, tag_line: str = "CN") -> Dict:
        """
        通过游戏名和标签获取账号信息（Account-V1）
        
        Args:
            game_name: 游戏名（如 "玩家名"）
            tag_line: 标签（默认 "CN"）
            
        Returns:
            dict: 账号信息，包含 puuid
        """
        url = f"{self.ASIA_API}/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
        return self._request(url)
    
    # ==================== 2. Summoner-V4 ====================
    def get_summoner_by_puuid(self, puuid: str) -> Dict:
        """
        通过puuid获取召唤师信息（Summoner-V4）
        
        Args:
            puuid: 玩家唯一ID
            
        Returns:
            dict: 召唤师信息（等级、头像、ID等）
        """
        url = f"{self.CN_API}/lol/summoner/v4/summoners/by-puuid/{puuid}"
        return self._request(url)
    
    def get_summoner_by_name(self, summoner_name: str) -> Dict:
        """
        通过召唤师名称获取召唤师信息（Summoner-V4）
        
        Args:
            summoner_name: 召唤师名称
            
        Returns:
            dict: 召唤师信息
        """
        url = f"{self.CN_API}/lol/summoner/v4/summoners/by-name/{summoner_name}"
        return self._request(url)
    
    # ==================== 3. Champion-Mastery-V4 ====================
    def get_champion_mastery(self, puuid: str, champion_id: int) -> Dict:
        """
        获取指定英雄的熟练度（Champion-Mastery-V4）
        
        Args:
            puuid: 玩家唯一ID
            champion_id: 英雄ID（阿卡丽=84）
            
        Returns:
            dict: 英雄熟练度信息
        """
        url = f"{self.CN_API}/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/by-champion/{champion_id}"
        return self._request(url)
    
    def get_all_champion_masteries(self, puuid: str) -> List[Dict]:
        """
        获取所有英雄的熟练度
        
        Args:
            puuid: 玩家唯一ID
            
        Returns:
            list: 所有英雄熟练度列表
        """
        url = f"{self.CN_API}/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}"
        return self._request(url)
    
    # ==================== 4. Match-V5 ====================
    def get_match_ids_by_puuid(self, puuid: str, count: int = 20) -> List[str]:
        """
        获取玩家的比赛ID列表（Match-V5）
        
        Args:
            puuid: 玩家唯一ID
            count: 获取的比赛数量（默认20）
            
        Returns:
            list: 比赛ID列表
        """
        url = f"{self.ASIA_API}/lol/match/v5/matches/by-puuid/{puuid}/ids"
        params = {"count": count}
        return self._request(url, params)
    
    def get_match_details(self, match_id: str) -> Dict:
        """
        获取比赛详情（Match-V5）
        
        Args:
            match_id: 比赛ID
            
        Returns:
            dict: 比赛详情（包含KDA、出装、符文等）
        """
        url = f"{self.ASIA_API}/lol/match/v5/matches/{match_id}"
        return self._request(url)
    
    # ==================== 综合功能 ====================
    def get_player_info(self, game_name: str, tag_line: str = "CN") -> Dict:
        """
        综合获取玩家信息（一键查询）
        
        Args:
            game_name: 游戏名
            tag_line: 标签（默认 "CN"）
            
        Returns:
            dict: 完整的玩家信息
        """
        result = {
            "game_name": game_name,
            "tag_line": tag_line,
            "success": False
        }
        
        # 1. 获取账号信息（Account-V1）
        account_info = self.get_account_by_riot_id(game_name, tag_line)
        if "error" in account_info:
            result["error"] = "获取账号信息失败"
            return result
        
        puuid = account_info.get("puuid")
        result["puuid"] = puuid
        result["account_info"] = account_info
        
        # 2. 获取召唤师信息（Summoner-V4）
        summoner_info = self.get_summoner_by_puuid(puuid)
        if "error" in summoner_info:
            result["error"] = "获取召唤师信息失败"
            return result
        
        result["summoner_info"] = summoner_info
        
        # 3. 获取英雄熟练度（Champion-Mastery-V4）
        champion_masteries = self.get_all_champion_masteries(puuid)
        if "error" not in champion_masteries:
            result["champion_masteries"] = champion_masteries[:5]  # 只取前5个
        
        # 4. 获取最近比赛（Match-V5）
        match_ids = self.get_match_ids_by_puuid(puuid, count=20)
        if "error" not in match_ids and len(match_ids) > 0:
            # 获取最近3场比赛详情
            matches = []
            for match_id in match_ids[:3]:
                match_details = self.get_match_details(match_id)
                if "error" not in match_details:
                    matches.append(match_details)
            result["recent_matches"] = matches
        
        result["success"] = True
        return result


# 测试代码
if __name__ == "__main__":
    import pprint
    
    # 创建API客户端
    client = RiotAPIClient()
    
    print("=" * 60)
    print("Riot API 客户端测试（国服）")
    print("=" * 60)
    
    # 测试：查询指定玩家
    game_name = "G2"  # 替换为你要查询的玩家名
    tag_line = "CN"
    
    print(f"\n正在查询玩家: {game_name}#{tag_line}")
    
    # 方法1：分步查询
    print("\n1. Account-V1（获取puuid）")
    account_info = client.get_account_by_riot_id(game_name, tag_line)
    pprint.pprint(account_info)
    
    if "puuid" in account_info:
        puuid = account_info["puuid"]
        
        print("\n2. Summoner-V4（获取召唤师信息）")
        summoner_info = client.get_summoner_by_puuid(puuid)
        pprint.pprint(summoner_info)
        
        print("\n3. Champion-Mastery-V4（获取阿卡丽熟练度）")
        akali_mastery = client.get_champion_mastery(puuid, 84)  # 阿卡丽ID=84
        pprint.pprint(akali_mastery)
        
        print("\n4. Match-V5（获取最近比赛）")
        match_ids = client.get_match_ids_by_puuid(puuid, count=5)
        print(f"最近5场比赛ID: {match_ids}")
        
        if match_ids:
            print("\n第一场比赛详情:")
            match_details = client.get_match_details(match_ids[0])
            pprint.pprint(match_details)
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
